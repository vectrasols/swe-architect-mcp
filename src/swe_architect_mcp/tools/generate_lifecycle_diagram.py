"""Generate Mermaid lifecycle diagrams."""

from __future__ import annotations

from swe_architect_mcp.llm.base import LLMProvider
from swe_architect_mcp.prompts.diagram import SYSTEM_PROMPT
from swe_architect_mcp.tools._llm import generate_with_fallback, strip_mermaid_fence
from swe_architect_mcp.workspace import WorkspaceError, load_state, save_diagram, save_state


SUPPORTED_DIAGRAMS = {
    "context",
    "flow",
    "erd",
    "architecture",
    "sequence",
    "state",
    "deployment",
    "roadmap",
    "use_case",
    "activity",
    "class",
    "component",
}


def _build_user_message(
    *,
    project_id: str,
    diagram_type: str,
    source_artifact: str,
) -> str:
    """Build the diagram prompt message."""
    return f"""Project id: {project_id}
Diagram type: {diagram_type}

Source artifact:
{source_artifact}
"""


def _fallback_diagram(diagram_type: str, source_artifact: str) -> str:
    """Create deterministic Mermaid diagrams."""
    title = (source_artifact.strip().splitlines() or ["Product"])[0]
    title = title.replace("#", "").strip() or "Product"

    if diagram_type == "context":
        return f"""flowchart LR
    User[Primary User] --> Product[{title}]
    Product --> Data[(Product Data)]
    Product --> Feedback[User Feedback]
"""
    if diagram_type == "flow":
        return """flowchart TD
    A[User starts primary workflow] --> B[Validate input]
    B -->|Valid| C[Execute domain operation]
    B -->|Invalid| D[Show actionable error]
    C --> E[Persist state]
    E --> F[Return result]
"""
    if diagram_type == "erd":
        return """erDiagram
    USER ||--o{ DOMAIN_RECORD : creates
    DOMAIN_RECORD ||--o{ OPERATION_RESULT : produces
    USER {
        string id
        string role
    }
    DOMAIN_RECORD {
        string id
        string status
    }
    OPERATION_RESULT {
        string id
        string message
    }
"""
    if diagram_type == "architecture":
        return """flowchart TB
    UI[Interface Layer] --> APP[Application Services]
    APP --> DOMAIN[Domain Model]
    APP --> PORTS[Ports / Interfaces]
    PORTS --> INFRA[Infrastructure Adapters]
    INFRA --> DB[(Data Store)]
"""
    if diagram_type == "sequence":
        return """sequenceDiagram
    actor User
    participant UI as Interface
    participant App as Application Service
    participant Domain as Domain Model
    participant Store as Data Store
    User->>UI: Submit request
    UI->>App: Send command
    App->>Domain: Apply business rule
    App->>Store: Persist result
    Store-->>App: Confirm
    App-->>UI: Return result
    UI-->>User: Show feedback
"""
    if diagram_type == "state":
        return """stateDiagram-v2
    [*] --> Draft
    Draft --> Validated: input accepted
    Draft --> Rejected: validation failed
    Validated --> Persisted: save succeeds
    Persisted --> Completed
    Rejected --> Draft: user corrects input
"""
    if diagram_type == "deployment":
        return """flowchart TB
    Dev[Developer Machine] --> Build[Build and Test]
    Build --> Runtime[Application Runtime]
    Runtime --> Config[Environment Config]
    Runtime --> Storage[(Storage)]
    Runtime --> Logs[Logs / Diagnostics]
"""
    if diagram_type == "use_case":
        return """flowchart LR
    subgraph Actors
        PrimaryUser((Primary User))
        Admin((Admin))
    end
    subgraph System
        UC1[Create Record]
        UC2[View Records]
        UC3[Update Record]
        UC4[Delete Record]
        UC5[Manage Settings]
    end
    PrimaryUser --> UC1
    PrimaryUser --> UC2
    PrimaryUser --> UC3
    Admin --> UC4
    Admin --> UC5
"""
    if diagram_type == "activity":
        return """flowchart TD
    Start([Start]) --> Input[User provides input]
    Input --> Validate{Valid input?}
    Validate -->|Yes| Process[Process request]
    Validate -->|No| Error[Show error message]
    Error --> Input
    Process --> Save[Save to storage]
    Save --> Success{Save successful?}
    Success -->|Yes| Result[Return success]
    Success -->|No| Retry[Retry or report failure]
    Retry --> Process
    Result --> End([End])
"""
    if diagram_type == "class":
        return """classDiagram
    class DomainEntity {
        +String id
        +String name
        +String status
        +create()
        +update()
        +validate()
    }
    class Repository {
        <<interface>>
        +save(entity)
        +findById(id)
        +findAll()
        +delete(id)
    }
    class ApplicationService {
        -Repository repository
        +execute(command)
        +query(criteria)
    }
    ApplicationService --> Repository : uses
    Repository ..> DomainEntity : manages
"""
    if diagram_type == "component":
        return """flowchart TB
    subgraph Presentation
        UI[User Interface]
    end
    subgraph Application
        SVC[Application Services]
        CMD[Command Handlers]
        QRY[Query Handlers]
    end
    subgraph Domain
        ENT[Domain Entities]
        RULES[Business Rules]
    end
    subgraph Infrastructure
        REPO[Repository Adapters]
        DB[(Database)]
        EXT[External APIs]
    end
    UI --> SVC
    SVC --> CMD
    SVC --> QRY
    CMD --> ENT
    CMD --> RULES
    QRY --> REPO
    CMD --> REPO
    REPO --> DB
    REPO --> EXT
"""
    return """timeline
    title Product Roadmap
    MVP : Requirements : Design : Core workflow : Tests
    Next : Feedback : Hardening : Deployment polish
"""


