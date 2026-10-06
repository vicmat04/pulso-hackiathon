"""Etapa 6 · Producir: paquete editorial TVN con citas por afirmación.

Generador por plantilla (determinista, offline, sin inventar). Un LLM puede reescribir el estilo
(llm.py) pero su salida se valida: toda afirmación debe citar evidencia existente.
Hechos = datos oficiales. Lo publicado por medios = declaraciones atribuidas.
Inferencias e hipótesis = marcadas como tales."""
from __future__ import annotations

from . import config
from .models import Afirmacion, Borrador, Cita, Noticia
from .text import hora_panama, words

ENFOQUE = {
    "economia": "Cómo afecta a los hogares y si el dato se compara con la serie oficial correcta.",
    "logistica_canal": "Efecto en el comercio y el empleo ligado al Canal y los puertos.",
    "turismo": "Qué tan sólida es la cifra y quién la respalda más allá del emisor.",
    "servicios_publicos": "Cuántas personas están afectadas y qué responde la institución responsable.",
    "eventos_naturales": "Seguridad de la población y qué confirman las fuentes oficiales.",
    "regulacion": "Qué cambia para ciudadanos y empresas y si la medida existe en documento oficial.",
    "otros": "Por qué importa a la audiencia panameña.",
}
PREGUNTAS = {
    "economia": ["¿Qué fuente y período usa la cifra publicada?",
                 "¿Cómo se compara con la serie oficial más reciente?",
                 "¿Qué grupos o sectores explican el cambio?"],
    "logistica_canal": ["¿Qué dice la autoridad responsable con datos de tránsito?",
                        "¿Desde cuándo ocurre y cuánto se espera que dure?",
                        "¿Qué sectores o empresas están afectados?"],
    "turismo": ["¿Hay una fuente independiente del emisor que confirme la cifra?",
                "¿Con qué período se compara el 'récord'?",
                "¿Qué dice la autoridad de turismo?"],
    "servicios_publicos": ["¿Cuántos usuarios están afectados según la institución?",
                           "¿Cuál es la causa confirmada?",
                           "¿Cuándo se restablece el servicio?"],
    "eventos_naturales": ["¿Qué confirma el registro oficial del evento?",
                          "¿Hay reportes oficiales de afectaciones?",
                          "¿Qué recomiendan las autoridades?"],
    "regulacion": ["¿Existe el documento oficial (Gaceta, resolución) que lo respalde?",
                   "¿Desde cuándo aplicaría y a quién?",
                   "¿Qué dicen los sectores afectados?"],
    "otros": ["¿Quién es la fuente primaria?", "¿Qué falta confirmar?", "¿Por qué importa ahora?"],
}


def fmt(v: float) -> str:
    s = f"{v:,.1f}" if abs(v) < 1000 else f"{v:,.0f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def _cut(text: str, max_words: int) -> str:
    w = text.split()
    return text if len(w) <= max_words else " ".join(w[:max_words]).rstrip(",;:") + "…"


