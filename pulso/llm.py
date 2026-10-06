"""LLM OPCIONAL para reescribir el estilo del brief. Nunca agrega hechos.

Controles (bases, sección 8): instrucciones separadas del contenido de fuentes (<fuente>),
salida JSON obligatoria con citas, validación posterior y caída a plantilla si algo falla.
Proveedor y modelo se documentan en Notion (Diseño de solución) con costo medido."""
from __future__ import annotations

import json
import os
import time

from . import config
from .guard import wrap_source

PROMPT = (config.ROOT / "prompts" / "brief_v1.md")


def _call(system: str, user: str) -> tuple[str, dict]:
    prov = config.LLM_PROVIDER
    t0 = time.perf_counter()
    if prov == "ollama":
        import ollama
        model = os.environ["PULSO_OLLAMA_MODEL"]
        r = ollama.chat(model=model, format="json", options={"temperature": 0},
                        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}])
        return r["message"]["content"], {"proveedor": "ollama", "modelo": model,
                                         "ms": round((time.perf_counter() - t0) * 1000)}
    if prov == "anthropic":
        import anthropic
        model = os.environ["PULSO_ANTHROPIC_MODEL"]
        r = anthropic.Anthropic().messages.create(model=model, max_tokens=900, temperature=0, system=system,
                                                  messages=[{"role": "user", "content": user}])
        return r.content[0].text, {"proveedor": "anthropic", "modelo": model,
                                   "tokens_in": r.usage.input_tokens, "tokens_out": r.usage.output_tokens,
                                   "ms": round((time.perf_counter() - t0) * 1000)}
    raise RuntimeError("sin proveedor")


def rewrite_brief(ficha: dict, valid_ids: set[str]) -> tuple[list[dict] | None, dict]:
    """Devuelve afirmaciones reescritas o None (usar plantilla). Valida citas contra valid_ids."""
    if config.LLM_PROVIDER == "none" or not ficha.get("borrador"):
        return None, {"proveedor": "none"}
    fuentes = "\n".join(wrap_source(c["evidencia_id"], a["texto"])
                        for a in ficha["borrador"]["brief"] for c in a["citas"][:1])
    try:
        raw, meta = _call(PROMPT.read_text(encoding="utf-8"), f"FUENTES:\n{fuentes}\n\nDevuelve solo JSON.")
        data = json.loads(raw.strip().removeprefix("```json").removesuffix("```"))
        out = []
        for a in data["afirmaciones"]:
            if a["tipo"] not in ("hecho", "declaracion", "inferencia", "hipotesis"):
                raise ValueError("tipo inválido")
            if a["tipo"] in ("hecho", "declaracion") and (not a.get("citas") or not set(a["citas"]) <= valid_ids):
                raise ValueError("afirmación sin cita válida")
            out.append(a)
        if sum(len(a["texto"].split()) for a in out) > 250:
            raise ValueError("excede 250 palabras")
        return out, meta
    except Exception as e:  # noqa: BLE001 — la demo nunca se rompe por el LLM
        return None, {"proveedor": config.LLM_PROVIDER, "error": str(e)[:200], "fallback": "plantilla"}
