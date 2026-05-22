"""Advance a product build through the lifecycle state machine."""

from __future__ import annotations

import json

from swe_architect_mcp.llm.base import LLMProvider
from swe_architect_mcp.models import (
    DecisionRecord,
    LifecyclePhase,
    PHASES,
    ProjectState,
    TraceabilityRecord,
    is_valid_phase,
    next_phase,
)
from swe_architect_mcp.prompts.phase import SYSTEM_PROMPT
from swe_architect_mcp.tools._llm import generate_with_fallback
from swe_architect_mcp.workspace import (
    WorkspaceError,
    append_markdown_log,
    load_state,
    project_dir,
    record_virtual_artifact,
    save_state,
    write_artifact,
)


PHASE_TITLES: dict[LifecyclePhase, str] = {
    "communication": "Communication",
    "requirements": "Requirements Engineering",
    "modeling": "Requirements Modeling",
    "design": "Solution Design",
    "planning": "Iteration Planning",
    "construction": "Construction Support",
    "testing": "Testing Strategy",
    "deployment": "Deployment And Handoff",
}

# Phase-specific interview questions — asked BEFORE generating the artifact.
# Derived from standard industry and academic software engineering principles.
# These ensure every universally-verified SDLC activity is covered.
PHASE_INTERVIEW_QUESTIONS: dict[LifecyclePhase, list[str]] = {
    # ── Communication (Inception + Feasibility Study) ─────────
    "communication": [
        "Who are the primary users and what is the single most important job "
        "each user needs to complete?",
        "What is the ONE workflow that must work for this product to be useful? "
        "(Tracer Bullet — the thinnest end-to-end slice)",
        "What can be EXPLICITLY left out of the first version? "
        "(Scope control — YAGNI)",
        "Are there any technology, security, budget, platform, or compliance "
        "constraints?",
        "FEASIBILITY CHECK: Is this idea technically feasible "
        "with available technology? Is it financially justified? Will users "
        "actually adopt it?",
        "How will you measure success? What does 'done' look like for v1?",
    ],
    # ── Requirements (Elicitation → Specification → Validation) ─
    "requirements": [
        "FUNCTIONAL: What are ALL the things the system must DO? "
        "(list each action the user or system performs)",
        "NON-FUNCTIONAL: What qualities must the system HAVE? "
        "- Product: performance, reliability, usability, efficiency? "
        "- Organizational: development standards, delivery timeline? "
        "- External: regulatory, legal, ethical, interoperability?",
        "DOMAIN: Are there any business rules specific to this domain that a "
        "developer might not know about?",
        "INVERSE: What must the system NEVER do? (security, safety, data loss)",
        "ACCEPTANCE CRITERIA: For each major feature, how would you verify it "
        "works? What is the pass/fail test?",
        "CONSTRAINTS: Any mandated technology, database, platform, or "
        "integration requirements?",
    ],
    # ── Modeling (4 perspectives, 5 UML diagrams) ──────
    "modeling": [
        "INTERACTIONS: Which requirements involve the most complex user "
        "interaction or branching workflows?",
        "DATA ENTITIES: What are the main data objects? How do they relate to "
        "each other? (e.g., User has many Orders, Order has many Items)",
        "BEHAVIOR: Are there objects with a lifecycle? (e.g., Order: "
        "created→confirmed→shipped→delivered→cancelled)",
        "EXTERNAL BOUNDARIES: Which parts of the system interact with external "
        "services, APIs, or third-party systems?",
        "MAIN WORKFLOW: Can you walk through the primary workflow step by step, "
        "including what happens when something goes wrong?",
    ],
    # ── Design (4 design activities, 9 questions) ──────
    "design": [
        "ARCHITECTURE: Do you have preferences for the overall architecture "
        "style? (layered, microservices, monolith, serverless, etc.)",
        "COMPONENT DESIGN: How should we split the system into modules? Any "
        "technology preferences for frontend, backend, or database?",
        "INTERFACE DESIGN: What are the key interfaces between components? "
        "(APIs, event buses, shared databases, message queues)",
        "DATABASE DESIGN: What data must be persisted? SQL, NoSQL, files, "
        "or a mix? Any performance requirements for data access?",
        "ERROR HANDLING: How should the system handle errors — retry, fail "
        "fast, degrade gracefully, or notify the user?",
        "CHANGE TOLERANCE: What parts of the system are most likely to change "
        "in the future? (so we can hide them behind interfaces)",
    ],
    # ── Planning (Risk mgmt, project planning) ─────
    "planning": [
        "PRIORITY: What is the order of features you want built? "
        "What is the minimum viable first delivery?",
        "TIMELINE: Are there any hard deadlines or time constraints?",
        "TEAM: Are you building this alone or with a team? "
        "What skills are available?",
        "RISK: What could go wrong? Any known technical "
        "risks (unfamiliar technology, complex integration, performance)?",
        "TRADEOFFS: What is more important — speed of delivery, code quality, "
        "completeness, or learning?",
    ],
    # ── Construction (Clean Code + Code Complete) ────────────────────────
    "construction": [
        "Which task from the approved plan are you implementing now?",
        "Did the implementation follow the approved design for this component?",
        "Are there any deviations from the plan? If so, what is the rationale?",
        "Have you run the existing tests after your changes? Any failures?",
        "Are there any unplanned features that crept in? (scope creep check)",
    ],
    # ── Testing (3 stages + V&V) ──────────────────────
    "testing": [
        "CRITICAL REQUIREMENTS: Which requirements are the most important to "
        "test? (must-have features that CANNOT fail)",
        "EDGE CASES: Are there boundary conditions or error scenarios you are "
        "worried about? (empty input, max values, concurrent access, etc.)",
        "FRAMEWORK: What testing framework do you prefer? "
        "(pytest, jest, junit, etc.)",
        "EXISTING TESTS: Do you have any existing tests we should incorporate?",
        "ACCEPTANCE: How will you validate that the system meets YOUR "
        "expectations? (Validation: building the RIGHT product)",
    ],
    # ── Deployment (RUP Transition + Evolution) ─────────────
    "deployment": [
        "ENVIRONMENT: Where should the final product run? "
        "(local, server, cloud, container, mobile, desktop)",
        "CONFIGURATION: What environment variables, secrets, or external "
        "services are needed to run?",
        "CONSTRAINTS: Are there any deployment constraints? "
        "(specific OS, hosting provider, CI/CD pipeline, domain)",
        "MAINTENANCE: Who will maintain this after handoff? "
        "How will bugs be reported and fixed?",
        "EVOLUTION: What features should be built in the next iteration? "
        "Any known limitations to document?",
    ],
}


