"""Anti-inyección (T07): el texto de una fuente es DATO, nunca instrucción.

Las fuentes marcadas se muestran como 'contenido no confiable', se excluyen de borradores y
nunca se concatenan a instrucciones de un LLM sin delimitarlas."""
from __future__ import annotations

import re

from .text import norm

PATTERNS = [
    r"ignora(r)? (todas |tus |las )?(instrucciones|reglas)", r"ignore (all |previous |your )?instructions",
    r"revela(r)? (tu|el|la|los) (prompt|clave|secreto|token|api)", r"system prompt",
    r"actua como", r"act as", r"olvida (todo|tus reglas)", r"api[_ ]?key", r"contrasena", r"password",
    r"cambia(r)? (tus|las) reglas", r"ejecuta(r)? (el|este) (comando|codigo)",
]
_RX = re.compile("|".join(PATTERNS), re.I)

USER_ABUSE = re.compile(
    r"(revela|muestra|dime).*(prompt|instrucciones|clave|token|secreto)|ignora.*(reglas|instrucciones)|"
    r"(marca|declara|etiqueta).*(falsa|verdadera|fake)", re.I)


def is_injection(text: str | None) -> bool:
    return bool(text) and bool(_RX.search(norm(text)))


def wrap_source(source_id: str, text: str) -> str:
    """Delimita contenido de fuente para prompts de LLM."""
    safe = text.replace("</fuente>", "")
    return f'<fuente id="{source_id}">{safe}</fuente>'
