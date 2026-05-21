# SE Lifecycle MCP - Complete Project Documentation

## 1. Project Overview

SE Lifecycle MCP is a Model Context Protocol server that helps AI coding agents
build software products through a complete software engineering lifecycle. The
main idea is simple: instead of asking an agent to immediately code after a
one-line request like "Build me a pharmacy inventory system", the MCP guides the
agent through product discovery, requirements, modeling, design, planning,
construction review, testing, deployment, and handoff.

The server acts as a **Software Engineering interviewer** — it asks the user
questions at every phase before generating artifacts. It never advances without
user permission. Each phase follows a sub-step flow:
**interview → draft → review → finalize → gate review → next phase**.

All prompts and quality gates are enriched with deep knowledge from 8 major SE
books: The Pragmatic Programmer, Clean Code, Code Complete, Design Patterns,
Refactoring, Pressman SE, Sommerville SE (9th Edition), and Designing
Data-Intensive Applications.

The product is designed for local and remote MCP-compatible coding agents. The
agent still performs the actual code edits, but this MCP acts as the software
engineering guide, artifact generator, phase gate, diagram producer, and project
memory layer.

## 2. Problem Statement

AI coding agents can create code quickly, but they often skip the engineering
thinking that makes a product useful and maintainable. Common problems include:

- The agent starts coding before understanding the user problem.
- Requirements are vague, incomplete, or mixed with implementation details.
- The architecture is chosen too early or without trade-off analysis.
- Tests are added late or not connected to requirements.
- The final product may run, but may not solve the actual user need.
- The user has no clear lifecycle artifacts to review.

SE Lifecycle MCP solves this by making the agent follow a structured,
lightweight lifecycle before and during implementation.

## 3. Core Product Promise

The target user experience is:

```text
Build me a <product idea>
```

After that one line, the coding agent should use this MCP to:

1. Understand the product vision.
2. Ask focused questions.
3. Produce requirements.
4. Model the system.
5. Design the solution.
6. Plan the build.
7. Generate diagrams when permitted.
8. Review phase gates.
9. Support construction.
10. Define testing strategy.
11. Prepare deployment and handoff.

The goal is not academic paperwork. The goal is better software: clearer
requirements, better architecture, safer implementation, stronger tests, and a
more useful final product.

## 4. Current Product Scope

The active product is the lifecycle MCP under:

```text
src/se_lifecycle_mcp/
```

## 5. Main Architecture

The project follows a modular Python structure:

```text
src/se_lifecycle_mcp/
|-- __init__.py
|-- __main__.py
|-- server.py
|-- models.py
|-- workspace.py
|-- llm/
|   |-- base.py
|   |-- factory.py
|   |-- anthropic.py
|   |-- openai.py
|   `-- google.py
|-- prompts/
|   |-- discovery.py
|   |-- phase.py
|   |-- gate_review.py
|   `-- diagram.py
`-- tools/
    |-- __init__.py
    |-- _llm.py
    |-- start_product_build.py
    |-- advance_lifecycle_phase.py
    |-- review_lifecycle_gate.py
    |-- generate_lifecycle_diagram.py
    `-- summarize_project_state.py
```

### Main Responsibilities

| Area | Responsibility |
|---|---|
| `server.py` | Creates the FastMCP server and registers the public tools. |
| `models.py` | Defines typed lifecycle state, artifacts, risks, decisions, gates, diagrams, and traceability records. |
| `workspace.py` | Manages `.se-lifecycle/<project_id>/` artifact storage. |
| `llm/` | Provides a provider abstraction for Anthropic, OpenAI, and Google. |
| `prompts/` | Stores system prompts for lifecycle generation, gate review, and diagrams. |
| `tools/` | Implements the public MCP tool behavior. |
| `tests/` | Verifies lifecycle flow without real LLM API calls. |

## 6. MCP Server

The active MCP server is:

```text
src/se_lifecycle_mcp/server.py
```

The server object is:

```python
mcp
```

The FastMCP Cloud entrypoint is:

```text
src/se_lifecycle_mcp/server.py:mcp
```

The local module entrypoint is:

```bash
python -m se_lifecycle_mcp
```

The convenience root entrypoint is:

```bash
python main.py
```

## 7. Public MCP Tools

### 7.1 `start_product_build`

