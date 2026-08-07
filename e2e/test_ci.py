"""E2E tests: --ci flag exit code behavior."""

from __future__ import annotations

from pathlib import Path

from aicfg.config import ASSISTANTS, Category
from e2e.conftest import AicfgWorkspace


class TestCiFlag:
    """--ci exits 1 when symlinks are created, 0 when already linked."""

    def test_ci_exits_1_when_new_symlinks_created(self, tmp_path: Path) -> None:
        """agents → claude-code --ci: exits 1 on first link."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target("claude-code")

        result = ws.run("claude-code", "--ci")
        assert result.returncode == 1
        assert "Symlinked:" in result.stdout

        # Verify symlinks were actually created
        target = ASSISTANTS["claude-code"]
        full_instr = tmp_path / target.paths[Category.instructions]
        assert full_instr.is_symlink()

    def test_ci_exits_0_when_all_already_linked(self, tmp_path: Path) -> None:
        """agents → claude-code --ci: exits 0 on second run."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target("claude-code")

        # First run creates symlinks
        result1 = ws.run("claude-code", "--ci")
        assert result1.returncode == 1

        # Second run sees everything already linked
        result2 = ws.run("claude-code", "--ci")
        assert result2.returncode == 0

    def test_ci_exits_1_when_wrong_symlink_replaced(self, tmp_path: Path) -> None:
        """agents → claude-code --ci: exits 1 when wrong symlink is replaced."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target("claude-code")

        # First run creates correct symlinks
        result1 = ws.run("claude-code", "--ci")
        assert result1.returncode == 1

        # Overwrite the target with a wrong symlink
        existing_file = tmp_path / "existing.md"
        existing_file.write_text("existing")
        target_instr = tmp_path / ASSISTANTS["claude-code"].paths[Category.instructions]
        target_instr.unlink()
        target_instr.symlink_to(existing_file)

        # Second run replaces the wrong symlink
        result2 = ws.run("claude-code", "--ci")
        assert result2.returncode == 1
        assert (tmp_path / "AGENTS.md").read_text() == (
            tmp_path / ASSISTANTS["claude-code"].paths[Category.instructions]
        ).read_text()

    def test_ci_exits_0_on_multi_target_all_linked(self, tmp_path: Path) -> None:
        """agents → claude-code,cursor --ci: exits 0 when both already linked."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target("claude-code")
        ws.setup_target("cursor")

        # First run creates all symlinks
        result1 = ws.run("claude-code", "cursor", "--ci")
        assert result1.returncode == 1

        # Second run: everything already linked
        result2 = ws.run("claude-code", "cursor", "--ci")
        assert result2.returncode == 0

    def test_ci_exits_1_on_multi_target_one_wrong(self, tmp_path: Path) -> None:
        """agents → claude-code,cursor --ci: exits 1 when one target has wrong symlink."""
        ws = AicfgWorkspace(tmp_path)
        ws.setup_agents_source()
        ws.setup_target("claude-code")
        ws.setup_target("cursor")

        # First run creates all symlinks
        result1 = ws.run("claude-code", "cursor", "--ci")
        assert result1.returncode == 1

        # Replace one cursor symlink with a wrong one
        existing_file = tmp_path / "existing.md"
        existing_file.write_text("existing")
        cursor_instr = tmp_path / ASSISTANTS["cursor"].paths[Category.instructions]
        cursor_instr.unlink()
        cursor_instr.symlink_to(existing_file)

        # Second run: claude-code is fine, cursor needs fixing → exit 1
        result2 = ws.run("claude-code", "cursor", "--ci")
        assert result2.returncode == 1

        # Verify cursor's symlink is now correct
        assert (tmp_path / "AGENTS.md").read_text() == cursor_instr.read_text()
