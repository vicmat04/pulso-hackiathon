"""CU-03 · Repetición ≠ corroboración. Una agencia replicada cuenta como UNA procedencia.

Con solo titulares no se puede ver el cuerpo; se usan señales disponibles:
1) mención de agencia en titular/descripción; 2) titular casi idéntico a uno anterior;
3) si nada aplica, el propio medio es la procedencia.
"""
from __future__ import annotations

import re

from . import config
from .embed import Embedder, cosine
from .models import Noticia
from .organize import doc_text
from .text import norm, parse_dt, quantities

_AG = [(a, re.compile(rf"(\(|\b|segun\s+(la\s+)?(agencia\s+)?){re.escape(norm(a))}(\)|\b)")) for a in config.AGENCIES]


def agency_of(n: Noticia) -> str | None:
    t = norm(doc_text(n))
    for name, rx in _AG:
        if rx.search(t):
            return name
    return None


def provenances(items: list[Noticia], emb: Embedder) -> dict[str, list[str]]:
    order = sorted(items, key=lambda n: (parse_dt(n.fecha_publicacion or n.fecha_deteccion) is None,
                                         n.fecha_publicacion or n.fecha_deteccion or "", n.id_noticia))
    key_of: dict[str, str] = {}
    if order:
        x = emb.encode([n.titulo for n in order])
        sim = cosine(x, x)
    for i, n in enumerate(order):
        ag = agency_of(n)
        if ag:
            key_of[n.id_noticia] = f"agencia:{ag}"
            continue
        # copia = titular casi idéntico Y mismas cifras (si las cifras difieren, son reportes distintos)
        prev = [j for j in range(i) if sim[i, j] >= config.NEAR_DUP_SIM
                and quantities(order[j].titulo) == quantities(n.titulo)]
        key_of[n.id_noticia] = key_of[order[prev[0]].id_noticia] if prev else f"medio:{n.medio}"
    out: dict[str, list[str]] = {}
    for nid, k in key_of.items():
        out.setdefault(k, []).append(nid)
    return out
