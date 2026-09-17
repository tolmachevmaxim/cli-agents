# Aider in this skill

## Install and verify

```bash
uv tool install --force --python python3.12 --with pip aider-chat@latest
aider --version
```

Credentials remain user-managed. The wrapper never asks for, prints, or passes
API keys in prompts.

## Default routing

With no explicit `--model`, the wrapper uses direct Z.ai GLM-5.2 High:

- model: `openai/glm-5.2`;
- Coding Plan endpoint: `https://api.z.ai/api/coding/paas/v4`;
- reasoning: `high`;
- bundled model settings and 1M-context metadata.

The target repository must provide its own uncommitted `.env` with
`OPENAI_API_KEY=<Z.ai API Key>`. Passing `--model` opts out of this default and
lets Aider use the selected provider's configuration.

## Wrapper behavior

`scripts/delegate.py --agent aider` launches Aider in single-message mode.

- Both modes use `--no-auto-commits --no-dirty-commits`.
- Read-only work uses `--dry-run`, `--no-git`, `--no-gitignore`, and redirects
  Aider's input/chat history to `/dev/null`; this avoids skill-file changes,
  Git initialization, `.gitignore` edits, and history artifacts in the target.
- Edit work requires one or more explicit `--aider-file` values and uses
  `--yes-always`; inspect `git diff` yourself afterwards.
- Use `--aider-read /absolute/path/to/SKILL.md` to attach one relevant skill as
  read-only context. Never load a whole personal skill directory.

Examples:

```bash
scripts/delegate.py --agent aider --mode read-only --cwd /repo \
  --aider-read /path/to/relevant/SKILL.md \
  --prompt "Review the browser automation against this skill."

scripts/delegate.py --agent aider --mode edit --cwd /repo \
  --aider-file src/app.py --prompt "Implement the approved, scoped change."
```

## Skills and conventions

Aider has no native Agent-Skills discovery directory. Attach only a selected
`SKILL.md` through `--aider-read`. Keep personal skills in their canonical
roots.

Official docs: [installation](https://aider.chat/docs/install.html),
[scripting](https://aider.chat/docs/scripting.html),
[conventions](https://aider.chat/docs/usage/conventions.html), and
[configuration](https://aider.chat/docs/config/aider_conf.html).
