"""Workspace helpers for lifecycle artifacts."""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path

from se_lifecycle_mcp.models import (
    ARTIFACT_FILENAMES,
    ArtifactRecord,
    DiagramRecord,
    LifecyclePhase,
    ProjectState,
)

WORKSPACE_DIR = ".se-lifecycle"


class WorkspaceError(ValueError):
    """Raised when a workspace operation is unsafe or impossible."""


def slugify(value: str, *, fallback: str = "product") -> str:
    """Create a filesystem-safe slug."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return (slug or fallback)[:64].strip("-") or fallback


def new_project_id(idea: str) -> str:
    """Create a readable unique project id from a product idea."""
    return f"{slugify(idea)[:42]}-{uuid.uuid4().hex[:8]}"


def resolve_workspace_root(workspace_root: str | Path) -> Path:
    """Resolve the user supplied workspace root."""
    root = Path(workspace_root or ".").expanduser().resolve()
    if not root.exists():
        raise WorkspaceError(f"Workspace root does not exist: {root}")
    if not root.is_dir():
        raise WorkspaceError(f"Workspace root is not a directory: {root}")
    return root


def lifecycle_root(workspace_root: str | Path) -> Path:
    """Return the lifecycle root for a workspace."""
    return resolve_workspace_root(workspace_root) / WORKSPACE_DIR


def project_dir(workspace_root: str | Path, project_id: str) -> Path:
    """Return the safe project artifact directory."""
    safe_id = slugify(project_id)
    root = lifecycle_root(workspace_root)
    directory = (root / safe_id).resolve()
    try:
        directory.relative_to(root.resolve())
    except ValueError as exc:
        raise WorkspaceError("Project id resolves outside lifecycle root.") from exc
    return directory


def diagrams_dir(workspace_root: str | Path, project_id: str) -> Path:
    """Return the safe diagrams directory."""
    return project_dir(workspace_root, project_id) / "diagrams"


def state_path(workspace_root: str | Path, project_id: str) -> Path:
    """Return the state file path."""
    return project_dir(workspace_root, project_id) / "state.json"


def ensure_project_workspace(workspace_root: str | Path, project_id: str) -> Path:
    """Create a lifecycle project workspace."""
    directory = project_dir(workspace_root, project_id)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "diagrams").mkdir(exist_ok=True)
    return directory


def load_state(workspace_root: str | Path, project_id: str) -> ProjectState:
    """Load persisted lifecycle state."""
    path = state_path(workspace_root, project_id)
    if not path.exists():
        raise WorkspaceError(f"No lifecycle state found at {path}")
    return ProjectState.from_dict(json.loads(path.read_text(encoding="utf-8")))


def save_state(state: ProjectState) -> Path:
    """Persist lifecycle state."""
    directory = ensure_project_workspace(state.workspace_root, state.project_id)
    path = directory / "state.json"
    state.touch()
    path.write_text(
        json.dumps(state.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path


def write_artifact(
    state: ProjectState,
    phase: LifecyclePhase,
    content: str,
) -> ArtifactRecord:
    """Write a phase artifact and update the state record."""
    directory = ensure_project_workspace(state.workspace_root, state.project_id)
    filename = ARTIFACT_FILENAMES[phase]
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    record = ArtifactRecord(
        kind=phase,
        filename=filename,
        path=str(path),
        written=True,
    )
    state.artifacts[phase] = record
    return record


def record_virtual_artifact(
    state: ProjectState,
    phase: LifecyclePhase,
) -> ArtifactRecord:
    """Record an artifact returned to the caller but not written."""
    filename = ARTIFACT_FILENAMES[phase]
    record = ArtifactRecord(kind=phase, filename=filename, written=False)
    state.artifacts[phase] = record
    return record


def append_markdown_log(
    workspace_root: str | Path,
    project_id: str,
    filename: str,
    entry: str,
) -> Path:
    """Append a markdown entry inside the project workspace."""
    directory = ensure_project_workspace(workspace_root, project_id)
    path = directory / filename
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    separator = "\n\n" if existing.strip() else ""
    path.write_text(f"{existing}{separator}{entry}\n", encoding="utf-8")
    return path


def write_standard_registers(state: ProjectState) -> None:
    """Create baseline lifecycle support artifacts."""
    directory = ensure_project_workspace(state.workspace_root, state.project_id)
    files = {
        "decision_log.md": "# Decision Log\n",
        "risk_register.md": "# Risk Register\n",
        "traceability_matrix.md": (
            "# Traceability Matrix\n\n"
            "| Requirement | Model | Design | Task | Test | Verification |\n"
            "|---|---|---|---|---|---|\n"
        ),
    }
    for filename, content in files.items():
        path = directory / filename
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def save_diagram(
    state: ProjectState,
    diagram_type: str,
    mermaid: str,
) -> DiagramRecord:
    """Save a Mermaid diagram and update state."""
    directory = diagrams_dir(state.workspace_root, state.project_id)
    directory.mkdir(parents=True, exist_ok=True)
    filename = f"{slugify(diagram_type)}.mmd"
    path = directory / filename
    path.write_text(mermaid, encoding="utf-8")
    record = DiagramRecord(
        diagram_type=diagram_type,
        filename=filename,
        path=str(path),
        written=True,
    )
    state.diagrams[diagram_type] = record
    return record


def read_optional(path: str) -> str:
    """Read a text file if a safe file path was provided."""
    if not path:
        return ""
    candidate = Path(path).expanduser()
    if not candidate.exists() or not candidate.is_file():
        return ""
    return candidate.read_text(encoding="utf-8")
