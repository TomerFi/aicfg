"""E2E tests: happy path — link agents to each target."""

from __future__ import annotations

from pathlib import Path

import pytest

from aicfg.config import ASSISTANT_NAMES, ASSISTANTS, Category
from e2e.conftest import (
    AicfgWorkspace,
    _verify_linked_dir,
    _verify_linked_file,
)

# agents is excluded — it would be a self-link with nothing created


class TestHappyPath:
    """Link agents → each target assistant, verify symlinks via subprocess."""

    @pytest.mark.parametrize("assistant", [n for n in ASSISTANT_NAMES if n != "agents"])
    def test_link_to_all_assistants(self, tmp_path: Path, assistant: str) -> None:
        """Agents → assistant: all categories link correctly."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target(assistant)

        result = ws.run(assistant)
        assert result.returncode == 0, f"stderr: {result.stderr}"

        agents = ASSISTANTS["agents"]
        target = ASSISTANTS[assistant]

        # File link (instructions) — skip self-symlink case (opencode)
        source_instr = agents.paths[Category.instructions]
        target_instr = target.paths[Category.instructions]
        if source_instr != target_instr:
            _verify_linked_file(tmp_path, source_instr, target_instr)

        # Dir link (skills, rules, agents) — each entry inside the target dir is a symlink
        for category in (Category.skills, Category.rules, Category.agents):
            _verify_linked_dir(tmp_path, agents.paths[category], target.paths[category])


class TestMultiTarget:
    """Link agents → multiple targets at once via subprocess."""

    def test_link_to_claude_and_cursor(self, tmp_path: Path) -> None:
        """agents → claude-code,cursor: both targets get symlinks."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target("claude-code")
        ws.setup_target("cursor")

        result = ws.run("claude-code", "cursor")
        assert result.returncode == 0, f"stderr: {result.stderr}"

        for assistant in ("claude-code", "cursor"):
            target = ASSISTANTS[assistant]

            # File link (instructions)
            target_instr = target.paths[Category.instructions]
            full_instr = tmp_path / target_instr
            assert full_instr.is_symlink(), f"{assistant}/{target_instr} should be symlink"
            assert full_instr.read_text() == "Agents instructions"

            # Dir link — each dir should exist with symlinks inside
            for category in (Category.skills, Category.rules, Category.agents):
                target_path = target.paths[category]
                full_dir = tmp_path / target_path
                assert full_dir.is_dir(), f"{assistant}/{target_path} should be a dir"
                # Each entry inside should be a symlink
                source = tmp_path / ASSISTANTS["agents"].paths[category]
                for entry in source.iterdir():
                    target_entry = full_dir / entry.name
                    assert target_entry.is_symlink(), (
                        f"{assistant}/{target_path}/{entry.name} should be symlink"
                    )

    def test_link_to_all_assistants(self, tmp_path: Path) -> None:
        """agents → all assistants at once."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        for assistant in ASSISTANT_NAMES:
            ws.setup_target(assistant)

        result = ws.run(*[n for n in ASSISTANT_NAMES if n != "agents"])
        assert result.returncode == 0, f"stderr: {result.stderr}"

        for assistant in [n for n in ASSISTANT_NAMES if n != "agents"]:
            target = ASSISTANTS[assistant]

            # File link — skip opencode (self-symlink)
            target_instr = target.paths[Category.instructions]
            if target_instr == "AGENTS.md":
                assert (tmp_path / target_instr).is_file()
                assert (tmp_path / target_instr).read_text() == "Agents instructions"
            else:
                full_instr = tmp_path / target_instr
                assert full_instr.is_symlink(), f"{assistant}/{target_instr} should be symlink"

            # Dir link
            for category in (Category.skills, Category.rules, Category.agents):
                target_path = target.paths[category]
                full_dir = tmp_path / target_path
                assert full_dir.is_dir(), f"{assistant}/{target_path} should be a dir"
