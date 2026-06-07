from jarvis.skills.comms.music import MusicSkill
from jarvis.skills.knowledge.datetime_skill import DateTimeSkill
from jarvis.skills.productivity.notes_todo import NotesSkill
from jarvis.skills.system.apps_web import AppsWebSkill
from jarvis.skills.system.controls import ControlsSkill

from .fakes import make_context


def _tool(skill, name):
    return next(t for t in skill.tools() if t.name == name)


def test_datetime_tools(tmp_path):
    ctx = make_context(tmp_path)
    skill = DateTimeSkill()
    assert "It's" in _tool(skill, "get_time").handler({}, ctx)
    assert "Today is" in _tool(skill, "get_date").handler({}, ctx)


def test_notes_roundtrip(tmp_path):
    ctx = make_context(tmp_path)
    skill = NotesSkill()
    _tool(skill, "add_note").handler({"text": "buy milk"}, ctx)
    _tool(skill, "add_note").handler({"text": "call mom"}, ctx)
    listed = _tool(skill, "list_notes").handler({}, ctx)
    assert "buy milk" in listed and "call mom" in listed
    assert "Cleared 2" in _tool(skill, "clear_notes").handler({}, ctx)


def test_apps_web_delegates_to_platform(tmp_path):
    ctx = make_context(tmp_path)
    skill = AppsWebSkill()
    _tool(skill, "open_app").handler({"name": "spotify"}, ctx)
    _tool(skill, "open_website").handler({"url": "github.com"}, ctx)
    assert ("open_app", "spotify") in ctx.platform.calls
    assert any(c[0] == "open_url" for c in ctx.platform.calls)


def test_controls_volume_and_brightness(tmp_path):
    ctx = make_context(tmp_path)
    skill = ControlsSkill()
    _tool(skill, "set_volume").handler({"percent": 30}, ctx)
    _tool(skill, "set_brightness").handler({"percent": 80}, ctx)
    assert ("set_volume", 30) in ctx.platform.calls
    assert ("set_brightness", 80) in ctx.platform.calls


def test_music_opens_spotify(tmp_path):
    ctx = make_context(tmp_path)
    skill = MusicSkill()
    result = _tool(skill, "play_music").handler({"query": "Thunderstruck"}, ctx)
    assert "Spotify" in result
    assert any("spotify.com" in str(c[1]) for c in ctx.platform.calls)
