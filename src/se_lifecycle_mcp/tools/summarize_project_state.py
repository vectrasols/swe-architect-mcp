"""Summarize a persisted lifecycle project state."""

from __future__ import annotations

from se_lifecycle_mcp.workspace import WorkspaceError, load_state


def _render_list(values: list[str]) -> str:
    """Render a compact markdown list."""
    return "\n".join(f"- {value}" for value in values) or "- None."


def _render_artifacts(state) -> str:
    """Render artifact records."""
    if not state.artifacts:
        return "- None."
    lines = []
    for key, record in sorted(state.artifacts.items()):
        target = record.path or record.filename
        written = "written" if record.written else "not written"
        lines.append(f"- `{key}`: {target} ({written})")
    return "\n".join(lines)


def _render_diagrams(state) -> str:
    """Render diagram records."""
    if not state.diagrams:
        return "- None."
    lines = []
    for key, record in sorted(state.diagrams.items()):
        target = record.path or record.filename
        written = "written" if record.written else "not written"
        lines.append(f"- `{key}`: {target} ({written})")
    return "\n".join(lines)


def _render_gates(state) -> str:
    """Render gate records."""
    if not state.completed_gates:
        return "- None."
    lines = []
    for key, gate in sorted(state.completed_gates.items()):
        lines.append(f"- `{key}`: {gate.status}, {gate.score}/100")
    return "\n".join(lines)


def _render_risks(state) -> str:
    """Render risk records."""
    if not state.risks:
        return "- None."
    return "\n".join(
        f"- {risk.category}: {risk.description} "
        f"(impact: {risk.impact}, status: {risk.status})"
        for risk in state.risks
    )


async def run(
    *,
    project_id: str,
    workspace_root: str,
) -> str:
    """Summarize current project state."""
    try:
        state = load_state(workspace_root, project_id)
    except WorkspaceError as exc:
        return f"""# Project State Unavailable

Status: `blocked`

{exc}
"""

    return f"""# SE Lifecycle Project State

Project id: `{state.project_id}`
Idea: {state.idea}
Current phase: `{state.phase}`
Status: `{state.status}`
Updated: {state.updated_at}

## Next Action
{state.next_recommended_action or "Call advance_lifecycle_phase."}

## Pending Questions
{_render_list(state.pending_questions)}

## Artifacts
{_render_artifacts(state)}

## Diagrams
{_render_diagrams(state)}

## Completed Gates
{_render_gates(state)}

## Open Risks
{_render_risks(state)}

## Assumptions
{_render_list(state.assumptions)}

## Agent Instruction
Continue only from the current phase. Do not start construction until
requirements, modeling, design, and planning artifacts have been reviewed.
"""
