from jarvis.config.settings import Settings
from jarvis.core.router import Router
from jarvis.core.session import Session
from jarvis.llm.base import LLMResult, ToolCall
from jarvis.llm.fake_provider import ScriptedLLMProvider
from jarvis.skills.base import Context
from jarvis.skills.registry import build_registry

from .fakes import FakePlatform
from jarvis.services import Services


def _context(tmp_path) -> Context:
    settings = Settings()
    settings.data_dir = tmp_path
    return Context(
        settings=settings,
        session=Session(channel="test"),
        services=Services.create(settings),
        platform=FakePlatform(),
    )


def test_router_executes_tool_then_returns_text(tmp_path):
    # First the model asks for a tool, then it produces a final answer.
    llm = ScriptedLLMProvider(
        [
            LLMResult(tool_calls=[ToolCall(id="1", name="get_time", arguments={})]),
            LLMResult(text="It is time."),
        ]
    )
    registry = build_registry(Settings())
    router = Router(llm, registry, system_prompt="sys", max_iterations=5)

    ctx = _context(tmp_path)
    response = router.run("what time is it?", ctx.session, ctx)

    assert response.text == "It is time."
    # The second LLM call must have seen the tool result message.
    second_call_roles = [m.role for m in llm.calls[1]]
    assert "tool" in second_call_roles


def test_router_plain_answer_without_tools(tmp_path):
    llm = ScriptedLLMProvider([LLMResult(text="Hello, Boss.")])
    router = Router(llm, build_registry(Settings()), system_prompt="sys")
    ctx = _context(tmp_path)
    response = router.run("hi", ctx.session, ctx)
    assert response.text == "Hello, Boss."
    # History should contain the exchange.
    assert len(ctx.session.memory.history()) == 2


def test_router_respects_max_iterations(tmp_path):
    # Model keeps asking for tools forever; router must give up gracefully.
    looping = [
        LLMResult(tool_calls=[ToolCall(id=str(i), name="get_time", arguments={})])
        for i in range(10)
    ]
    llm = ScriptedLLMProvider(looping)
    router = Router(llm, build_registry(Settings()), system_prompt="sys", max_iterations=3)
    ctx = _context(tmp_path)
    response = router.run("loop", ctx.session, ctx)
    assert response.text  # non-empty fallback
    assert len(llm.calls) == 3
