"""Entry point for the chat-bot face: ``jarvis bot``."""

from __future__ import annotations

from ...config.settings import Settings, load_settings
from ...core.assistant import Assistant
from .engine import BotEngine
from .telegram import TelegramBot


def run_bot(allow_power: bool = False) -> None:
    settings = load_settings()
    platform = settings.bot.platform.lower()

    if platform != "telegram":
        print(f"Unknown bot platform '{platform}'. Supported: telegram.")
        return

    token = Settings.secret("TELEGRAM_BOT_TOKEN")
    if not token:
        print(
            "No TELEGRAM_BOT_TOKEN found.\n"
            "  1. Talk to @BotFather on Telegram, /newbot, copy the token.\n"
            "  2. Put TELEGRAM_BOT_TOKEN=... in your .env (see .env.example).\n"
            "  3. Optionally set TELEGRAM_OWNER_ID=... to keep the bot private.\n"
            "Then run 'jarvis bot' again."
        )
        return

    assistant = Assistant.create(settings=settings, allow_power=allow_power)
    engine = BotEngine(assistant, owner_id=Settings.secret("TELEGRAM_OWNER_ID"))
    bot = TelegramBot(token, engine, poll_timeout=settings.bot.poll_timeout)

    print(
        f"Jarvis Telegram bot online [{settings.llm.provider}:{settings.llm.model}] "
        f"— {len(assistant.registry)} tools. Message it on Telegram. Ctrl+C to stop."
    )
    try:
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped.")
    finally:
        assistant.shutdown()
