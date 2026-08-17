# AICfg

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)](https://pypi.org/project/aicfg/)
[![PyPI Version](https://img.shields.io/pypi/v/aicfg)](https://pypi.org/project/aicfg/)
[![npm Version](https://img.shields.io/npm/v/aicfg)](https://www.npmjs.com/package/aicfg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Unified AI assistant configuration management.

Built in Python, consumable from both Python and Node.js projects.

Currently, AICfg has only one command: `link`.

## Link Command

One source of truth per assistant. Pick any as your source.

### What It Does

AI coding assistants each have their own config files — instructions, skills, rules, agents. Managing them across multiple tools means editing the same content in multiple places. `aicfg link` solves this by creating symlinks so all assistants point to a single source.

![aicfg screencast](https://raw.githubusercontent.com/TomerFi/aicfg/main/screencast.gif)
> **Note:** you can pick any of the supported assistants as a source or a target.

### Supported Assistants

| Name           | Instructions                      | Skills               | Rules                   | Agents               |
|----------------|-----------------------------------|----------------------|-------------------------|----------------------|
| claude-code    | `CLAUDE.md`                       | `.claude/skills/`    | `.claude/rules/`        | `.claude/agents/`    |
| cursor         | `.cursorrules`                    | `.cursor/skills/`    | `.cursor/rules/`        | `.cursor/agents/`    |
| github-copilot | `.github/copilot-instructions.md` | `.github/skills/`    | `.github/instructions/` | `.github/agents/`    |
| agents         | `AGENTS.md`                       | `.agents/skills/`    | `.agents/rules/`        | `.agents/agents/`    |
| opencode       | `AGENTS.md`                       | `.opencode/skills/`  | `.opencode/rules/`      | `.opencode/agents/`  |

### Usage

```bash
# Dry run — see what would happen without creating symlinks
uvx aicfg link github-copilot --to claude-code,cursor --dry-run

# Link github-copilot → claude-code and cursor
uvx aicfg link github-copilot --to claude-code,cursor

# Link to all assistants at once
uvx aicfg link agents --to claude-code,cursor,github-copilot,opencode

# Verbose output
uvx aicfg link cursor --to claude-code --verbose
```

**Python projects** — skip `uvx`: add `aicfg` to your project and run `uv` instead of `uvx` to reuse your existing environment:

```bash
uv add --dev aicfg
uv run aicfg link cursor --to claude-code
```

**npm users** — install Python 3.11+ first, then replace `uvx` with `npx`, or install globally with `npm install -g aicfg`.

<details>
<summary><b>Install with pip</b></summary>

```
# Install with pip
pip install aicfg

# Run installed
aicfg link agents --to claude-code

```
</details>

### Pre-commit Hook

Add this to your `.pre-commit-config.yaml`:

<!-- editorconfig-checker-disable -->
```yaml
- repo: https://github.com/TomerFi/aicfg
  rev: "0.2.0"
  hooks:
    - id: link
      args: ["cursor", "--to", "claude-code", "opencode"]
```
<!-- editorconfig-checker-enable -->

Choose a source from the table above as the first arg and your targets via `--to`.

### GitHub Action

Add this to a GitHub Action to fail if symlinks drift:

<!-- editorconfig-checker-disable -->
```yaml
- name: Ensure assistant files are linked
  uses: tomerfi/aicfg/link@0.2.0
  with:
    source: agents
    target: claude-code,opencode
    verbose: true
```
<!-- editorconfig-checker-enable -->

### How It Works

`aicfg link` creates **relative symlinks** between assistants. For instructions, a file symlink is created at the target path pointing back to the source. For directory categories (skills, rules, agents), the target directory is created and each direct entry inside it is symlinked.

For directories, each entry (file or subdirectory) is symlinked as-is into the target directory. Files become file symlinks, directories become directory symlinks — the entries themselves are symlinked, not their individual contents.
The source file acts as the single source of truth — edit it once and all targets receive your changes immediately.

### Troubleshooting

**Symlinks cloned as regular files** — if your git checkout has symlinks as regular files instead of `→` links, your git config has `core.symlinks=false`. Fix it with:

```bash
git config core.symlinks true
git checkout -- <path>        # e.g. .claude/ .agents/
```

For future clones, run `git config --global core.symlinks true` beforehand. This is the default behavior for most modern git clients.
