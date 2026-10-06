"""T01–T10 de las bases (sección 9). Cada prueba también alimenta la matriz de Notion."""
import pytest

from pulso.acceptance import SPEC, TESTS


@pytest.mark.parametrize("tid", list(TESTS))
def test_aceptacion(tid, snap):
    ok, observado = TESTS[tid](snap)
    assert ok, f"{tid} · {SPEC[tid][0]}: {observado}"
