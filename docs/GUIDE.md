# Navigating Jarvis — a developer's field guide

This is your map for driving and extending Jarvis. It explains how the pieces
fit, what happens when you talk to it, where everything lives, and how to add to
it. Read it top-to-bottom once; after that it's a reference.

---

## 1. The one idea: "one core, many faces"

Everything funnels through a single brain. The interfaces (CLI, voice, web,
soon a bot) are thin **faces** that only do input/output — they convert your
words to text, hand the text to the core, and render the reply. They contain no
assistant logic, so they're interchangeable and you never duplicate behavior.

```
        ┌── CLI ──┐   ┌── Voice ──┐   ┌── Web UI ──┐   ┌── Bot ──┐   (faces)
        └────┬────┘   └─────┬─────┘   └─────┬──────┘   └────┬────┘
             └──────────────┴──── text ─────┴───────────────┘
                                   │
                         Assistant.handle(text)            (the core)
                                   │
                     ┌─────────────┼──────────────┐
                     ▼             ▼               ▼
                   llm/         skills/        services/ + platform/
              (the brain)   (the abilities)   (storage, OS actions)
```

**Golden rule:** the brain decides *which* tool to run; Python functions do the
actual work. The LLM never touches your filesystem or runs a command directly —
it only emits a structured "call `set_volume` with `{percent: 30}`", and a
deterministic handler executes it. That keeps actions safe and testable.

---

## 2. What happens when you say something

Text path (CLI / web / bot):

1. A face captures your text and calls `Assistant.handle(text, session)`
   (`jarvis/core/assistant.py`).
2. The **Router** (`jarvis/core/router.py`) builds the message list: the persona
   system prompt + your conversation history + your new message, plus the JSON
   schemas of every available tool.
3. It calls the configured **LLM provider** (`jarvis/llm/`). The model replies
   with either final text *or* a request to call one or more tools.
4. If tools are requested, the Router looks each up in the **skill registry**
   (`jarvis/skills/registry.py`), runs the handler, and feeds the result back to
   the model. This loops (capped) until the model returns plain text.
5. The reply (plus the list of tools that ran) is returned as a `Response` and
   rendered by the face.

Voice path adds two ends around that core:

```
"Jarvis" (wake word) → record → speech-to-text → [the text path above] → text-to-speech → 🔊
```

See `jarvis/voice/pipeline.py`. Each stage (wake word, STT, TTS) is a swappable
provider.

---

## 3. Project map

```
jarvis/
├── core/         The brain hub.
│   ├── assistant.py   Builds everything from settings; exposes handle().
│   ├── router.py      The LLM tool-call loop (the heart).
│   ├── memory.py      Sliding-window conversation history.
│   ├── session.py     Per-conversation state.
│   └── response.py     The reply object (text + meta like tools_used).
│
├── llm/          The swappable brain.
│   ├── base.py        Neutral types: Message, ToolCall, ToolSpec, LLMResult.
│   ├── litellm_provider.py   Talks to Claude/OpenAI/Ollama/local via LiteLLM.
│   ├── fake_provider.py      Offline echo + scripted brains (tests, no key).
│   └── factory.py     Picks the provider from config.
│
├── skills/       The abilities. Drop a file here = new capability.
│   ├── base.py        Skill / Tool / Context contracts.
│   ├── registry.py    Auto-discovers skills, exposes them as LLM tools.
│   ├── knowledge/     time, wikipedia, web_search, weather*, news*
│   ├── productivity/  notes, reminders, timers
│   ├── system/        open app/website, volume, brightness, power
│   └── comms/         email*, music
│
├── platform/     OS abstraction (Windows / macOS / Linux) for system actions.
├── services/     Shared infra: sqlite store, scheduler, http helper.
│
├── voice/        Phase 2. Pluggable wake word / STT / TTS + the pipeline.
│   ├── audio_io.py    All microphone/speaker code lives here (only here).
│   ├── stt/  tts/  wakeword/   each: base + factory + adapters.
│   └── pipeline.py    wake → record → STT → core → TTS → play.
│
├── interfaces/   The faces.
│   ├── cli.py         Typed chat.
│   ├── voice_app.py   Hands-free voice app.
│   └── web/           FastAPI server + React HUD (static/).
│
├── autostart/    Launch-at-login: systemd / launchd / Task Scheduler.
└── config/       settings.py (typed) + defaults.toml (non-secret choices).

* = needs an API key/credentials; auto-disabled until configured.
```

