# Prompt Templates

Reusable prompts for delegated workers. Keep them specific and scoped. Fill the
`<...>` placeholders before sending. Pass via `--prompt-file` or stdin.

## Read-only code review

```text
You are an external reviewer. Do not edit files.
Repository: <abs path>
Scope: <files/directories>
Question: <specific review question>
Return:
- Findings ordered by severity
- File/line references where possible
- Missing tests or residual risk
```

## Bounded code edit

```text
You are an external CLI agent working under another agent's orchestration.
Repository: <abs path>
Task: <specific implementation task>
Allowed write scope: <exact files/directories>
Do not modify unrelated files. Do not deploy, push, delete, or run destructive commands.
Run these checks if possible: <commands>
Final output:
- Summary
- Changed files
- Verification results
- Risks / open questions
```

## Compare two agents (second opinion)

Send the SAME read-only prompt to two agents (e.g. `--agent codex --agent antigravity`),
then synthesize locally:

```text
Task: <question>
Scope: <paths>
Output: concise findings only. Do not edit files.
```

Then compare: overlapping findings · contradictions · findings with concrete
file/line evidence · items that are plausible but unsupported.

## Long-context summarization / extraction

```text
You are an analyst. Do not edit files.
Source: <compact extracted text or allowed file paths>
Goal: <what to extract / summarize>
Return:
- 3-5 key points with source evidence
- Note whether each is verbatim or inferred
```
