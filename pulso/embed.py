"""Representación semántica. Backend 'tfidf' (scikit-learn, offline, sin descargas) o 'st'
(sentence-transformers multilingüe, mejor calidad; descargar antes con `make models`)."""
from __future__ import annotations

import numpy as np

from . import config
from .text import norm


class Embedder:
    def __init__(self, corpus: list[str], backend: str | None = None):
        self.backend = backend or config.EMBED_BACKEND
        if self.backend == "st":
            from sentence_transformers import SentenceTransformer  # grupo nlp
            if not config.ST_MODEL:
                raise RuntimeError("Define PULSO_ST_MODEL para usar el backend 'st'")
            self.model = SentenceTransformer(config.ST_MODEL)
        else:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self.model = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
            self.model.fit([norm(t) for t in corpus] or ["vacio"])

    @property
    def name(self) -> str:
        return f"st:{config.ST_MODEL}" if self.backend == "st" else "tfidf-char3-5"

    def encode(self, texts: list[str]) -> np.ndarray:
        if self.backend == "st":
            return np.asarray(self.model.encode(texts, normalize_embeddings=True))
        m = self.model.transform([norm(t) for t in texts]).toarray()
        n = np.linalg.norm(m, axis=1, keepdims=True)
        return m / np.where(n == 0, 1, n)


def cosine(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b.T
