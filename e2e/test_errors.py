"""E2E tests: error handling scenarios."""

from __future__ import annotations

import subprocess
from pathlib import Path

from e2e.conftest import (
    AicfgWorkspace,
    _create_agents_source,
    _run_aicfg,
)


class TestBadAssistantName:
    """Errors when an unknown assistant is specified."""

    def test_unknown_source(self, tmp_path: Path) -> None:
        result = subprocess.run(
            [
                "uv",
                "run",
                "--with",
                str(Path(__file__).parent.parent),
                "aicfg",
                "link",
                "badname",
                "--to",
                "claude-code",
            ],
            cwd=str(tmp_path),
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "invalid choice" in result.stderr or "unknown assistant" in result.stderr

    def test_unknown_target(self, tmp_path: Path) -> None:
        _create_agents_source(tmp_path)
        result = _run_aicfg(tmp_path, "nonexistent")
        # Unknown targets are warned, but link exits 0 since no targets to create
        assert result.returncode == 0
        assert "unknown assistant" in result.stderr

    def test_mixed_known_and_unknown_targets(self, tmp_path: Path) -> None:
        _create_agents_source(tmp_path)
        ws = AicfgWorkspace(tmp_path)
        ws.setup_target("claude-code")

        result = _run_aicfg(tmp_path, "claude-code", "nonexistent")
        assert result.returncode == 0
        assert "unknown assistant" in result.stderr
        # Known target should still be linked
        full_target = tmp_path / "CLAUDE.md"
        assert full_target.is_symlink()


class TestMissingSource:
    """Errors when source files don't exist."""

    def test_missing_instructions_file(self, tmp_path: Path) -> None:
        # Only create dir structures, no AGENTS.md
        _create_agents_source(tmp_path)
        (tmp_path / "AGENTS.md").unlink()

        result = _run_aicfg(tmp_path, "claude-code")
        assert result.returncode == 1
        assert "does not exist" in result.stderr


class TestFileConflict:
    """Errors when target has a non-symlink file."""

    def test_existing_regular_file_at_target(self, tmp_path: Path) -> None:
        _create_agents_source(tmp_path)

        # Create a regular file where claude's instructions should go
        (tmp_path / "CLAUDE.md").write_text("existing claude instructions")

        result = _run_aicfg(tmp_path, "claude-code")
        assert result.returncode == 1
        assert "exists and is not a symlink" in result.stderr

    def test_existing_regular_file_in_dir_target(self, tmp_path: Path) -> None:
        _create_agents_source(tmp_path)

        # Create a regular file inside claude's rules directory (flat file entry)
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "a-set-of-custom-rules.md").write_text("existing rule")

        result = _run_aicfg(tmp_path, "claude-code")
        assert result.returncode == 1
        assert "exists and is not a symlink" in result.stderr
