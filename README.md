# SE Lifecycle MCP

SE Lifecycle MCP is a Model Context Protocol server that helps local coding
agents build software through a complete software engineering lifecycle from a
single product request.

Instead of jumping directly from "Build me this app" to code, the MCP guides the
agent through communication, requirements, modeling, design, planning,
construction review, testing, deployment, and handoff.

## What Problem It Solves

AI coding agents are fast, but they often start coding before the product is
understood. That creates vague requirements, weak architecture, missing tests,
and products that work technically but fail the real user need.

This MCP gives the agent a disciplined workflow:

1. Understand the product idea.
2. Ask the right questions.
3. Produce lifecycle artifacts.
4. Generate diagrams when permitted.
5. Gate each phase before moving forward.
6. Keep traceability from requirement to design, task, test, and handoff.

## Public Tools

| Tool | Purpose |
|---|---|
| `start_product_build` | Starts from a one-line idea and creates the product vision. |
| `advance_lifecycle_phase` | Moves the project through the SDLC state machine. |
| `review_lifecycle_gate` | Returns `pass`, `needs_work`, or `blocked` for a lifecycle artifact. |
| `generate_lifecycle_diagram` | Produces Mermaid diagrams for architecture, flows, ERD, state, sequence, deployment, and roadmap views. |
| `summarize_project_state` | Shows current phase, artifacts, open questions, risks, gates, and next action. |

## Lifecycle Phases

- Communication
- Requirements engineering
- Requirements modeling
- Design
- Planning
- Construction support
- Testing
- Deployment and handoff

The server tells the coding agent not to start implementation until
requirements, modeling, design, and planning are ready.

## Project Workspace

When `allow_workspace_write=True`, lifecycle artifacts are stored under:

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

Writing is explicit. If `allow_workspace_write=False`, tools return artifacts
without creating files.

## Install

```bash
pip install "se-lifecycle-mcp[anthropic]"
```

Other provider extras:

```bash
pip install "se-lifecycle-mcp[openai]"
pip install "se-lifecycle-mcp[google]"
pip install "se-lifecycle-mcp[all]"
```

## Configure

Only one provider key is required.

```bash
export ANTHROPIC_API_KEY="sk-ant-..."

# Optional:
export SE_MCP_PROVIDER="anthropic"
export SE_MCP_MODEL="claude-sonnet-4-20250514"
```

If no provider is configured, the MCP still starts and returns deterministic
fallback artifacts. This is useful for installation checks and tests.

## Connect To Claude Code

```bash
claude mcp add se-lifecycle -- python -m se_lifecycle_mcp
```

## Generic MCP Configuration

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

## Example Agent Flow

User:

```text
Build me a pharmacy inventory system
```

Agent should call:

```text
start_product_build(
  idea="Build me a pharmacy inventory system",
  workspace_root="/path/to/project",
  allow_workspace_write=true,
  allow_diagrams=true
)
```

Then the agent should:

1. Ask the returned discovery questions.
2. Call `advance_lifecycle_phase` for requirements.
3. Review the requirements gate.
4. Continue through modeling, design, and planning.
5. Generate Mermaid diagrams when useful and permitted.
6. Implement only after the lifecycle artifacts are ready.
7. Review construction and testing before handoff.

## Development

```bash
python -m pytest
python -m se_lifecycle_mcp
```

The previous SE principles tools are archived in `archive/se_principles_mcp/`.
They are not registered as public MCP tools in the new lifecycle product.