Starts a lifecycle project from a one-line idea.

Inputs:

| Parameter | Purpose |
|---|---|
| `idea` | The product request, such as "Build me a task management app". |
| `workspace_root` | Root folder where `.se-lifecycle/` may be created. |
| `target_users` | Optional known user roles or audiences. |
| `constraints` | Optional business, technical, security, or scale constraints. |
| `allow_workspace_write` | If true, writes lifecycle state and artifacts. |
| `allow_diagrams` | If true, allows Mermaid diagram guidance. |

Outputs:

- Project id.
- Current phase.
- Product vision.
- Initial assumptions.
- Key risks.
- First questions for the user.
- Next MCP action.

Typical first call:

```text
start_product_build(
  idea="Build me a pharmacy inventory system",
  workspace_root=".",
  allow_workspace_write=true,
  allow_diagrams=true
)
```

### 7.2 `advance_lifecycle_phase`

Moves a project from one lifecycle phase to the next.

Inputs:

| Parameter | Purpose |
|---|---|
| `project_id` | Project id returned by `start_product_build`. |
| `workspace_root` | Workspace root containing `.se-lifecycle/`. |
| `user_response` | User answers, context, or override rationale. |
| `phase_override` | Optional explicit target phase. |
| `allow_workspace_write` | If true, writes the phase artifact and state. |
| `allow_diagrams` | If true, includes diagram guidance. |

Important behavior:

- The tool follows the lifecycle state machine.
- It does not skip major phases unless an override rationale is supplied.
- It maintains traceability records as the lifecycle advances.

### 7.3 `review_lifecycle_gate`

Reviews a lifecycle artifact and returns a phase gate decision.

Inputs:

| Parameter | Purpose |
|---|---|
| `project_id` | Lifecycle project id. |
| `workspace_root` | Workspace root containing `.se-lifecycle/`. |
| `phase` | Phase being reviewed. |
| `artifact_text` | Artifact content to review. |
| `changed_files` | Changed files for construction or testing review. |
| `strictness` | `balanced`, `strict`, or `advisory`. |
| `allow_workspace_write` | If true, stores gate results in `state.json`. |

Gate statuses:

| Status | Meaning |
|---|---|
| `pass` | Artifact is ready for the next phase. |
| `needs_work` | Artifact is usable but has important gaps. |
| `blocked` | Artifact has serious problems and should not advance. |

Serious blockers include:

- Unclear product goal.
- Missing acceptance criteria.
- Missing critical requirements.
- Incoherent architecture.
- Untestable design.
- Security or reliability gaps.
- Implementation that does not match approved requirements.

### 7.4 `generate_lifecycle_diagram`

Generates Mermaid diagrams from lifecycle artifacts.

Inputs:

| Parameter | Purpose |
|---|---|
| `project_id` | Lifecycle project id. |
| `workspace_root` | Workspace root containing `.se-lifecycle/`. |
| `diagram_type` | Type of diagram to generate. |
| `source_artifact` | Source text to convert into a diagram. |
| `allow_workspace_write` | If true, writes `.mmd` files. |

Supported diagram types:

- `context`
- `flow`
- `erd`
- `use_case`
- `activity`
- `architecture`
- `class`
- `component`
- `sequence`
- `state`
- `deployment`
- `roadmap`
- `deployment`
- `roadmap`

Generated diagrams are Mermaid text. When writing is allowed, they are saved
under:

```text
.se-lifecycle/<project_id>/diagrams/
```

### 7.5 `summarize_project_state`

Summarizes the current project state.

Outputs:

- Current phase.
- Current status.
- Next action.
- Pending questions.
- Artifacts.
- Diagrams.
- Completed gates.
- Open risks.
- Assumptions.
- Agent instruction.

This tool is useful when a coding agent resumes work after a context break.

## 8. Lifecycle Phases

### 8.1 Communication

Purpose:

- Understand the product idea.
- Identify stakeholders and target users.
- Clarify business value.
- Define initial scope.
- Capture assumptions and unknowns.

Typical artifact:

```text
00_vision.md
```

### 8.2 Requirements Engineering

Purpose:

- Convert the product vision into structured requirements.
- Separate requirement categories clearly.
- Add acceptance criteria and priorities.

Expected sections:

