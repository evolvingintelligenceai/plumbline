# Plumbline Tester Recruitment Kit

Goal: recruit 10 AI-heavy developers to install `plumbline-ai[all]`, connect it to Claude Code, use it on real code, and report whether the `/btw` hook and pre-commit verification changed their behavior.

## Positioning

Primary line:

> Plumbline makes AI coding agents work against your project, not their priors.

Shorter line:

> Write-time context and pre-commit verification for AI-generated code.

What to emphasize for v0.1.0:

- One MCP server, eight tools, one `/btw` hook.
- The hook injects co-change context before Write/Edit operations.
- `plumbline_verify` runs mutation-oriented verification on staged diffs before commit.
- `plumbline_advance` keeps multi-step work disciplined through evidence gates.
- v0.1.0 is INFORM-level for writes: context injection, not write blocking.

What not to imply yet:

- Do not claim v0.1.0 blocks file writes.
- Do not lead with "54 MCP tools" or the old sidecar names.
- Do not sell enterprise governance before developer usefulness is proven.
- Do not make "0% action rate" the first sentence; use it after the mechanism is clear.

## Ideal Testers

Prioritize developers who:

- use Claude Code, Cursor, Cline, Aider, Codex, or another coding agent several times a week
- work in repos with real git history, not only greenfield prototypes
- have tests they can run locally
- are willing to install a local MCP server
- will give blunt feedback on false positives, noise, and setup friction

Avoid first-round testers who:

- do not use AI coding agents regularly
- mainly want a hosted SaaS product
- cannot share even anonymized feedback
- are only looking for a generic linter

## Ask

Ask for one real session, not a vague trial:

1. Install `plumbline-ai[all]`.
2. Run `plumbline setup`.
3. Initialize Sentinel data in a repo with history.
4. Use Claude Code on one real bug fix or feature.
5. Before committing, run `plumbline_verify`.
6. Send feedback using the questions below.

## Feedback Questions

Send these after the test:

1. Did install and setup work without hand-holding?
2. Did `/btw` fire at the right moment?
3. Was the `/btw` context useful, noisy, or absent?
4. Did it cause you or the agent to read a related file you otherwise would have skipped?
5. Did `plumbline_verify` find anything actionable?
6. What was the first confusing moment?
7. Would you keep this enabled for a week? Why or why not?
8. What would make this a must-have instead of a curiosity?

## Direct DM

Subject:

> Looking for 10 AI-heavy devs to test Plumbline

Message:

> I just shipped Plumbline 0.1.0: one MCP server for AI coding agents that injects project context before writes and verifies staged diffs before commit.
>
> The thesis is simple: agents skip optional checks, especially under context pressure. Plumbline puts the context where the agent is already working:
>
> - `/btw` fires before Write/Edit and surfaces files that usually change together
> - `plumbline_verify` checks staged diffs before commit
> - `plumbline_advance` gates multi-step work with evidence
>
> I am looking for 10 developers who use AI coding agents on real repos and will give blunt feedback. The ask is one real coding session, then 8 feedback questions. MIT, local-first, no hosted service.
>
> Install:
>
> `pip install plumbline-ai[all]`
>
> Repo:
>
> https://github.com/evolvingintelligenceai/plumbline
>
> Interested?

## LinkedIn Post

> I am looking for 10 developers who use AI coding agents heavily and are willing to test Plumbline on a real repo.
>
> Plumbline is a local MCP server that makes agents work against your project's reality, not their priors.
>
> v0.1.0 does three things:
>
> - injects project knowledge before the agent writes
> - surfaces co-change files through a `/btw` hook before Write/Edit
> - verifies staged diffs before commit
>
> The problem it targets is not "models are bad at code." The problem is timing. Most feedback arrives after the agent has already made the decision. Plumbline moves the useful context earlier.
>
> First release is intentionally small: one install, eight MCP tools, one hook. Works with Claude Code. MIT.
>
> `pip install plumbline-ai[all]`
>
> Repo: https://github.com/evolvingintelligenceai/plumbline
>
> If you use AI agents on real code and can give direct feedback on setup friction, hook usefulness, and false positives, I would like you in the first 10 testers.

## Show HN Draft

> Show HN: Plumbline - write-time context for AI coding agents
>
> I built Plumbline because most AI code-quality feedback arrives too late. The agent writes the code, moves on, and the warning lands after the decision has already been made.
>
> Plumbline is a local MCP server for Claude Code and other MCP-capable agents. It wraps project intelligence, staged-diff verification, and evidence gates under one small tool surface.
>
> The first release includes:
>
> - `plumbline_context` for project conventions, pitfalls, and co-change patterns
> - a `/btw` PreToolUse hook that fires before Write/Edit and says which files usually change together
> - `plumbline_verify` for pre-commit verification on staged diffs
> - `plumbline_advance` for evidence-gated multi-step work
>
> v0.1.0 is deliberately scoped: the `/btw` hook informs but does not block writes yet. The next release adds pre-write blocking for high-confidence findings.
>
> Install:
>
> `pip install plumbline-ai[all]`
>
> Repo: https://github.com/evolvingintelligenceai/plumbline
>
> I am looking for 10 AI-heavy developers to try it on real repos and tell me where the hook is useful, noisy, or missing the point.

## Tester Tracking

Track each tester by:

- name / handle
- agent used
- repo type
- installed successfully
- `/btw` fired
- useful hook count
- noisy hook count
- `plumbline_verify` outcome
- would keep enabled for a week
- strongest quote
- blocking issue

Success threshold for the first cohort:

- 7/10 complete install without live help
- 5/10 see at least one useful `/btw` injection
- 3/10 say they would keep it enabled for a week
- at least 5 concrete setup or signal-quality issues captured

