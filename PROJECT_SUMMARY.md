# SE Lifecycle MCP - Project Summary

## Mission

SE Lifecycle MCP helps local AI coding agents build software products through a
complete software engineering lifecycle. The user can begin with one line, such
as "Build me a task management app", and the MCP guides the agent through
discovery, requirements, modeling, design, planning, construction review,
testing, deployment, and handoff.

## Product Direction

The project is no longer centered on standalone principle-checking tools. Those
tools have been archived under `archive/se_principles_mcp/`. The active product
surface is now a lifecycle orchestrator with phase gates, persisted artifacts,
traceability, risks, decisions, and Mermaid diagrams.

## Active MCP Tools

1. `start_product_build`
   - Converts a one-line product idea into an initial vision.
   - Creates `.se-lifecycle/<project_id>/` when writing is allowed.

2. `advance_lifecycle_phase`
   - Moves through the lifecycle state machine one phase at a time.
   - Prevents accidental jumps unless an override rationale is provided.

3. `review_lifecycle_gate`
   - Reviews a phase artifact and returns `pass`, `needs_work`, or `blocked`.
   - Blocks serious lifecycle problems without enforcing academic ceremony.

4. `generate_lifecycle_diagram`
   - Produces Mermaid diagrams for context, flow, ERD, architecture, sequence,
     state, deployment, and roadmap views.

5. `summarize_project_state`
   - Reports current phase, artifacts, diagrams, gates, assumptions, risks, and
     next agent action.

## Architecture

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
    |-- start_product_build.py
    |-- advance_lifecycle_phase.py
    |-- review_lifecycle_gate.py
    |-- generate_lifecycle_diagram.py
    `-- summarize_project_state.py
```

## Lifecycle Workspace

When `allow_workspace_write=True`, project artifacts are stored in:

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
`-- diagrams/*.mmd
```

## Execution Flow

1. Agent receives a user request like "Build me this product".
2. Agent calls `start_product_build`.
3. MCP creates or returns the product vision and first questions.
4. Agent gathers user answers.
5. Agent advances through requirements, modeling, design, and planning.
6. MCP reviews phase gates.
7. Agent implements the product only after the planning gate is ready.
8. MCP reviews construction, testing, and handoff artifacts.

## Design Notes

- LLM providers remain interchangeable through `LLMProvider`.
- Tools use deterministic fallbacks when no provider is configured.
- Mermaid is the default diagram format because it is portable and reviewable.
- The local coding agent performs file edits; the MCP guides, validates, and
  stores lifecycle artifacts.
