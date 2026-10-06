# 04 · Funcionamiento sin internet (T10)

## Qué piden las bases
- "Para el MVP basta una carga por lote; no se exige monitoreo continuo **ni acceso a internet
  durante el pitch**."
- T10: "Funcionar con snapshot y **fallback documentado**; dejar evidencia en Notion."
- Entregable: "demo reproducible **sin depender de una fuente en vivo**."

Conclusión: offline no es opcional para la demo. Lo que no se pide es extraer datos sin red.

## Qué funciona sin red en PULSO

| Pieza | Sin red | Cómo |
|---|---|---|
| Carga, validación, manifest | ✔ | Paquete congelado en disco |
| Clasificación, agrupación, procedencias | ✔ | TF-IDF (scikit-learn), sin descargas |
| Embeddings multilingües | ✔ si se descargan antes | `make models` con red; luego `HF_HUB_OFFLINE=1` |
| Puntaje, fichas, borradores por plantilla | ✔ | Determinista |
| Consultas | ✔ | `pulso serve` (motor completo) o archivo con respuestas precalculadas |
| LLM local (Ollama) | ✔ | Modelo descargado y precalentado |
| LLM por API | ✖ | **Fallback automático a plantilla**, indicado en la interfaz |
| Extracción (`pulso fetch`) | ✖ | Solo antes del evento |
| **Notion** | ⚠ | Ver abajo: es el punto débil real |

T10 está automatizado: `pulso aceptacion` bloquea los sockets, reconstruye todo y consulta.

## El riesgo real: el pitch es desde Notion
El pitch debe presentarse **desde Notion**, que es un servicio en línea. Plan:
1. Confirmar con la organización conectividad en la sala (las bases dicen que tendrán
   "conectividad y fallback local").
2. Abrir las páginas del pitch antes de empezar y no recargarlas. Si la versión de la app de
   escritorio de Notion permite marcar páginas para uso sin conexión, hacerlo y probarlo.
3. La demo del prototipo **no** se incrusta como embed de `localhost` (el jurado no podrá
   abrirla): en Notion va el enlace a GitHub, capturas y un video corto del recorrido.
4. PDF de respaldo exportado de Notion (permitido como respaldo, nunca como sustituto).

## Fallbacks documentados (copiar a Notion · Pruebas y métricas, T10)

| Falla | Fallback | Cómo se nota en pantalla |
|---|---|---|
| Sin red | Snapshot local | "Snapshot local · funciona sin internet" |
| Servidor no arranca | Abrir `web/index.html` con doble clic | "modo archivo: respuestas precalculadas y reglas" |
| LLM caído o sin red | Plantilla determinista | "generado por plantilla" |
| Modelo de embeddings ausente | `PULSO_EMBED=tfidf` | Nombre del embedder en la barra lateral |
| Portátil falla | Copia del repo + `out/` en USB y segundo equipo con `uv` | — |

## Ensayo de víspera
1. Con red: `uv sync`, `make models` (si usan `st`), `make demo`, `make test`.
2. Apagar wifi. `make serve`. Recorrer el guion de `02_PRODUCTO.md` cronometrado.
3. Cerrar servidor, abrir `web/index.html` con doble clic; repetir las consultas sugeridas.
4. Guardar captura de ambos modos como evidencia de T10 en Notion.
