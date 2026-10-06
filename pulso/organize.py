"""Etapa 2 · Organizar: clasificación temática y agrupación de noticias del mismo evento.

- Baseline: reglas de palabras clave (TOPIC_KEYWORDS) — requerido por las bases para comparar.
- IA: similitud semántica con prototipos de tema + agrupación aglomerativa por similitud.
"""
from __future__ import annotations

import numpy as np
from sklearn.cluster import AgglomerativeClustering

from . import config
from .embed import Embedder, cosine
from .models import Noticia
from .text import norm, parse_dt


def doc_text(n: Noticia) -> str:
    return f"{n.titulo}. {n.descripcion or ''}"


def classify_keywords(text: str) -> str:
    t = norm(text)
    scores = {k: sum(t.count(w) for w in ws) for k, ws in config.TOPIC_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "otros"


def classify_semantic(texts: list[str], emb: Embedder, min_sim: float = 0.08) -> list[str]:
    """Tema = prototipo más similar (prototipo = descripción + palabras clave del tema)."""
    keys = list(config.TOPIC_PROTOTYPES)
    protos = [config.TOPIC_PROTOTYPES[k] + " " + " ".join(config.TOPIC_KEYWORDS[k]) for k in keys]
    sims = cosine(emb.encode(texts), emb.encode(protos))
    out = []
    for row in sims:
        j = int(np.argmax(row))
        out.append(keys[j] if row[j] >= min_sim else "otros")
    return out


def cluster(noticias: list[Noticia], emb: Embedder) -> list[list[int]]:
    """Agrupa índices de noticias del mismo evento. Ventana temporal evita unir eventos lejanos."""
    if len(noticias) < 2:
        return [[i] for i in range(len(noticias))]
    x = emb.encode([doc_text(n) for n in noticias])
    dist = 1 - cosine(x, x)
    dates = [parse_dt(n.fecha_publicacion or n.fecha_deteccion) for n in noticias]
    for i in range(len(noticias)):
        for j in range(len(noticias)):
            if dates[i] and dates[j] and abs((dates[i] - dates[j]).days) > config.CLUSTER_WINDOW_DAYS:
                dist[i, j] = 1.0
    np.fill_diagonal(dist, 0)
    labels = AgglomerativeClustering(n_clusters=None, metric="precomputed", linkage="average",
                                     distance_threshold=config.CLUSTER_DISTANCE).fit_predict(dist)
    groups: dict[int, list[int]] = {}
    for i, lab in enumerate(labels):
        groups.setdefault(int(lab), []).append(i)
    return sorted(groups.values(), key=lambda g: min(g))
