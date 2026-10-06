"""Evaluación reproducible (bases, sección 9.1). Reporta numerador, denominador y fallos."""
from __future__ import annotations

import csv
import json
import statistics
from itertools import combinations
from pathlib import Path

from sklearn.metrics import f1_score

from . import config
from .ask import ask


def _valid_ids(snap: dict) -> set[str]:
    ids = {f["id_caso"] for f in snap["fichas"]} | {n["id_noticia"] for n in snap["noticias"]}
    ids |= {f"ind:{i['pais_iso3']}:{i['indicador_id']}:{i['anio']}" for i in snap["indicadores"]}
    ids |= {c["evidencia_id"] for f in snap["fichas"] for c in f["contexto_oficial"] if c.get("evidencia_id")}
    return ids


def run_benchmark(snap: dict, path: Path, split: str = "dev") -> dict:
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    rows = [r for r in rows if r.get("split", "dev") == split]
    valid = _valid_ids(snap)
    res, lat, fallos = [], [], []
    for r in rows:
        a = ask(r["consulta"], snap)
        lat.append(a["ms"])
        ok_abst = a["abstencion"] == r["espera_abstencion"]
        citas_ok = a["abstencion"] or (bool(a["citas"]) and set(a["citas"]) <= valid)
        esperado = r.get("debe_citar_alguno") or []
        acierto = (not esperado) or bool(set(esperado) & set(a["citas"]))
        ok = ok_abst and citas_ok and acierto
        res.append({**r, "respuesta": a["respuesta"], "citas": a["citas"], "abstencion": a["abstencion"],
                    "ms": a["ms"], "ok": ok})
        if not ok:
            fallos.append({"id": r["id"], "tipo": r["tipo"], "abstencion_obtenida": a["abstencion"],
                           "citas": a["citas"], "motivo": "abstención" if not ok_abst else "citas" if not citas_ok else "cita esperada ausente"})

    def frac(cond, pool):
        pool = list(pool)
        n = sum(1 for x in pool if cond(x))
        return {"numerador": n, "denominador": len(pool), "valor": round(n / len(pool), 3) if pool else None}

    emitted = [x for x in res if not x["abstencion"]]
    lat_sorted = sorted(lat)
    return {
        "split": split, "n": len(res),
        "aciertos": frac(lambda x: x["ok"], res),
        "abstencion_correcta_sin_respuesta": frac(lambda x: x["abstencion"], [x for x in res if x["tipo"] == "sin_respuesta"]),
        "rechazo_adversarial": frac(lambda x: x["abstencion"], [x for x in res if x["tipo"] == "adversarial"]),
        "abstencion_incorrecta_respondibles": frac(lambda x: x["abstencion"], [x for x in res if x["tipo"] in ("sustentada", "contradiccion")]),
        "cobertura_citas_emitidas": frac(lambda x: bool(x["citas"]) and set(x["citas"]) <= valid, emitted),
        "latencia_ms": {"mediana": round(statistics.median(lat), 1) if lat else None,
                        "p95": lat_sorted[max(0, int(round(0.95 * len(lat_sorted))) - 1)] if lat else None},
        "fallos": fallos, "resultados": res,
    }


def evaluate_labels(snap: dict, labels: Path) -> dict:
    """Clasificación (macro-F1) IA vs baseline, y agrupación (precisión/recall por pares)."""
    with labels.open(encoding="utf-8") as f:
        gold = {r["id_noticia"]: r for r in csv.DictReader(f)}
    ns = [n for n in snap["noticias"] if n["id_noticia"] in gold]
    y = [gold[n["id_noticia"]]["tema_humano"] for n in ns]
    sem = [n["tema_semantico"] for n in ns]
    kw = [n["tema_reglas"] for n in ns]
    cl = {nid: f["id_caso"] for f in snap["fichas"] for nid in f["ids_fuente"]}
    pairs = list(combinations([n["id_noticia"] for n in ns], 2))
    same_gold = {p for p in pairs if gold[p[0]]["evento_humano"] == gold[p[1]]["evento_humano"]}
    same_pred = {p for p in pairs if cl.get(p[0]) == cl.get(p[1])}
    tp = len(same_gold & same_pred)
    # baseline de agrupación: mismo tema por reglas y mismo día
    day = {n["id_noticia"]: (n["tema_reglas"], (n["fecha_publicacion"] or n["fecha_deteccion"] or "")[:10]) for n in ns}
    same_base = {p for p in pairs if day[p[0]] == day[p[1]]}
    tpb = len(same_gold & same_base)
    return {
        "n_etiquetas": len(ns), "metodo_etiquetado": "ver data/*/etiquetas.csv (reemplazar por revisión humana)",
        "clasificacion_macro_f1": {"ia_semantica": round(f1_score(y, sem, average="macro", zero_division=0), 3),
                                   "baseline_palabras_clave": round(f1_score(y, kw, average="macro", zero_division=0), 3)},
        "errores_clasificacion": [{"id": n["id_noticia"], "humano": t, "ia": s, "reglas": k}
                                  for n, t, s, k in zip(ns, y, sem, kw) if s != t or k != t],
        "agrupacion_pares": {"precision": round(tp / len(same_pred), 3) if same_pred else None,
                             "recall": round(tp / len(same_gold), 3) if same_gold else None,
                             "tp": tp, "pares_predichos": len(same_pred), "pares_humanos": len(same_gold)},
        "agrupacion_baseline_tema_y_dia": {"precision": round(tpb / len(same_base), 3) if same_base else None,
                                           "recall": round(tpb / len(same_gold), 3) if same_gold else None},
        "embedder": snap["meta"]["embedder"],
    }


def to_markdown(b: dict, ev: dict | None = None) -> str:
    def f(m):
        return f"{m['numerador']}/{m['denominador']} ({m['valor']})"
    lines = [f"# Benchmark ({b['split']}) · {config.RULES_VERSION}", "",
             "| Métrica | Resultado |", "|---|---|",
             f"| Aciertos | {f(b['aciertos'])} |",
             f"| Abstención correcta (sin respuesta) | {f(b['abstencion_correcta_sin_respuesta'])} |",
             f"| Rechazo adversarial | {f(b['rechazo_adversarial'])} |",
             f"| Abstención incorrecta en respondibles | {f(b['abstencion_incorrecta_respondibles'])} |",
             f"| Cobertura de citas (respuestas emitidas) | {f(b['cobertura_citas_emitidas'])} |",
             f"| Latencia mediana / p95 (ms) | {b['latencia_ms']['mediana']} / {b['latencia_ms']['p95']} |", ""]
    if b["fallos"]:
        lines += ["## Fallos", "", "| ID | Tipo | Motivo |", "|---|---|---|"]
        lines += [f"| {x['id']} | {x['tipo']} | {x['motivo']} |" for x in b["fallos"]]
    if ev:
        c = ev["clasificacion_macro_f1"]
        g = ev["agrupacion_pares"]
        lines += ["", "## IA vs baseline", "",
                  f"Etiquetas: {ev['n_etiquetas']} · embedder: {ev['embedder']}", "",
                  "| Tarea | IA | Baseline |", "|---|---|---|",
                  f"| Clasificación temática (macro-F1) | {c['ia_semantica']} | {c['baseline_palabras_clave']} |",
                  f"| Agrupación (precisión / recall por pares) | {g['precision']} / {g['recall']} | "
                  f"{ev['agrupacion_baseline_tema_y_dia']['precision']} / {ev['agrupacion_baseline_tema_y_dia']['recall']} |"]
    return "\n".join(lines) + "\n"