- Functional requirements.
- Non-functional requirements.
- Domain requirements.
- Inverse requirements.
- Design constraints.
- Acceptance criteria.
- Open questions.

Typical artifact:

```text
01_requirements.md
```

### 8.3 Requirements Modeling

Purpose:

- Model the problem before designing the solution.
- Identify use cases, data flows, entities, states, and interactions.
- Build traceability from requirements to models.

Expected content:

- Use cases or user stories.
- Context model.
- DFD-style flow.
- Core entities.
- Data dictionary.
- Behavior/state candidates.
- Sequence candidates.
- Traceability candidates.

Typical artifact:

```text
02_models.md
```

### 8.4 Design

Purpose:

- Convert requirements and models into an implementation-ready design.
- Choose architecture, module boundaries, contracts, and storage strategy.
- Consider scalability, security, reliability, and testability.

Expected content:

- Architecture style.
- Module responsibilities.
- Interfaces and contracts.
- Data storage approach.
- UI states if relevant.
- Failure modes.
- Security notes.
- Scalability notes.
- Testing impact.

Typical artifact:

```text
03_design.md
```

### 8.5 Planning

Purpose:

- Convert design into a buildable MVP backlog.
- Define tasks, milestones, dependencies, quality checks, and definition of done.

Expected content:

- MVP backlog.
- Task sets.
- Milestones.
- Definition of done.
- Risk controls.
- Quality checkpoints.
- Implementation sequence.

Typical artifact:

```text
04_plan.md
```

### 8.6 Construction Support

Purpose:

- Help the coding agent implement only the approved MVP.
- Review changed files against requirements, models, and design.
- Prevent unplanned complexity and scope drift.

Typical artifact:

```text
construction_review.md
```

### 8.7 Testing

Purpose:

- Define a test strategy tied to requirements.
- Ensure the product is verifiable and regression-safe.

Expected test types:

- Unit tests.
- Integration tests.
- Smoke tests.
- Regression tests.
- Acceptance tests.

Typical artifact:

```text
05_test_strategy.md
```

### 8.8 Deployment And Handoff

Purpose:

- Prepare the product for user handoff.
- Document setup, environment, known limitations, release checklist, and next
  iteration recommendations.

Typical artifact:

```text
06_handoff.md
```

## 9. Lifecycle State Machine

The phase order is:

```text
communication
requirements
modeling
design
planning
construction
testing
deployment
```

The active status values are:

```text
not_started
in_progress
needs_user_input
needs_work
blocked
passed
```

The state machine protects the project from jumping directly from idea to code.
Overrides are possible, but the user or agent must provide a rationale.

## 10. Project Workspace

When `allow_workspace_write=True`, the MCP creates:

```text
.se-lifecycle/<project_id>/
|-- state.json
|-- 00_vision.md
|-- 01_requirements.md
|-- 02_models.md
|-- 03_design.md
|-- 04_plan.md
|-- 05_test_strategy.md
|-- 06_handoff.md
|-- construction_review.md
|-- decision_log.md
|-- risk_register.md
|-- traceability_matrix.md
`-- diagrams/
    `-- *.mmd
```

### 10.1 `state.json`

Stores:

- Project id.
- Idea.
- Workspace root.
- Current phase.
- Current status.
- Target users.
- Constraints.
- Assumptions.
- Pending questions.
- Completed gates.
- Artifact records.
- Diagram records.
- Risks.
- Decisions.
- Traceability records.
- Phase history.
- Next recommended action.

### 10.2 `decision_log.md`

Stores important product, process, and architecture decisions.

Examples:

- Choosing hybrid-agile lifecycle.
- Skipping a phase with rationale.
- Selecting architecture style.
- Choosing a database or deployment model.

### 10.3 `risk_register.md`

Stores risks and mitigations.

Risk categories include:

- Requirement ambiguity.
- Technical risk.
- Schedule risk.
- Scalability risk.
- Security risk.
- UX risk.

### 10.4 `traceability_matrix.md`

Links requirements to downstream lifecycle work.

Columns:

- Requirement.
- Model.
- Design.
- Task.
- Test.
- Verification.

This gives the final product a clear proof chain from user need to delivery.

## 11. LLM Provider System

The project uses a provider abstraction:

```text
src/se_lifecycle_mcp/llm/base.py
```

Supported providers:

- Anthropic.
- OpenAI.
- Google Gemini.

