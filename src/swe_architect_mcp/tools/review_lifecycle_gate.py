"""Review lifecycle artifacts with balanced phase gates."""

from __future__ import annotations

from swe_architect_mcp.llm.base import LLMProvider
from swe_architect_mcp.models import GateRecord, is_valid_phase
from swe_architect_mcp.prompts.gate_review import SYSTEM_PROMPT
from swe_architect_mcp.tools._llm import generate_with_fallback
from swe_architect_mcp.workspace import WorkspaceError, load_state, save_state


PHASE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "communication": (
        "problem",
        "target users",
        "scope",
        "success criteria",
        "assumptions",
        "risks",
    ),
    "requirements": (
        "functional",
        "non-functional",
        "domain",
        "inverse",
        "constraints",
        "acceptance criteria",
        "priority",
    ),
    "modeling": (
        "use case",
        "data flow",
        "entity",
        "state",
        "sequence",
        "traceability",
    ),
    "design": (
        "architecture",
        "module",
        "interface",
        "data",
        "failure",
        "security",
        "scalability",
        "testing",
    ),
    "planning": (
        "backlog",
        "task",
        "milestone",
        "definition of done",
        "risk",
        "quality",
    ),
    "construction": (
        "implementation",
        "requirements",
        "design",
        "changed",
        "tests",
    ),
    "testing": (
        "unit",
        "integration",
        "smoke",
        "regression",
        "acceptance",
        "traceability",
    ),
    "deployment": (
        "run",
        "environment",
        "release",
        "limitations",
        "handoff",
        "next iteration",
    ),
}


def _build_user_message(
    *,
    project_id: str,
    phase: str,
    artifact_text: str,
    changed_files: list[str],
    strictness: str,
) -> str:
    """Build the LLM message for a gate review."""
    changed = "\n".join(f"- {path}" for path in changed_files) or "None supplied."
    return f"""Project id: {project_id}
Phase: {phase}
Strictness: {strictness}

Changed files:
{changed}

Artifact:
{artifact_text}
"""


def _local_gate_review(
    *,
    phase: str,
    artifact_text: str,
    changed_files: list[str],
    strictness: str,
) -> tuple[str, int, list[str], list[str], str]:
    """Run deterministic gate heuristics."""
    text = artifact_text.strip()
    lower = text.lower()
    score = 100
    required_fixes: list[str] = []
    suggested: list[str] = []

    if len(text) < 120:
        score -= 45
        required_fixes.append("Expand the artifact; it is too thin for a phase gate.")

    keywords = PHASE_KEYWORDS.get(phase, ())
    missing = [keyword for keyword in keywords if keyword not in lower]
    if missing:
        penalty = min(45, len(missing) * 8)
        score -= penalty
        required_fixes.append(
            "Add missing phase coverage: " + ", ".join(missing) + "."
        )

    weak_markers = ("tbd", "todo", "unknown", "not sure", "later", "n/a")
    marker_hits = sum(lower.count(marker) for marker in weak_markers)
    if marker_hits:
        score -= min(25, marker_hits * 5)
        suggested.append("Resolve placeholder language before advancing.")

    if phase in {"requirements", "testing"} and "acceptance" not in lower:
        score -= 15
        required_fixes.append("Add acceptance criteria or acceptance tests.")

    if phase == "design" and "security" not in lower:
        score -= 10
        suggested.append("Add security considerations to the design.")

    if phase == "construction" and not changed_files:
        score -= 20
        required_fixes.append("Provide changed files for construction review.")

    strictness_normalized = strictness.strip().lower()
    pass_threshold = 75
    block_threshold = 45
    if strictness_normalized == "strict":
        pass_threshold = 85
        block_threshold = 55
    elif strictness_normalized == "advisory":
        pass_threshold = 65
        block_threshold = 25

    score = max(0, min(100, score))
    if score >= pass_threshold:
        status = "pass"
    elif score < block_threshold:
        status = "blocked"
    else:
        status = "needs_work"

    if status == "pass" and not suggested:
        suggested.append("Keep the artifact linked to downstream tasks and tests.")
    if status != "pass" and not required_fixes:
        required_fixes.append("Address the phase gaps before advancing.")

    rationale = (
        f"Local gate scored {score}/100 using balanced lifecycle heuristics "
        f"for the `{phase}` phase."
    )
    return status, score, required_fixes, suggested, rationale


def _fallback_review(
    *,
    status: str,
    score: int,
    required_fixes: list[str],
    suggested: list[str],
    rationale: str,
    phase: str,
) -> str:
    """Render deterministic gate review markdown."""
    required = "\n".join(f"- {item}" for item in required_fixes) or "- None."
    improvements = "\n".join(f"- {item}" for item in suggested) or "- None."
    instruction = (
        "Proceed to the next lifecycle phase."
        if status == "pass"
        else f"Fix the required `{phase}` issues, then run this gate again."
    )
    return f"""# Lifecycle Gate Review

## Status
{status}

## Score
{score}/100

## Required Fixes
{required}

## Suggested Improvements
{improvements}

## Rationale
{rationale}

## Agent Instruction
{instruction}
"""


async def run(
    *,
    project_id: str,
    workspace_root: str,
    phase: str,
    artifact_text: str,
    changed_files: list[str] | None = None,
    strictness: str = "balanced",
    allow_workspace_write: bool = False,
    llm: LLMProvider | None,
) -> str:
    """Review a lifecycle phase gate."""
    normalized_phase = phase.strip().lower().replace("-", "_")
    if not is_valid_phase(normalized_phase):
        return f"""# Lifecycle Gate Review

## Status
blocked

## Score
0/100

## Required Fixes
- Use a valid lifecycle phase.

## Agent Instruction
Valid phases are: {", ".join(PHASE_KEYWORDS)}.
"""

    changed = changed_files or []
    status, score, required_fixes, suggested, rationale = _local_gate_review(
        phase=normalized_phase,
        artifact_text=artifact_text,
        changed_files=changed,
        strictness=strictness,
    )

    fallback = _fallback_review(
        status=status,
        score=score,
        required_fixes=required_fixes,
        suggested=suggested,
        rationale=rationale,
        phase=normalized_phase,
    )
    expert = await generate_with_fallback(
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        user_message=_build_user_message(
            project_id=project_id,
            phase=normalized_phase,
            artifact_text=artifact_text,
            changed_files=changed,
            strictness=strictness,
        ),
        fallback=fallback,
    )

    if allow_workspace_write:
        try:
            state = load_state(workspace_root, project_id)
        except WorkspaceError:
            state = None
        if state is not None:
            state.completed_gates[normalized_phase] = GateRecord(
                phase=normalized_phase,
                status=status,
                score=score,
                summary=rationale,
            )
            state.status = "passed" if status == "pass" else status
            state.next_recommended_action = (
                "Advance to the next lifecycle phase."
                if status == "pass"
                else f"Revise the `{normalized_phase}` artifact and review again."
            )
            save_state(state)

    if expert == fallback:
        return expert

    return f"""{fallback}

## LLM Expert Review
{expert}
"""
