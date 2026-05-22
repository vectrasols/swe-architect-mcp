"""Generate Mermaid lifecycle diagrams."""

from __future__ import annotations

from swe_architect_mcp.llm.base import LLMProvider
from swe_architect_mcp.prompts.diagram import SYSTEM_PROMPT
from swe_architect_mcp.tools._llm import generate_with_fallback, strip_mermaid_fence
from swe_architect_mcp.tools._local_content import (
    infer_product_context,
    mermaid_id,
    mermaid_label,
)
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
    context = infer_product_context(idea=source_artifact)
    title = mermaid_label(context.product_name)
    actor = mermaid_label(context.actor_label)
    entity = mermaid_label(context.primary_entity)
    event = mermaid_label(context.secondary_entity)
    entity_id = mermaid_id(entity, "DomainRecord")
    event_id = mermaid_id(event, "WorkflowEvent")

    if diagram_type == "context":
        return f"""flowchart LR
    User[{actor}] --> Product[{title}]
    Product --> Data[({entity} Data)]
    Product --> Feedback[User Feedback]
"""
    if diagram_type == "flow":
        return f"""flowchart TD
    A[User starts primary workflow] --> B[Validate input]
    B -->|Valid| C[Create or update {entity}]
    B -->|Invalid| D[Show actionable error]
    C --> E[Persist state]
    E --> F[Return result]
"""
    if diagram_type == "erd":
        return f"""erDiagram
    USER ||--o{{ {entity_id.upper()} : manages
    {entity_id.upper()} ||--o{{ {event_id.upper()} : records
    USER {{
        string id
        string role
    }}
    {entity_id.upper()} {{
        string id
        string name
        string status
    }}
    {event_id.upper()} {{
        string id
        string type
        string message
    }}
"""
    if diagram_type == "architecture":
        return f"""flowchart TB
    UI[Interface Layer] --> APP[Application Services]
    APP --> DOMAIN[{entity} Domain Model]
    APP --> PORTS[Repository Interfaces]
    PORTS --> INFRA[Infrastructure Adapters]
    INFRA --> DB[({entity} Store)]
"""
    if diagram_type == "sequence":
        return f"""sequenceDiagram
    actor User
    participant UI as Interface
    participant App as Application Service
    participant Domain as {entity} Domain
    participant Store as Data Store
    User->>UI: Submit request
    UI->>App: Send {entity} command
    App->>Domain: Validate and apply rules
    App->>Store: Persist {entity}
    Store-->>App: Confirm
    App-->>UI: Return result
    UI-->>User: Show feedback
"""
    if diagram_type == "state":
        return f"""stateDiagram-v2
    [*] --> Draft{entity_id}
    Draft{entity_id} --> Validated: input accepted
    Draft{entity_id} --> Rejected: validation failed
    Validated --> Persisted: save succeeds
    Persisted --> Active
    Active --> Archived: user archives
    Rejected --> Draft{entity_id}: user corrects input
"""
    if diagram_type == "deployment":
        return f"""flowchart TB
    Dev[Developer Machine] --> Build[Build and Test]
    Build --> Runtime[{title} Runtime]
    Runtime --> Config[Environment Config]
    Runtime --> Storage[({entity} Storage)]
    Runtime --> Logs[Logs / Diagnostics]
"""
    if diagram_type == "use_case":
        return f"""flowchart LR
    subgraph Actors
        PrimaryUser(({actor}))
        Admin((Admin))
    end
    subgraph System
        UC1[Create {entity}]
        UC2[View {entity}]
        UC3[Update {entity}]
        UC4[Archive {entity}]
        UC5[Manage Settings]
    end
    PrimaryUser --> UC1
    PrimaryUser --> UC2
    PrimaryUser --> UC3
    Admin --> UC4
    Admin --> UC5
"""
    if diagram_type == "activity":
        return f"""flowchart TD
    Start([Start]) --> Input[User provides input]
    Input --> Validate{{Valid input?}}
    Validate -->|Yes| Process[Process {entity}]
    Validate -->|No| Error[Show error message]
    Error --> Input
    Process --> Save[Save to storage]
    Save --> Success{{Save successful?}}
    Success -->|Yes| Result[Return success]
    Success -->|No| Retry[Retry or report failure]
    Retry --> Process
    Result --> End([End])
"""
    if diagram_type == "class":
        return f"""classDiagram
    class {entity_id} {{
        +String id
        +String name
        +String status
        +create()
        +update()
        +validate()
    }}
    class Repository {{
        <<interface>>
        +save(entity)
        +findById(id)
        +findAll()
        +delete(id)
    }}
    class ApplicationService {{
        -Repository repository
        +execute(command)
        +query(criteria)
    }}
    ApplicationService --> Repository : uses
    Repository ..> {entity_id} : manages
"""
    if diagram_type == "component":
        return f"""flowchart TB
    subgraph Presentation
        UI[User Interface]
    end
    subgraph Application
        SVC[Application Services]
        CMD[Command Handlers]
        QRY[Query Handlers]
    end
    subgraph Domain
        ENT[{entity} Entities]
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
    return f"""timeline
    title {title} Roadmap
    MVP : Requirements : Design : {entity} workflow : Tests
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
