"""Start a one-line product build through the SE lifecycle."""

from __future__ import annotations

from swe_architect_mcp.llm.base import LLMProvider
from swe_architect_mcp.models import DecisionRecord, ProjectState, RiskRecord
from swe_architect_mcp.prompts.discovery import SYSTEM_PROMPT
from swe_architect_mcp.tools._llm import generate_with_fallback
from swe_architect_mcp.workspace import (
    new_project_id,
    record_virtual_artifact,
    save_state,
    write_artifact,
    write_standard_registers,
)


DEFAULT_QUESTIONS = [
    "Who are the primary users and what is the single most important job "
    "each user needs to complete?",
    "What is the ONE workflow that must work for this to be useful? "
    "(Tracer Bullet — the thinnest end-to-end slice)",
    "What can be EXPLICITLY left out of the first version? (YAGNI)",
    "Are there any technology, security, budget, platform, or compliance "
    "constraints?",
    "FEASIBILITY CHECK: Is this technically feasible with available technology? "
    "Is it financially justified? Will users actually adopt it?",
    "How will you measure success? What does 'done' look like for v1?",
]


def _build_user_message(
    idea: str,
    target_users: str = "",
    constraints: str = "",
    allow_diagrams: bool = True,
) -> str:
    """Build the LLM user message for product discovery."""
    parts = [
        f"Product idea: {idea}",
        f"Target users: {target_users or 'unspecified'}",
        f"Constraints: {constraints or 'unspecified'}",
        f"Mermaid diagrams allowed: {allow_diagrams}",
    ]
    return "\n".join(parts)


def _fallback_vision(
    idea: str,
    target_users: str = "",
    constraints: str = "",
) -> str:
    """Create a useful deterministic discovery artifact."""
    users = target_users or "Primary users still need to be identified."
    constraints_text = constraints or "No hard constraints have been supplied yet."
    return f"""# Product Vision

## Problem
The user wants to build: {idea}

## Target Users
{users}

## Product Goal
Create a working product through a disciplined lifecycle before writing code:
communication, requirements, modeling, design, planning, construction, testing,
and handoff.

## Scope
- Clarify the user problem and success criteria.
- Produce requirements with acceptance criteria.
- Model data, flows, behavior, and user interactions.
- Design a scalable MVP architecture.
- Plan implementation tasks and quality gates.
- Review construction and testing before handoff.

## Out Of Scope
- Starting implementation before the requirements, models, design, and plan are
  reviewed.
- Adding speculative features that do not support the MVP.

## Success Criteria
- The user can confirm the MVP goal in plain language.
- Each requirement has acceptance criteria.
- Design decisions are traceable to requirements.
- Implementation tasks map to tests and final verification.

## Initial Assumptions
- The first release should be an MVP.
- The local coding agent will perform file edits.
- This MCP will guide, validate, and store lifecycle artifacts.

## Key Risks
- Requirement ambiguity can cause the wrong product to be built.
- Missing non-functional requirements can create security, reliability, or scale
  issues later.
- Skipping modeling/design can cause rework during implementation.

## First Questions For The User
1. Who are the primary users and what jobs do they need to complete?
2. What is the smallest useful MVP you would accept as successful?
3. Are there security, privacy, scale, budget, or technology constraints?

## Agent Instruction
Do not start coding yet. Ask the user the first questions, then call
`advance_lifecycle_phase` to produce the requirements artifact.

## Supplied Constraints
{constraints_text}
"""


async def run(
    *,
    idea: str,
    workspace_root: str,
    target_users: str = "",
    constraints: str = "",
    allow_workspace_write: bool = False,
    allow_diagrams: bool = True,
    llm: LLMProvider | None,
) -> str:
    """Start a product build and optionally create its lifecycle workspace."""
    # ── Input validation (robustness for different users) ───────────────
    if not idea or not idea.strip():
        return """# Product Build Blocked

Status: `blocked`

**Error**: `idea` is required. Please describe what you want to build.

Example: `start_product_build(idea="A task management app with Kanban boards")`
"""

    if not workspace_root or not workspace_root.strip():
        return """# Product Build Blocked

Status: `blocked`

**Error**: `workspace_root` is required. This should be the path to the \
directory where your project files will be stored.
"""

    idea = idea.strip()
    workspace_root = workspace_root.strip()
    target_users = (target_users or "").strip()
    constraints = (constraints or "").strip()

    project_id = new_project_id(idea)
    state = ProjectState(
        project_id=project_id,
        idea=idea,
        workspace_root=workspace_root,
        phase="communication",
        sub_step="interview",
        status="needs_user_input",
        target_users=target_users,
        constraints=constraints,
        allow_diagrams=allow_diagrams,
        assumptions=[
            "Use a hybrid-agile lifecycle: disciplined phases with iterative feedback.",
            "The coding agent implements files only after lifecycle gates are ready.",
            "Mermaid is the default diagram format when diagrams are allowed.",
        ],
        pending_questions=list(DEFAULT_QUESTIONS),
        risks=[
            RiskRecord(
                category="requirements",
                description="The initial idea may be too broad or ambiguous.",
                impact="high",
                mitigation="Ask targeted product and acceptance questions before modeling.",
            ),
            RiskRecord(
                category="technical",
                description="The target stack and scale are not yet known.",
                impact="medium",
                mitigation="Record constraints before architecture decisions.",
            ),
        ],
        decisions=[
            DecisionRecord(
                title="Default process model",
                decision="Use hybrid-agile lifecycle guidance.",
                rationale="It keeps SDLC discipline while still supporting fast MVP iteration.",
            )
        ],
        next_recommended_action=(
            "Ask the user the first questions, then call advance_lifecycle_phase."
        ),
    )
    state.record_phase("communication", "needs_user_input", "Product build started.")

    user_message = _build_user_message(
        idea=idea,
        target_users=target_users,
        constraints=constraints,
        allow_diagrams=allow_diagrams,
    )
    artifact = await generate_with_fallback(
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        user_message=user_message,
        fallback=_fallback_vision(idea, target_users, constraints),
    )

    if allow_workspace_write:
        write_standard_registers(state)
        record = write_artifact(state, "communication", artifact)
        save_state(state)
        persistence = f"Workspace created at `{record.path}`."
    else:
        record_virtual_artifact(state, "communication")
        persistence = (
            "Workspace write was not allowed, so no files were created. "
            "Call again with `allow_workspace_write=True` to persist state."
        )

    return f"""# SE Lifecycle Build Started

Project id: `{project_id}`
Current phase: `communication`
Status: `needs_user_input`

{persistence}

{artifact}

## Next MCP Action
After the user answers the discovery questions, call:
`advance_lifecycle_phase(project_id="{project_id}", workspace_root="{workspace_root}")`
"""
