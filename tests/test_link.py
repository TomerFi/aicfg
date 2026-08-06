"""Unit tests for aicfg.link."""

from __future__ import annotations

from pathlib import Path

import pytest

from aicfg.link import _link_dir, _link_file, _relative_to


class TestRelativePath:
    """Test _relative_to computes correct relative paths."""

    def test_sibling_dirs(self) -> None:
        result = _relative_to(Path("a/file.md"), Path("b/file.md"))
        assert result == "../a/file.md"

    def test_same_parent(self) -> None:
        result = _relative_to(Path("dir/file.md"), Path("dir/file.md"))
        assert result == "file.md"

    def test_nested_target(self) -> None:
        result = _relative_to(Path("source.md"), Path("target/subdir/file.md"))
        assert result == "../../source.md"


class TestLinkFile:
    """Test _link_file with tmp_path fixtures."""

    def test_creates_file_symlink(self, tmp_path: Path) -> None:
        source = tmp_path / "source.md"
        source.write_text("hello")
        target = tmp_path / "target.md"

        _link_file(source, target, False, False)

        assert target.is_symlink()
        assert target.read_text() == "hello"

    def test_error_on_missing_source(self, tmp_path: Path) -> None:
        target = tmp_path / "target.md"

        with pytest.raises(SystemExit) as exc_info:
            _link_file(tmp_path / "non-existent.md", target, False, False)
        assert exc_info.value.code == 1

    def test_error_on_existing_non_symlink(self, tmp_path: Path) -> None:
        target = tmp_path / "target.md"
        target.write_text("existing")

        with pytest.raises(SystemExit) as exc_info:
            _link_file(tmp_path / "source.md", target, False, False)
        assert exc_info.value.code == 1

    def test_replaces_existing_symlink(self, tmp_path: Path) -> None:
        source = tmp_path / "source.md"
        source.write_text("new content")
        target = tmp_path / "target.md"
        old_source = tmp_path / "old.md"
        old_source.write_text("old content")
        target.symlink_to(old_source)

        _link_file(source, target, False, False)

        assert target.is_symlink()
        assert target.read_text() == "new content"

    def test_dry_run_creates_nothing(self, tmp_path: Path) -> None:
        source = tmp_path / "source.md"
        source.write_text("hello")
        target = tmp_path / "target.md"

        _link_file(source, target, True, False)

        assert not target.exists()

    def test_skips_same_source_and_target(self, tmp_path: Path) -> None:
        same_file = tmp_path / "shared.md"
        same_file.write_text("content")

        _link_file(same_file, same_file, False, False)

        assert same_file.exists()
        assert not same_file.is_symlink()
        assert same_file.read_text() == "content"


class TestLinkDir:
    """Test _link_dir with tmp_path fixtures.

    Source directories contain a mix of file and folder entries,
    matching the real assistant config structure (skills as folders, rules/agents as files).
    """

    def test_links_all_entries(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        source.mkdir()
        # Flat file entry (rules/agents style)
        (source / "rule.md").write_text("# rule")
        # Folder entry (skills style)
        skill = source / "my-skill"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# skill")
        (skill / "context.md").write_text("# context")

        target = tmp_path / "target"

        _link_dir(source, target, False, False)

        assert target.is_dir()
        assert (target / "rule.md").is_symlink()
        assert (target / "rule.md").read_text() == "# rule"
        assert (target / "my-skill").is_symlink()
        assert (target / "my-skill" / "SKILL.md").read_text() == "# skill"
        assert (target / "my-skill" / "context.md").read_text() == "# context"

    def test_creates_target_directory(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.md").write_text("# file")
        target = tmp_path / "target"

        _link_dir(source, target, False, False)

        assert target.is_dir()

    def test_preserves_user_files(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        source.mkdir()
        (source / "from-source.md").write_text("# source")
        target = tmp_path / "target"
        target.mkdir()
        (target / "user.md").write_text("# user")

        _link_dir(source, target, False, False)

        assert (target / "user.md").exists()
        assert (target / "user.md").read_text() == "# user"
        assert (target / "from-source.md").is_symlink()

    def test_empty_source_creates_no_target(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        source.mkdir()
        target = tmp_path / "target"

        _link_dir(source, target, False, False)

        assert not target.exists()

    def test_missing_source_creates_no_target(self, tmp_path: Path) -> None:
        target = tmp_path / "target"

        _link_dir(tmp_path / "missing", target, dry_run=False, verbose=False)

        assert not target.exists()

    def test_replaces_existing_symlink(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        source.mkdir()
        (source / "new.md").write_text("# new")
        old_source = tmp_path / "old"
        old_source.mkdir()
        (old_source / "new.md").write_text("# old")
        target = tmp_path / "target"
        target.mkdir()
        target_symlink = target / "new.md"
        target_symlink.symlink_to(old_source / "new.md")

        _link_dir(source, target, False, False)

        assert (target / "new.md").read_text() == "# new"

    def test_skips_self_symlink_entry(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        source.mkdir()
        # Mixed: folder entry (skill) and flat file (rule)
        (source / "rule.md").write_text("# rule")
        skill = source / "skill-a"
        skill.mkdir()
        (skill / "SKILL.md").write_text("# skill A")

        target = source

        _link_dir(source, target, False, False)

        assert (target / "rule.md").exists()
        assert not (target / "rule.md").is_symlink()
        assert (target / "skill-a").exists()
        assert not (target / "skill-a").is_symlink()
        assert (target / "skill-a" / "SKILL.md").read_text() == "# skill A"
