# Codex CLI Reference (worker)

Observed locally: `codex-cli 0.142.1`. Use `codex exec` for non-interactive runs.

## Non-interactive execution

```bash
codex exec [OPTIONS] [PROMPT]        # prompt as arg
codex exec [OPTIONS] -               # prompt read from stdin (preferred for long/multiline)
echo "task" | codex exec -s read-only -
```

If stdin is piped AND a prompt arg is given, stdin is appended as a `<stdin>` block.

## Key flags

```bash
-s, --sandbox read-only|workspace-write|danger-full-access   # safety scope
-m, --model <MODEL>            # override model
-C, --cd <DIR>                 # working root for the agent
    --add-dir <DIR>            # extra writable dir alongside the workspace
    --skip-git-repo-check      # allow running outside a git repo
    --json                     # stream events as JSONL
-o, --output-last-message <FILE>   # write ONLY the final message to FILE (clean capture)
    --output-schema <FILE>     # JSON Schema for a structured final response
    --ephemeral                # don't persist session files
    --color never              # disable ANSI in piped output
-c, --config key=value         # override config.toml (dotted path, TOML value)
```

## Safety guidance

- Default to `-s read-only` for analysis/review/planning.
- Use `-s workspace-write` for bounded edits; inspect `git diff` afterwards.
- NEVER use `-s danger-full-access` or `--dangerously-bypass-approvals-and-sandbox`
  from delegation — those defeat the sandbox.
- Capture the answer cleanly with `-o <file>` rather than scraping stdout.

## Failure modes

- Outside a git repo → add `--skip-git-repo-check`.
- Hang → `ps -axo pid,command | grep 'codex exec'` and kill only that PID.
- Empty `-o` file → check stderr (auth, model name, sandbox denial).
