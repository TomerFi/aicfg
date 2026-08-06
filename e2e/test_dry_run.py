"""E2E tests: dry-run mode — no symlinks should be created."""

from __future__ import annotations

from pathlib import Path

from aicfg.config import ASSISTANTS, Category
from e2e.conftest import AicfgWorkspace


class TestDryRun:
    """Dry-run prints actions without creating symlinks."""

    def test_dry_run_creates_nothing(self, tmp_path: Path) -> None:
        """agents → claude-code --dry-run: no symlinks, but [dry-run] message in output."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target("claude-code")

        result = ws.run("claude-code", "--dry-run")
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "[dry-run]" in result.stdout

        target = ASSISTANTS["claude-code"]

        # No symlinks created
        for category in Category:
            target_path = target.paths[category]
            full_target = tmp_path / target_path
            assert not full_target.is_symlink(), f"{target_path} should not be a symlink"

        # Source files untouched
        assert (tmp_path / "AGENTS.md").is_file()
        assert (tmp_path / "AGENTS.md").read_text() == "Agents instructions"

    def test_dry_run_multi_target(self, tmp_path: Path) -> None:
        """agents → claude,cursor --dry-run: no symlinks for either."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target("claude-code")
        ws.setup_target("cursor")

        result = ws.run("claude-code", "cursor", "--dry-run")
        assert result.returncode == 0

        for assistant in ("claude-code", "cursor"):
            target = ASSISTANTS[assistant]
            for category in Category:
                target_path = target.paths[category]
                full_target = tmp_path / target_path
                assert not full_target.is_symlink()
