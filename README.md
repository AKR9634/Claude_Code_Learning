<div align="center">

<!-- HERO BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=Claude%20Code%20Learning&fontSize=48&fontColor=fff&animation=twinkling&fontAlignY=35&desc=A%20full-stack%20agentic%20dev%20workflow%20built%20end-to-end%20with%20Claude%20Code&descAlignY=57&descSize=18" width="100%"/>

<br/>

<!-- BADGES -->
[![Claude Code](https://img.shields.io/badge/Claude_Code-Agentic_CLI-orange?style=for-the-badge&logo=anthropic&logoColor=white)](https://code.claude.com)
[![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-blue?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.ai)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-Backend-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Railway](https://img.shields.io/badge/Deployed_on-Railway-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)](https://railway.app)
[![GitHub](https://img.shields.io/badge/GitHub-MCP_Connected-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](./LICENSE)

<br/>

> **[Spendly](https://github.com/campusx-official/spendly)** — a Flask-based expense tracker built end-to-end through an AI-native workflow.
> 13 learning milestones. Custom commands, specs, subagents, hooks, MCP servers, and plugins. Zero boilerplate hand-holding.

<br/>

[![⭐ Star this repo](https://img.shields.io/github/stars/campusx-official/spendly?style=social)](https://github.com/campusx-official/spendly)
&nbsp;·&nbsp;
[![🍴 Fork](https://img.shields.io/github/forks/campusx-official/spendly?style=social)](https://github.com/campusx-official/spendly/fork)
&nbsp;·&nbsp;
[![Issues](https://img.shields.io/github/issues/campusx-official/spendly?style=social)](https://github.com/campusx-official/spendly/issues)

</div>

---

## 📌 Table of Contents

- [📌 Table of Contents](#-table-of-contents)
- [🧠 What is this?](#-what-is-this)
- [🗺️ The Full Workflow](#️-the-full-workflow)
- [🏗️ Project Structure](#️-project-structure)
- [🚀 Phase 1 — Foundation](#-phase-1--foundation)
  - [Step 1 · Ollama as the Model Backend](#step-1--ollama-as-the-model-backend)
  - [Step 2 · Core Slash Commands](#step-2--core-slash-commands)
  - [Step 3 · Context Window Management](#step-3--context-window-management)
- [📐 Phase 2 — Project Structure \& Planning](#-phase-2--project-structure--planning)
  - [Step 4 · The CLAUDE.md File](#step-4--the-claudemd-file)
  - [Step 5 · Spec-Driven Development](#step-5--spec-driven-development)
  - [Step 6 · Custom `/create-spec` Command](#step-6--custom-create-spec-command)
- [⚙️ Phase 3 — Development Workflow](#️-phase-3--development-workflow)
  - [Step 7 · Plan Mode](#step-7--plan-mode)
  - [Step 8 · Git Branch Workflow](#step-8--git-branch-workflow)
  - [Step 9 · Frontend-Design Skill](#step-9--frontend-design-skill)
- [🤖 Phase 4 — Automation \& Integration](#-phase-4--automation--integration)
  - [Step 10 · Custom Subagents](#step-10--custom-subagents)
  - [Step 11 · MCP Server Integration](#step-11--mcp-server-integration)
- [🔒 Hooks Configuration](#-hooks-configuration)
  - [Hook 1 — Python Auto-formatter (PostToolUse)](#hook-1--python-auto-formatter-posttooluse)
  - [Hook 2 — Destructive-Command Guard (PreToolUse)](#hook-2--destructive-command-guard-pretooluse)
- [📦 Custom Slash Commands](#-custom-slash-commands)
- [🚢 Deployment](#-deployment)
- [🛠️ Tech Stack](#️-tech-stack)
- [📖 Resources](#-resources)

---

## 🧠 What is this?

This repository is the **complete learning artifact** of mastering [Claude Code](https://code.claude.com) — Anthropic's agentic terminal coding tool — by building **[Spendly](https://github.com/campusx-official/spendly)**, a real Flask expense-tracking web app, from scratch.

Every feature was built using Claude Code's native workflow:

| Layer | What I built |
|---|---|
| 🧠 **AI backbone** | Ollama local LLM → Claude API |
| 📁 **Memory** | A project-scoped `CLAUDE.md`, with user/local scopes layered on top |
| 📋 **Planning** | Spec-driven development (`.claude/specs/`) with plan mode |
| ⚡ **Commands** | Custom slash commands in `.claude/commands/`: `/create-spec`, `/test-feature`, `/code-review-feature` |
| 🤖 **Agents** | Specialized subagents: test-writer, test-runner, quality-reviewer, security-reviewer |
| 🔌 **Integration** | MCP servers: GitHub, Figma, and more |
| 🪝 **Automation** | Hooks: Python formatter + destructive-command guard |
| 🚀 **Deploy** | Railway plugin from the Claude Code marketplace |

---

## 🗺️ The Full Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CLAUDE CODE LEARNING WORKFLOW                         │
│                        [ Spendly — Expense Tracker ]                        │
└─────────────────────────────────────────────────────────────────────────────┘

 PHASE 1 ─ FOUNDATION
 ╔══════════════╗    ╔══════════════════╗    ╔═══════════════════════╗
 ║  1. Ollama   ║───►║  2. Slash cmds   ║───►║  3. Context window   ║
 ║  Local LLM   ║    ║  /init /memory   ║    ║  /compact strategy   ║
 ╚══════════════╝    ╚══════════════════╝    ╚═══════════════════════╝
         │
         ▼
 PHASE 2 ─ PROJECT STRUCTURE & PLANNING
 ╔══════════════╗    ╔══════════════════╗    ╔═══════════════════════╗
 ║  4. CLAUDE   ║───►║  5. Spec-driven  ║───►║  6. /create-spec     ║
 ║   .md file   ║    ║    development   ║    ║  custom command      ║
 ╚══════════════╝    ╚══════════════════╝    ╚═══════════════════════╝
         │
         ▼
 PHASE 3 ─ DEVELOPMENT WORKFLOW
 ╔══════════════╗    ╔══════════════════╗    ╔═══════════════════════╗
 ║  7. Plan     ║───►║  8. Git branch   ║───►║  9. Skills           ║
 ║     mode     ║    ║     workflow     ║    ║  frontend-design     ║
 ╚══════════════╝    ╚══════════════════╝    ╚═══════════════════════╝
         │
         ▼
 PHASE 4 ─ AUTOMATION & INTEGRATION
 ╔══════════════╗    ╔══════════════════╗    ╔══════════╗    ╔══════╗
 ║  10. Sub-    ║───►║  11. MCP servers ║───►║ 12. Hooks║───►║  13. ║
 ║    agents    ║    ║  GitHub, Figma   ║    ║  Pre/Post║    ║Plugin║
 ╚══════════════╝    ╚══════════════════╝    ╚══════════╝    ╚══════╝
                                                                  │
                                                                  ▼
                                                         [ 🚀 Deployed on Railway ]
```

---

## 🏗️ Project Structure

This mirrors the actual layout of the [Spendly repo](https://github.com/campusx-official/spendly) — a flat Flask app rather than a deeply nested package, which kept Claude Code's context lean throughout the build:

```
spendly/
│
├── 📄 CLAUDE.md                    # Project-scoped persistent context (repo root)
│
├── 🗂️ .claude/
│   ├── commands/                   # Custom slash commands
│   │   ├── create-spec.md          # /create-spec — generates spec files
│   │   ├── test-feature.md         # /test-feature — runs test subagents
│   │   └── code-review-feature.md  # /code-review-feature — review pipeline
│   │
│   ├── specs/                      # Specification documents (from /create-spec)
│   │   └── *.md
│   │
│   └── launch.json                 # Editor launch/debug config for the session
│
├── 🐍 app.py                       # Flask application — routes, views, app logic
├── 🗄️ database/                    # SQLite schema & seed/setup scripts
├── 🎨 static/                      # CSS (no JS framework — plain HTML + CSS)
├── 🖼️ templates/                   # Jinja2 templates
├── 🧪 tests/                       # pytest suite (auto-generated by test-writer agent)
│
├── 🗄️ spendly.db                   # Runtime SQLite database (guarded by a hook)
├── 🗄️ spendly-backup.db            # Backup database snapshot
├── pytest.ini                       # pytest configuration
├── requirements.txt                  # Python dependencies
├── .gitignore
└── README.md                       # You are here
```

> Note: agent definitions, the frontend-design skill, the hooks config, and the full MCP server list shown below lived in my local Claude Code setup (`~/.claude/`) while driving the build — what's committed to the repo itself is the source app plus `.claude/commands/` and `.claude/specs/`.

---

## 🚀 Phase 1 — Foundation

### Step 1 · Ollama as the Model Backend

Instead of burning API credits while learning, Claude Code was pointed at a local [Ollama](https://ollama.ai) instance via the OpenAI-compatible endpoint:

```bash
# Install Ollama and pull a model
ollama pull llama3.3

# Point Claude Code at Ollama
export ANTHROPIC_BASE_URL=http://localhost:11434/v1
export ANTHROPIC_API_KEY=ollama   # any non-empty string

# Start Claude Code
claude
```

> 💡 **Why this matters:** Zero cost during learning, full offline capability, and identical API surface to Anthropic's hosted models.

---

### Step 2 · Core Slash Commands

The built-in command surface that drives every Claude Code session:

| Command | What it does |
|---|---|
| `/init` | Bootstraps a `CLAUDE.md` from your codebase |
| `/memory` | Inspects what Claude currently remembers |
| `/clear` | Resets the context window entirely |
| `/compact` | Summarizes history to free context space |
| `/context` | Shows current window usage |
| `/model` | Swaps the model mid-session |
| `/permissions` | Audits which tools are allowed |
| `/mcp` | Lists and manages MCP servers |
| `/agents` | Shows running subagents |
| `/tasks` | Task management and dependency tracking |

---

### Step 3 · Context Window Management

Context fills as work accumulates. The strategy:

```
 0% ──────── 50% ──────── 70% ─── 85% ─── 90%+
   Work freely   Start watching   /compact   /clear
```

Key insight: `/compact` creates a compressed summary so the session can keep going without losing track of earlier decisions and conventions.

---

## 📐 Phase 2 — Project Structure & Planning

### Step 4 · The CLAUDE.md File

A single project-level `CLAUDE.md` at the repo root holds Spendly's persistent context — conventions, commands, and architecture notes that get pulled into every session automatically. Claude Code also supports layering this with a personal user-global file and a gitignored local override, useful once a project grows beyond one contributor:

```
~/.claude/CLAUDE.md          ← User-global (personal preferences)
    └── ./CLAUDE.md          ← Project (team conventions, committed)
        └── CLAUDE.local.md  ← Local (machine-specific, gitignored)
```

---

### Step 5 · Spec-Driven Development

The workflow that replaced "just start coding":

```
 ┌─────────────────┐     ┌──────────────────┐     ┌────────────────────┐
 │  SPECIFICATION  │────►│     DESIGN       │────►│  IMPLEMENTATION    │
 │  What to build  │     │  How to build it │     │  Claude writes     │
 │  & why          │     │  Architecture,   │     │  from the design,  │
 │                 │     │  data model,     │     │  not from scratch  │
 │                 │     │  API contracts   │     │                    │
 └─────────────────┘     └──────────────────┘     └────────────────────┘
```

---

### Step 6 · Custom `/create-spec` Command

```markdown
<!-- .claude/commands/create-spec.md -->
---
description: Generate a specification document for a new feature
allowed-tools: Read, Write, Glob
---

Gather requirements for the feature the user wants to build.
Ask clarifying questions about scope, constraints, and acceptance criteria.
Write the spec to `.claude/specs/<feature-name>-spec.md`.
```

---

## ⚙️ Phase 3 — Development Workflow

### Step 7 · Plan Mode

Before touching a single file, plan mode reads the codebase and spec, then produces a full implementation plan for review:

```bash
# Activate plan mode
Shift+Tab   # in the Claude Code UI
```

```
USER: implement the budget alert feature from the spec

CLAUDE (Plan Mode):
  ✦ Read .claude/specs/budget-alert-spec.md
  ✦ Scan app.py, database/, templates/
  ✦ Proposed plan:
      1. Add a BudgetAlert table/helper to database/
      2. Add /alerts route with POST + GET handlers in app.py
      3. Add a notification trigger in the expense-creation logic
      4. Write pytest cases covering happy path + edge cases
  
  Proceed? [Y/n]
```

---

### Step 8 · Git Branch Workflow

Every feature → a fresh branch → merge → delete:

```bash
# Per feature (later automated via MCP)
git checkout -b feature/budget-alerts
# ... Claude implements ...
git add . && git commit -m "feat: add budget alert system"
git checkout main && git merge feature/budget-alerts
git branch -d feature/budget-alerts
```

This entire flow was later **automated** with a custom slash command backed by the GitHub MCP server.

---

### Step 9 · Frontend-Design Skill

Spendly's UI is plain HTML templates styled with hand-written CSS — no JS framework. A `frontend-design` skill captured the design tokens and component conventions so every new template stayed visually consistent:

```markdown
---
name: frontend-design
description: Spendly UI design tokens, component patterns, and style conventions
---

## Design tokens
- Primary: indigo accent
- Surface: light neutral background
- Typography: system sans-serif, 14px base

## Component conventions
- Cards: rounded corners, subtle 1px border, consistent padding
- Buttons: rounded, medium weight, no uppercase
...
```

Skills persist across the session and survive `/compact`, so this UI knowledge stayed available throughout the build.

---

## 🤖 Phase 4 — Automation & Integration

### Step 10 · Custom Subagents

Four specialized agents handled distinct parts of the workflow:

<table>
<tr>
<th>Agent</th>
<th>Frontmatter</th>
<th>Role</th>
</tr>
<tr>
<td>

**test-writer**

</td>
<td>

```yaml
tools: Read, Grep, Glob, Write
model: sonnet
```

</td>
<td>Reads implementation, writes pytest test suites</td>
</tr>
<tr>
<td>

**test-runner**

</td>
<td>

```yaml
tools: Read, Bash
model: haiku
```

</td>
<td>Executes tests, parses results, reports failures</td>
</tr>
<tr>
<td>

**quality-reviewer**

</td>
<td>

```yaml
tools: Read, Grep, Glob
model: sonnet
```

</td>
<td>Code quality, complexity, duplication checks</td>
</tr>
<tr>
<td>

**security-reviewer**

</td>
<td>

```yaml
tools: Read, Grep, Glob
model: opus
```

</td>
<td>Vulnerability scan, injection risks, secrets exposure</td>
</tr>
</table>

Invoked via custom commands:

```bash
/test-feature        # → spawns test-writer then test-runner in sequence
/code-review-feature  # → spawns quality-reviewer + security-reviewer in parallel
```

---

### Step 11 · MCP Server Integration

```jsonc
// .mcp.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" }
    },
    "figma": {
      "command": "npx",
      "args": ["-y", "@figma/mcp-server"],
      "env": { "FIGMA_ACCESS_TOKEN": "${FIGMA_TOKEN}" }
    }
  }
}
```

The **auto-merge command** (backed by GitHub MCP):

```markdown
<!-- .claude/commands/merge-and-cleanup.md -->
---
description: Merge current branch to main and delete it
allowed-tools: Bash, mcp__github__create_pull_request, mcp__github__merge_pull_request
---

Use the GitHub MCP to:
1. Create a PR from the current branch to main
2. Merge it with squash strategy
3. Delete the feature branch remotely and locally
```

---

## 🔒 Hooks Configuration

The hooks live in `.claude/settings.json` and fire **deterministically** — unlike prompts, they can't be skipped.

```jsonc
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"\nimport sys, json, subprocess\ndata = json.load(sys.stdin)\nfile = data.get('tool_input', {}).get('file_path', '')\nif file.endswith('.py'):\n    subprocess.run(['python3', '-m', 'black', '--quiet', file])\n\""
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 -c \"\nimport sys, json\ndata = json.load(sys.stdin)\ncmd = data.get('tool_input', {}).get('command', '')\nprotected = ['spendly.db', '.env', 'migrations/']\ndangerous = ['rm ', 'rm -', 'unlink ', 'truncate ']\nfor d in dangerous:\n    if d in cmd:\n        for p in protected:\n            if p in cmd:\n                print(f'BLOCKED: Cannot run destructive command on protected file: {p}', file=__import__(\\\"sys\\\").stderr)\n                raise SystemExit(2)\n\""
          }
        ]
      }
    ]
  }
}
```

### Hook 1 — Python Auto-formatter (PostToolUse)

```
Claude writes/edits any .py file
        │
        ▼
PostToolUse fires → reads file_path from tool_input
        │
        ▼ (if .py)
python3 -m black --quiet <file>    ← formats in-place silently
```

### Hook 2 — Destructive-Command Guard (PreToolUse)

```
Claude attempts a Bash command
        │
        ▼
PreToolUse fires → reads command from tool_input
        │
        ├── contains: rm / unlink / truncate ?
        │       └── AND targets: spendly.db / .env / migrations/ ?
        │               │
        │               ▼
        │          exit(2) → BLOCKED message sent back to Claude
        │
        └── safe → exit(0) → command proceeds
```

> **Why exit code 2?** Per the Claude Code hooks spec, exit code 2 blocks the tool call *and* feeds the stderr message back to Claude as context, allowing it to self-correct — this is exactly what saved `spendly.db` more than once during the build.

---

## 📦 Custom Slash Commands

| Command | File | What it does |
|---|---|---|
| `/create-spec` | `.claude/commands/create-spec.md` | Interviews you and writes a spec file |
| `/test-feature` | `.claude/commands/test-feature.md` | Runs test-writer → test-runner agents |
| `/code-review-feature` | `.claude/commands/code-review-feature.md` | Runs quality + security review agents |
| `/merge-and-cleanup` | `.claude/commands/merge-and-cleanup.md` | GitHub MCP: PR → merge → branch delete |

---

## 🚢 Deployment

Deployed via the **Railway plugin** from Claude Code's official plugin marketplace.

```bash
# Inside Claude Code
/plugin install railway

# Then simply ask Claude:
"Deploy the current project to Railway and give me the public URL"
```

Railway's plugin bundled a deployment skill + MCP server that handled environment configuration, build pipeline, and public URL generation — all from within the Claude Code session.

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology |
|---|---|
| 🤖 AI Engine | Claude Code + Anthropic API |
| 🧠 Local Model | Ollama (llama3.3 / qwen2.5-coder) |
| 🐍 Backend | Python + Flask (`app.py`) |
| 🗄️ Database | SQLite (`spendly.db`, schema in `database/`) |
| 🎨 Frontend | HTML templates (`templates/`) + plain CSS (`static/`) |
| 🔌 MCP | GitHub, Figma |
| 🧪 Testing | pytest (generated by test-writer agent) |
| 📐 Formatting | black (enforced by PostToolUse hook) |
| 🚀 Deployment | Railway (via Claude Code plugin) |

</div>

---

## 📖 Resources

- 📚 [Claude Code Official Docs](https://code.claude.com/docs/en/overview)
- 🔗 [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- 🤖 [Subagents Guide](https://code.claude.com/docs/en/sub-agents)
- 🧩 [Skills Documentation](https://code.claude.com/docs/en/skills)
- 🔌 [MCP Integration](https://code.claude.com/docs/en/mcp)
- 🔌 [Extend Claude Code](https://code.claude.com/docs/en/features-overview)
- 💻 [Spendly source code](https://github.com/campusx-official/spendly)

---

<div align="center">

**Built with 🤖 Claude Code · Deployed on 🚄 Railway · 100% AI-native workflow**

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=100&section=footer" width="100%"/>

</div>