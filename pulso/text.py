"""Utilidades de texto en español: normalización, cifras, atribuciones, fechas."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

PANAMA = ZoneInfo("America/Panama")

ATTRIBUTION = re.compile(
    r"\b(segun|afirma|asegura|dice|denuncia|advierte|anuncia|informa|senala|declara|"
    r"niega|desmiente|confirma|estima|reporta)\b", re.I)
NUM_UNIT = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(mil|millones|%|por ciento)?\s*"
    r"(usuarios|personas|buques|turistas|pasajeros|horas|dias|familias|viviendas|cruceros)?", re.I)


def norm(t: str | None) -> str:
    t = unicodedata.normalize("NFD", (t or "").lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return re.sub(r"\s+", " ", t).strip()


def parse_dt(s: str | None) -> datetime | None:
    """ISO 8601 o formato GDELT (YYYYMMDDTHHMMSSZ). Devuelve UTC o None si inválida."""
    if not s or not str(s).strip():
        return None
    s = str(s).strip()
    for fmt in ("%Y%m%dT%H%M%SZ", "%Y%m%d%H%M%S"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            pass
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc)


def iso(d: datetime | None) -> str | None:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


def hora_panama(s: str | None) -> str:
    d = parse_dt(s)
    return d.astimezone(PANAMA).strftime("%d/%m/%Y %H:%M") if d else "sin fecha"


def is_declaration(t: str) -> bool:
    return bool(ATTRIBUTION.search(norm(t))) or ":" in t


def quantities(t: str) -> list[tuple[float, str]]:
    """Extrae (valor, unidad) comparables: '30 mil usuarios' -> (30000, 'usuarios')."""
    out = []
    for m in NUM_UNIT.finditer(norm(t)):
        num, mult, unit = m.groups()
        if not unit and mult not in ("%", "por ciento"):
            continue
        v = float(num.replace(",", "."))
        if mult == "mil":
            v *= 1_000
        elif mult == "millones":
            v *= 1_000_000
        out.append((v, unit or "%"))
    return out


def words(t: str) -> int:
    return len(re.findall(r"\w+", t))
