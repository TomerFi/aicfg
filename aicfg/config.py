"""Assistant definitions.

Each assistant maps to file/dir paths for its 4 categories.
The link direction is determined by command arguments, not baked in.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Category(StrEnum):
    instructions = "instructions"
    skills = "skills"
    rules = "rules"
    agents = "agents"


@dataclass(frozen=True)
class Assistant:
    paths: dict[Category, str]


ASSISTANTS: dict[str, Assistant] = {
    "claude-code": Assistant(
        paths={
            Category.instructions: "CLAUDE.md",
            Category.skills: ".claude/skills",
            Category.rules: ".claude/rules",
            Category.agents: ".claude/agents",
        },
    ),
    "cursor": Assistant(
        paths={
            Category.instructions: ".cursorrules",
            Category.skills: ".cursor/skills",
            Category.rules: ".cursor/rules",
            Category.agents: ".cursor/agents",
        },
    ),
    "github-copilot": Assistant(
        paths={
            Category.instructions: ".github/copilot-instructions.md",
            Category.skills: ".github/skills",
            Category.rules: ".github/instructions",
            Category.agents: ".github/agents",
        },
    ),
    "agents": Assistant(
        paths={
            Category.instructions: "AGENTS.md",
            Category.skills: ".agents/skills",
            Category.rules: ".agents/rules",
            Category.agents: ".agents/agents",
        },
    ),
    "opencode": Assistant(
        paths={
            Category.instructions: "AGENTS.md",
            Category.skills: ".opencode/skills",
            Category.rules: ".opencode/rules",
            Category.agents: ".opencode/agents",
        },
    ),
}

ASSISTANT_NAMES = sorted(ASSISTANTS.keys())
