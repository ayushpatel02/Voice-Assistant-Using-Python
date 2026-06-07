"""Shared HTTP helper used by web/weather/news skills.

Lazily uses ``httpx`` if installed, otherwise falls back to the standard
library so basic GET-JSON works without extra dependencies.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any


def get_json(url: str, params: dict[str, Any] | None = None, timeout: float = 10.0) -> Any:
    full_url = url
    if params:
        full_url = f"{url}?{urllib.parse.urlencode(params)}"
    try:
        import httpx

        resp = httpx.get(full_url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except ImportError:
        req = urllib.request.Request(full_url, headers={"User-Agent": "Jarvis/0.1"})
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
            return json.loads(r.read().decode("utf-8"))