def build(tema: str, noticias: list[Noticia], procedencias: dict[str, list[str]],
          contexto: list[dict], contradicciones: list[dict], recirculada: str | None,
          faltantes: list[str]) -> Borrador:
    by_id = {n.id_noticia: n for n in noticias}
    brief: list[Afirmacion] = []
    for proc, ids in procedencias.items():
        rep = by_id[ids[0]]
        medios = sorted({by_id[i].medio for i in ids})
        quien = medios[0] if len(medios) == 1 else f"{len(medios)} medios ({', '.join(medios[:3])}{'…' if len(medios) > 3 else ''})"
        brief.append(Afirmacion(texto=f"Según {quien}: «{rep.titulo}».", tipo="declaracion",
                                citas=[Cita(evidencia_id=i, campo="titulo") for i in ids]))
    total = sum(len(v) for v in procedencias.values())
    if total > len(procedencias):
        brief.append(Afirmacion(
            texto=f"Las {total} publicaciones provienen de {len(procedencias)} procedencia(s); "
                  "la repetición no equivale a corroboración.", tipo="inferencia",
            citas=[Cita(evidencia_id=i, campo="medio") for v in procedencias.values() for i in v]))
    for c in contradicciones:
        brief.append(Afirmacion(
            texto=f"Las versiones no coinciden: {c['a_medio']} reporta {fmt(c['a_valor'])} {c['unidad']} "
                  f"y {c['b_medio']} {fmt(c['b_valor'])} {c['unidad']}. Revisión pendiente.",
            tipo="declaracion", citas=[Cita(evidencia_id=c["a_id"], campo="titulo"),
                                       Cita(evidencia_id=c["b_id"], campo="titulo")]))
    for ctx in contexto:
        if ctx["tipo"] == "indicador" and ctx.get("evidencia_id"):
            brief.append(Afirmacion(
                texto=f"Dato oficial: {ctx['indicador']} de {config.COUNTRIES.get(ctx['pais'], ctx['pais'])} "
                      f"fue {fmt(ctx['valor'])} ({ctx['unidad']}) en {ctx['anio']}, según el Banco Mundial. "
                      "Es un dato anual, no una medición de hoy.", tipo="hecho",
                citas=[Cita(evidencia_id=ctx["evidencia_id"], campo="valor")]))
        elif ctx["tipo"] == "sismo":
            brief.append(Afirmacion(
                texto=f"Dato oficial: el catálogo del USGS registra un sismo de magnitud {fmt(ctx['magnitud'])} "
                      f"el {hora_panama(ctx['fecha'])} (hora de Panamá), {ctx['lugar']}.", tipo="hecho",
                citas=[Cita(evidencia_id=ctx["evidencia_id"], campo="magnitude")]))
    if recirculada:
        brief.append(Afirmacion(texto=f"La publicación original es del {recirculada}; no es un evento nuevo.",
                                tipo="inferencia", citas=[Cita(evidencia_id=noticias[0].id_noticia,
                                                               campo="fecha_publicacion")]))
    brief.append(Afirmacion(texto="Hipótesis a verificar: " + ENFOQUE.get(tema, ENFOQUE["otros"]).lower(),
                            tipo="hipotesis", citas=[]))
    # recorte a 250 palabras conservando orden
    acc, kept = 0, []
    for a in brief:
        if acc + words(a.texto) > 250:
            break
        kept.append(a)
        acc += words(a.texto)

    rep = noticias[0]
    hechos = [a for a in kept if a.tipo == "hecho"]
    decl = [a for a in kept if a.tipo == "declaracion"]
    guion = [Afirmacion(texto=f"Presentador: {config.TOPIC_LABEL[tema]}. Esto es lo que se ha publicado y lo que aún no está confirmado.",
                        tipo="inferencia", citas=[])]
    guion += decl[:3] + hechos[:1]
    guion.append(Afirmacion(texto=f"Hasta ahora lo reportan {len(procedencias)} procedencia(s) independiente(s), "
                                  f"a partir de {total} publicación(es).", tipo="inferencia",
                            citas=[Cita(evidencia_id=i, campo="medio") for v in procedencias.values() for i in v]))
    guion.append(Afirmacion(texto=f"La pregunta que debemos responder: {PREGUNTAS.get(tema, PREGUNTAS['otros'])[0]}",
                            tipo="hipotesis", citas=[]))
    guion.append(Afirmacion(texto="Pendiente de verificar: " + "; ".join(f.rstrip(".") for f in faltantes[:2]) + ".",
                            tipo="inferencia", citas=[]))
    guion.append(Afirmacion(texto="Cierre: ampliaremos cuando haya confirmación de fuentes oficiales.",
                            tipo="inferencia", citas=[]))
    segs = round(sum(words(a.texto) for a in guion) / 2.5)  # ~150 palabras/minuto

    copy = _cut(f"{rep.titulo}. Lo que sabemos: {len(procedencias)} procedencia(s) "
                f"{'y un dato oficial relacionado' if hechos else 'y ningún dato oficial relacionado'}. "
                f"Falta verificar: {faltantes[0].rstrip('.').lower() if faltantes else 'nada pendiente'}.", 80)
    solo_titular = all(n.alcance_texto == "titular" for n in noticias)
    return Borrador(
        titulo_propuesto=f"{config.TOPIC_LABEL[tema]}: {_cut(rep.titulo, 12)}",
        enfoque_interes_publico=ENFOQUE.get(tema, ENFOQUE["otros"]),
        brief=kept, preguntas=PREGUNTAS.get(tema, PREGUNTAS["otros"])[:3],
        fuentes=[f"{n.id_noticia} · {n.medio} · {n.url}" for n in noticias]
                + [f"{c['evidencia_id']} · {c.get('fuente_url') or c.get('url')}" for c in contexto if c.get("evidencia_id")],
        verificaciones_pendientes=faltantes, guion=guion, guion_segundos_estimados=segs,
        copy_digital=copy,
        aviso_alcance="Basado únicamente en titular/metadatos." if solo_titular else None,
    )
