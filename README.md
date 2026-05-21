# SE Lifecycle MCP

> **Your AI coding agent's Software Engineering consultant.**

SE Lifecycle MCP is a Model Context Protocol server that transforms a one-line product idea into a **disciplined, step-by-step engineering build** — guided by principles from **8 authoritative SE books** and **university-level software engineering** rigor.

Instead of letting AI agents jump from *"Build me this app"* to code, this MCP ensures every project goes through the **complete SDLC** — with user involvement at every phase.

---

## 📚 Built on 8 SE Books

| Book | What It Contributes |
|------|-------------------|
| **Sommerville, Software Engineering 9th Ed** | SDLC phases, feasibility study, NFR taxonomy, 4 modeling perspectives, 9 architectural questions, V&V, 3 testing stages |
| **The Pragmatic Programmer** | DRY, Orthogonality, Tracer Bullets, Broken Windows |
| **Clean Code** | SOLID, naming, functions, error handling, testing (FIRST) |
| **Code Complete** | Defensive programming, complexity management, boundary analysis |
| **Design Patterns (GoF)** | 23 classical patterns + modern patterns |
| **Refactoring** | Code smell detection and elimination |
| **Pressman, Software Engineering** | Full SDLC phases, requirements engineering, modeling |
| **Designing Data-Intensive Applications** | Consistency, scalability, data design |

---

## 🔄 How It Works

```
User: "Build me a pharmacy inventory system"
         │
         ▼
┌─────────────────────────────────────────────┐
│ Phase 1: COMMUNICATION (Feasibility Study)  │
│  ├─ interview → ask user questions          │
│  ├─ draft    → generate vision doc          │
│  ├─ review   → user reviews & gives feedback│
│  └─ finalize → produce final artifact       │
│  └─ gate     → quality review               │
│                                             │
│ Phase 2: REQUIREMENTS (NFR Taxonomy)        │
│ Phase 3: MODELING (4 Perspectives, 5 UML)   │
│ Phase 4: DESIGN (4 Activities, 9 Questions) │
│ Phase 5: PLANNING (Risk Management)         │
│ Phase 6: CONSTRUCTION (Code Quality)        │
│ Phase 7: TESTING (V&V, 3 Stages)            │
│ Phase 8: DEPLOYMENT (Transition + Evolution)│
│                                             │
│ Each phase: interview → draft → review →    │
│             finalize → gate review → next   │
└─────────────────────────────────────────────┘
```

**Key principle**: The server **NEVER** advances without user permission. Every phase starts with an interview.

---

## 🛠️ Public Tools

| Tool | Purpose |
|------|---------|
| `start_product_build` | Starts from a one-line idea. Creates the project and product vision. |
| `advance_lifecycle_phase` | Moves through the SDLC with interview→draft→review→finalize flow. |
| `review_lifecycle_gate` | Quality gate: `pass`, `needs_work`, or `blocked` — uses deep SE book knowledge. |
| `generate_lifecycle_diagram` | Produces 12 Mermaid diagram types with **rendered images** via mermaid.ink. |
| `summarize_project_state` | Shows current phase, sub-step, artifacts, risks, gates, and next action. |

---

## 📊 12 Diagram Types (with Rendered Images)