---

## 4. Running it

```bash
pip install -e '.[full]'         # core + all v1 skills + LiteLLM
# optional faces:
pip install -e '.[web]'          # browser UI
pip install -e '.[voice]'        # mic/speaker (also: portaudio system lib)

jarvis            # typed CLI chat (default)
jarvis web        # browser HUD at http://127.0.0.1:8765
jarvis voice      # say "Jarvis", then speak
jarvis autostart install         # boot with the machine, always listening
jarvis --allow-power             # also permit shutdown/restart/logout
```

No API key yet? Explore the plumbing with the offline brain:
`JARVIS_LLM_PROVIDER=fake jarvis web` (replies are echoed; tools still list).

### The web HUD at a glance
- **Sidebar:** every loaded tool (the assistant's capabilities).
- **Chat:** your conversation; assistant replies show 🔧 **tool-trace chips**
  so you can *see* which skills the brain invoked.
- **🎙 mic button:** speak in the browser (Web Speech API); **🔊 toggle** speaks
  replies back. The page talks to the server over a WebSocket (`/ws`).

---

## 5. Configuration & secrets

- **Choices** (model, voice, which STT/TTS, enabled skills, web port) live in
  `jarvis/config/defaults.toml`. Override any with a `JARVIS_*` env var
  (e.g. `JARVIS_LLM_MODEL=gpt-4o`) or your own TOML via `JARVIS_CONFIG=...`.
- **Secrets** (API keys, email password) live ONLY in `.env` (gitignored).
  Copy `.env.example` and fill what you need. Read them in code via
  `Settings.secret("NAME")` — never hard-code, never log.

---

## 6. Adding a new skill (the one-file pattern)

Create `jarvis/skills/<area>/my_skill.py`:

```python
from ..base import Context, Skill, Tool, no_params

class CoinFlipSkill(Skill):
    name = "coinflip"                      # used for enable/disable config
    # required_secrets = ("SOME_KEY",)     # auto-disables if missing

    def tools(self) -> list[Tool]:
        return [Tool(
            name="flip_coin",
            description="Flip a coin and return heads or tails.",
            parameters=no_params(),        # or a JSON-Schema dict for args
            handler=self._flip,
        )]

    def _flip(self, args: dict, ctx: Context) -> str:
        import random
        return random.choice(["Heads", "Tails"])
```

That's it — no registration. The registry discovers it on next start and the
brain can call `flip_coin`. The `ctx` gives handlers access to
`ctx.services.store`, `ctx.platform`, `ctx.settings`, and `ctx.session`.

**Tips:** the `description` *is* the prompt the model reads — be precise. Keep
handlers deterministic and return a short string the model can relay.

---

## 7. Swapping providers

All set in `defaults.toml` (or env), no code changes:

| Concern | Setting | Options |
|---|---|---|
| Brain | `[llm] provider` / `model` | `litellm` + any model string (`claude-…`, `gpt-4o`, `ollama/llama3.1`); or `fake` |
| Speech-in | `[voice] stt` | `faster_whisper`, `vosk`, `openai` |
| Speech-out | `[voice] tts` | `edge_tts`, `piper`, `elevenlabs` |
| Wake word | `[voice] wakeword` | `openwakeword`, `porcupine` |

Want the cinematic voice? `tts = "elevenlabs"` + `ELEVENLABS_API_KEY` in `.env`.

---

## 8. Testing

```bash
python -m pytest        # runs with no network, mic, or API keys
```

The suite swaps in fakes: `ScriptedLLMProvider` (a model that returns canned
tool calls), `FakePlatform` (records OS calls instead of running them), and
`FakeSTT`/`FakeTTS`/`FakeWakeWord`. The voice pipeline is exercised file-based
(`respond_to_audio`), and the web API via FastAPI's `TestClient`. This is why
you can develop the whole thing on a machine with no microphone.

---

## 9. Where we are

- ✅ **Phase 1** — core brain, skill plugins, CLI, v1 skills.
- ✅ **Phase 2** — voice (wake word + STT/TTS) and launch-at-login autostart.
- ✅ **Phase 3** — web HUD (FastAPI + React, tool trace, browser voice).
- ⏭ **Phase 4** — Telegram/Discord bot face (same core, new adapter).

To extend Jarvis you'll almost always be adding a **skill** (section 6) or a new
**face** under `interfaces/` that calls `Assistant.handle`. The core rarely
needs to change.
