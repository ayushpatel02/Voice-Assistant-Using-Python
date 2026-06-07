import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from jarvis.config.settings import Settings  # noqa: E402
from jarvis.core.assistant import Assistant  # noqa: E402
from jarvis.interfaces.web.server import create_app  # noqa: E402


def _client(tmp_path) -> TestClient:
    settings = Settings()
    settings.data_dir = tmp_path
    settings.llm.provider = "fake"
    return TestClient(create_app(Assistant.create(settings=settings)))


def test_info_endpoint(tmp_path):
    body = _client(tmp_path).get("/api/info").json()
    assert body["name"] == "Jarvis"
    assert body["tool_count"] > 0


def test_skills_endpoint_lists_tools(tmp_path):
    skills = _client(tmp_path).get("/api/skills").json()
    names = {s["name"] for s in skills}
    assert "get_time" in names


def test_chat_endpoint_returns_reply(tmp_path):
    resp = _client(tmp_path).post(
        "/api/chat", json={"message": "hello", "session_id": "t1"}
    )
    data = resp.json()
    assert "reply" in data
    assert "tools_used" in data


def test_websocket_chat(tmp_path):
    with _client(tmp_path).websocket_connect("/ws") as ws:
        ws.send_json({"message": "hi", "session_id": "t2"})
        first = ws.receive_json()
        assert first == {"type": "status", "state": "thinking"}
        reply = ws.receive_json()
        assert reply["type"] == "reply"
        assert "reply" in reply


def test_index_served(tmp_path):
    r = _client(tmp_path).get("/")
    assert r.status_code == 200
    assert "J.A.R.V.I.S" in r.text
