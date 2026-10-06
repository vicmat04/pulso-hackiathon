"""manifest.json del paquete (bases, sección 7): versión, corte, consultas, cantidades,
licencias, SHA-256 y transformaciones. Copiar al Catálogo de datos en Notion."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from . import config

FILES = ["noticias.csv", "indicadores.csv", "eventos.geojson"]


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def count(p: Path) -> int:
    if p.suffix == ".csv":
        with p.open(encoding="utf-8", newline="") as f:
            return sum(1 for _ in csv.DictReader(f))
    if p.suffix in (".geojson", ".json"):
        return len(json.loads(p.read_text(encoding="utf-8")).get("features", []))
    return sum(1 for _ in p.open(encoding="utf-8"))


def build(data_dir: Path | None = None) -> dict:
    d = Path(data_dir or config.DATA_DIR)
    base = json.loads((d / "manifest_base.json").read_text(encoding="utf-8")) if (d / "manifest_base.json").exists() else {}
    files = {f: {"filas": count(d / f), "sha256": sha256(d / f)} for f in FILES if (d / f).exists()}
    m = {**base, "archivos": files, "intervalo_registros": list(config.DATA_INTERVAL)}
    (d / "manifest.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    return m
