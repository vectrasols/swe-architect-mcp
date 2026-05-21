"""Typed lifecycle models for the SE Lifecycle MCP.

Includes sub-phase interview system for step-by-step user interaction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal


LifecyclePhase = Literal[
    "communication",
    "requirements",
    "modeling",
    "design",
    "planning",
    "construction",
    "testing",
    "deployment",
]

LifecycleStatus = Literal[
    "not_started",
    "in_progress",
    "needs_user_input",
    "needs_work",
    "blocked",
    "passed",
]

GateStatus = Literal["pass", "needs_work", "blocked"]

SubStep = Literal[
    "interview",
    "draft",
    "review",
    "finalize",
]

SUB_STEPS: tuple[SubStep, ...] = (
    "interview",
    "draft",
    "review",
    "finalize",
)

PHASES: tuple[LifecyclePhase, ...] = (
    "communication",
    "requirements",
    "modeling",
    "design",
    "planning",
    "construction",
    "testing",
    "deployment",
)

STATUS_VALUES: tuple[LifecycleStatus, ...] = (
    "not_started",
    "in_progress",
    "needs_user_input",
    "needs_work",
    "blocked",
    "passed",
)

ARTIFACT_FILENAMES: dict[LifecyclePhase, str] = {
    "communication": "00_vision.md",
    "requirements": "01_requirements.md",
    "modeling": "02_models.md",
    "design": "03_design.md",
    "planning": "04_plan.md",
    "construction": "construction_review.md",
    "testing": "05_test_strategy.md",
    "deployment": "06_handoff.md",
}


def utc_now() -> str:
    """Return an ISO 8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat()


def next_phase(current: LifecyclePhase) -> LifecyclePhase | None:
    """Return the next lifecycle phase, if any."""
    index = PHASES.index(current)
    if index + 1 >= len(PHASES):
        return None
    return PHASES[index + 1]


def is_valid_phase(value: str) -> bool:
    """Return whether a string is a known lifecycle phase."""
    return value in PHASES


@dataclass
class ArtifactRecord:
    """A generated or persisted lifecycle artifact."""

    kind: str
    filename: str
    path: str = ""
    written: bool = False


@dataclass
class GateRecord:
    """A stored phase gate decision."""

    phase: str
    status: GateStatus
    score: int
    reviewed_at: str = field(default_factory=utc_now)
    summary: str = ""


@dataclass
class RiskRecord:
    """A risk tracked during the lifecycle."""

    category: str
    description: str
    impact: str = "medium"
    mitigation: str = ""
    status: str = "open"


@dataclass
class DecisionRecord:
    """An architectural, product, or process decision."""

    title: str
    decision: str
    rationale: str = ""
    created_at: str = field(default_factory=utc_now)


@dataclass
class TraceabilityRecord:
    """Links a requirement to downstream lifecycle artifacts."""

    requirement_id: str
    model_ref: str = ""
    design_ref: str = ""
    task_ref: str = ""
    test_ref: str = ""
    verification_ref: str = ""


@dataclass
class DiagramRecord:
    """A generated Mermaid diagram with optional rendered image."""

    diagram_type: str
    filename: str
    path: str = ""
    written: bool = False
    image_path: str = ""
    image_url: str = ""
    editor_url: str = ""


@dataclass
class ProjectState:
    """Persisted state for a lifecycle-guided product build."""

    project_id: str
    idea: str
    workspace_root: str
    phase: LifecyclePhase = "communication"
    sub_step: SubStep = "interview"
    status: LifecycleStatus = "in_progress"
    target_users: str = ""
    constraints: str = ""
    allow_diagrams: bool = True
    assumptions: list[str] = field(default_factory=list)
    phase_interview_answers: dict[str, list[str]] = field(default_factory=dict)
    pending_questions: list[str] = field(default_factory=list)
    completed_gates: dict[str, GateRecord] = field(default_factory=dict)
    artifacts: dict[str, ArtifactRecord] = field(default_factory=dict)
    diagrams: dict[str, DiagramRecord] = field(default_factory=dict)
    risks: list[RiskRecord] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    traceability: list[TraceabilityRecord] = field(default_factory=list)
    phase_history: list[dict[str, str]] = field(default_factory=list)
    next_recommended_action: str = ""
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def touch(self) -> None:
        """Update the modification timestamp."""
        self.updated_at = utc_now()

    def record_phase(self, phase: str, status: str, note: str = "") -> None:
        """Append a compact phase history entry."""
        self.phase_history.append(
            {
                "phase": phase,
                "status": status,
                "note": note,
                "at": utc_now(),
            }
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the project state to plain JSON data."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectState":
        """Deserialize project state while tolerating older state files."""
        completed_gates = {
            key: GateRecord(**value)
            for key, value in data.get("completed_gates", {}).items()
        }
        artifacts = {
            key: ArtifactRecord(**value)
            for key, value in data.get("artifacts", {}).items()
        }
        diagrams = {
            key: DiagramRecord(**value)
            for key, value in data.get("diagrams", {}).items()
        }
        risks = [RiskRecord(**value) for value in data.get("risks", [])]
        decisions = [
            DecisionRecord(**value) for value in data.get("decisions", [])
        ]
        traceability = [
            TraceabilityRecord(**value)
            for value in data.get("traceability", [])
        ]

        return cls(
            project_id=data["project_id"],
            idea=data["idea"],
            workspace_root=data.get("workspace_root", ""),
            phase=data.get("phase", "communication"),
            sub_step=data.get("sub_step", "interview"),
            status=data.get("status", "in_progress"),
            target_users=data.get("target_users", ""),
            constraints=data.get("constraints", ""),
            allow_diagrams=data.get("allow_diagrams", True),
            assumptions=list(data.get("assumptions", [])),
            phase_interview_answers=dict(data.get("phase_interview_answers", {})),
            pending_questions=list(data.get("pending_questions", [])),
            completed_gates=completed_gates,
            artifacts=artifacts,
            diagrams=diagrams,
            risks=risks,
            decisions=decisions,
            traceability=traceability,
            phase_history=list(data.get("phase_history", [])),
            next_recommended_action=data.get("next_recommended_action", ""),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
        )
