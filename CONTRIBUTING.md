# Contributing to aicfg

Thank you for contributing. This guide covers the essentials.

## AI Policy

This project has a clear AI policy — read [AI_POLICY.md](AI_POLICY.md) and follow it. You're responsible for everything you submit.

## Setup

```bash
git clone <repo-url>
cd aicfg
uv sync
```

See [AGENTS.md](AGENTS.md) for testing and lint commands.

## How to Add Assistants

1. Edit `aicfg/config.py` — add a new `Assistant` entry with paths for each `Category` (`instructions`, `skills`, `rules`, `agents`)
2. The name must be unique and lowercase
3. Update the README.md table
4. Add tests — at minimum, verify in an e2e test
5. Run the full test suite: `uv run pytest tests/ e2e/ -v`

## Local Checks

This project uses [prek](https://github.com/j178/prek) (parallel pre-commit) to run lint and format checks automatically before each commit.

```bash
uv run prek install
```

This installs the Git hook. After that, checks run automatically on every commit. To run them manually against all files:

```bash
uv run prek run --all-files
```

## Commit Style

- Conventional commits: `feat:`, `fix:`, `docs:`, `chore:`, `refactor:`, `test:`
- GPG sign all commits (`-s` for signoff, plus `--gpg-sign`)
- One logical change per commit

## PR Process

1. Branch from `main` with a conventional name: `feat/add-assistant`, `fix/self-link-bug`
2. Commit with a descriptive message
3. Run all checks before submitting: `uv run ruff check . --fix && uv run ruff format . && uv run ty check . && uv run pytest tests/ e2e/ -v`
4. Open PR with a clear description of what changed and why
5. Address feedback

