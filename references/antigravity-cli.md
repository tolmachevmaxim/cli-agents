# Antigravity CLI Reference (worker)

Google's terminal coding agent. Binary: `agy`. Observed locally: `agy 1.0.12`.
Auth comes from the signed-in Antigravity account (no API key needed locally if
you're logged into the Antigravity app/IDE; for unattended CI set
`ANTIGRAVITY_API_KEY` or `GEMINI_API_KEY`).

> Replaces the legacy `gemini` CLI, whose free "Code Assist for individuals"
> OAuth tier was discontinued (`IneligibleTierError`). Antigravity is the
> product Google migrated that to.

## Non-interactive execution

```bash
agy -p "Summarize this repository." --print-timeout 5m
agy --print "Review this plan for risks."
```

`-p` / `--print` / `--prompt` run a single prompt non-interactively and print the
response to stdout. The prompt is the value passed to `-p`.

## Key flags

```bash
-p, --print "<prompt>"      # single non-interactive prompt → stdout
--model <name>              # session model (see: agy models)
--add-dir <DIR>            # add a directory to the workspace (repeatable)
--project <id>             # project ID for the session
--sandbox                  # run with terminal restrictions (safer for read-only)
--print-timeout 5m         # wait timeout for print mode (default 5m)
--dangerously-skip-permissions   # auto-approve ALL tool requests — do NOT use in delegation
--continue / -c            # continue the most recent conversation
--conversation <id>        # resume a conversation
```

Subcommands: `agy models` (list models), `agy update`, `agy plugin …`, `agy install`.

## Safety guidance

- read-only delegation → add `--sandbox` (terminal restrictions); do not skip permissions.
- edit delegation → plain `agy -p` (no `--sandbox`); inspect `git diff` afterwards.
- NEVER pass `--dangerously-skip-permissions` from delegation — it auto-approves
  every tool call. For bounded edits that need many approvals, prefer codex or
  claude as the edit worker; use antigravity mainly for read-only / second opinions.
- The worker runs in the launcher's `cwd`; scope context with `--add-dir`.

## Failure modes

- Hangs / no output in print mode → an approval prompt is waiting; it will end at
  `--print-timeout`. Re-scope to a read-only `--sandbox` task or use codex/claude for edits.
- Auth error → sign in via the Antigravity app, or set `ANTIGRAVITY_API_KEY` / `GEMINI_API_KEY`.
- Non-TTY stdout dropping the final line (older builds) → upgrade with `agy update`.
