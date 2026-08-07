"""Link command — create symlinks between assistant config files."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from aicfg.config import ASSISTANTS, Category


def link(
    source: str,
    targets: list[str],
    dry_run: bool = False,
    verbose: bool = False,
    ci: bool = False,
) -> None:
    """Create symlinks from a source assistant's files to target assistants' files.

    Args:
        source: The assistant whose files will be linked to targets.
        targets: Target assistant names. Required — at least one.
        dry_run: If True, only print what would be done without creating symlinks.
        verbose: If True, print informational messages.
        ci: If True, exit 1 when symlinks are created or replaced.
    """
    source_assistant = ASSISTANTS.get(source)
    if source_assistant is None:
        sys.stderr.write(f"Error: unknown assistant '{source}'\n")
        sys.exit(1)

    created = 0

    for target in targets:
        target_assistant = ASSISTANTS.get(target)
        if target_assistant is None:
            sys.stderr.write(f"Warning: unknown assistant '{target}', skipping.\n")
            continue

        for category in Category:
            source_path = Path(source_assistant.paths[category])
            target_path = Path(target_assistant.paths[category])

            if category == Category.instructions:
                created += _link_file(source_path, target_path, dry_run, verbose)
            else:
                created += _link_dir(
                    source_path,
                    target_path,
                    dry_run,
                    verbose,
                )

    if (ci or os.environ.get("PRE_COMMIT") == "1") and created > 0:
        sys.exit(1)


def _relative_to(source_path: Path, target_path: Path) -> str:
    """Compute relative path from target to source."""
    return os.path.relpath(source_path, target_path.parent)


def _link_file(
    source_path: Path,
    target_path: Path,
    dry_run: bool,
    verbose: bool,
) -> int:
    """Link source file to target file.

    Returns:
        1 if a new or replaced symlink was created, 0 if skipped.
    """
    if not source_path.exists():
        sys.stderr.write(f"Error: {source_path} does not exist.\n")
        sys.exit(1)

    if source_path.resolve() == target_path.resolve():
        if verbose:
            print(f"Note: {source_path} and {target_path} are the same file, skipping.")
        return 0

    if target_path.is_symlink():
        resolved_target = target_path.resolve()
        if resolved_target == source_path.resolve():
            if verbose:
                print(f"Already linked: {source_path} -> {target_path}")
            return 0

    if target_path.exists() and not target_path.is_symlink():
        sys.stderr.write(
            f"Error: {target_path} exists and is not a symlink. "
            "Please remove or rename it before running link.\n",
        )
        sys.exit(1)

    if dry_run:
        print(f"[dry-run] Would link {source_path} -> {target_path}")
        return 0

    try:
        if target_path.exists():
            target_path.unlink()
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.symlink_to(_relative_to(source_path, target_path))
        print(f"Symlinked: {source_path} -> {target_path}")
        return 1
    except OSError as error:
        sys.stderr.write(f"Error linking {target_path}: {error}\n")
        sys.exit(1)


def _link_dir(
    source_path: Path,
    target_path: Path,
    dry_run: bool,
    verbose: bool,
) -> int:
    """Symlink each entry in source directory to target directory.

    Returns:
        The number of symlinks created or replaced.
    """
    if not source_path.exists():
        if verbose:
            print(f"Note: {source_path} does not exist, skipping.")
        return 0

    entries = sorted(source_path.iterdir())

    if not entries:
        if verbose:
            print(f"Skipping empty directory: {source_path}")
        return 0

    if not target_path.exists():
        target_path.mkdir(parents=True)
        if verbose:
            print(f"Created directory: {target_path}")

    created = 0

    for source_entry in entries:
        target_entry = target_path / source_entry.name

        if source_entry.resolve() == target_entry.resolve():
            if verbose:
                print(f"Note: {source_entry} and {target_entry} are the same file, skipping.")
            continue

        if target_entry.is_symlink():
            resolved_target = target_entry.resolve()
            if resolved_target == source_entry.resolve():
                if verbose:
                    print(f"Already linked: {source_entry} -> {target_entry}")
                continue

        if target_entry.exists() and not target_entry.is_symlink():
            sys.stderr.write(
                f"Error: {target_entry} exists and is not a symlink. "
                "Please remove or rename it before running link.\n",
            )
            sys.exit(1)

        if dry_run:
            print(f"[dry-run] Would link {source_entry} -> {target_entry}")
            continue

        try:
            if target_entry.exists():
                target_entry.unlink()
            is_directory = source_entry.is_dir()
            target_entry.symlink_to(
                _relative_to(source_entry, target_entry),
                target_is_directory=is_directory,
            )
            print(f"Symlinked: {source_entry} -> {target_entry}")
            created += 1
        except OSError as error:
            sys.stderr.write(f"Error linking {target_entry}: {error}\n")
            sys.exit(1)

    return created
