# Plumbline

**Write-time intelligence for AI-generated code.**

Plumbline is an MCP server that makes AI coding agents work against your project's reality — not their priors. It injects project knowledge before the agent writes, runs mutation testing before you commit, and keeps multi-step work from going off the rails.

One install. One server. Eight tools. One spotter hook.

```bash
pip install plumbline-ai[all]
```

## What it does

| Problem | Tool | What happens |
|---------|------|-------------|
| AI doesn't understand your project | `plumbline_context` | Injects conventions, pitfalls, and patterns from your git history |
| AI forgets related files | `/btw` hook | Before every Write/Edit, tells the agent which files usually change together |
| AI commits untested mutations | `plumbline_verify` | Runs mutation testing on staged changes before commit |
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

- **`plumbline_verify`** — Pre-commit mutation testing on staged changes. Reports surviving mutants as questions: *"Your code still passes tests if X is changed to Y. Is that intentional?"*
- **`plumbline_explain`** — Understand a finding in detail.

### Gate (stay disciplined)

- **`plumbline_init`** — Start tracking a development plan.
- **`plumbline_advance`** — Move through phase gates with evidence. The gate validates your evidence is real, not bare assertions.
- **`plumbline_status`** — Check where you are.

## The `/btw` hook

Plumbline includes a spotter hook that fires before every file write. It doesn't wait for the agent to ask for help — it injects relevant context when the agent is about to edit a file.

```
/btw — src/auth.py usually changes with:
  - tests/test_auth.py
  - middleware/session.py
Did you read these before editing?
```

The agent never asked. The spotter saw what was happening and briefed it.

v0.1.0 ships at **INFORM level** — the hook injects context but does not block writes. **GATE level** — pre-write blocking via mutation analysis of the proposed content — ships in v0.2.0.

## Health check

```bash
plumbline doctor
```

Shows which engines are installed and healthy.

## Architecture

Plumbline wraps three proven engines under one surface:

- **Context** — powered by [Sentinel](https://github.com/evo-hydra/sentinel) (project intelligence from git history)
- **Verify** — powered by [Seraph](https://github.com/evo-hydra/seraph) (mutation testing, static analysis)
- **Gate** — powered by [Morpheus](https://github.com/evo-hydra/morpheus-mcp) (plan state, phase gates, evidence validation)

Each engine is optional — install what you need:

```bash
pip install plumbline-ai[context]    # just project intelligence
pip install plumbline-ai[verify]     # just code verification
pip install plumbline-ai[gate]       # just plan enforcement
pip install plumbline-ai[all]        # everything
```

## Why

AI coding agents skip optional quality checks every time. Not sometimes — every time. We measured this across 49 tool invocations, 9 controlled experiments, and 5 production projects.

Advisory feedback (letter grades, suggestions, warnings) has a **0% action rate**. Blocking gates have a **~100% action rate**.

Plumbline doesn't advise. It enforces — through evidence-gated task advancement, mutation-based commit verification, and write-time context injection.

## Roadmap

**v0.1.0 (current):** 8 MCP tools + `/btw` INFORM hook. Pre-commit verification. Plan-state gating. Project intelligence injection.

**v0.2.0:** `plumbline_check` returns — pre-write blocking via the `/btw` hook automatically running mutation analysis on proposed file content before the Write/Edit tool call completes.

**v0.3.0:** Debrief loop — post-session `/plumbline:debrief` skill that interviews the agent and feeds hook tuning back into the signal-to-noise optimizer.

## License

MIT.

*Built by [Evolving Intelligence AI](https://evolvingintelligence.ai).*