Provider selection is handled by:

```text
src/se_lifecycle_mcp/llm/factory.py
```

Detection order:

1. Explicit provider argument.
2. `SE_MCP_PROVIDER` environment variable.
3. Auto-detection from available API keys.

Supported environment variables:

```text
ANTHROPIC_API_KEY
OPENAI_API_KEY
GOOGLE_API_KEY
SE_MCP_PROVIDER
SE_MCP_MODEL
```

If no provider is configured, tools still work using deterministic fallback
outputs. This makes the MCP easier to test and deploy.

## 12. Prompt System

Prompts are separated by responsibility:

| Prompt file | Purpose |
|---|---|
| `discovery.py` | Converts a one-line idea into product vision and first questions. |
| `phase.py` | Generates lifecycle phase artifacts. |
| `gate_review.py` | Reviews artifacts and returns phase gate decisions. |
| `diagram.py` | Generates Mermaid diagrams. |

This separation keeps the MCP easier to maintain and extend.

## 13. Deterministic Fallbacks

The MCP is designed to work even when no LLM provider is configured.

Fallbacks exist for:

- Product vision.
- Requirements artifact.
- Modeling artifact.
- Design artifact.
- Planning artifact.
- Construction review guidance.
- Testing strategy.
- Handoff checklist.
- Gate reviews.
- Mermaid diagrams.

This is useful for:

- Local development.
- Unit tests.
- First deployment checks.
- Environments where API keys are not yet configured.

## 14. Diagram System

Mermaid is used because it is:

- Text-based.
- Easy to version-control.
- Readable in Markdown.
- Supported by many developer tools.
- Easy for agents to generate and modify.