def _is_likely_mermaid(diagram_type: str, text: str) -> bool:
    """Validate the broad Mermaid family for supported diagrams."""
    stripped = text.lstrip()
    starters = {
        "context": ("flowchart", "graph"),
        "flow": ("flowchart", "graph"),
        "architecture": ("flowchart", "graph"),
        "deployment": ("flowchart", "graph"),
        "use_case": ("flowchart", "graph"),
        "activity": ("flowchart", "graph"),
        "component": ("flowchart", "graph"),
        "erd": ("erDiagram",),
        "sequence": ("sequenceDiagram",),
        "state": ("stateDiagram", "stateDiagram-v2"),
        "class": ("classDiagram",),
        "roadmap": ("timeline", "gantt", "flowchart"),
    }
    return stripped.startswith(starters.get(diagram_type, ("flowchart",)))


async def run(
    *,
    project_id: str,
    workspace_root: str,
    diagram_type: str,
    source_artifact: str,
    allow_workspace_write: bool = False,
    llm: LLMProvider | None,
) -> str:
    """Generate a Mermaid diagram and optionally save it."""
    normalized = diagram_type.strip().lower().replace("-", "_")
    if normalized not in SUPPORTED_DIAGRAMS:
        return f"""# Diagram Generation Blocked

Status: `blocked`

Unsupported diagram type `{diagram_type}`.
Supported types: {", ".join(sorted(SUPPORTED_DIAGRAMS))}
"""

    fallback = _fallback_diagram(normalized, source_artifact)
    generated = await generate_with_fallback(
        llm=llm,
        system_prompt=SYSTEM_PROMPT,
        user_message=_build_user_message(
            project_id=project_id,
            diagram_type=normalized,
            source_artifact=source_artifact,
        ),
        fallback=fallback,
    )
    mermaid = strip_mermaid_fence(generated)
    if not _is_likely_mermaid(normalized, mermaid):
        mermaid = fallback

    if allow_workspace_write:
        try:
            state = load_state(workspace_root, project_id)
        except WorkspaceError as exc:
            return f"""# Diagram Generation Blocked

Status: `blocked`

{exc}
"""
        record = save_diagram(state, normalized, mermaid)
        save_state(state)
        persistence = f"Mermaid source written to `{record.path}`."
        if record.image_path:
            persistence += f"\nRendered image saved to `{record.image_path}`."
    else:
        persistence = "Workspace write was not allowed, so the diagram was returned only."
        record = None

    # Build viewable links
    from swe_architect_mcp.diagram_renderer import (
        get_mermaid_ink_url,
        get_mermaid_live_url,
    )

    image_url = record.image_url if record else get_mermaid_ink_url(mermaid)
    editor_url = record.editor_url if record else get_mermaid_live_url(mermaid)

    return f"""# Lifecycle Diagram

Project id: `{project_id}`
Diagram type: `{normalized}`

{persistence}

## 🔗 View Diagram

- **View rendered diagram**: [Open in browser]({image_url})
- **Edit interactively**: [Open in Mermaid Live Editor]({editor_url})

## Mermaid Source

```mermaid
{mermaid}
```
"""

