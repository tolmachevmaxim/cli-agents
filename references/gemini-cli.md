# Gemini CLI reference (worker)

Gemini CLI is a separate Google CLI from Antigravity CLI (`agy`). Use
`gemini -p` for one-shot headless execution. The official headless interface
prints text by default and supports JSON or JSONL output when needed.

## Wrapper mapping

- Read-only worker: `gemini -p <prompt> --output-format text --sandbox --approval-mode plan`
- Bounded edit worker: `gemini -p <prompt> --output-format text --approval-mode auto_edit`
- Extra context directory: `--include-directories <absolute-path>`
- Model override: `--model <name>`

The wrapper never uses `--yolo`. Gemini's `auto_edit` mode can still ask for
shell approvals in a headless edit, so use Codex or Claude when a bounded edit
must run without interactive approval. Inspect `git diff` after every edit.

Gemini's `--approval-mode plan` is the read-only route. Keep the prompt scoped
to review, planning, or analysis and do not ask the worker to implement changes.
`--sandbox` adds a second boundary for tool execution.

Official docs: [headless mode](https://geminicli.com/docs/cli/headless/),
[CLI reference](https://geminicli.com/docs/cli/cli-reference/),
[sandboxing](https://geminicli.com/docs/cli/sandbox/), and
[plan mode](https://geminicli.com/docs/cli/plan-mode/).
