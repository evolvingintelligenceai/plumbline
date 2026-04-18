# Changelog

All notable changes to `plumbline-ai` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] — 2026-04-18

The calibration ship. Released same day as 0.1.0 after a cross-model review
(Codex) and the first real dogfood session (an AI agent using Plumbline to
build an AI persistence architecture) surfaced blockers that would have
poisoned first-tester experience.

### Added

- **`plumbline-btw` console script** — new entry point in `[project.scripts]`.
  Replaces the ambiguous `python -m plumbline.hooks.btw` hook command. The
  `plumbline setup` command now emits the absolute path to `plumbline-btw`,
  eliminating the "wrong python resolved the hook" silent-fail mode.

### Changed

- **`plumbline setup` overhauled.** Actually writes `.mcp.json` and
  `.claude/settings.json` instead of printing config for the user to copy-paste.
  Installs Sentinel's git hooks via `sentinel watch --install`. Runs an initial
  `sentinel swarm` to backfill commit history. Merges into existing config
  files rather than overwriting. Idempotent re-run. `--dry-run` and `--force`
  flags added.
- **Claude Code PreToolUse hook schema updated** to the current nested shape:
  `hooks.PreToolUse[].hooks[] = [{type: "command", command: "..."}]`. The v0.1.0
  output used a deprecated flat schema that Claude Code silently ignored —
  the `/btw` hook never fired.
- **Morpheus evidence field `fdmc_review` renamed to `quality_review`.** The
  validator is now lens-agnostic — any quality framework's labels (FDMC, CLAMP,
  SOLID, custom) that use a `<Label> — <reason with file>` structure are
  accepted. Backward-compatible: morpheus-mcp 0.3.1 accepts both field names.
  Plans written against v0.1.0 continue to work.
- **`recommend_gates` output reframed** from directive ("skip — low historical
  ROI") to informational ("low historical ROI … informational; gate continues
  to enforce"). The old phrasing surfaced the exact advisory-drift pattern the
  tool was built to eliminate.
- **`plumbline_status` heading** now includes the plan's project path, making
  cross-project state bleed visible at a glance when Morpheus's global DB
  returns a plan from an unexpected project.
- **Parser accepts `### Task N[.N] — Title`** heading format in addition to
  `## N. Title`. On format mismatch, the error message lists both supported
  formats and points at a working example plan file.
- **Dependency constraints tightened:**
  - `morpheus-mcp>=0.3.1` (was `>=0.3.0`) — required for CHECK gate
    substance enforcement and `quality_review` rename.
  - `seraph-ai>=0.2.1` (was `>=0.1.1`) — required for honest mutation-score
    reporting.

### Fixed

- **CHECK gate now enforces substance.** The load-bearing thesis bug. Before
  v0.1.1, `plumbline_advance(phase=CHECK, evidence={"summary": "ok"})`
  silently passed — the single most important gate in Plumbline's
  "enforcement over advisory" thesis was itself advisory. Now rejects bare
  assertions (`ok`, `done`, `yes`, `true`, etc.) with an actionable message
  naming the failure and prescribing the minimum substantive content. Applies
  to MEDIUM+ tasks; MICRO/SMALL bypass; verify-mode (`status: pre_implemented`)
  preserved.
- **`plumbline_verify` no longer reports "100.0% mutation score" on 0 tested
  mutants.** Now reports `Mutation score: N/A — no mutable code in staged
  diff`. Previously implied perfect coverage on diffs with no mutable code
  (e.g., Markdown-only commits).
- **`plumbline setup` no longer silently leaves the Context pillar inert.**
  Previously required the user to discover and run `sentinel watch --install`
  manually; a fresh Plumbline project after `plumbline setup` would never
  learn from commits. Setup now wires the git hooks and swarm as part of
  its flow.
- **sdist no longer ships development artifacts.** `.plan_file`, `plans/`,
  `.env`, caches excluded via hatch sdist config.
- **`__version__` string aligned with `pyproject.toml` version.**

### Known issues (scheduled for v0.1.2)

- **COMMIT gate `seraph_id` evidence chain.** `plumbline_verify` doesn't
  return an assessment ID in its output; COMMIT gate still accepts
  `seraph_unavailable` as a free pass.
- **Phase-gate evidence vocabulary is code-centric.** Writing-mode tasks
  (Markdown deliverables, design docs) require loose mapping of
  `sibling_read` / `build_verified` / `tests_passed` to non-code equivalents.
  Design work in progress.
- **`plumbline setup` does not detect legacy hook entries.** If a user
  previously pasted a manual `python -m plumbline.hooks.btw` hook, v0.1.1
  setup appends the new one rather than replacing — resulting in duplicate
  hook firings.
- **`persistance` typo in `plumbline_context` header.** Lives in Sentinel
  source; blocked on next `git-sentinel` release.
- **`plumbline doctor` reports "OK" when engines are installed but not
  operational** (e.g., Sentinel installed but no `.sentinel/` data).
  Under consideration for v0.1.2.

## [0.1.0] — 2026-04-18

Initial release.

### Added

- **Unified MCP server** — one install (`pip install plumbline-ai[all]`),
  one `.mcp.json` entry, 8 tools under the `plumbline_*` prefix.
- **Context pillar (powered by Sentinel):**
  - `plumbline_context` — project intelligence at session start
    (conventions, pitfalls, decisions, hot files).
  - `plumbline_query` — free-text search across project knowledge.
  - `plumbline_co_changes` — files that change together with a target file.
- **Verify pillar (powered by Seraph):**
  - `plumbline_verify` — pre-commit mutation testing on staged diffs.
    Reports surviving mutants as questions, not scores.
  - `plumbline_explain` — understand a finding in detail.
- **Gate pillar (powered by Morpheus):**
  - `plumbline_init` — load a plan file and start tracking.
  - `plumbline_advance` — advance tasks through phase gates with evidence.
  - `plumbline_status` — check plan progress.
- **`/btw` PreToolUse spotter hook (INFORM level)** — fires before `Write`
  and `Edit` tool calls, injects co-change context from Sentinel.
- **`plumbline` CLI:**
  - `plumbline doctor` — check engine install status.
  - `plumbline version` — print version.
  - `plumbline setup` — emit configuration (v0.1.1 overhauls this).
- **MIT license.**
- **Python 3.10+ supported.**

### Deferred from v0.1.0

- **`plumbline_check` (pre-write tier-1 verification).** Descoped pre-launch
  after a Codex review found the call was passing `content=""` to Seraph,
  blinding all security/import/escalation checks. Returns in v0.2.0 with
  hook auto-invocation against proposed file content.

[0.1.1]: https://github.com/evolvingintelligenceai/plumbline/releases/tag/v0.1.1
[0.1.0]: https://github.com/evolvingintelligenceai/plumbline/releases/tag/v0.1.0
