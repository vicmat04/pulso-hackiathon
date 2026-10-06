"""Etapa 7 · Revisar: estados y registro de decisión humana (bases, sección 8).
Aprobar como borrador NO significa publicar. Registro append-only en data/review_log.jsonl."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import config

TRANSITIONS = {
    "nuevo": {"en_revision", "descartado"},
    "en_revision": {"requiere_evidencia", "aprobado_como_borrador", "descartado"},
    "requiere_evidencia": {"en_revision", "descartado"},
    "aprobado_como_borrador": {"en_revision"},
    "descartado": {"en_revision"},
}


def latest() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if config.REVIEW_LOG.exists():
        for line in config.REVIEW_LOG.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                out[r["id_caso"]] = r
    return out


def check(actual: str, nuevo: str, estado_evidencia: str, revisor: str) -> None:
    """Reglas de control humano. Lanza ValueError si la transición no es válida."""
    if nuevo not in TRANSITIONS.get(actual, set()):
        raise ValueError(f"Transición no permitida: {actual} → {nuevo}")
    if nuevo == "aprobado_como_borrador" and estado_evidencia == "insuficiente":
        raise ValueError("Evidencia insuficiente: usar 'requiere_evidencia', no aprobar.")
    if not revisor.strip():
        raise ValueError("Se requiere persona revisora responsable.")


def record(ficha: dict, nuevo: str, revisor: str, decision: str, nota: str = "") -> dict:
    """decision: aceptacion | correccion | descarte (bases, etapa 7)."""
    actual = latest().get(ficha["id_caso"], {}).get("estado", ficha.get("estado_revision", "nuevo"))
    check(actual, nuevo, ficha["estado_evidencia"], revisor)
    r = {"id_caso": ficha["id_caso"], "de": actual, "estado": nuevo, "revisor": revisor,
         "decision": decision, "nota": nota, "puntaje": ficha["puntaje"],
         "version_reglas": ficha["version_reglas"],
         "fecha_UTC": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    config.REVIEW_LOG.parent.mkdir(parents=True, exist_ok=True)
    with config.REVIEW_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return r
