# aicfg

[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)](https://pypi.org/project/aicfg/)
[![PyPI Version](https://img.shields.io/pypi/v/aicfg)](https://pypi.org/project/aicfg/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Unified AI assistant configuration management.

Currently, aicfg has only one command: `link`.

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

<details>
<summary><b>Install with pip</b></summary>

```
# Install with pip
pip install aicfg

# Run installed
aicfg link agents --to claude-code

```
</details>


### How It Works

`aicfg link` creates **relative symlinks** from each target's config files to the source's. For each category (instructions, skills, rules, agents), a symlink is created at the target path pointing back to the source.

For directories, each file inside the source directory is symlinked individually into the target directory, preserving the directory structure.
The source file acts as the single source of truth — edit it once and all targets receive your changes immediately.