Diagrams are automatically rendered to **SVG images** via [mermaid.ink](https://mermaid.ink) and saved alongside the Mermaid source files. Each diagram also gets a **viewable URL** and an **interactive editor link**.

| Type | Phase | Description |
|------|-------|-------------|
| `context` | Communication | System context: users, data, external systems |
| `use_case` | Requirements | Actors and system interactions |
| `activity` | Requirements | Workflow with decisions and parallel paths |
| `flow` | Modeling | Data flow through the system |
| `erd` | Modeling | Entity-relationship diagram |
| `state` | Modeling | State transitions for domain objects |
| `architecture` | Design | Layered/modular component view |
| `class` | Design | Classes, interfaces, and relationships |
| `component` | Design | Modules, packages, and connections |
| `sequence` | Design | Runtime interaction between services |
| `deployment` | Deployment | Servers, containers, databases |
| `roadmap` | Planning | Timeline with milestones |

---

## 📦 Installation

### Prerequisites

- **Python 3.10+** (3.11+ recommended)
- **pip** or **uv** package manager
- An API key from at least one LLM provider (Anthropic, OpenAI, or Google)

### Install from Source

```bash
git clone https://github.com/Stranger-S8/Se-lifecycle-mcp.git
cd Se-lifecycle-mcp
pip install -e ".[all,dev]"
```

Or with **uv** (faster):
```bash
git clone https://github.com/Stranger-S8/Se-lifecycle-mcp.git
cd Se-lifecycle-mcp
uv sync
```

### Install from PyPI (when published)

```bash
pip install se-lifecycle-mcp
```

---

## ⚙️ Configuration

### 1. Set Your API Key

Copy the example environment file and add your key:

```bash
cp .env.example .env
```

Then edit `.env`:

```bash
# Only ONE provider is required. The server auto-detects which key is available.

# Anthropic (recommended)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OR OpenAI
OPENAI_API_KEY=sk-your-key-here

# OR Google Gemini
GOOGLE_API_KEY=your-google-key-here
```

### 2. Optional Settings

```bash
# Override auto-detection
SE_MCP_PROVIDER=anthropic
SE_MCP_MODEL=claude-sonnet-4-20250514

# Diagram rendering: mermaid_ink (default) or none
SE_MCP_DIAGRAM_RENDERER=mermaid_ink
```

> **Note**: If no API key is configured, the server still works using deterministic fallback templates — no LLM required for basic functionality.

---

## 🔌 Connecting to Your AI Agent

### Claude Desktop

<details>
<summary><strong>🐧 Linux</strong></summary>

Edit `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "python3",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "/path/to/Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```

If using **uv**:
```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/Se-lifecycle-mcp", "python", "-m", "se_lifecycle_mcp"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```
</details>

<details>
<summary><strong>🍎 macOS</strong></summary>

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "python3",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "/path/to/Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```

If using **uv**:
```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/Se-lifecycle-mcp", "python", "-m", "se_lifecycle_mcp"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```
</details>

<details>
<summary><strong>🪟 Windows</strong></summary>

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "python",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "C:\\path\\to\\Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```

If using **uv**:
```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "uv",
      "args": ["run", "--directory", "C:\\path\\to\\Se-lifecycle-mcp", "python", "-m", "se_lifecycle_mcp"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```
</details>

---

### Claude Code (CLI)

```bash
# Add the MCP server
claude mcp add se-lifecycle -- python -m se_lifecycle_mcp

# Or with a specific path
claude mcp add se-lifecycle -- python -m se_lifecycle_mcp --directory /path/to/Se-lifecycle-mcp
```

---

### VS Code / Cursor

<details>
<summary><strong>🐧 Linux / 🍎 macOS</strong></summary>

Create or edit `.vscode/mcp.json` in your workspace:

```json
{
  "servers": {
    "se-lifecycle": {
      "command": "python3",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "/path/to/Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```
</details>

<details>
<summary><strong>🪟 Windows</strong></summary>

Create or edit `.vscode\mcp.json` in your workspace:

```json
{
  "servers": {
    "se-lifecycle": {
      "command": "python",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "C:\\path\\to\\Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```
</details>

---

### GitHub Copilot (VS Code)

<details>
<summary><strong>All Platforms</strong></summary>

Add to your VS Code `settings.json`:

```json
{
  "github.copilot.chat.mcpServers": {
    "se-lifecycle": {
      "command": "python3",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "/path/to/Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```

> **Windows**: Use `"python"` instead of `"python3"` and backslash paths.
</details>

---

### Windsurf / Codeium

<details>
<summary><strong>All Platforms</strong></summary>

Edit `~/.codeium/windsurf/mcp_config.json` (Linux/macOS) or `%USERPROFILE%\.codeium\windsurf\mcp_config.json` (Windows):

```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "python3",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "/path/to/Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```
</details>

---

### Antigravity (Google DeepMind)

<details>
<summary><strong>All Platforms</strong></summary>

Antigravity auto-discovers MCP servers. Add to your workspace's MCP config:

```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "python3",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "/path/to/Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```
</details>

---

### Generic MCP Client

For any MCP-compatible client, use this configuration:

```json
{
  "mcpServers": {
    "se-lifecycle": {
      "command": "python3",
      "args": ["-m", "se_lifecycle_mcp"],
      "cwd": "/path/to/Se-lifecycle-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-your-key-here"
      }
    }
  }
}
```

> **Platform Notes:**
> - **Windows**: Use `"python"` instead of `"python3"`, and use backslash (`\`) paths
> - **macOS/Linux**: Use `"python3"` and forward slash (`/`) paths
> - **Virtual environments**: Point `command` to the venv Python: `"/path/to/venv/bin/python"`

---

## 🔧 Verify Installation

After configuring, test your setup:

```bash
# Run the server directly to check for errors
python -m se_lifecycle_mcp

# Run the test suite
python -m pytest tests/ -v

# Check that imports work
python -c "from se_lifecycle_mcp.server import mcp; print('✅ Server loaded')"
```

---

## 📊 Diagram Rendering

Diagrams are automatically rendered as **SVG images** via the free [mermaid.ink](https://mermaid.ink) service.

### How It Works

1. Our tool generates Mermaid markup (e.g., flowchart, sequence diagram)
2. The markup is encoded and sent to `mermaid.ink`
3. An SVG image is saved to your project's `diagrams/` folder
4. You get:
   - **`.mmd` file** — Mermaid source code (editable)
   - **`.svg` file** — Rendered image (viewable in any browser)
   - **View URL** — Opens the rendered diagram in your browser
   - **Editor URL** — Opens in [Mermaid Live Editor](https://mermaid.live) for interactive editing

### Configuration

```bash
# Default: render via mermaid.ink (requires internet)
SE_MCP_DIAGRAM_RENDERER=mermaid_ink

# Disable rendering (only save .mmd text files)
SE_MCP_DIAGRAM_RENDERER=none
```

### Companion Diagram MCPs (Optional)

For **live preview** in your IDE, you can also connect these open-source diagram MCPs alongside SE Lifecycle:

| MCP | What It Does | Install |
|-----|-------------|---------|
| [mermaid-live-mcp](https://github.com/veelenga/mermaid-mcp) | Live browser preview with auto-refresh | `npx -y mermaid-live-mcp` |
| [draw.io MCP](https://github.com/jgraph/draw-io-mcp) | Opens diagrams in draw.io editor | `npx -y @jgraph/drawio-mcp` |

---

## 🏗️ Lifecycle Phases

| # | Phase | Sommerville Reference | What Happens |
|---|-------|----------------------|-------------|
| 1 | **Communication** | Ch.2: Inception + Feasibility Study | Understand idea, users, scope. Assess technical, economic, operational feasibility. |
| 2 | **Requirements** | Ch.4: RE Process (Elicitation → Specification → Validation) | Functional, non-functional (product/organizational/external), domain, inverse requirements. |
| 3 | **Modeling** | Ch.5: 4 Perspectives (External, Interaction, Structural, Behavioral) | Use cases, data models, state machines, sequence diagrams. 5 essential UML diagram types. |
| 4 | **Design** | Ch.6: 4 Design Activities + 9 Architectural Questions | Architecture, interfaces, components, database. SOLID, orthogonality, reversibility. |
| 5 | **Planning** | Ch.22-23: Risk Management + Project Planning | Priority ordering, risk classification (project/product/business), milestones. |
| 6 | **Construction** | Ch.7 + Clean Code + Code Complete | Code against approved design. Scope creep checks, code smell detection. |
| 7 | **Testing** | Ch.8: V&V + 3 Testing Stages | Development → System → Acceptance testing. Verification AND validation. |
| 8 | **Deployment** | RUP Transition + Ch.9: Software Evolution | Environment setup, handoff, maintenance strategy, evolution planning. |

---

## 🧑‍💻 Development

```bash
# Clone and setup
git clone https://github.com/Stranger-S8/Se-lifecycle-mcp.git
cd Se-lifecycle-mcp
pip install -e ".[all,dev]"

# Run tests
python -m pytest tests/ -v

# Run the server
python -m se_lifecycle_mcp

# Lint
ruff check src/

# Type check
mypy src/
```

---

## 📁 Project Structure

```
Se-lifecycle-mcp/
├── src/se_lifecycle_mcp/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py                 # FastMCP server with 5 tools
│   ├── models.py                 # ProjectState, phases, sub-steps
│   ├── workspace.py              # File I/O, state persistence
│   ├── diagram_renderer.py       # mermaid.ink rendering (zero deps)
│   ├── llm/                      # LLM provider abstraction
│   │   ├── base.py               # Abstract provider interface
│   │   ├── anthropic_provider.py
│   │   ├── openai_provider.py
│   │   └── google_provider.py
│   ├── prompts/                  # System prompts (SE book knowledge)
│   │   ├── discovery.py          # Product discovery prompt
│   │   ├── phase.py              # Phase-specific knowledge (8 books)
│   │   ├── gate_review.py        # Quality gate criteria
│   │   └── diagram.py            # Diagram generation prompt
│   └── tools/                    # MCP tool implementations
│       ├── start_product_build.py
│       ├── advance_lifecycle_phase.py
│       ├── review_lifecycle_gate.py
│       ├── generate_lifecycle_diagram.py
│       └── summarize_project_state.py
├── tests/
│   └── test_lifecycle_tools.py
├── docs/
│   └── PROJECT_DOCUMENTATION.md
├── lectures/                     # Reference SE textbooks
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**5 tools. 8 books. 43 interview questions. 12 diagram types. One MCP server.**

**Write better software.** 🚀
