"""Command-line entry point: ``python -m jarvis <command>`` / ``jarvis``."""

from __future__ import annotations

import argparse
import logging
import sys

from . import __version__

_FUTURE = {
    "web": "The web UI arrives in Phase 3.",
    "bot": "The messaging bot arrives in Phase 4.",
}


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="jarvis", description="Jarvis assistant")
    parser.add_argument(
        "--allow-power",
        action="store_true",
        help="Permit shutdown/restart/logout actions.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging.")

    sub = parser.add_subparsers(dest="command")
    sub.add_parser("cli", help="Typed chat (default).")
    sub.add_parser("voice", help="Hands-free voice assistant with wake word.")
    sub.add_parser("version", help="Print version.")
    for name in _FUTURE:
        sub.add_parser(name, help=_FUTURE[name])

    auto = sub.add_parser("autostart", help="Manage launch-at-login.")
    auto.add_argument("action", choices=["install", "uninstall", "status"])
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    command = args.command or "cli"

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if command == "version":
        print(f"jarvis {__version__}")
        return 0

    if command in _FUTURE:
        print(_FUTURE[command])
        return 0

    if command == "autostart":
        from .autostart import manager

        print(manager.run(args.action))
        return 0

    if command == "voice":
        from .interfaces.voice_app import run_voice

        run_voice(allow_power=args.allow_power)
        return 0

    from .interfaces.cli import run_cli

    run_cli(allow_power=args.allow_power)
    return 0


if __name__ == "__main__":
    sys.exit(main())