def _build_user_message(
    *,
    state: ProjectState,
    target_phase: LifecyclePhase,
    user_response: str,
    allow_diagrams: bool,
) -> str:
    """Build the phase advancement message."""
    compact_state = {
        "project_id": state.project_id,
        "idea": state.idea,
        "current_phase": state.phase,
        "sub_step": state.sub_step,
        "target_phase": target_phase,
        "target_users": state.target_users,
        "constraints": state.constraints,
        "assumptions": state.assumptions,
        "pending_questions": state.pending_questions,
        "interview_answers": state.phase_interview_answers.get(target_phase, []),
        "known_artifacts": sorted(state.artifacts.keys()),
        "known_diagrams": sorted(state.diagrams.keys()),
        "allow_diagrams": allow_diagrams,
    }

    sub_step_instruction = ""
    if state.sub_step == "interview":
        sub_step_instruction = (
            "\n\nIMPORTANT: The user has NOT yet answered all phase questions. "
            "Generate a QUESTION LIST for this phase, not the full artifact. "
            "Ask 3-5 focused questions specific to this phase."
        )
    elif state.sub_step == "draft":
        sub_step_instruction = (
            "\n\nThe user has answered the interview questions (see interview_answers). "
            "Generate a DRAFT artifact based on their answers. Mark it as DRAFT "
            "and ask the user to review before finalizing."
        )
    elif state.sub_step == "review":
        sub_step_instruction = (
            "\n\nThe user has reviewed the draft and provided feedback. "
            "Apply their feedback and generate the FINALIZED artifact."
        )

    return (
        f"Target phase: {target_phase}\n"
        f"Sub-step: {state.sub_step}\n"
        f"User response or new context:\n{user_response or 'No new user response.'}\n"
        f"{sub_step_instruction}\n\n"
        f"Current project state:\n{json.dumps(compact_state, indent=2)}"
    )


