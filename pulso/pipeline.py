"""Orquestación de las etapas 1–6 (bases, sección 3). Salidas en out/:
snapshot.json (para web y chat), fichas.jsonl (contrato), calidad.json (reporte de carga)."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from . import config, context, draft, review, score
from .embed import Embedder
from .guard import is_injection
from .load import Corpus, load_corpus, quality_report
from .models import Afirmacion, Cita, Componentes, Ficha, Noticia
from .organize import classify_keywords, classify_semantic, cluster, doc_text
from .provenance import provenances
from .text import hora_panama, iso, norm, parse_dt, quantities


def _corte(c: Corpus) -> datetime:
    if c.fecha_corte:
        return parse_dt(c.fecha_corte)
    ds = [parse_dt(n.fecha_extraccion) for n in c.noticias]
    return max(d for d in ds if d) if any(ds) else datetime.now(timezone.utc)


def _contradictions(items: list[Noticia], proc_of: dict[str, str]) -> list[dict]:
    out, seen = [], set()
    for a in items:
        for b in items:
            if a.id_noticia >= b.id_noticia or proc_of[a.id_noticia] == proc_of[b.id_noticia]:
                continue
            for va, ua in quantities(a.titulo):
                for vb, ub in quantities(b.titulo):
                    if ua == ub and max(va, vb) > 0 and abs(va - vb) / max(va, vb) > 0.10:
                        k = (a.id_noticia, b.id_noticia, ua)
                        if k not in seen:
                            seen.add(k)
                            out.append({"a_id": a.id_noticia, "a_medio": a.medio, "a_valor": va,
                                        "b_id": b.id_noticia, "b_medio": b.medio, "b_valor": vb,
                                        "unidad": ua})
    return out


def _evidence_state(indep: int, has_ctx: bool, contra: bool, usable: int) -> str:
    if usable == 0:
        return "insuficiente"
    if contra:
        return "parcial"
    if indep >= 2:
        return "suficiente_para_borrador"
    return "parcial" if has_ctx else "insuficiente"


def build(data_dir: Path | None = None) -> dict:
    c = load_corpus(data_dir)
    corte = _corte(c)
    ns = c.noticias
    emb = Embedder([doc_text(n) for n in ns] + list(config.TOPIC_PROTOTYPES.values()))
    sem = classify_semantic([doc_text(n) for n in ns], emb)
    kw = [classify_keywords(doc_text(n)) for n in ns]
    tema_of = {n.id_noticia: (s if s != "otros" else k) for n, s, k in zip(ns, sem, kw)}
    inj = {n.id_noticia for n in ns if is_injection(n.titulo) or is_injection(n.descripcion)}
    reviews = review.latest()
    fichas: list[Ficha] = []

    for group in cluster(ns, emb):
        items = [ns[i] for i in group]
        items.sort(key=lambda n: (n.fecha_publicacion or n.fecha_deteccion or "9999", n.id_noticia))
        usable = [n for n in items if n.id_noticia not in inj]
        procs = provenances(usable, emb) if usable else {}
        proc_of = {nid: p for p, ids in procs.items() for nid in ids}
        tema = Counter(tema_of[n.id_noticia] for n in (usable or items)).most_common(1)[0][0]
        text = " ".join(doc_text(n) for n in usable)

        pubs = [parse_dt(n.fecha_publicacion) for n in items if n.fecha_publicacion]
        dets = [parse_dt(n.fecha_deteccion) for n in items if n.fecha_deteccion]
        f_orig = min(pubs) if pubs else (min(dets) if dets else None)
        f_last = max(pubs + dets) if (pubs or dets) else None
        recirc = None
        for n in items:
            p, d = parse_dt(n.fecha_publicacion), parse_dt(n.fecha_deteccion)
            if p and d and (d - p).days > config.RECIRCULATION_DAYS:
                recirc = hora_panama(n.fecha_publicacion)

        ctx = context.indicators_for(text, c.indicadores) if tema == "economia" else []
        for n in usable:
            ctx += [s for s in context.seismic_for(n, c.sismos)
                    if s["evidencia_id"] not in {x.get("evidencia_id") for x in ctx}]
        has_ctx = any(x.get("evidencia_id") for x in ctx)
        contra = _contradictions(usable, proc_of)
        indep = len(procs)

        alertas = []
        if inj & {n.id_noticia for n in items}:
            alertas.append("Contenido no confiable: una fuente contiene instrucciones; se trata como dato y se excluye del borrador.")
        if recirc:
            alertas.append(f"Noticia recirculada: fecha original {recirc}.")
        if usable and all(n.alcance_texto == "titular" for n in usable):
            alertas.append("Basado únicamente en titular/metadatos.")
        if any(n.fecha_publicacion is None for n in items):
            alertas.append("Alguna fuente sin fecha de publicación (GDELT indica detección, no publicación).")

        falta = []
        if indep < 2 and usable:
            falta.append("Conseguir una segunda fuente independiente.")
        for p in procs:
            if p.startswith("agencia:") and len(procs[p]) > 1:
                falta.append(f"Confirmar con la fuente original ({p.split(':', 1)[1]}); {len(procs[p])} medios la replican.")
        for x in contra:
            falta.append(f"Resolver versiones: {x['a_medio']} ({draft.fmt(x['a_valor'])}) vs {x['b_medio']} ({draft.fmt(x['b_valor'])}) {x['unidad']}.")
        if tema == "economia":
            falta.append("Buscar el dato oficial más reciente (INEC); el Banco Mundial es anual."
                         if has_ctx else "No hay serie oficial relacionada en el corpus.")
        if tema in ("eventos_naturales", "servicios_publicos", "regulacion", "logistica_canal") and not has_ctx:
            falta.append("Confirmar con la institución oficial responsable (no hay dato oficial en el corpus).")
        if recirc:
            falta.append("No presentarla como evento nuevo; confirmar si hay hechos recientes.")
        if any(n.alcance_texto == "titular" for n in usable):
            falta.append("Leer el artículo completo en la fuente: solo hay titular/metadatos.")

        estado = _evidence_state(indep, has_ctx, bool(contra), len(usable))
        menciona = any(p in norm(text) for p in config.PANAMA_PLACES) or any(n.origen == "tvn_rss" for n in usable)
        r, rj = score.r_relevancia(menciona, tema)
        i_, ij = score.i_impacto(tema, has_ctx)
        u, uj = score.u_urgencia(f_orig, corte)
        nn, nj = score.n_novedad(bool(recirc), f_orig, corte)
        e, ej = score.e_evidencia(indep, has_ctx)
        comp = Componentes(R=r, I=i_, U=u, N=nn, E=e, justificacion={"R": rj, "I": ij, "U": uj, "N": nj, "E": ej})
        p = score.total(comp)

        afirm = [Afirmacion(texto=f"Según {n.medio}: «{n.titulo}».", tipo="declaracion",
                            citas=[Cita(evidencia_id=n.id_noticia, campo="titulo")]) for n in usable]
        afirm += [Afirmacion(texto=f"{x['indicador']} {x['pais']} {x['anio']}: {x['valor']} ({x['unidad']})",
                             tipo="hecho", citas=[Cita(evidencia_id=x["evidencia_id"], campo="valor")])
                  for x in ctx if x["tipo"] == "indicador" and x.get("evidencia_id")]
        afirm += [Afirmacion(texto=f"Sismo M{x['magnitud']} · {x['lugar']}", tipo="hecho",
                             citas=[Cita(evidencia_id=x["evidencia_id"], campo="magnitude")])
                  for x in ctx if x["tipo"] == "sismo"]
        respaldado = [a for a in afirm if a.tipo == "hecho"] or (
            [a for a in afirm] if indep >= 2 and not contra else [])

        if not usable:
            accion = "Revisar manualmente y descartar: la fuente contiene instrucciones, no información."
        elif estado == "insuficiente":
            accion = "Investigar antes de producir: la evidencia es insuficiente para un borrador."
        elif contra:
            accion = "Mostrar ambas versiones y su alcance; no escoger una sin fuente primaria."
        elif estado == "parcial":
            accion = "Completar verificaciones pendientes antes de aprobar el borrador."
        else:
            accion = "Revisar el borrador; aprobarlo como borrador no significa publicar."

        borr = None
        if usable and estado != "insuficiente":
            borr = draft.build(tema, usable, procs, ctx, contra,
                               recirc, falta)

        cid = "CASO-" + hashlib.sha1("|".join(sorted(n.id_noticia for n in items)).encode()).hexdigest()[:8]
        rv = reviews.get(cid, {})
        fichas.append(Ficha(
            id_caso=cid, modalidad=config.MODALIDAD, titulo=(usable or items)[0].titulo, tema=tema,
            ids_fuente=[n.id_noticia for n in items], procedencias=procs, fuentes_independientes=indep,
            que_se_reporta=(usable or items)[0].titulo, quien_lo_reporta=sorted({n.medio for n in usable}),
            respaldado=respaldado, falta_comprobar=falta, accion_recomendada=accion,
            contexto_oficial=ctx, contradicciones=contra, alertas=alertas, afirmaciones=afirm,
            citas=[ci for a in afirm for ci in a.citas], puntaje=p, banda=score.band(p),
            componentes=comp, version_reglas=config.RULES_VERSION, estado_evidencia=estado,
            borrador=borr, estado_revision=rv.get("estado", "nuevo"), revisor=rv.get("revisor"),
            fecha_primera=iso(f_orig), fecha_ultima=iso(f_last)))

    fichas.sort(key=score.sort_key)
    return {
        "meta": {"version_reglas": config.RULES_VERSION, "pesos": config.WEIGHTS,
                 "fecha_corte_UTC": iso(corte), "embedder": emb.name, "modalidad": config.MODALIDAD,
                 "generado_UTC": iso(datetime.now(timezone.utc)),
                 "sintetico": any(n.origen == "sintetico" for n in ns),
                 "noticias_validas": len(ns), "eventos": len(fichas),
                 "indicadores": len(c.indicadores), "sismos": len(c.sismos),
                 "sugeridas": config.SUGGESTED},
        "calidad": quality_report(c),
        "fichas": [json.loads(f.model_dump_json()) for f in fichas],
        "noticias": [json.loads(n.model_dump_json()) | {"tema_semantico": s, "tema_reglas": k}
                     for n, s, k in zip(ns, sem, kw)],
        "indicadores": [json.loads(i.model_dump_json()) for i in c.indicadores],
    }


def write_outputs(snap: dict, out: Path | None = None) -> Path:
    out = Path(out or config.OUT_DIR)
    out.mkdir(parents=True, exist_ok=True)
    (out / "snapshot.json").write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "calidad.json").write_text(json.dumps(snap["calidad"], ensure_ascii=False, indent=1), encoding="utf-8")
    with (out / "fichas.jsonl").open("w", encoding="utf-8") as f:
        for fi in snap["fichas"]:
            f.write(json.dumps(fi, ensure_ascii=False) + "\n")
    # respuestas precalculadas para la interfaz abierta como archivo (sin servidor)
    from .ask import ask
    qs = list(config.SUGGESTED)
    bench = config.ROOT / "data" / "benchmark" / "benchmark_dev.jsonl"
    if bench.exists():
        qs += [json.loads(x)["consulta"] for x in bench.read_text(encoding="utf-8").splitlines() if x.strip()]
    snap = {**snap, "respuestas": {norm(q): ask(q, snap) for q in dict.fromkeys(qs)}}
    web = config.ROOT / "web" / "snapshot.js"
    web.write_text("// Generado por `pulso build`. No editar.\nwindow.PULSO_SNAPSHOT = "
                   + json.dumps(snap, ensure_ascii=False) + ";\n", encoding="utf-8")
    return out
