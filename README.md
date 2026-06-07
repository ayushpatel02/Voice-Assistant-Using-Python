# Jarvis — Cross-Platform LLM Voice + Chat Assistant

Jarvis is a modular, provider-agnostic AI assistant in the spirit of Tony Stark's
AI. An LLM understands what you ask in natural language and calls real **skills**
(tools) to get things done. The brain, the voice stack, and the OS layer are all
swappable via config, and every interface (CLI, voice, web, bot) plugs into one
shared core.

> **Status:** Phases 1–3 complete — the core brain, skill-plugin system, a typed
> CLI, a hands-free **voice mode** (wake word "Jarvis" + STT/TTS) with
> **launch-at-login autostart**, and a **browser HUD** (React + FastAPI, tool
> trace, in-browser voice) are working. A messaging bot is next.
>
> 📖 New here? Read **[docs/GUIDE.md](docs/GUIDE.md)** — a guided tour of how it
> all fits together and how to extend it.

## Architecture: one core, many faces

```
interfaces (cli · voice · web · bot)   ← thin adapters, just I/O
            │  call Assistant.handle(text) → Response
            ▼
core  (assistant · router · memory · session)
            │  router runs the LLM tool-call loop
   ┌────────┼─────────────┐
   ▼        ▼             ▼
 llm/     skills/      services/        platform/
(LiteLLM, (auto-       (sqlite store,   (Windows /
 swappable)discovered  scheduler,       macOS /
           plugins)    http)            Linux)
```

- **LLM-as-router, Python-as-executor:** the model only decides *which* tool to
  call with *what* arguments; deterministic Python does the work.
- **Provider-agnostic brain:** via [LiteLLM](https://docs.litellm.ai), the same
  code talks to Claude, OpenAI, Ollama, or a local model — chosen in config.
- **Skills are one-file drop-ins:** subclass `Skill` anywhere under
  `jarvis/skills/` and it's auto-discovered and exposed to the model.
- **Secrets only from the environment** (`.env`), never in code or config.

## Install

```bash
python -m pip install -e '.[full]'     # core + all v1 skills + LiteLLM
# or a minimal dev install:
python -m pip install -e '.[dev]'
```

Optional extras: `llm`, `knowledge`, `productivity`, `system`, `comms`, `voice`,
`web`, `bots`.

## Configure

1. Copy `.env.example` to `.env` and fill in the keys you want (LLM provider key,
   and any skill keys like `OPENWEATHER_API_KEY`). For email, use a Gmail
   **App Password**, not your account password.
2. Non-secret choices (which model, voice, enabled skills) live in
   `jarvis/config/defaults.toml`. Override any value with a `JARVIS_*` env var,
   e.g. `JARVIS_LLM_MODEL=gpt-4o`, or point `JARVIS_CONFIG` at your own TOML file.

No API key handy? Run with the offline echo brain to try the plumbing:

```bash
JARVIS_LLM_PROVIDER=fake python -m jarvis
```

## Run

```bash
jarvis                 # typed CLI chat (default)
jarvis web             # browser HUD at http://127.0.0.1:8765
jarvis voice           # hands-free: say "Jarvis", then speak your command
jarvis --allow-power   # also permit shutdown/restart/logout actions
jarvis version
```

### Web UI

```bash
pip install -e '.[web]'
jarvis web             # open the printed URL in your browser
```

A dark **Iron-Man-style HUD**: a capabilities sidebar, a chat that shows 🔧
**tool-trace chips** (so you can see which skills the brain invoked), a mic
button for **in-browser voice** (Web Speech API), and a toggle to have replies
spoken back. Built with React + JSX served straight from FastAPI — no build step.

### Voice mode

Install the voice extras (needs PortAudio on the system), then run `jarvis voice`:

```bash
pip install -e '.[voice]'      # sounddevice, faster-whisper, edge-tts, openWakeWord
# Linux may need: sudo apt-get install portaudio19-dev
jarvis voice
```

Say **"Jarvis"** to wake it, then speak. STT (faster-whisper), TTS (edge-tts),
and the wake-word backend (openWakeWord; Porcupine optional) are all chosen in
`jarvis/config/defaults.toml` and swappable — e.g. set `tts = "elevenlabs"` for
a cinematic voice (with `ELEVENLABS_API_KEY`).

### Auto-start at login

Make Jarvis boot with your machine and always listen for "Jarvis":

```bash
jarvis autostart install     # systemd user service / launchd agent / Task Scheduler
jarvis autostart status
jarvis autostart uninstall
```

## Skills shipped in v1

| Area | Tools |
|---|---|
| Knowledge & web | `get_time`, `get_date`, `wikipedia_summary`, `web_search`, `get_weather`*, `get_news`* |
| Productivity | `add_note`, `list_notes`, `clear_notes`, `add_reminder`, `list_reminders`, `set_timer` |
| System control | `open_app`, `open_website`, `set_volume`, `set_brightness`, `shutdown_computer`†, `restart_computer`†, `logout`† |
| Comms & media | `send_email`*, `play_music` |

\* needs an API key/credentials (auto-disabled until configured).
† disabled unless you pass `--allow-power`.

## Test

```bash
python -m pytest
```

The suite runs with no network, no microphone, and no API keys — a `ScriptedLLMProvider`
and a `FakePlatform` stand in for the model and the OS.

## Roadmap

- **Phase 2 — Voice + autostart** ✅ wake word "Jarvis", pluggable STT/TTS, and
  launch-at-login (systemd / launchd / Task Scheduler).
- **Phase 3 — Web UI** ✅ React HUD over FastAPI: tool trace, capabilities
  sidebar, in-browser voice.
- **Phase 4 — Messaging bot:** reach Jarvis from Telegram/Discord.

## Adding a skill

Create a file under `jarvis/skills/<area>/` with a `Skill` subclass that returns
`Tool`s from `tools()`. That's it — no registration step. See
`jarvis/skills/knowledge/datetime_skill.py` for the smallest example.
