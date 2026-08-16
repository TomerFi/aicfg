# AICfg AGENTS.md

## AI Policy

This project has an [AI policy](AI_POLICY.md). Always read it and ensure all suggestions, code, and contributions comply. If any behavior seems to conflict with the policy, warn the user and ask for guidance.

## Project Overview

aicfg is a tool for unified AI assistant configuration management. Its only command today is `link` — it creates relative symlinks between assistants so all assistants point to a single source file. Each symlink is relative to its target, not absolute.

## Architecture

```
aicfg/
    cli.py       — CLI entry point, argparse setup
    config.py    — Assistant definitions (names, paths per category)
    link.py      — Core link logic (file and directory symlinks)
    __init__.py  — Package init
tests/
    test_link.py — Unit tests for link logic
e2e/
    conftest.py        — Shared test fixtures and helpers
    test_happy_path.py — Happy path e2e tests
    test_errors.py     — Error handling e2e tests
    test_dry_run.py    — Dry-run mode e2e tests
npm/
    bin/aicfg.js       — npm CLI entry point (spawns Python with PYTHONPATH)
    package.json       — npm package config (syncs aicfg/ → npm/src/aicfg/ on publish)
    src/aicfg/         — synced from ../aicfg/ before each npm publish
```

## Commands

### `link`

```bash
aicfg link <source> --to <target> [,<target2>,...] [--dry-run] [--ci] [--verbose]
```

- `--dry-run` prints actions without creating symlinks
- `--ci` exits 1 if any symlinks are created or replaced (for CI/pre-commit hooks)
- `--verbose` prints informational messages (created dirs, skipped entries)
- Multiple targets: `--to claude-code,cursor` or `--to claude-code --to cursor`

**Published hook** — this project publishes a pre-commit hook (`id: link`) defined in `.pre-commit-hooks.yaml`. It can be consumed by adding `https://github.com/TomerFi/aicfg` as a remote repo. Under pre-commit, `PRE_COMMIT=1` is set automatically, triggering `--ci` behavior.

**Assistant definitions** — each assistant is configured in `aicfg/config.py` with paths for 4 categories:

- **instructions** — single file (linked via `_link_file`)
- **skills** — directory, each entry symlinked via `_link_dir`
- **rules** — directory, each entry symlinked via `_link_dir`
- **agents** — directory, each entry symlinked via `_link_dir`

Each category directory is **not** symlinked in its entirety. Instead, `link` creates the target directory if it doesn't exist and symlinks each top-level entry as-is — folders are folder symlinks, files are file symlinks. `link` does not walk into subdirectories, and it never overwrites user content in the target.

**Symlink behavior**:

- If a target symlink doesn't exist → create it
- If a target symlink already points to the correct source → skip it (print "Already linked:" with `--verbose`)
- If a target symlink points to a different source → replace it

To add a new assistant, add an `Assistant` entry in the `ASSISTANTS` dict in `aicfg/config.py` and test with `uv run pytest tests/ e2e/`.

**Directory structure** — `link` operates per-project root. A typical workspace:

```
my-project/
├── AGENTS.md                    ← source (instructions)
├── .agents/
│   ├── skills/
│   │   └── my-skill/
│   │       ├── SKILL.md
│   │       └── some-context.md
│   ├── rules/
│   │   └── a-rule.md
│   └── agents/
│       └── my-agent.md
├── .claude/
│   ├── CLAUDE.md → AGENTS.md (file symlink)
│   ├── skills/
│   │   └── my-skill → ../../.agents/skills/my-skill (folder symlink)
│   ├── rules/
│   │   └── a-rule.md → ../../.agents/rules/a-rule.md (file symlink)
│   └── agents/
│       └── my-agent.md → ../../.agents/agents/my-agent.md (file symlink)
```

**Error handling**:

- Unknown assistant name in `--to`: warns and skips
- Unknown assistant as `source`: exits with code 1
- Target path already contains a non-symlink file: exits with code 1
- Source doesn't exist: exits with code 1 (or skips for directories if file is missing)
- Source and target resolve to the same path (e.g. opencode ← agents for AGENTS.md): skips silently

## Working Environment

- This is primarily a **Python** project. Development is most likely in Python unless changes are needed for the wrapper.
- Always use **`uv`** — it handles package management, virtual envs, and running commands. Never use `pip` or `venv` directly.
- **`pyproject.toml`** is the single source of truth for dependencies, build config, and tool settings.
- Dev dependencies are managed in `[tool.uv]` / the `dependency-groups` table.
- This project uses [**prek**](https://github.com/j178/prek) (pre-commit replacement). Install the hook with `uv run prek install`.

### npm Wrapper

The npm package (`npm/`) is a thin Node.js wrapper that spawns the Python code. It uses `PYTHONPATH` to import from the synced `npm/src/aicfg/` directory. The wrapper checks that Python 3.11+ is available on PATH before running.

Before publishing to npm, the wrapper's `npm/src/aicfg/` directory is synced from the main `aicfg/` package via the `prepublishOnly` script in `npm/package.json`. Do **not** edit files in `npm/src/aicfg/` directly — they get overwritten. Make changes in `aicfg/` instead.

## Testing

```bash
# All tests
uv run pytest tests/ e2e/ -v

# Unit tests only
uv run pytest tests/

# E2E tests only
uv run pytest e2e/

# Lint
uv run ruff check .                  # check (read-only)
uv run ruff check . --fix            # check + fix
uv run ruff format --check .         # format check (read-only)
uv run ruff format .                 # format (apply changes)

# Types
uv run ty check .
```

For commit style, PR process, and other contributing guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).
