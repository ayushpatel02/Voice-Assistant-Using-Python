"""FastAPI web interface — a browser chat that drives the same Assistant core.

Exposes a REST endpoint and a WebSocket, plus a static React (CDN/JSX, no build
step) front-end. Every request flows through ``Assistant.handle`` exactly like
the CLI and voice faces; nothing about the brain or skills is duplicated here.

Note: this module intentionally does NOT use ``from __future__ import
annotations``. FastAPI must see the real ``Request``/``WebSocket`` classes (which
are imported inside ``create_app``) to bind route parameters; stringized hints
would resolve against module globals and fail.
"""

import logging
from pathlib import Path

from ...core.assistant import Assistant
from ...core.session import Session

log = logging.getLogger(__name__)

STATIC_DIR = Path(__file__).parent / "static"


def create_app(assistant: Assistant | None = None):
    try:
        from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
        from fastapi.responses import FileResponse
    except ImportError as exc:  # pragma: no cover - needs web extras
        raise RuntimeError(
            "The web UI requires FastAPI/uvicorn. "
            "Install with: pip install 'jarvis-assistant[web]'"
        ) from exc

    assistant = assistant or Assistant.create()
    sessions: dict[str, Session] = {}

    def get_session(session_id: str) -> Session:
        if session_id not in sessions:
            session = assistant.new_session("web")
            session.session_id = session_id
            sessions[session_id] = session
        return sessions[session_id]

    def answer(message: str, session_id: str) -> dict:
        session = get_session(session_id)
        response = assistant.handle(message, session)
        return {"reply": response.text, "tools_used": response.meta.get("tools_used", [])}

    app = FastAPI(title="Jarvis")

    @app.get("/api/info")
    def info() -> dict:
        return {
            "name": assistant.settings.assistant.name,
            "model": assistant.settings.llm.model,
            "provider": assistant.settings.llm.provider,
            "tool_count": len(assistant.registry),
        }

    @app.get("/api/skills")
    def skills() -> list[dict]:
        return [
            {"name": spec.name, "description": spec.description}
            for spec in assistant.registry.tool_specs()
        ]

    @app.post("/api/chat")
    async def chat(request: Request) -> dict:
        data = await request.json()
        return answer(data.get("message", ""), data.get("session_id", "default"))

    @app.websocket("/ws")
    async def ws(websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_json()
                await websocket.send_json({"type": "status", "state": "thinking"})
                result = answer(data.get("message", ""), data.get("session_id", "default"))
                await websocket.send_json({"type": "reply", **result})
        except WebSocketDisconnect:
            return

    # Explicit static routes (no catch-all mount, so /ws and /api keep working).
    @app.get("/")
    def index():
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/{filename:path}")
    def static_file(filename: str):
        target = (STATIC_DIR / filename).resolve()
        if STATIC_DIR.resolve() in target.parents and target.is_file():
            return FileResponse(target)
        return FileResponse(STATIC_DIR / "index.html")

    return app


def run_web(allow_power: bool = False) -> None:
    from ...config.settings import load_settings

    settings = load_settings()
    try:
        import uvicorn

        app = create_app(Assistant.create(settings=settings, allow_power=allow_power))
    except RuntimeError as exc:
        print(exc)
        return
    print(f"Jarvis web UI on http://{settings.web.host}:{settings.web.port}")
    uvicorn.run(app, host=settings.web.host, port=settings.web.port)
