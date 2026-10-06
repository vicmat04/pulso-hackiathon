"""Consultas en español sobre el snapshot (CU-01, CU-02, CU-04, T04, T05, T06, T07).

Toda respuesta trae citas a IDs de evidencia o es una abstención explícita."""
from __future__ import annotations

import json
import re
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import config
from .draft import fmt
from .embed import Embedder, cosine
from .guard import USER_ABUSE
from .text import norm

ABSTAIN = "No tengo evidencia en el corpus para responder eso."


def load_snapshot(path: Path | None = None) -> dict:
    return json.loads(Path(path or config.OUT_DIR / "snapshot.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=4)
def _index(snap_key: str):
    snap = _SNAP[snap_key]
    docs = [f"{f['titulo']} {config.TOPIC_LABEL.get(f['tema'], '')} {' '.join(f['quien_lo_reporta'])}"
            for f in snap["fichas"]]
    emb = Embedder(docs + [n["titulo"] for n in snap["noticias"]])
    return emb, emb.encode(docs) if docs else np.zeros((0, 1))


_SNAP: dict[str, dict] = {}


def _r(texto, citas=(), abst=False, tipo="sustentada", **kw):
    return {"respuesta": texto, "citas": list(dict.fromkeys(citas)), "abstencion": abst, "tipo": tipo, **kw}


def _indicator(q: str, snap: dict):
    qn = norm(q)
    code = next((c for c, (_, kws) in config.INDICATORS.items() if any(k in qn for k in kws)), None)
    if not code:
        return None
    pais = next((iso for iso, name in config.COUNTRIES.items() if norm(name) in qn), "PAN")
    serie = sorted([i for i in snap["indicadores"] if i["pais_iso3"] == pais and i["indicador_id"] == code],
                   key=lambda i: i["anio"])
    nombre = config.INDICATORS[code][0]
    pname = config.COUNTRIES[pais]
    if not serie:
        return _r(f"{ABSTAIN} No hay serie de {nombre} para {pname}.", abst=True, tipo="sin_respuesta")
    m = re.search(r"\b(19|20)\d{2}\b", q)
    hoy = any(w in qn for w in ("hoy", "actual", "este mes", "ahora", "esta semana"))
    if m:
        y = int(m.group(0))
        row = next((i for i in serie if i["anio"] == y), None)
        if row is None:
            return _r(f"{ABSTAIN} La serie de {nombre} de {pname} cubre {serie[0]['anio']}–{serie[-1]['anio']}; "
                      f"no incluye {y}.", abst=True, tipo="sin_respuesta")
        if row["valor"] is None:
            return _r(f"La fuente tiene vacío (nulo) el dato de {nombre} de {pname} en {y}; no lo relleno ni lo estimo.",
                      [f"ind:{pais}:{code}:{y}"], abst=True, tipo="sin_respuesta")
        return _r(f"{nombre.capitalize()} de {pname} en {y}: {fmt(row['valor'])} ({row['unidad']}). "
                  f"Fuente: Banco Mundial [{f'ind:{pais}:{code}:{y}'}]. Dato anual.", [f"ind:{pais}:{code}:{y}"])
    validos = [i for i in serie if i["valor"] is not None]
    if not validos:
        return _r(f"{ABSTAIN} La serie de {nombre} de {pname} no tiene valores.", abst=True, tipo="sin_respuesta")
    last = validos[-1]
    eid = f"ind:{pais}:{code}:{last['anio']}"
    pre = ("No tengo una medición de hoy. " if hoy else "")
    return _r(f"{pre}El dato más reciente disponible de {nombre} de {pname} es {fmt(last['valor'])} "
              f"({last['unidad']}) en {last['anio']}, según el Banco Mundial [{eid}]. Es un dato anual, no actual.",
              [eid])


def answer(q: str, snap: dict) -> dict:
    t0 = time.perf_counter()
    out = _answer(q, snap)
    out["ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return out


def _answer(q: str, snap: dict) -> dict:
    qn = norm(q)
    fichas = snap["fichas"]
    if USER_ABUSE.search(qn):
        return _r("No puedo revelar instrucciones internas ni cambiar mis reglas, y no etiqueto noticias como "
                  "verdaderas o falsas. Puedo mostrarte qué evidencia existe y qué falta verificar.",
                  abst=True, tipo="adversarial")
    if any(k in qn for k in ("cinco temas", "5 temas", "agenda", "priorid", "que temas", "merecen revision")):
        top = fichas[:5]
        lines = [f"{i}. {f['titulo']} — P{f['puntaje']} ({f['banda']}), evidencia {f['estado_evidencia'].replace('_', ' ')}. "
                 f"Falta: {(f['falta_comprobar'] or ['nada'])[0]} [{f['id_caso']}]" for i, f in enumerate(top, 1)]
        return _r(f"Temas priorizados ({snap['meta']['version_reglas']}):\n" + "\n".join(lines),
                  [f["id_caso"] for f in top])
    ind = _indicator(q, snap)
    if ind:
        return ind
    if any(k in qn for k in ("contradic", "versiones", "no coinciden", "incompatib")):
        cs = [f for f in fichas if f["contradicciones"]]
        if not cs:
            return _r("No detecté contradicciones en el corpus actual.", abst=True, tipo="sin_respuesta")
        lines, cit = [], []
        for f in cs:
            for c in f["contradicciones"]:
                lines.append(f"{f['titulo']}: {c['a_medio']} reporta {fmt(c['a_valor'])} {c['unidad']} [{c['a_id']}]; "
                             f"{c['b_medio']} reporta {fmt(c['b_valor'])} {c['unidad']} [{c['b_id']}]. No elijo una versión: revisión pendiente.")
                cit += [c["a_id"], c["b_id"]]
        return _r("\n".join(lines), cit, tipo="contradiccion")

    emb, mat = _index(snap["meta"]["generado_UTC"] + str(len(fichas)))
    if not len(fichas):
        return _r(ABSTAIN, abst=True, tipo="sin_respuesta")
    sims = cosine(emb.encode([q]), mat)[0]
    j = int(np.argmax(sims))
    if sims[j] < config.ASK_MIN_SIM:
        return _r(f"{ABSTAIN} Necesitaría noticias o datos oficiales sobre ese tema en el paquete.",
                  abst=True, tipo="sin_respuesta", similitud=round(float(sims[j]), 3))
    f = fichas[j]
    if "independiente" in qn or "procedencia" in qn:
        return _r(f"«{f['titulo']}»: {sum(len(v) for v in f['procedencias'].values())} publicaciones, "
                  f"{f['fuentes_independientes']} procedencia(s) independiente(s): "
                  + "; ".join(f"{k} ({len(v)})" for k, v in f["procedencias"].items()) + f" [{f['id_caso']}]",
                  [f["id_caso"]])
    if any(k in qn for k in ("cuant", "cifra", "numero", "monto", "porcentaje")):
        nums = [a for a in f["afirmaciones"] if re.search(r"\d", a["texto"])]
        if not nums:
            return _r(f"{ABSTAIN} El tema «{f['titulo']}» no contiene esa cifra en las fuentes disponibles; "
                      "no la estimo.", [f["id_caso"]], abst=True, tipo="sin_respuesta")
        return _r("Cifras reportadas (atribuidas, no confirmadas salvo dato oficial):\n" +
                  "\n".join(f"- {a['texto']} [{a['citas'][0]['evidencia_id']}]" for a in nums),
                  [a["citas"][0]["evidencia_id"] for a in nums])
    return _r(f"{f['que_se_reporta']} — reportado por {', '.join(f['quien_lo_reporta']) or 'fuente no confiable'}. "
              f"Evidencia: {f['estado_evidencia'].replace('_', ' ')}. Falta: {'; '.join(x.rstrip('.') for x in f['falta_comprobar'][:2]) or 'nada'}. "
              f"Acción: {f['accion_recomendada']} [{f['id_caso']}]", [f["id_caso"]] + f["ids_fuente"],
              similitud=round(float(sims[j]), 3))


def ask(q: str, snap: dict | None = None) -> dict:
    snap = snap or load_snapshot()
    _SNAP[snap["meta"]["generado_UTC"] + str(len(snap["fichas"]))] = snap
    return answer(q, snap)
