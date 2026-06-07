from jarvis.config.settings import Settings
from jarvis.core.assistant import Assistant
from jarvis.interfaces.bot.engine import BotEngine
from jarvis.interfaces.bot.telegram import TelegramBot


def _engine(tmp_path, **kwargs) -> BotEngine:
    settings = Settings()
    settings.data_dir = tmp_path
    settings.llm.provider = "fake"
    return BotEngine(Assistant.create(settings=settings), **kwargs)


def test_help_command(tmp_path):
    out = _engine(tmp_path).handle_message("1", "/help")
    assert "Commands" in out and "/reset" in out


def test_start_is_help(tmp_path):
    eng = _engine(tmp_path)
    assert eng.handle_message("1", "/start") == eng.handle_message("1", "/help")


def test_whoami_reports_chat_id(tmp_path):
    assert "42" in _engine(tmp_path).handle_message("42", "/whoami")


def test_group_command_with_mention(tmp_path):
    # "/help@JarvisBot" should still be recognised as /help.
    out = _engine(tmp_path).handle_message("1", "/help@JarvisBot")
    assert "Commands" in out


def test_normal_message_goes_to_assistant(tmp_path):
    out = _engine(tmp_path).handle_message("1", "what time is it")
    assert out  # the fake echo brain returns a non-empty reply


def test_reset_clears_session(tmp_path):
    eng = _engine(tmp_path)
    eng.handle_message("7", "hello")
    assert "7" in eng._sessions
    eng.handle_message("7", "/reset")
    assert "7" not in eng._sessions


def test_sessions_are_per_chat(tmp_path):
    eng = _engine(tmp_path)
    eng.handle_message("a", "hi")
    eng.handle_message("b", "hi")
    assert eng.session_for("a") is not eng.session_for("b")


def test_owner_restriction(tmp_path):
    eng = _engine(tmp_path, owner_id="100")
    assert "private" in eng.handle_message("1", "hi", user_id=999).lower()
    assert "private" not in eng.handle_message("1", "/help", user_id=100).lower()


def test_empty_message_ignored(tmp_path):
    assert _engine(tmp_path).handle_message("1", "   ") == ""


# --- Telegram transport (no network) ---------------------------------------


class _RecordingBot(TelegramBot):
    """A TelegramBot whose network calls are captured instead of sent."""

    def __init__(self, engine):
        super().__init__("TESTTOKEN", engine)
        self.calls = []

    def _call(self, method, payload, timeout=None):
        self.calls.append((method, payload))
        return {"ok": True, "result": []}


def _update(text, chat_id=5, user_id=5):
    return {
        "update_id": 1,
        "message": {
            "chat": {"id": chat_id},
            "from": {"id": user_id, "first_name": "Boss"},
            "text": text,
        },
    }


def test_process_update_sends_reply(tmp_path):
    bot = _RecordingBot(_engine(tmp_path))
    reply = bot.process_update(_update("/help"))
    assert "Commands" in reply
    methods = [m for m, _ in bot.calls]
    assert "sendChatAction" in methods  # typing indicator
    sends = [p for m, p in bot.calls if m == "sendMessage"]
    assert sends and sends[0]["text"] == reply
    assert sends[0]["chat_id"] == "5"


def test_process_update_ignores_non_text(tmp_path):
    bot = _RecordingBot(_engine(tmp_path))
    assert bot.process_update({"update_id": 2, "message": {"chat": {"id": 1}}}) is None


def test_long_reply_is_chunked(tmp_path):
    bot = _RecordingBot(_engine(tmp_path))
    bot.send_message("9", "x" * 9000)
    sends = [p for m, p in bot.calls if m == "sendMessage"]
    assert len(sends) == 3  # 9000 chars -> 4096 + 4096 + 808
