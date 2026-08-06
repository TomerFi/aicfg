"""Shared fixtures and helpers for aicfg e2e tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from aicfg.config import ASSISTANTS, Category


def _skill_content() -> str:
    """Return a valid SKILL.md with YAML frontmatter and body."""
    return (
        "---\n"
        "name: my-dummy-skill\n"
        "description: A dummy skill for e2e verification.\n"
        "---\n"
        "# Dummy Skill\n\n"
        "This is a dummy skill for e2e tests.\n"
    )


def _skill_context_content() -> str:
    """Return dummy context content for a skill folder."""
    return "# Repository Info\n\nTech stack: Python 3.11, uv, pytest.\n"


def _create_agents_source(root: Path) -> None:
    """Create the agents assistant source files under `root`.

    Skills use a folder structure (matching the skill spec):
        <skills-dir>/
            <skill-name>/
                SKILL.md
                <context files>

    Rules and agents are flat .md files.

    _link_dir symlinks each top-level entry as-is (folder or file).
    """
    agents = ASSISTANTS["agents"]

    (root / agents.paths[Category.instructions]).write_text("Agents instructions")

    # Skills: folder-based structure (SKILL.md inside skill folder)
    skills_dir = root / agents.paths[Category.skills]
    skills_dir.mkdir(parents=True)
    skill_folder = skills_dir / "my-dummy-skill"
    skill_folder.mkdir(parents=True)
    (skill_folder / "SKILL.md").write_text(_skill_content())
    (skill_folder / "some-context.md").write_text(_skill_context_content())

    # Rules: flat files
    rules_dir = root / agents.paths[Category.rules]
    rules_dir.mkdir(parents=True)
    (rules_dir / "a-set-of-custom-rules.md").write_text("Rule content")

    # Agents: flat files
    agents_dir = root / agents.paths[Category.agents]
    agents_dir.mkdir(parents=True)
    (agents_dir / "my-custom-agent.md").write_text("Agent definition")


def _create_target_structure(root: Path, assistant: str) -> None:
    """Create the target assistant's directory structure (empty, no files)."""
    for rel_path in ASSISTANTS[assistant].paths.values():
        full = root / rel_path
        # Create parent dirs if it's not a directory itself
        if full.is_dir():
            full.mkdir(parents=True, exist_ok=True)
        else:
            full.parent.mkdir(parents=True, exist_ok=True)


def _run_aicfg(root: Path, *targets: str) -> subprocess.CompletedProcess[str]:
    """Run aicfg link agents --to <targets> in an isolated tmp env."""
    env = os.environ.copy()
    project_path = Path(__file__).parent.parent
    return subprocess.run(
        ["uv", "run", "--with", str(project_path), "aicfg", "link", "agents", "--to", *targets],
        cwd=str(root),
        capture_output=True,
        text=True,
        env=env,
    )


def _verify_linked_file(root: Path, source_rel: str, target_rel: str) -> None:
    """Verify a linked file is a valid symlink with correct content."""
    target = root / target_rel
    assert target.is_symlink(), f"{target_rel} is not a symlink"
    assert target.is_file(), f"{target_rel} is not a file"
    assert target.read_text() == (root / source_rel).read_text(), f"{target_rel} content mismatch"


def _verify_linked_dir(root: Path, source_rel: str, target_rel: str) -> None:
    """Verify a linked directory — each top-level entry is symlinked as-is.

    For file entries, verify content. For folder entries (skills), verify the
    symlink exists — the source is a real folder, so we can't call read_text on it.
    """
    target = root / target_rel
    assert target.is_dir(), f"{target_rel} is not a directory"
    source = root / source_rel

    for entry in sorted(source.iterdir()):
        target_entry = target / entry.name
        assert target_entry.is_symlink(), f"{target_rel}/{entry.name} is not a symlink"
        if entry.is_file():
            assert target_entry.read_text() == entry.read_text(), (
                f"{target_rel}/{entry.name} content mismatch"
            )


class AicfgWorkspace:
    """Helper to set up and run aicfg in an isolated directory."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def setup_agents_source(self) -> None:
        """Create agents assistant source files."""
        _create_agents_source(self.root)

    def setup_target(self, assistant: str) -> None:
        """Create target assistant directory structure."""
        _create_target_structure(self.root, assistant)

    def run(self, *targets: str) -> subprocess.CompletedProcess[str]:
        """Run aicfg link agents --to <targets>."""
        return _run_aicfg(self.root, *targets)