def _fallback_phase_artifact(
    *,
    state: ProjectState,
    target_phase: LifecyclePhase,
    user_response: str,
    allow_diagrams: bool,
) -> str:
    """Create a deterministic phase artifact."""
    title = PHASE_TITLES[target_phase]
    context = user_response or "No additional user context was provided."
    diagram_note = (
        "Mermaid diagrams are allowed and should be generated where helpful."
        if allow_diagrams
        else "Diagrams are not allowed for this step."
    )

    phase_sections: dict[LifecyclePhase, str] = {
        "requirements": """## Functional Requirements
| ID | Requirement | Priority | Acceptance Criteria |
|---|---|---|---|
| FR-1 | Define the core MVP workflow. | Must | User can complete the primary product workflow. |
| FR-2 | Persist the main product data. | Must | Data survives refresh/restart according to the chosen stack. |
| FR-3 | Provide clear feedback for success and failure states. | Should | User sees actionable messages for normal and error cases. |

## Non-Functional Requirements
- Reliability: handle invalid input without data loss.
- Usability: primary workflows should be discoverable without training.
- Security: avoid exposing secrets and validate untrusted input.
- Scalability: keep module boundaries ready for future growth.

## Domain Requirements
- Confirm domain entities and business rules with the user.

## Inverse Requirements
- The MVP must not include speculative features outside confirmed scope.

## Design Constraints
- The coding agent must not choose a stack that conflicts with user constraints.

## Open Questions
- Which exact user roles are required for MVP?
- Which data must be stored permanently?
""",
        "modeling": """## Use Cases / User Stories
- As a primary user, I can complete the central product workflow.
- As a maintainer, I can understand the system boundaries and data flow.

## Context Model
- User interacts with the product through the chosen interface.
- Product reads/writes core domain data.
- External services remain optional until explicitly required.

## DFD-Style Flow
1. User submits an intent.
2. System validates the input.
3. System performs domain operation.
4. System persists state.
5. System returns feedback.

## Core Entities
| Entity | Responsibility |
|---|---|
| User | Initiates product workflows. |
| DomainRecord | Represents the main business object. |
| OperationResult | Captures success, failure, and messages. |

## Behavior Candidates
- Happy path, validation failure, persistence failure, and retry path.

## Traceability Candidates
- FR-1 maps to use cases and primary sequence flow.
- FR-2 maps to data model and persistence design.
""",
        "design": """## Architecture
Use a simple layered or modular architecture for MVP:
- Interface layer for user interaction.
- Application layer for use cases.
- Domain layer for business rules.
- Infrastructure layer for persistence and external adapters.

## Module Boundaries
| Module | Responsibility |
|---|---|
| interface | Collect input and display results. |
| application | Coordinate use cases. |
| domain | Enforce business rules. |
| infrastructure | Store data and talk to external systems. |

## Interfaces And Contracts
- Application services accept validated commands and return typed results.
- Infrastructure adapters hide storage implementation details.

## Data Storage
- Start with the simplest persistence that satisfies MVP constraints.
- Keep data access behind an interface so it can be replaced later.

## Failure Modes
- Invalid input, persistence failure, unavailable dependency, duplicate action.

## Security And Scalability
- Validate untrusted input.
- Keep secrets outside source control.
- Avoid global mutable state and tight coupling.

## Testing Impact
- Unit test domain rules.
- Integration test persistence boundaries.
- Smoke test the primary workflow.
""",
        "planning": """## MVP Backlog
| ID | Task | Depends On | Definition Of Done |
|---|---|---|---|
| T-1 | Scaffold the product structure. | Design gate | Project runs locally. |
| T-2 | Implement core domain model. | T-1 | Unit tests cover business rules. |
| T-3 | Implement primary workflow. | T-2 | Acceptance path passes. |
| T-4 | Add persistence. | T-2 | Data is saved and loaded correctly. |
| T-5 | Add smoke and regression tests. | T-3,T-4 | Tests run from one command. |

## Milestones
- M1: runnable skeleton
- M2: core workflow
- M3: persistence and tests
- M4: handoff-ready MVP

## Definition Of Done
- Requirements traced to code and tests.
- Primary workflow works locally.
- Known limitations are documented.
""",
        "construction": """## Construction Review Focus
- Confirm the implementation follows the approved requirements and design.
- Check changed files against planned tasks.
- Verify no major unplanned features were added.
- Confirm errors, empty states, and persistence paths are handled.

## Agent Instruction
Implement only the planned MVP tasks. After file edits, run relevant tests and
call `review_lifecycle_gate` for the construction phase.
""",
        "testing": """## Test Strategy
| Test Type | Purpose |
|---|---|
| Unit | Validate domain rules and small pure functions. |
| Integration | Validate persistence and module boundaries. |
| Smoke | Verify the main workflow still works after changes. |
| Regression | Protect fixed defects and critical flows. |
| Acceptance | Prove each must-have requirement is satisfied. |

## Traceability
- FR-1 must have at least one acceptance test.
- FR-2 must have persistence/integration coverage.
- Error and empty states must be tested.
""",
        "deployment": """## Handoff Checklist
- Provide install and run commands.
- Document environment variables and secrets.
- List completed requirements.
- List known limitations.
- Include test command and latest verification result.
- Recommend next iteration tasks.

## Release Readiness
The product is ready to hand off only after construction and testing gates pass.
""",
        "communication": """## Communication Refresh
Restate the product vision, stakeholders, value, scope, assumptions, and first
questions before continuing.
""",
    }

    return f"""# {title}

## Source Context
Project: `{state.project_id}`
Idea: {state.idea}

## Latest User Input
{context}

{phase_sections[target_phase]}

## Diagram Guidance
{diagram_note}

## Risks And Mitigations
- Requirement ambiguity: confirm open questions before coding.
- Technical mismatch: validate stack and constraints before implementation.
- Quality drift: run the lifecycle gate before moving to the next phase.

## Quality Gate Checklist
- Artifact is specific enough for the next phase.
- Open decisions are visible.
- Acceptance or verification criteria exist.
- Risks have mitigations.

## Agent Instruction
Do not skip the next lifecycle gate. If this artifact is accepted, call
`review_lifecycle_gate` for `{target_phase}`, then proceed to the next phase.
"""


