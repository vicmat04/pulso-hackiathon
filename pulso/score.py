"""Etapa 4 · Priorizar. P = 30R + 25I + 20U + 15N + 10E (bases, sección 4).
Herramienta de ordenamiento: NO es probabilidad de verdad. Estado de evidencia va aparte."""
from __future__ import annotations

from datetime import datetime

from . import config
from .models import Componentes


def r_relevancia(menciona_panama: bool, tema: str) -> tuple[float, str]:
    v = 0.5 * menciona_panama + 0.5 * (tema != "otros")
    return v, f"relación con Panamá (país o lugar) {'sí' if menciona_panama else 'no'} (0,5) + tema de la modalidad {'sí' if tema != 'otros' else 'no'} (0,5)"


def i_impacto(tema: str, con_contexto_oficial: bool) -> tuple[float, str]:
    base = config.IMPACT_BASE.get(tema, 0.3)
    v = min(1.0, base + (0.2 if con_contexto_oficial else 0))
    return v, f"base del tema {base} + {0.2 if con_contexto_oficial else 0} por dato oficial relacionado"


def u_urgencia(fecha_original: datetime | None, corte: datetime) -> tuple[float, str]:
    if not fecha_original:
        return 0.3, "sin fecha original: urgencia prudente 0,3"
    dias = (corte - fecha_original).total_seconds() / 86400
    v = 1.0 if dias <= 1 else 0.7 if dias <= 3 else 0.4 if dias <= 7 else 0.1
    return v, f"{dias:.1f} días desde la fecha original (≤1:1 · ≤3:0,7 · ≤7:0,4 · resto:0,1)"


def n_novedad(recirculada: bool, fecha_original: datetime | None, corte: datetime) -> tuple[float, str]:
    if recirculada:
        return 0.1, "noticia recirculada: el evento no es nuevo"
    if fecha_original and (corte - fecha_original).days <= 7:
        return 1.0, "evento nuevo en la ventana; duplicados no suman"
    return 0.5, "evento previo a la ventana de 7 días"


def e_evidencia(fuentes_independientes: int, con_contexto_oficial: bool) -> tuple[float, str]:
    v = min(1.0, 0.6 * min(fuentes_independientes, 3) / 3 + 0.4 * con_contexto_oficial)
    return round(v, 3), f"{fuentes_independientes} procedencias (máx. 3 → 0,6) + dato oficial {'sí' if con_contexto_oficial else 'no'} (0,4)"


def total(c: Componentes) -> int:
    w = config.WEIGHTS
    return round(sum(w[k] * getattr(c, k) for k in w))


def band(p: int) -> str:
    return next(name for lim, name in config.BANDS if p >= lim)


def sort_key(ficha) -> tuple:
    """Empates: mayor urgencia y luego ID (bases)."""
    return (-ficha.puntaje, -ficha.componentes.U, ficha.id_caso)
