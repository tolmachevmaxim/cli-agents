# Claude Code CLI Reference (worker)

Use `claude --print` / `-p` for non-interactive runs. Pipe long prompts via stdin.

## Non-interactive execution

```bash
cat prompt.md | claude --print --model sonnet --permission-mode plan
claude --print "Summarize this repository structure."
```

`--max-budget-usd <N>` works only with `--print` (caps spend per call).

## Key flags

```bash
--model sonnet|opus|<full-id>          # prefer sonnet; opus only for high-value reasoning
--effort low|medium|high|xhigh|max     # low for extraction, high+ for deep review
--permission-mode plan|acceptEdits|default|dontAsk|auto|bypassPermissions
--allowedTools 'Read,Edit,Bash(git diff*)'
--disallowedTools 'Bash(rm *),Bash(git push*)'
--add-dir /abs/path                    # extra allowed directory
--output-format text|json|stream-json  # text unless the caller parses it
--max-budget-usd 1.00
--append-system-prompt "..."
```

## Safety guidance

- `--permission-mode plan` → read-only analysis/planning.
- `--permission-mode acceptEdits` → bounded edits; keep `--allowedTools` tight.
- Use `--dangerously-skip-permissions` only in disposable/trusted sandboxes, never
  for tasks with external side effects (push/deploy/email/delete).
- Keep analysis read-only with `--allowedTools 'Read,Bash(git diff*)'`.

## Failure modes

- "budget exceeded" → raise/remove `--max-budget-usd`.
- Hang → `ps -axo pid,command | grep 'claude --print'` and kill only that PID.
- No output on a big file → pre-extract a compact text slice and pass that.
