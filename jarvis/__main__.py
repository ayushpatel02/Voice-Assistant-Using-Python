"""Command-line entry point: ``python -m jarvis [command]`` / ``jarvis``."""

from __future__ import annotations

import argparse
import logging
import sys

from . import __version__

_FUTURE = {
    "voice": "Voice mode arrives in Phase 2 (wake word + STT/TTS).",
    "web": "The web UI arrives in Phase 3.",
    "bot": "The messaging bot arrives in Phase 4.",
    "autostart": "Autostart management arrives in Phase 2.",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="jarvis", description="Jarvis assistant")
    parser.add_argument(
        "command",
        nargs="?",
        default="cli",
        choices=["cli", "version", *_FUTURE],
        help="Which face to launch (default: cli).",
    )
    parser.add_argument(
        "--allow-power",
        action="store_true",
        help="Permit shutdown/restart/logout actions.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging.")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )

    if args.command == "version":
        print(f"jarvis {__version__}")
        return 0

    if args.command in _FUTURE:
        print(_FUTURE[args.command])
        return 0

    from .interfaces.cli import run_cli

    run_cli(allow_power=args.allow_power)
    return 0


if __name__ == "__main__":
    sys.exit(main())
