# Plumbline

**Write-time verification for AI-generated code.**

Plumbline is an MCP server that makes AI coding agents write better code. It injects project knowledge before the agent writes, blocks bad code before it ships, and keeps multi-step work from going off the rails.

One install. One server. Nine tools.

```bash
pip install plumbline-ai[all]
```

## What it does

| Problem | Tool | What happens |
|---------|------|-------------|
| AI doesn't understand your project | `plumbline_context` | Injects conventions, pitfalls, and patterns from your git history |
| AI writes code that breaks things | `plumbline_check` | Blocks writes that will fail — bad imports, security issues, spec drift |
| AI commits untested mutations | `plumbline_verify` | Runs mutation testing on your changes before commit |
| AI gets sloppy on task 5 of 10 | `plumbline_advance` | Evidence gates force discipline across every task |

## Quick start

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "plumbline": {
      "command": "plumbline-mcp"
    }
  }
}
```

Or run `plumbline setup` for guided configuration including the `/btw` hook.

## Tools

### Context (know your project)

- **`plumbline_context`** — Project intelligence at session start. Conventions, pitfalls, decisions, hot files.
- **`plumbline_query`** — Search project knowledge mid-task.
- **`plumbline_co_changes`** — Files that change together. Read them before you edit.

### Verify (catch mistakes)

- **`plumbline_check`** — Fast pre-write gate (<500ms). Blocks bad code before it's written.
- **`plumbline_verify`** — Deep pre-commit gate (<30s). Mutation testing on changed lines.
- **`plumbline_explain`** — Understand why you were blocked.

### Gate (stay disciplined)

- **`plumbline_init`** — Start tracking a development plan.
- **`plumbline_advance`** — Move through phase gates with evidence.
- **`plumbline_status`** — Check where you are.

## The /btw hook

Plumbline includes a spotter hook that fires before every file write. It doesn't wait for the agent to ask for help — it injects relevant context right when the agent needs it.

```
/btw — auth.py usually changes with:
  - tests/test_auth.py
  - middleware/session.py
Did you read these before editing?
```

The agent never asked. The spotter saw what was happening and briefed it.

## Health check

```bash
plumbline doctor
```

Shows which engines are installed and healthy.

## Architecture

Plumbline wraps three proven engines under one surface:

- **Context** — powered by [Sentinel](https://github.com/evo-hydra/sentinel) (project intelligence from git history)
- **Verify** — powered by [Seraph](https://github.com/evo-hydra/seraph) (mutation testing, static analysis, security scanning)
- **Gate** — powered by [Morpheus](https://github.com/evo-hydra/morpheus-mcp) (plan state, phase gates, evidence validation)

Each engine is optional — install what you need:

```bash
pip install plumbline-ai[context]    # just project intelligence
pip install plumbline-ai[verify]     # just code verification
pip install plumbline-ai[gate]       # just plan enforcement
pip install plumbline-ai[all]        # everything
```

## Why

AI coding agents skip optional quality checks every time. Not sometimes — every time. We proved this across 49 tool invocations, 9 controlled experiments, and 5 production projects.

Advisory feedback (letter grades, suggestions, warnings) has a **0% action rate**. Blocking gates have a **~100% action rate**.

Plumbline doesn't advise. It verifies. At write time, not after.

*Built by [Evolving Intelligence AI](https://evolvingintelligence.ai)*

## License

MIT
