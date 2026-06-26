# cli-agents

A universal **Agent Skill** that lets one command-line AI agent delegate bounded
sub-tasks to the *others* — **Codex CLI**, **Claude Code CLI**, and **Antigravity
CLI (`agy`)** — from whichever agent is orchestrating.

Whoever is driving stays the orchestrator (final judgment, verification, anything
with side effects); the workers do scoped analysis, review, or bounded edits, with
safe defaults and clean output capture. Run two in parallel for an instant second
opinion.

Built to the [Agent Skills open standard](https://agentskills.io) — one portable
`SKILL.md` works across Claude Code, Codex, Cursor, and Gemini/Antigravity.

## What it does

- **One wrapper, three workers** — `scripts/delegate.py` builds the right command
  per agent (`codex exec`, `claude --print`, `agy -p`), applies safe defaults, and
  returns only the final message.
- **Two scoped modes** — `read-only` (analysis/review/planning) and `edit` (bounded
  code edits). Never enables destructive auto-approval (no codex
  `danger-full-access`, no `--dangerously-skip-permissions`).
- **Parallel / second opinion** — `--agent codex --agent antigravity` (or `--all`)
  runs workers concurrently; compare or synthesize locally.
- **Progressive disclosure** — lean `SKILL.md`; CLI details live in `references/`,
  loaded on demand.

## Quick start

```bash
# Read-only review by Codex
scripts/delegate.py --agent codex --mode read-only --cwd /repo \
  --prompt "Review auth.py for security issues; list by severity."

# Same prompt to two agents at once, then synthesize locally
echo "List concrete risks in this migration plan: $(cat plan.md)" | \
  scripts/delegate.py --agent codex --agent antigravity --cwd /repo

# Bounded edit by Claude Code, then YOU inspect the diff
scripts/delegate.py --agent claude --mode edit --cwd /repo --prompt-file task.md
git -C /repo diff

# Machine-readable output
scripts/delegate.py --all --json --cwd /repo --prompt "Summarize the architecture."
```

Run `scripts/delegate.py -h` for all flags (`--model`, `--add-dir`, `--timeout`, `--json`).

## Install

As an agent skill, drop the folder into your skills directory:

```bash
# Claude Code
git clone https://github.com/tolmachevmaxim/cli-agents.git ~/.claude/skills/cli-agents

# Codex / Cursor / Gemini-CLI all read ~/.agents/skills
ln -s ~/.claude/skills/cli-agents ~/.agents/skills/cli-agents
```

Requirements: Python 3.10+, and whichever worker CLIs you want to delegate to on
`PATH` — [`codex`](https://developers.openai.com/codex),
[`claude`](https://code.claude.com/docs), and/or
[`agy`](https://antigravity.google) (Antigravity CLI). Missing binaries are
reported per-agent and skipped, not fatal.

## How it works

1. You write a focused, scoped prompt (file or stdin) and pick agent(s) + mode.
2. `delegate.py` runs the worker(s) with a scoped `--cwd`, safe mode, and a timeout.
3. If a worker edited files, you inspect `git diff` yourself.
4. You run verification locally — the worker's self-report is not trusted.
5. You summarize only the useful result; raw agent logs stay out.

## Safety

- Read-only by default; edit mode is bounded and still requires you to review the diff.
- Never delegates deploy / push / delete / send / post — those stay with the orchestrator.
- Never passes secrets or unnecessary personal data into a delegated prompt.
- Reference docs (`references/`) explain each CLI's exact safe flags.

## License

MIT — see [LICENSE](LICENSE).
