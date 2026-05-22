"""FastMCP server for the SWE Architect MCP."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Annotated

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from swe_architect_mcp.llm.factory import create_provider
from swe_architect_mcp.tools import (
    advance_lifecycle_phase,
    generate_lifecycle_diagram,
    review_lifecycle_gate,
    start_product_build,
    summarize_project_state,
)

load_dotenv()

mcp = FastMCP(
    "swe-architect-mcp",
    instructions=(
        "SWE Architect MCP turns a one-line product idea into a disciplined "
        "software engineering build flow guided by core industry principles.\n\n"
        "PHASES (aligned with standard academic SDLC):\n"
        "1. Communication — Inception, stakeholders, feasibility study\n"
        "2. Requirements — Elicitation, specification, validation (NFR taxonomy)\n"
        "3. Modeling — 4 perspectives, 5 UML diagram types\n"
        "4. Design — 4 design activities, 9 architectural questions\n"
        "5. Planning — Risk management, project scheduling\n"
        "6. Construction — Implementation, code quality\n"
        "7. Testing — V&V, 3 testing stages\n"
        "8. Deployment — RUP Transition, evolution strategy\n\n"
        "WORKFLOW:\n"
        "1. Use start_product_build first to create the project.\n"
        "2. For each phase, the server follows an INTERVIEW flow:\n"
        "   - interview: Ask the user phase-specific questions FIRST.\n"
        "   - draft: Generate a DRAFT artifact from user answers.\n"
        "   - review: Let the user review and provide feedback.\n"
        "   - finalize: Produce the final artifact.\n"
        "3. After each phase is finalized, run review_lifecycle_gate.\n"
        "4. Only advance to the next phase after the gate passes.\n"
        "5. Do NOT start implementation until requirements, modeling, design, "
        "and planning gates are ready.\n"
        "6. Generate Mermaid diagrams when the user permits (12 types: "
        "context, flow, erd, use_case, activity, state, architecture, class, "
        "component, sequence, deployment, roadmap).\n\n"
        "CRITICAL: Always ask the user before generating. Never skip the "
        "interview step. The user must be involved in every phase."
    ),
)

try:
    _provider = create_provider()
except (ValueError, ImportError) as exc:
    sys.stderr.write(f"SWE Architect MCP provider warning: {exc}\n")
    sys.stderr.write("Server will start; tools will use deterministic fallbacks.\n")
    _provider = None


@mcp.tool()
async def start_product_build_tool(
    idea: Annotated[
        str,
        "One-line product request, e.g. 'Build me a pharmacy inventory system'.",
    ],
    workspace_root: Annotated[
        str,
        "Project workspace root where .se-lifecycle/<project_id>/ may be created.",
    ],
    target_users: Annotated[
        str,
        "Optional known target users or roles.",
    ] = "",
    constraints: Annotated[
        str,
        "Optional technology, business, security, budget, or scale constraints.",
    ] = "",
    allow_workspace_write: Annotated[
        bool,
        "When true, create .se-lifecycle/<project_id>/ and persist artifacts.",
    ] = False,
    allow_diagrams: Annotated[
        bool,
        "When true, allow Mermaid diagram recommendations and generation.",
    ] = True,
) -> str:
    """Start a one-line product build through the SE lifecycle."""
    return await start_product_build.run(
        idea=idea,
        workspace_root=workspace_root,
        target_users=target_users,
        constraints=constraints,
        allow_workspace_write=allow_workspace_write,
        allow_diagrams=allow_diagrams,
        llm=_provider,
    )


@mcp.tool()
async def advance_lifecycle_phase_tool(
    project_id: Annotated[str, "Lifecycle project id returned by start_product_build."],
    workspace_root: Annotated[str, "Workspace root containing .se-lifecycle."],
    user_response: Annotated[
        str,
        "User answers, new context, or override rationale.",
    ] = "",
    phase_override: Annotated[
        str,
        "Optional explicit target phase. Skips require rationale in user_response.",
    ] = "",
    allow_workspace_write: Annotated[
        bool,
        "When true, persist the generated phase artifact and update state.json.",
    ] = False,
    allow_diagrams: Annotated[
        bool,
        "When true, permit diagram guidance for this phase.",
    ] = True,
) -> str:
    """Advance the lifecycle state machine by one phase."""
    return await advance_lifecycle_phase.run(
        project_id=project_id,
        workspace_root=workspace_root,
        user_response=user_response,
        phase_override=phase_override,
        allow_workspace_write=allow_workspace_write,
        allow_diagrams=allow_diagrams,
        llm=_provider,
    )


@mcp.tool()
async def review_lifecycle_gate_tool(
    project_id: Annotated[str, "Lifecycle project id."],
    workspace_root: Annotated[str, "Workspace root containing .se-lifecycle."],
    phase: Annotated[
        str,
        "Phase to review: communication, requirements, modeling, design, planning, construction, testing, deployment.",
    ],
    artifact_text: Annotated[str, "Artifact text to review."],
    changed_files: Annotated[
        list[str] | None,
        "Changed files for construction/testing review.",
    ] = None,
    strictness: Annotated[
        str,
        "Review mode: balanced, strict, or advisory.",
    ] = "balanced",
    allow_workspace_write: Annotated[
        bool,
        "When true, persist the gate result into state.json.",
    ] = False,
) -> str:
    """Review a lifecycle artifact and return pass, needs_work, or blocked."""
    return await review_lifecycle_gate.run(
        project_id=project_id,
        workspace_root=workspace_root,
        phase=phase,
        artifact_text=artifact_text,
        changed_files=changed_files,
        strictness=strictness,
        allow_workspace_write=allow_workspace_write,
        llm=_provider,
    )


@mcp.tool()
async def generate_lifecycle_diagram_tool(
    project_id: Annotated[str, "Lifecycle project id."],
    workspace_root: Annotated[str, "Workspace root containing .se-lifecycle."],
    diagram_type: Annotated[
        str,
        "Diagram type: context, flow, erd, architecture, sequence, state, deployment, roadmap.",
    ],
    source_artifact: Annotated[
        str,
        "Lifecycle artifact text to convert into a Mermaid diagram.",
    ],
    allow_workspace_write: Annotated[
        bool,
        "When true, write diagrams/<diagram_type>.mmd and update state.json.",
    ] = False,
) -> str:
    """Generate a Mermaid lifecycle diagram."""
    return await generate_lifecycle_diagram.run(
        project_id=project_id,
        workspace_root=workspace_root,
        diagram_type=diagram_type,
        source_artifact=source_artifact,
        allow_workspace_write=allow_workspace_write,
        llm=_provider,
    )


@mcp.tool()
async def summarize_project_state_tool(
    project_id: Annotated[str, "Lifecycle project id."],
    workspace_root: Annotated[str, "Workspace root containing .se-lifecycle."],
) -> str:
    """Summarize current lifecycle project state."""
    return await summarize_project_state.run(
        project_id=project_id,
        workspace_root=workspace_root,
    )
