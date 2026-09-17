# Aider in this skill

## Install and verify

Use the isolated official installation:

```bash
uv tool install --force --python python3.12 --with pip aider-chat@latest
aider --version
```

Do not configure API keys for a user. Aider uses the user's already configured
provider credentials when they choose a model.

## Default: direct Z.ai GLM-5.2 High

The wrapper defaults Aider to direct Z.ai, not OpenRouter:

- model: `openai/glm-5.2`;
- Coding Plan endpoint: `https://api.z.ai/api/coding/paas/v4`;
- reasoning: `high` (`GLM-5.2 High` is not a model ID);
- model settings and 1M-context metadata bundled beside this reference.

The target repository must provide its own uncommitted `.env`:

```dotenv
OPENAI_API_KEY=<Z.ai API Key>
```

The wrapper supplies the endpoint and model flags. Never ask for, print, pass
in prompts, or commit the key. Passing `--model` explicitly opts out of the
Z.ai default so a user can intentionally choose another provider.

## Wrapper behavior

`scripts/delegate.py --agent aider` launches Aider in single-message mode.

- Read-only work: `--dry-run --no-git --no-gitignore --yes-always` prevents
  skill-file writes and avoids Git/history artifacts in the target repository.
- Edit work: require one or more `--aider-file` values and disable Aider's
  automatic Git commits with `--no-auto-commits --no-dirty-commits`.
- Use `--aider-read /absolute/path/to/SKILL.md` for one relevant personal skill
  as read-only context. Never load the global skill set wholesale.

Examples:

```bash
scripts/delegate.py --agent aider --mode read-only --cwd /repo \
  --aider-read /abs/path/to/relevant/SKILL.md \
  --prompt "Review the browser automation against this skill."

scripts/delegate.py --agent aider --mode edit --cwd /repo \
  --aider-file src/app.py --prompt "Implement the approved, scoped change."
```

## Skills and conventions

Aider has no Agent-Skills discovery directory. Its supported instruction
mechanisms are read-only files (`--read` or `read:` in `.aider.conf.yml`) and
small conventions files. Keep personal skills in their existing canonical
roots; attach only a selected `SKILL.md` to an Aider task with `--aider-read`.

Official docs: [installation](https://aider.chat/docs/install.html),
[scripting](https://aider.chat/docs/scripting.html),
[conventions](https://aider.chat/docs/usage/conventions.html), and
[configuration](https://aider.chat/docs/config/aider_conf.html). Z.ai:
[Coding Plan integration](https://docs.z.ai/devpack/tool/others) and
[GLM-5.2 parameters](https://docs.z.ai/guides/overview/concept-param).
