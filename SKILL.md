---
name: cli-agents
description: Delegate bounded sub-tasks to other command-line AI agents — Codex CLI, Claude Code CLI, and Antigravity CLI (agy) — from whichever agent is orchestrating. Use whenever the user asks to use Codex, use Claude Code, use Antigravity/agy, run an external/CLI agent, get a second opinion, compare agent outputs, parallelize work, or save tokens/quota by offloading analysis or bounded edits. Make sure to use this even if the user just names another agent ("ask Codex to…", "let Antigravity review…").
---

# CLI Agents

You are the orchestrator. Delegate bounded, well-scoped work to the OTHER
command-line agents (Codex, Claude Code, Antigravity/`agy`), keep final judgment
yourself, and never hand off destructive or external-side-effect actions.

Run delegations through the wrapper — it builds the right command per agent,
applies safe defaults, captures only the final message, and can run several in
parallel:

```bash
scripts/delegate.py --agent codex --mode read-only --cwd /repo \
  --prompt "Review auth.py for security issues; list by severity."
```

## When to use which agent

- **Codex** — code generation, refactors, repo-aware implementation; strong default worker.
- **Claude Code** — codebase edits, code review, repository reasoning, tool-heavy tasks.
- **Antigravity** (`agy`) — Google's agent: long-context summarization, independent
  critique, second opinions, Google-model perspective. Best for read-only work.
- **Two+ in parallel** — comparison / second opinion: `--agent codex --agent antigravity` (or `--all`).
- Do the critical-path step yourself if waiting on a worker would block progress.

## Quick commands

```bash
# Second opinion from two agents at once (prompt via stdin), then synthesize locally
echo "List concrete risks in this migration plan: $(cat plan.md)" | \
  scripts/delegate.py --agent codex --agent antigravity --cwd /repo

# Bounded edit by one worker, then YOU inspect the diff
scripts/delegate.py --agent codex --mode edit --cwd /repo --prompt-file task.md
git -C /repo diff

# Machine-readable output for scripting
scripts/delegate.py --all --json --prompt "Summarize the architecture in 5 bullets." --cwd /repo
```

Run `scripts/delegate.py -h` for all flags (`--model`, `--add-dir`, `--timeout`, `--json`).

## Modes & safety

- `--mode read-only` (default): analysis / review / planning. Maps to codex
  `-s read-only`, claude `--permission-mode plan`, antigravity `--sandbox`.
- `--mode edit`: bounded code edits. Maps to codex `-s workspace-write`, claude
  `acceptEdits`, antigravity plain print (prefer codex/claude for heavy edits).
- The wrapper never enables destructive modes (no codex danger-full-access, no
  `--dangerously-skip-permissions`).
- Never delegate deploy / push / delete / send / post — do those yourself with
  explicit user intent.
- Never pass secrets, tokens, or unnecessary personal data into a delegated prompt.

## Prompt contract

Every delegated prompt should state: **Role** (what the worker does), **Scope**
(exact files/dirs it may touch), **Constraints** (no deploy/secrets/unrelated
refactors), **Output** (concise result + changed-files list if editing),
**Verification** (checks to run/report). Ready-made templates:
`references/prompt-templates.md`.

## Workflow

1. Write a focused prompt (file or stdin), pick agent(s) and mode.
2. Run `scripts/delegate.py` with a scoped `--cwd` and a timeout.
3. If it edited files, inspect `git diff` yourself.
4. Run verification locally — don't trust the worker's self-report.
5. Summarize only the useful result to the user; don't paste raw agent logs.

## References

- `references/codex-cli.md` — `codex exec` flags, sandbox modes, clean capture.
- `references/claude-code.md` — `claude --print` flags, permission modes, budget.
- `references/antigravity-cli.md` — `agy -p` flags, sandbox, auth, models.
- `references/prompt-templates.md` — review / edit / compare / extract templates.
