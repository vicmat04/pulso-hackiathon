"""Receta de extracción (solo con red). Úsala si la organización no entrega el paquete congelado
o para documentar la receta en el Catálogo de datos. Endpoints públicos citados en las bases;
verificar funcionamiento y condiciones al congelar. Nada de esto corre durante la demo."""
from __future__ import annotations

import csv
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from . import config

UA = {"User-Agent": "PULSO-hackIAthon/0.2 (investigación; contacto en README)"}
NOW = lambda: datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: E731


def _get(url: str) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        return r.read()


def worldbank(out: Path, countries=tuple(config.COUNTRIES), years=(2010, 2024)) -> int:
    """Cuadrícula país × indicador × año con nulos explícitos (no prometer observaciones válidas)."""
    rows = []
    for code in config.INDICATORS:
        url = (f"https://api.worldbank.org/v2/country/{';'.join(countries)}/indicator/{code}"
               f"?date={years[0]}:{years[1]}&format=json&per_page=2000")
        data = json.loads(_get(url))
        got = {(d["countryiso3code"], int(d["date"])): d["value"] for d in (data[1] or [])}
        for c in countries:
            for y in range(years[0], years[1] + 1):
                v = got.get((c, y))
                rows.append([c, code, y, "" if v is None else v, "ver metadatos del indicador", url, NOW(),
                             "CC BY 4.0 salvo excepciones en metadatos"])
    with (out / "indicadores.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["pais_iso3", "indicador_id", "anio", "valor", "unidad", "fuente_url", "fecha_extraccion", "licencia"])
        w.writerows(rows)
    return len(rows)


def usgs(out: Path, start="2024-01-01", end="2024-12-31") -> int:
    q = urllib.parse.urlencode({"format": "geojson", "starttime": start, "endtime": end, "minlatitude": 5,
                                "maxlatitude": 12, "minlongitude": -86, "maxlongitude": -76, "minmagnitude": 3})
    data = _get(f"https://earthquake.usgs.gov/fdsnws/event/1/query?{q}")
    (out / "eventos.geojson").write_bytes(data)
    return len(json.loads(data)["features"])


def gdelt(query: str, start: str, end: str) -> list[dict]:
    """DOC 2.0 ArtList; máx. 250 por consulta: dividir por fechas. seendate = DETECCIÓN, no publicación."""
    q = urllib.parse.urlencode({"query": query, "mode": "ArtList", "format": "json", "maxrecords": 250,
                                "startdatetime": start, "enddatetime": end})
    data = json.loads(_get(f"https://api.gdeltproject.org/api/v2/doc/doc?{q}") or b"{}")
    return [{"titulo": a.get("title"), "url": a.get("url"), "medio": a.get("domain"), "idioma": a.get("language"),
             "fecha_publicacion": "", "fecha_deteccion": a.get("seendate"), "origen": "gdelt",
             "alcance_texto": "titular"} for a in data.get("articles", [])]


def rss(url: str, medio: str) -> list[dict]:
    root = ET.fromstring(_get(url))
    out = []
    for it in root.iter("item"):
        pub = it.findtext("pubDate")
        try:
            pub = parsedate_to_datetime(pub).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if pub else ""
        except (TypeError, ValueError):
            pub = ""
        out.append({"titulo": it.findtext("title"), "url": it.findtext("link"), "medio": medio, "idioma": "es",
                    "fecha_publicacion": pub, "fecha_deteccion": "", "origen": "tvn_rss",
                    "alcance_texto": "titular+descripcion", "descripcion": (it.findtext("description") or "")[:300]})
    return out


def write_noticias(items: list[dict], out: Path) -> int:
    seen, rows = set(), []
    for i, a in enumerate(items, 1):
        if not a.get("url") or a["url"] in seen:
            continue  # deduplicar por URL
        seen.add(a["url"])
        rows.append({"id_noticia": f"N{i:05d}", "fecha_extraccion": NOW(), "tema": "", **a})
    cols = ["id_noticia", "titulo", "url", "medio", "idioma", "fecha_publicacion", "fecha_deteccion",
            "fecha_extraccion", "tema", "origen", "alcance_texto", "descripcion"]
    with (out / "noticias.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return len(rows)
