"""Etapa 3 · Contextualizar: relacionar noticias con datos oficiales. Si no hay relación
sustentada, NO forzarla (bases). USGS solo para hechos sísmicos, nunca inundación ni pérdidas."""
from __future__ import annotations

from . import config
from .models import Indicador, Noticia, Sismo
from .text import norm, parse_dt


def ind_id(i: Indicador) -> str:
    return f"ind:{i.pais_iso3}:{i.indicador_id}:{i.anio}"


def indicators_for(text: str, inds: list[Indicador], pais: str = "PAN") -> list[dict]:
    t = norm(text)
    out = []
    for code, (nombre, kws) in config.INDICATORS.items():
        if not any(k in t for k in kws):
            continue
        serie = sorted([i for i in inds if i.pais_iso3 == pais and i.indicador_id == code],
                       key=lambda i: i.anio)
        if not serie:
            continue
        validos = [i for i in serie if i.valor is not None]
        ult = serie[-1]
        ref = validos[-1] if validos else None
        lim = ["Dato anual; no es una medición de hoy."]
        if ult.valor is None:
            lim.append(f"El año {ult.anio} está vacío (nulo) en la fuente; no se rellena.")
        if ref is None:
            out.append({"tipo": "indicador", "indicador": nombre, "indicador_id": code, "pais": pais,
                        "valor": None, "anio": None, "unidad": ult.unidad, "evidencia_id": None,
                        "fuente_url": ult.fuente_url, "limitaciones": lim + ["Sin valores en la serie."]})
            continue
        out.append({"tipo": "indicador", "indicador": nombre, "indicador_id": code, "pais": pais,
                    "valor": ref.valor, "anio": ref.anio, "unidad": ref.unidad,
                    "evidencia_id": ind_id(ref), "fuente_url": ref.fuente_url,
                    "periodo": f"{serie[0].anio}–{serie[-1].anio}",
                    "serie": [[i.anio, i.valor] for i in serie[-6:]],
                    "licencia": ref.licencia, "limitaciones": lim})
    return out


def seismic_for(n: Noticia, sismos: list[Sismo], days: int = 2) -> list[dict]:
    t = norm(n.titulo + " " + (n.descripcion or ""))
    if not any(w in t for w in config.SEISMIC_WORDS):
        return []  # una inundación nunca se "respalda" con un sismo
    d = parse_dt(n.fecha_publicacion or n.fecha_deteccion)
    if not d:
        return []
    out = []
    for s in sismos:
        sd = parse_dt(s.time)
        if sd and abs((sd - d).total_seconds()) <= days * 86400:
            out.append({"tipo": "sismo", "evidencia_id": s.id, "magnitud": s.magnitude, "lugar": s.place,
                        "fecha": s.time, "url": s.url,
                        "limitaciones": ["Caja regional lat 5–12, lon −86 a −76: no equivale al territorio de Panamá.",
                                         "Solo respalda el hecho sísmico; no daños ni pérdidas."]})
    return out