def _choose_target_phase(
    state: ProjectState,
    phase_override: str,
    user_response: str,
) -> tuple[LifecyclePhase | None, str]:
    """Choose the next phase while enforcing the state machine."""
    if phase_override:
        normalized = phase_override.strip().lower().replace("_", "-")
        normalized = normalized.replace("-", "_")
        aliases = {
            "requirements_engineering": "requirements",
            "requirements_modeling": "modeling",
            "solution_design": "design",
            "iteration_planning": "planning",
            "deployment_and_handoff": "deployment",
        }
        normalized = aliases.get(normalized, normalized)
        if not is_valid_phase(normalized):
            return None, f"Unknown phase override: {phase_override}"

        expected = next_phase(state.phase)
        if normalized not in {state.phase, expected} and not user_response.strip():
            return (
                None,
                "Phase override would skip lifecycle work. Provide a reason in "
                "`user_response` to record the override.",
            )
        return normalized, ""

    if state.sub_step in {"draft", "review", "finalize"}:
        return state.phase, ""

    if (
        state.sub_step == "interview"
        and state.status == "needs_user_input"
        and state.phase != "communication"
    ):
        return state.phase, ""

    expected = next_phase(state.phase)
    if expected is None:
        return None, "Project is already at the final lifecycle phase."
    return expected, ""


