"""Typed CLI chat — the Phase 1 face and test harness for the core."""

from __future__ import annotations

from datetime import datetime

from ..core.assistant import Assistant

_QUIT = {"quit", "exit", "bye", "stop", "q"}


def _greeting() -> str:
    hour = datetime.now().hour
    part = "Morning" if 5 <= hour < 12 else "Afternoon" if 12 <= hour < 18 else "Evening"
    return f"Good {part}, Boss. Jarvis online. How may I help? (type 'quit' to exit)"


def run_cli(allow_power: bool = False) -> None:
    assistant = Assistant.create(allow_power=allow_power)
    session = assistant.new_session("cli")

    print(f"\nJarvis [{assistant.settings.llm.provider}:{assistant.settings.llm.model}] "
          f"— {len(assistant.registry)} tools ready.")
    print(_greeting())

    try:
        while True:
            try:
                text = input("\nYou > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not text:
                continue
            if text.lower() in _QUIT:
                print("Jarvis > Goodbye, Boss.")
                break
            response = assistant.handle(text, session)
            print(f"Jarvis > {response.text}")
    finally:
        assistant.shutdown()


if __name__ == "__main__":
    run_cli()
