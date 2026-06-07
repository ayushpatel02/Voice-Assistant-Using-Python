"""The Assistant: the single entry point every interface calls.

Builds the brain, skill registry, services, and platform layer from settings,
and exposes one method — :meth:`handle` — that turns user text into a Response.
Interfaces (CLI, voice, web, bot) depend on this; it depends on none of them.
"""

from __future__ import annotations

from ..config.settings import Settings, load_settings
from ..llm.base import LLMProvider
from ..llm.factory import build_llm
from ..platform.base import PlatformController
from ..platform.factory import build_platform
from ..services import Services
from ..skills.base import Context
from ..skills.registry import Registry, build_registry
from .response import Response
from .router import Router
from .session import Session


class Assistant:
    def __init__(
        self,
        settings: Settings,
        llm: LLMProvider,
        registry: Registry,
        services: Services,
        platform: PlatformController,
        router: Router,
    ) -> None:
        self.settings = settings
        self.llm = llm
        self.registry = registry
        self.services = services
        self.platform = platform
        self.router = router

    @classmethod
    def create(
        cls,
        settings: Settings | None = None,
        *,
        allow_power: bool = False,
    ) -> "Assistant":
        settings = settings or load_settings()
        llm = build_llm(settings)
        registry = build_registry(settings)
        services = Services.create(settings)
        platform = build_platform(allow_power=allow_power)
        router = Router(
            llm=llm,
            registry=registry,
            system_prompt=settings.assistant.persona,
            max_iterations=settings.llm.max_tool_iterations,
        )
        return cls(settings, llm, registry, services, platform, router)

    def handle(self, text: str, session: Session) -> Response:
        context = Context(
            settings=self.settings,
            session=session,
            services=self.services,
            platform=self.platform,
        )
        return self.router.run(text, session, context)

    def new_session(self, channel: str = "cli") -> Session:
        return Session(channel=channel)

    def shutdown(self) -> None:
        self.services.shutdown()