**Diagram Rendering:**
The MCP server automatically renders Mermaid text into visual diagrams using the free [mermaid.ink](https://mermaid.ink) API.
- Source `.mmd` files and rendered `.svg` images are saved side-by-side in the `diagrams/` folder.
- Generated diagrams include a browser-viewable URL and an interactive Mermaid Live Editor link.
- Rendering can be configured via `SE_MCP_DIAGRAM_RENDERER` (`mermaid_ink` or `none`).

Supported diagrams:

| Type | Use |
|---|---|
| `context` | Shows user, product, data, and external systems. |
| `flow` | Shows the main workflow. |
| `erd` | Shows entities and relationships. |
| `use_case` | Shows actors and system interactions. |
| `activity` | Shows workflow with decisions and parallel paths. |
| `architecture` | Shows layers/modules. |
| `class` | Shows classes, interfaces, and relationships. |
| `component` | Shows modules, packages, and connections. |
| `sequence` | Shows runtime interaction. |
| `state` | Shows lifecycle or domain state transitions. |
| `deployment` | Shows runtime/deployment components. |
| `roadmap` | Shows product evolution. |

## 15. Local Development

Install dependencies:

```bash
pip install -e ".[all]"
```

Run tests:

```bash
python -m unittest discover -s tests
```

Compile check:

```bash
python -m compileall src tests
```

Run local MCP server:

```bash
python -m se_lifecycle_mcp
```

## 16. FastMCP Cloud Deployment

Repository:

```text
https://github.com/Stranger-S8/Se-lifecycle-mcp
```

FastMCP Cloud project settings:

```text
Server name: se-lifecycle-mcp
Entrypoint: src/se_lifecycle_mcp/server.py:mcp
```

Suggested description:

```text
Guides AI coding agents through the full software engineering lifecycle from a one-line product idea: discovery, requirements, modeling, design, planning, testing, diagrams, and handoff.
```

Environment variables:

```text
ANTHROPIC_API_KEY=your_key_here
SE_MCP_PROVIDER=anthropic
SE_MCP_MODEL=claude-sonnet-4-20250514
```

Cloud note:

For remote FastMCP deployment, `allow_workspace_write=false` is recommended at
first. Remote filesystem state may not behave like a local project workspace.
For local agents building real products in local repositories,
`allow_workspace_write=true` is more useful.

## 17. MCP Client Usage

Local Claude Code example:

```bash
claude mcp add se-lifecycle -- python -m se_lifecycle_mcp
```

Generic MCP config:

```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "python",
      "args": ["-m", "se_lifecycle_mcp"],
      "env": {
        "ANTHROPIC_API_KEY": "your-key-here"
      }
    }
  }
}
```

Remote client URL after FastMCP Cloud deployment:

```text
https://<server-name>.fastmcp.app/mcp
```

## 18. Example End-To-End Flow

User asks:

```text
Build me a pharmacy inventory system
```

Agent calls:

```text
start_product_build
```

The MCP returns:

- Product vision.
- Risks.
- Assumptions.
- First questions.
- Project id.

User answers questions.

Agent calls:

```text
advance_lifecycle_phase
```

The MCP produces requirements.

Agent calls:

```text
review_lifecycle_gate
```

If requirements pass, the agent continues to modeling, design, and planning.
The agent may call:

```text
generate_lifecycle_diagram
```

After planning is ready, the agent implements the product. Then it reviews
construction, testing, and deployment/handoff.

## 19. Testing Strategy

The project includes tests in:

```text
tests/test_lifecycle_tools.py
```

Current coverage includes:

- Workspace creation when writing is allowed.
- No workspace creation when writing is not allowed.
- State machine skip prevention.
- Requirements section generation.
- Mermaid diagram generation and saving.
- Gate review pass/block behavior.
- Traceability matrix updates.
- Resume summary.
- Confirmation that old principle tools are not active in the new server.

The tests use a fake LLM provider and do not require real API keys.

## 20. Packaging

Package metadata lives in:

```text
pyproject.toml
```

Distribution name:

```text
se-lifecycle-mcp
```

Python package:

```text
se_lifecycle_mcp
```

Console script:

```text
se-lifecycle-mcp
```

Core dependencies:

```text
mcp>=1.0.0
python-dotenv>=1.0.0
```

Optional provider dependencies:

```text
anthropic
openai
google-genai
```

## 21. Important Design Decisions

### 21.1 MCP Guides, Agent Implements

The MCP does not directly build complete software products by itself. The local
coding agent performs actual code edits. The MCP guides the agent, produces
artifacts, validates phase gates, and stores lifecycle state.

### 21.2 Lifecycle First, Code Second

The core guardrail is that agents should not start implementation until
requirements, modeling, design, and planning are ready.

### 21.3 Balanced Strictness

The project avoids academic over-process. It blocks serious problems but does
not force unnecessary documentation.

### 21.4 Mermaid First

The first diagram format is Mermaid because it is text-based, portable, and
agent-friendly. Image rendering can be added later.

### 21.5 Interview Before Artifact

Every phase starts with an interview step. The server asks 3-5 phase-specific
questions before generating any artifact. The user must provide answers before
the draft is produced, and must review the draft before it is finalized.

## 22. Known Limitations

- Remote FastMCP deployments may not provide persistent project workspace
  storage in the same way as local development.
- The MCP currently generates artifacts and guidance; it does not inspect the
  entire local codebase automatically.
- Gate review uses heuristic checks plus optional LLM judgment.
- Mermaid output is text only; rendered images are not generated yet.
- No database-backed project state exists yet.
- No GitHub issue/PR integration exists yet.

## 23. Future Roadmap

Strong next features:

- Add a GitHub-backed workspace mode.
- Add rendered diagram export.
- Add richer codebase-aware construction review.
- Add artifact templates per product type.
- Add web app, SaaS, API, CLI, and mobile lifecycle profiles.
- Add security and privacy review gates.
- Add deployment readiness checks per platform.
- Add team/project-management metrics.
- Add FastMCP Cloud-specific deployment guide.
- Add docs site.

## 24. Glossary

| Term | Meaning |
|---|---|
| MCP | Model Context Protocol, a way for tools/servers to connect with AI clients. |
| SDLC | Software Development Life Cycle. |
| Phase gate | A review point before moving to the next lifecycle phase. |
| Artifact | A document or output produced during the lifecycle. |
| Traceability | Linking requirements to design, tasks, tests, and verification. |
| Mermaid | A text syntax for diagrams. |
| LLM provider | The model API backend used to generate richer outputs. |

## 25. Summary

SE Lifecycle MCP is a lifecycle orchestration server for AI coding agents. It
turns a rough product idea into structured engineering artifacts, phase gates,
diagrams, and implementation guidance. Its purpose is to help agents build
excellent software products, not just fast code. Every phase follows the
interview → draft → review → finalize flow, ensuring the user is involved at
every step.