def _traceability_by_id(state: ProjectState) -> dict[str, TraceabilityRecord]:
    """Return traceability records keyed by requirement id."""
    return {record.requirement_id: record for record in state.traceability}


def _apply_traceability_update(
    state: ProjectState,
    target_phase: LifecyclePhase,
) -> None:
    """Maintain lightweight requirement-to-handoff traceability."""
    records = _traceability_by_id(state)
    if target_phase == "requirements" and not records:
        state.traceability.extend(
            [
                TraceabilityRecord(requirement_id="FR-1"),
                TraceabilityRecord(requirement_id="FR-2"),
                TraceabilityRecord(requirement_id="FR-3"),
            ]
        )
        records = _traceability_by_id(state)

    if target_phase == "modeling":
        for requirement_id in ("FR-1", "FR-2", "FR-3"):
            records.setdefault(
                requirement_id,
                TraceabilityRecord(requirement_id=requirement_id),
            )
        records["FR-1"].model_ref = "Primary workflow use case and DFD"
        records["FR-2"].model_ref = "Core entity and data flow model"
        records["FR-3"].model_ref = "Error and feedback behavior paths"
    elif target_phase == "design":
        records.setdefault("FR-1", TraceabilityRecord("FR-1")).design_ref = (
            "Application service and interface layer"
        )
        records.setdefault("FR-2", TraceabilityRecord("FR-2")).design_ref = (
            "Persistence adapter and data store"
        )
        records.setdefault("FR-3", TraceabilityRecord("FR-3")).design_ref = (
            "Result object and UI feedback states"
        )
    elif target_phase == "planning":
        records.setdefault("FR-1", TraceabilityRecord("FR-1")).task_ref = "T-3"
        records.setdefault("FR-2", TraceabilityRecord("FR-2")).task_ref = "T-4"
        records.setdefault("FR-3", TraceabilityRecord("FR-3")).task_ref = "T-3/T-5"
    elif target_phase == "testing":
        records.setdefault("FR-1", TraceabilityRecord("FR-1")).test_ref = (
            "Acceptance test for primary workflow"
        )
        records.setdefault("FR-2", TraceabilityRecord("FR-2")).test_ref = (
            "Integration test for persistence"
        )
        records.setdefault("FR-3", TraceabilityRecord("FR-3")).test_ref = (
            "Error-state and feedback tests"
        )
    elif target_phase == "deployment":
        for record in records.values():
            record.verification_ref = "Handoff checklist and release verification"

    state.traceability = list(records.values())


def _write_traceability_matrix(state: ProjectState) -> None:
    """Persist the traceability matrix from state records."""
    directory = project_dir(state.workspace_root, state.project_id)
    lines = [
        "# Traceability Matrix",
        "",
        "| Requirement | Model | Design | Task | Test | Verification |",
        "|---|---|---|---|---|---|",
    ]
    for record in sorted(state.traceability, key=lambda item: item.requirement_id):
        lines.append(
            "| {requirement} | {model} | {design} | {task} | {test} | {verification} |".format(
                requirement=record.requirement_id,
                model=record.model_ref or "pending",
                design=record.design_ref or "pending",
                task=record.task_ref or "pending",
                test=record.test_ref or "pending",
                verification=record.verification_ref or "pending",
            )
        )
    (directory / "traceability_matrix.md").write_text(
        "\n".join(lines) + "\n",
        encoding="utf-8",
    )


