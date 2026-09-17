---
name: cli-agents
description: Delegate bounded sub-tasks to other command-line AI agents — Codex CLI, Claude Code CLI, Gemini CLI, Antigravity CLI (agy), and Aider (aider-chat) — from whichever agent is orchestrating. Use whenever the user asks to use Codex, Claude Code, Gemini, Antigravity/agy, Aider/aider-chat, an external/CLI agent, a second opinion, comparison, parallel work, or token/quota savings. Make sure to use this even if the user just names another agent ("ask Codex to…", "let Aider review…").
---

# CLI Agents

You are the orchestrator. Delegate bounded, well-scoped work to the OTHER
command-line agents (Codex, Claude Code, Gemini CLI, Antigravity/`agy`, Aider), keep final judgment
yourself, and never hand off destructive or external-side-effect actions.

Run delegations through the wrapper — it builds the right command per agent,
applies safe defaults, captures only the final message, and can run several in
parallel:

```bash
scripts/delegate.py --agent codex --mode read-only --cwd /repo \
  --prompt "Review auth.py for security issues; list by severity."
```

## Prerequisites

Each worker is a separate CLI that must be on `PATH`. Install only the ones you
delegate to — a missing binary is reported per-agent and skipped, never fatal.

- **Codex** (`codex`): `npm i -g @openai/codex` — see https://developers.openai.com/codex
- **Claude Code** (`claude`): https://code.claude.com/docs (usually already present)
- **Gemini CLI** (`gemini`): `npm install -g @google/gemini-cli` — see https://geminicli.com/docs/cli/
- **Antigravity** (`agy`): `curl -fsSL https://antigravity.google/cli/install.sh | bash`
- **Aider** (`aider`): `uv tool install --force --python python3.12 --with pip aider-chat@latest`.
  This machine has Aider installed through `uv`. The wrapper defaults to direct
  Z.ai GLM-5.2 High, not OpenRouter; its user-managed `OPENAI_API_KEY` must be
  a Z.ai key in the target repository's `.env`.

Auth is per-CLI and handled once by the user (sign-in or env key); this skill
never sets up credentials. `scripts/delegate.py` itself only needs Python 3.10+.

## When to use which agent

- **Codex** — code generation, refactors, repo-aware implementation; strong default worker.
- **Claude Code** — codebase edits, code review, repository reasoning, tool-heavy tasks.
- **Gemini CLI** (`gemini`) — Google's standalone CLI for headless reviews, long-context analysis, and Google-model second opinions. Use `--sandbox` and `--approval-mode plan` for read-only work.
- **Antigravity** (`agy`) — Google's agent: long-context summarization, independent
  critique, second opinions, Google-model perspective. Best for read-only work.
- **Aider** (`aider`) — focused local code review or edits when you want its
  repo-map workflow. By default it runs direct Z.ai `openai/glm-5.2` with High
  reasoning; use `--model` only for an intentional provider/model override.
  Use explicit files for edits; the wrapper disables its automatic Git commits.
- **Two+ in parallel** — comparison / second opinion: `--agent codex --agent gemini --agent antigravity` (or `--all`).
- Do the critical-path step yourself if waiting on a worker would block progress.

## Quick commands

```bash
# Second opinion from two agents at once (prompt via stdin), then synthesize locally
echo "List concrete risks in this migration plan: $(cat plan.md)" | \
  scripts/delegate.py --agent codex --agent gemini --agent antigravity --cwd /repo

# Bounded edit by one worker, then YOU inspect the diff
scripts/delegate.py --agent codex --mode edit --cwd /repo --prompt-file task.md
git -C /repo diff

# Machine-readable output for scripting
scripts/delegate.py --all --json --prompt "Summarize the architecture in 5 bullets." --cwd /repo

# Aider read-only review: dry-run plus no-Git/history side effects
scripts/delegate.py --agent aider --mode read-only --cwd /repo \
  --aider-read /abs/path/to/relevant/SKILL.md \
  --prompt "Review src/browser.py against the attached skill; list concrete gaps."

# Aider bounded edit: specify each editable file; inspect the diff yourself
scripts/delegate.py --agent aider --mode edit --cwd /repo \
  --aider-file src/browser.py --prompt "Implement the approved validation change."
git -C /repo diff
```

Run `scripts/delegate.py -h` for all flags (`--model`, `--add-dir`, `--timeout`, `--json`).

## Modes & safety

- `--mode read-only` (default): analysis / review / planning. Maps to codex
  `-s read-only`, claude `--permission-mode plan`, Gemini `--sandbox
  --approval-mode plan`, and antigravity `--sandbox`.
- `--mode edit`: bounded code edits. Maps to codex `-s workspace-write`, claude
  `acceptEdits`, Gemini `--approval-mode auto_edit`, antigravity plain print,
  and Aider explicit `--aider-file` edits. Gemini may still prompt for shell
  approvals in headless edit work; never replace that with `--yolo`.
- Aider read-only mode uses `--dry-run`, `--no-git`, `--no-gitignore`, and
  redirects its history files to `/dev/null`; this prevents worker-created
  repository artifacts as well as skill-file edits. Both Aider modes use
  `--no-auto-commits --no-dirty-commits`. It never receives all personal skills
  wholesale: attach only the relevant `SKILL.md` via `--aider-read`.
- Aider defaults to Z.ai GLM-5.2 High using the Coding Plan endpoint, bundled
  model settings, and 1M-context metadata. Do not put API keys in this skill;
  see `references/aider.md` for the required project-local `.env` names.
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
- `references/gemini-cli.md` — `gemini -p` headless mode, approval modes, and sandboxing.
- `references/antigravity-cli.md` — `agy -p` flags, sandbox, auth, models.
- `references/aider.md` — installation, one-shot command mode, safe wrapper flags,
  and the selected-skill convention.
- `references/prompt-templates.md` — review / edit / compare / extract templates.
