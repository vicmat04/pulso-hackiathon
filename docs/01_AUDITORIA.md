# 01 · Auditoría: idea PULSO + mockup frente a las bases del reto TVN

Fuentes auditadas: `mockup_original.html`, «De la señal a la decisión» (bases, 12 páginas) y
«Posteo en redes sociales».

## 1. Veredicto

**La idea encaja con el reto casi palabra por palabra**: bandeja priorizada, fichas de evidencia,
"varios medios pueden repetir una misma fuente", contradicciones, revisión humana. El mockup
acierta en el concepto pero **incumple requisitos concretos de las bases** que dan puntos o que
condicionan la admisión. La versión 0.2 del kit corrige todo lo que es código; lo que queda
depende de ustedes (Notion, etiquetas humanas, paquete oficial).

## 2. Lo que el mockup tenía y las bases piden (conservar)

| Mockup | Bases |
|---|---|
| "Historias que merecen revisión" ordenadas | Bandeja priorizada (etapa 4), CU-01 |
| "7 publicaciones, 1 procedencia" | CU-03: una agencia replicada cuenta como una procedencia |
| "Contradicción" | T05, CU-04 |
| "Dato requiere contexto con serie oficial" | CU-02, T04 |
| "Misión periodística" | Ficha: qué falta comprobar y acción recomendada (etapa 5) |
| "Abogado del Diablo", "NO aprobar" | Anti-alucinación, estado de evidencia, control humano |
| "Revisión humana" | Estados obligatorios (sección 8) |
| "100% offline para demo" | T10, demo sin fuente en vivo (sección 10) |

## 3. Brechas críticas (corregidas en el código v0.2)

| # | Brecha | Por qué importa | Corrección |
|---|---|---|---|
| 1 | Fórmula propia del Score | Las bases fijan P = 30R+25I+20U+15N+10E, bandas y desempate | `pulso/score.py`, versión `reglas-v1.0`, justificación por componente |
| 2 | Evidencia mezclada en el puntaje | Bases: "estado de evidencia independiente del puntaje" | `estado_evidencia` aparte: insuficiente / parcial / suficiente para el borrador |
| 3 | Lema "PULSO no redacta" | Bases exigen brief ≤250, guion 45–60 s, copy ≤80, con citas | `pulso/draft.py`: hechos, declaraciones, inferencias e hipótesis marcadas |
| 4 | Sin contrato de datos | noticias.csv, indicadores.csv, eventos.geojson, fichas.jsonl, manifest.json | `pulso/models.py`, `load.py`, `manifest.py` |
| 5 | Sin reporte de calidad | Etapa 1 y T01 | `pulso calidad`, panel en la interfaz |
| 6 | Estados de revisión inventados | Bases: nuevo, en revisión, requiere evidencia, aprobado como borrador, descartado | `pulso/review.py`; bloquea aprobar con evidencia insuficiente |
| 7 | Sin baseline | "Comparar al menos una tarea con un baseline simple" | `pulso bench`: macro-F1 IA vs palabras clave; agrupación IA vs tema+día |
| 8 | Chat por IF/ELSE | "Un conjunto de IF/ELSE no basta como uso de IA" | Recuperación semántica, clasificación por similitud y agrupación aglomerativa |
| 9 | Sin anti-inyección | T07 | `pulso/guard.py`; fuente marcada como no confiable y excluida del borrador |
| 10 | Mapa con "TVN replica" | Delicado con el patrocinador | Procedencias genéricas; decisión pendiente en `DECISIONES.md` |
| 11 | Lluvias como "anomalía" con USGS | Bases: USGS nunca respalda inundaciones ni pérdidas | Contexto sísmico solo para noticias sísmicas (test incluido) |
| 12 | Hora sin zona | Bases: UTC en datos, hora de Panamá en interfaz | `text.hora_panama`, `Intl` con `America/Panama` |
| 13 | Solo titulares tratados como texto completo | "basado únicamente en titular/metadatos" | Aviso automático en ficha y borrador |

## 4. Lo que el código NO puede resolver (depende del equipo)

- **Notion** es condición de admisión: 8 páginas, ≥8 tareas, ≥3 decisiones, ≥5 fichas (una
  insuficiente), matriz T01–T10, pitch de 10 minutos navegable. Ver `07_NOTION.md`.
- **Registro durante la ejecución**, no al final: el jurado pedirá "una prueba fallida y su
  corrección". Anoten fallos reales a medida que ocurran.
- **Etiquetas humanas** para macro-F1 y Precision@5: las de `data/sample/etiquetas.csv` son de
  ejemplo. Con el paquete oficial hay que etiquetar (≥50 noticias recomendado) y declarar método.
- **Persona editorial** para Precision@5; si no hay, declarar la evaluación "exploratoria".

## 5. Inconsistencias en las propias bases (preguntar a la organización)

Ver `09_PREGUNTAS_ORGANIZACION.md`. Las tres importantes:
1. Noticias de "los 30 días previos a la extracción" vs "excluir registros fuera de
   [2024-01-01, 2025-10-01)". Si se extrae en 2026, todo queda fuera.
2. Banco Mundial: 6 países × 6 indicadores × 15 años = **540** combinaciones, no 1.350.
3. USGS solo 2024 frente a noticias recientes: el cruce sismo↔noticia puede quedar vacío.

## 6. Resultado medido del kit (set sintético, no es el resultado final)

`make demo` sobre 22 filas sintéticas (18 válidas, 4 rechazadas a propósito):
T01–T10 pasan; benchmark dev 14/14; abstención 4/4; adversarial 2/2; cobertura de citas 8/8.
**IA vs baseline:** en este set pequeño las reglas de palabras clave igualan o superan a TF-IDF
(macro-F1 0,94 vs 1,00) y TF-IDF no une el titular en inglés con el evento en español. Es una
**limitación medida** útil para el pitch y el argumento para activar embeddings multilingües
(`PULSO_EMBED=st`) y medir de nuevo con el paquete oficial.
