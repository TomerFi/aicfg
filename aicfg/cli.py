"""CLI entry point for aicfg."""

from __future__ import annotations

import argparse

from aicfg.config import ASSISTANT_NAMES


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aicfg",
        description="Unified AI assistant configuration management.",
    )
    subparsers = parser.add_subparsers(dest="action", help="available commands")

    link_parser = subparsers.add_parser(
        "link",
        help="create symlinks between assistant config files",
    )
    link_parser.add_argument(
        "source",
        choices=ASSISTANT_NAMES,
        help="source assistant to link from",
    )
    link_parser.add_argument(
        "--to",
        nargs="+",
        required=True,
        help="target assistants to link to",
    )
    link_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print what would be done without creating symlinks",
    )
    link_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print informational messages",
    )

    args = parser.parse_args()

    if args.action == "link":
        targets = [t for name in args.to for t in name.split(",")]
        from aicfg.link import link

        link(args.source, targets, dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()
