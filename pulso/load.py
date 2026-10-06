"""Etapa 1 · Cargar: lee el paquete congelado, valida y emite reporte de calidad (T01).

Regla: separar filas con error SIN bloquear la carga; conservar nulos; no rellenar con cero.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from . import config
from .models import Indicador, Noticia, Sismo
from .text import iso, parse_dt

REQ_NOTICIA = ["id_noticia", "titulo", "url", "medio", "fecha_extraccion", "origen", "alcance_texto"]
REQ_IND = ["pais_iso3", "indicador_id", "anio", "unidad", "fuente_url", "fecha_extraccion", "licencia"]


@dataclass
class Calidad:
    archivo: str
    leidas: int = 0
    validas: int = 0
    errores: list[dict] = field(default_factory=list)
    advertencias: list[dict] = field(default_factory=list)
    nulos: dict[str, int] = field(default_factory=dict)

    def err(self, fila, motivo, **kw):
        self.errores.append({"fila": fila, "motivo": motivo, **kw})

    def warn(self, fila, motivo, **kw):
        self.advertencias.append({"fila": fila, "motivo": motivo, **kw})


@dataclass
class Corpus:
    noticias: list[Noticia]
    indicadores: list[Indicador]
    sismos: list[Sismo]
    calidad: list[Calidad]
    fecha_corte: str | None


def _blank(v) -> bool:
    return v is None or str(v).strip() == ""


def load_noticias(path: Path) -> tuple[list[Noticia], Calidad]:
    q = Calidad(path.name)
    out, seen_ids, seen_urls = [], set(), set()
    desde, hasta = (parse_dt(x) for x in config.DATA_INTERVAL)
    with path.open(encoding="utf-8", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):  # fila 1 = cabecera
            q.leidas += 1
            for k, v in row.items():
                if _blank(v):
                    q.nulos[k] = q.nulos.get(k, 0) + 1
            missing = [k for k in REQ_NOTICIA if _blank(row.get(k))]
            if missing:
                q.err(i, "campos obligatorios vacíos", campos=missing, id=row.get("id_noticia"))
                continue
            if not str(row["url"]).startswith(("http://", "https://")):
                q.err(i, "url inválida", id=row["id_noticia"])
                continue
            if row["id_noticia"] in seen_ids:
                q.err(i, "id duplicado", id=row["id_noticia"])
                continue
            if row["url"] in seen_urls:
                q.err(i, "url duplicada (deduplicar por URL)", id=row["id_noticia"])
                continue
            fechas = {}
            bad = False
            for k in ("fecha_publicacion", "fecha_deteccion", "fecha_extraccion"):
                if _blank(row.get(k)):
                    fechas[k] = None
                    continue
                d = parse_dt(row[k])
                if d is None:
                    q.err(i, f"{k} inválida", valor=row[k], id=row["id_noticia"])
                    bad = True
                fechas[k] = iso(d)
            if bad:
                continue
            ref = parse_dt(fechas["fecha_publicacion"] or fechas["fecha_deteccion"])
            if ref is None:
                q.warn(i, "sin fecha de publicación ni detección", id=row["id_noticia"])
            elif not (desde <= ref < hasta):
                q.err(i, "fuera del intervalo de datos", fecha=iso(ref), id=row["id_noticia"])
                continue
            try:
                n = Noticia(**{**{k: (None if _blank(v) else v) for k, v in row.items()}, **fechas})
            except ValidationError as e:
                q.err(i, "esquema", detalle=str(e.errors()[0]["msg"]), id=row.get("id_noticia"))
                continue
            seen_ids.add(n.id_noticia)
            seen_urls.add(n.url)
            out.append(n)
    q.validas = len(out)
    return out, q


def load_indicadores(path: Path) -> tuple[list[Indicador], Calidad]:
    q = Calidad(path.name)
    out = []
    with path.open(encoding="utf-8", newline="") as f:
        for i, row in enumerate(csv.DictReader(f), start=2):
            q.leidas += 1
            missing = [k for k in REQ_IND if _blank(row.get(k))]
            if missing:
                q.err(i, "campos obligatorios vacíos", campos=missing)
                continue
            valor = None if _blank(row.get("valor")) else row["valor"]
            if valor is None:
                q.nulos["valor"] = q.nulos.get("valor", 0) + 1
            try:
                out.append(Indicador(**{**row, "valor": valor, "anio": int(row["anio"])}))
            except (ValidationError, ValueError) as e:
                q.err(i, "esquema", detalle=str(e)[:120])
    q.validas = len(out)
    return out, q


def load_sismos(path: Path) -> tuple[list[Sismo], Calidad]:
    q = Calidad(path.name)
    out = []
    data = json.loads(path.read_text(encoding="utf-8"))
    for i, feat in enumerate(data.get("features", []), start=1):
        q.leidas += 1
        p, g = feat.get("properties", {}), feat.get("geometry", {}).get("coordinates", [None] * 3)
        try:
            t = p.get("time")
            t = iso(parse_dt(t)) if isinstance(t, str) else iso(
                datetime.fromtimestamp(t / 1000, tz=timezone.utc))
            out.append(Sismo(id=feat["id"], magnitude=p["mag"], time=t, updated=str(p.get("updated")),
                             longitude=g[0], latitude=g[1], depth=g[2] if len(g) > 2 else None,
                             place=p.get("place") or "", status=p.get("status"), url=p.get("url") or ""))
        except (KeyError, TypeError, ValidationError) as e:
            q.err(i, "evento inválido", detalle=str(e)[:120])
    q.validas = len(out)
    return out, q


def load_corpus(data_dir: Path | None = None) -> Corpus:
    d = Path(data_dir or config.DATA_DIR)
    noticias, qn = load_noticias(d / "noticias.csv")
    inds, qi = (load_indicadores(d / "indicadores.csv") if (d / "indicadores.csv").exists()
                else ([], Calidad("indicadores.csv")))
    sis, qs = (load_sismos(d / "eventos.geojson") if (d / "eventos.geojson").exists()
               else ([], Calidad("eventos.geojson")))
    corte = None
    for name in ("manifest.json", "manifest_base.json"):
        if (d / name).exists():
            corte = json.loads((d / name).read_text(encoding="utf-8")).get("fecha_corte_UTC")
            break
    return Corpus(noticias, inds, sis, [qn, qi, qs], corte)


def quality_report(c: Corpus) -> dict:
    return {q.archivo: {"leidas": q.leidas, "validas": q.validas, "errores": q.errores,
                        "advertencias": q.advertencias, "nulos": q.nulos} for q in c.calidad}