async def run(
    *,
    project_id: str,
    workspace_root: str,
    user_response: str = "",
    phase_override: str = "",
    allow_workspace_write: bool = False,
    allow_diagrams: bool = True,
    llm: LLMProvider | None,
) -> str:
    """Advance a lifecycle project by one controlled phase or sub-step.

    Sub-step flow within each phase:
        interview → draft → review → finalize

    The tool will NOT generate the full artifact until the user has
    answered the interview questions.
    """
    # ── Input validation (robustness for different users) ───────────────
    if not project_id or not project_id.strip():
        return """# Lifecycle Advance Blocked

Status: `blocked`

**Error**: `project_id` is required. Please provide the project ID returned by \
`start_product_build`.

If you haven't started a project yet, call `start_product_build` first.
"""

    if not workspace_root or not workspace_root.strip():
        return """# Lifecycle Advance Blocked

Status: `blocked`

**Error**: `workspace_root` is required. This should be the path to the \
directory where your project files are stored.
"""

    project_id = project_id.strip()
    workspace_root = workspace_root.strip()
    user_response = (user_response or "").strip()
    phase_override = (phase_override or "").strip()

    # Validate phase_override if provided
    if phase_override and phase_override not in PHASES:
        valid_phases = ", ".join(f"`{p}`" for p in PHASES)
        return f"""# Lifecycle Advance Blocked

Status: `blocked`

**Error**: `{phase_override}` is not a valid phase.

Valid phases: {valid_phases}

Current phases are aligned with standard academic SDLC models.
"""

    try:
        state = load_state(workspace_root, project_id)
    except WorkspaceError as exc:
        return f"""# Lifecycle Advance Blocked

Status: `blocked`

{exc}

Start or persist the project first with `start_product_build`.
"""

    target_phase, error = _choose_target_phase(state, phase_override, user_response)
    if target_phase is None:
        return f"""# Lifecycle Advance Blocked

Status: `blocked`

{error}

Current phase: `{state.phase}`
"""

    # ── Sub-step state machine ──────────────────────────────────────────
    # If we're entering a NEW phase (not continuing), start at interview
    if target_phase != state.phase:
        state.sub_step = "interview"

    # Determine what to do based on current sub-step
    current_sub_step = state.sub_step

    # INTERVIEW: Ask phase-specific questions
    if current_sub_step == "interview":
        if user_response.strip():
            # User answered questions — store and advance to draft
            answers = state.phase_interview_answers.get(target_phase, [])
            answers.append(user_response)
            state.phase_interview_answers[target_phase] = answers
            state.sub_step = "draft"
            state.status = "in_progress"
        else:
            # No answers yet — return questions
            questions = PHASE_INTERVIEW_QUESTIONS.get(target_phase, [])
            state.phase = target_phase
            state.status = "needs_user_input"
            state.pending_questions = list(questions)
            state.next_recommended_action = (
                f"Answer the {target_phase} interview questions, then call "
                f"advance_lifecycle_phase with the answers in user_response."
            )
            state.record_phase(
                target_phase, "needs_user_input",
                f"Entered {target_phase} phase — interview questions sent.",
            )
            if allow_workspace_write:
                save_state(state)

            q_list = "\n".join(f"{i+1}. {q}" for i, q in enumerate(questions))
            return f"""# {PHASE_TITLES[target_phase]} — Interview

Project id: `{project_id}`
Current phase: `{target_phase}`
Sub-step: `interview`
Status: `needs_user_input`

## Before I can generate the {target_phase} artifact, I need your input.

Please answer these questions:

{q_list}

## Agent Instruction
Ask the user these questions. After they answer, call:
`advance_lifecycle_phase(project_id="{project_id}", workspace_root="{workspace_root}", user_response="<their answers>")`
"""

    # DRAFT / REVIEW / FINALIZE: Generate artifact
    if current_sub_step == "review":
        # User reviewed the draft — with optional feedback — so finalize this phase.
        answers = state.phase_interview_answers.get(target_phase, [])
        if user_response.strip():
            answers.append(f"[REVIEW FEEDBACK]: {user_response}")
            state.phase_interview_answers[target_phase] = answers
        state.sub_step = "finalize"

    # Handle phase override logging
    if phase_override and target_phase != next_phase(state.phase):
        state.decisions.append(
            DecisionRecord(
                title="Lifecycle phase override",
                decision=f"Advanced from {state.phase} to {target_phase}.",
                rationale=user_response or "No rationale supplied.",
            )
        )
        if allow_workspace_write:
            append_markdown_log(
                workspace_root,
                project_id,
                "decision_log.md",
                (
                    "## Lifecycle Phase Override\n\n"
                    f"- From: `{state.phase}`\n"
                    f"- To: `{target_phase}`\n"
                    f"- Rationale: {user_response or 'No rationale supplied.'}"
                ),
            )

    user_message = _build_user_message(
        state=state,
        target_phase=target_phase,
        user_response=user_response,
        allow_diagrams=allow_diagrams,
    )
    artifact = await generate_with_fallback(
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        fallback=_fallback_phase_artifact(
            state=state,
            target_phase=target_phase,
            user_response=user_response,
            allow_diagrams=allow_diagrams,
        ),
    )

    previous_phase = state.phase
    state.phase = target_phase
    state.allow_diagrams = allow_diagrams
    state.pending_questions = []

    # Set sub-step for next call
    if state.sub_step == "draft":
        state.status = "needs_user_input"
        state.sub_step = "review"
        state.next_recommended_action = (
            f"Review the DRAFT {target_phase} artifact. Provide feedback or "
            f"approve by calling advance_lifecycle_phase again."
        )
        label = "DRAFT"
    elif state.sub_step == "finalize":
        state.status = "in_progress"
        state.sub_step = "interview"  # Reset for next phase
        state.next_recommended_action = (
            f"Review the finalized `{target_phase}` artifact with review_lifecycle_gate."
        )
        label = "FINAL"
    else:
        state.status = "in_progress"
        state.next_recommended_action = (
            f"Review the `{target_phase}` artifact with review_lifecycle_gate."
        )
        label = "FINAL"

    state.record_phase(
        target_phase,
        state.status,
        f"{label}: Advanced from {previous_phase} to {target_phase}.",
    )

    if allow_workspace_write:
        _apply_traceability_update(state, target_phase)
        record = write_artifact(state, target_phase, artifact)
        _write_traceability_matrix(state)
        save_state(state)
        persistence = f"Artifact written to `{record.path}`."
    else:
        record_virtual_artifact(state, target_phase)
        persistence = (
            "Workspace write was not allowed, so this phase artifact was returned "
            "without updating state.json."
        )

    # Different output for draft vs final
    if label == "DRAFT":
        return f"""# {PHASE_TITLES[target_phase]} — Draft For Review

Project id: `{project_id}`
Previous phase: `{previous_phase}`
Current phase: `{target_phase}`
Sub-step: `review`
Status: `needs_user_input`

{persistence}

{artifact}

---
## ⚠️ This is a DRAFT — Please Review
Please review the above artifact and provide feedback:
- Is anything missing?
- Is anything incorrect?
- Should anything be changed?

Once satisfied, call `advance_lifecycle_phase` again to finalize, or 
provide feedback in `user_response` for revisions.
"""

    return f"""# {PHASE_TITLES[target_phase]} — Finalized

Project id: `{project_id}`
Previous phase: `{previous_phase}`
Current phase: `{target_phase}`
Sub-step: `finalize`
Status: `in_progress`

{persistence}

{artifact}

## Next MCP Action
Review this artifact with `review_lifecycle_gate(phase="{target_phase}")`, 
then proceed to the next phase.
"""
