"""Vertical BANCA — RESERVADO. No entra en esta vuelta. Ver docs/06_BANCA_BASES.md."""
from __future__ import annotations

from ...models import Ficha as Story


class BancaVertical:
    name = "banca"

    def _off(self):
        raise NotImplementedError("Vertical banca desactivado en esta vuelta")

    def topics(self) -> list[str]:
        self._off()

    def extra_signals(self, story: Story) -> list[str]:
        self._off()

    def score_adjustments(self, story: Story) -> dict[str, float]:
        self._off()

    def mission_templates(self) -> dict[str, list[str]]:
        self._off()
