"""The LLM tool-call loop: the bridge between the brain and the skills.

Send message + history + tool schemas to the model. If it asks for tools, run
them via the registry, feed the results back, and loop. When it returns plain
text, that's the final answer. A hard iteration cap prevents infinite loops.
"""

from __future__ import annotations

import logging

from ..llm.base import LLMProvider, Message, ToolCall
from ..skills.base import Context
from ..skills.registry import Registry
from .response import Response
from .session import Session

log = logging.getLogger(__name__)


class Router:
    def __init__(
        self,
        llm: LLMProvider,
        registry: Registry,
        system_prompt: str,
        max_iterations: int = 6,
    ) -> None:
        self.llm = llm
        self.registry = registry
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations

    def run(self, text: str, session: Session, context: Context) -> Response:
        tools = self.registry.tool_specs()

        working: list[Message] = [Message(role="system", content=self.system_prompt)]
        working.extend(session.memory.history())
        working.append(Message(role="user", content=text))

        session.memory.add_user(text)

        final_text = ""
        for _ in range(self.max_iterations):
            result = self.llm.complete(working, tools or None)

            if not result.wants_tools:
                final_text = result.text or ""
                break

            working.append(
                Message(
                    role="assistant",
                    content=result.text,
                    tool_calls=result.tool_calls,
                )
            )
            for call in result.tool_calls:
                output = self._run_tool(call, context)
                working.append(
                    Message(
                        role="tool",
                        content=output,
                        tool_call_id=call.id,
                        name=call.name,
                    )
                )
        else:
            log.warning("Router hit max iterations (%d)", self.max_iterations)
            final_text = final_text or "I got stuck working on that. Could you rephrase?"

        session.memory.add_assistant(final_text)
        return Response(text=final_text)

    def _run_tool(self, call: ToolCall, context: Context) -> str:
        log.info("Tool call: %s(%s)", call.name, call.arguments)
        return self.registry.dispatch(call.name, call.arguments, context)
