"""Verticales temáticos que extienden el núcleo. Solo se ejecutan si config.VERTICALS[name]."""
from __future__ import annotations

from typing import Protocol

from ..models import Ficha as Story


class Vertical(Protocol):
    name: str

    def topics(self) -> list[str]: ...
    def extra_signals(self, story: Story) -> list[str]: ...
    def score_adjustments(self, story: Story) -> dict[str, float]: ...
    def mission_templates(self) -> dict[str, list[str]]: ...


def active() -> list[str]:
    from .. import config
    return [k for k, v in config.VERTICALS.items() if v and k != "general"]
