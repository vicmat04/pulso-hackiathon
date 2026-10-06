# 03 · Arquitectura, IA y controles

Sigue la arquitectura mínima de las bases (sección 8), en carga por lote:

```
paquete congelado (data/<paquete>/)
  noticias.csv · indicadores.csv · eventos.geojson · manifest.json
        │  1 Cargar ── load.py ── reporte de calidad (errores separados, nulos conservados)
        ▼
  Noticia / Indicador / Sismo (Pydantic, UTC)
        │  2 Organizar ── organize.py (tema semántico + baseline reglas; agrupación aglomerativa)
        │                provenance.py (agencia / casi-copia / medio → procedencias)
        │  3 Contextualizar ── context.py (Banco Mundial por tema; USGS solo sismos)
        │  4 Priorizar ── score.py (30R+25I+20U+15N+10E, banda, desempate)  ┐ independientes
        │  5 Explicar ── pipeline.py (ficha, faltantes, acción, estado de evidencia) ┘
        │  6 Producir ── draft.py (plantilla con citas) ± llm.py (reescritura validada)
        ▼
  out/snapshot.json · out/fichas.jsonl · out/calidad.json · web/snapshot.js
        │
        ├── web/index.html (abre con doble clic; o `pulso serve` con /api/ask)
        ├── pulso ask (consultas con citas o abstención) ── guard.py (anti-inyección)
        │  7 Revisar ── review.py (estados, persona responsable, registro JSONL)
        └── notion.py → out/notion/*.csv|md → importar en Notion
```

## Herramientas

| Capa | Herramienta | Uso | Offline |
|---|---|---|---|
| Entorno | Python 3.11+, `uv` | Dependencias fijadas, `uv.lock` | ✔ |
| CLI | Typer | `pulso calidad · build · ask · revisar · aceptacion · bench · export-notion · serve` | ✔ |
| Esquemas | Pydantic 2 | Contrato de datos y fichas | ✔ |
| NLP base | scikit-learn (TF-IDF n-gramas de caracteres, `AgglomerativeClustering`) | Similitud, agrupación, recuperación | ✔ sin descargas |
| NLP mejor | sentence-transformers multilingüe (`PULSO_EMBED=st`) | Paráfrasis y cruce español/inglés | ✔ tras `make models` |
| LLM opcional | Ollama local o API de Anthropic | Reescritura del brief, JSON con citas | Ollama ✔ · API ✖ |
| Servidor | `http.server` de la biblioteca estándar | Interfaz + `/api/ask` en localhost | ✔ |
| Interfaz | HTML + CSS + JS sin frameworks | Bandeja, ficha, borrador, revisión, consultas, calidad | ✔ |
| Pruebas | pytest, ruff | 20 pruebas: unidades + T01–T10 | ✔ |
| Documentación | Notion (obligatorio) | Registro y pitch | requiere red (ver 04) |

## Uso sustantivo de IA (y su baseline)

| Tarea | IA | Baseline | Métrica |
|---|---|---|---|
| Clasificación temática | Similitud con prototipos de tema (embeddings) | Palabras clave (`TOPIC_KEYWORDS`) | macro-F1 sobre etiquetas humanas |
| Agrupación de eventos | Aglomerativa por similitud con ventana temporal | Mismo tema por reglas y mismo día | precisión/recall por pares |
| Consultas | Recuperación semántica + umbral de abstención | — | abstención, cobertura de citas, latencia |
| Borrador (opcional) | LLM con salida JSON validada | Plantilla determinista | validez de sustento (revisión humana ≥30 afirmaciones) |

**Cuándo no ayuda:** con titulares cortos y un set pequeño, TF-IDF iguala a las reglas y no cruza
idiomas. Reportarlo tal cual; es lo que pide la rúbrica ("mejora o limitación medida").

## Puntaje de atención (reglas-v1.0)

| Comp. | Peso | Criterio de normalización a 0–1 |
|---|---|---|
| R | 30 | 0,5 si menciona Panamá o un lugar panameño (`PANAMA_PLACES`) o es de TVN + 0,5 si el tema es de la modalidad |
| I | 25 | Base por tema (supuesto editorial en `config.IMPACT_BASE`) + 0,2 si hay dato oficial relacionado |
| U | 20 | Días desde la fecha **original**: ≤1 → 1 · ≤3 → 0,7 · ≤7 → 0,4 · resto → 0,1 |
| N | 15 | Recirculada → 0,1 · evento nuevo ≤7 días → 1 · anterior → 0,5. Duplicados no suman |
| E | 10 | 0,6 × min(procedencias, 3)/3 + 0,4 si hay dato oficial |

Bandas [0,40) bajo · [40,70) medio · [70,100] alto. Desempate: mayor U y luego ID.
Cambiar un peso = nueva versión de reglas + decisión justificada en Notion.

## Estado de evidencia (independiente del puntaje)

| Condición | Estado |
|---|---|
| Solo fuentes no confiables | insuficiente |
| Hay contradicción entre procedencias | parcial (se muestran ambas versiones) |
| ≥2 procedencias independientes | suficiente para el borrador |
| 1 procedencia + dato oficial relacionado | parcial |
| 1 procedencia sin dato oficial | insuficiente (no se genera borrador: abstención) |

## Controles (sección 8)

- **Citas:** cada afirmación de tipo hecho o declaración lleva `evidencia_id` + `campo`.
  Hechos solo desde datos oficiales; lo publicado por medios va atribuido ("Según…").
- **Abstención:** sin coincidencia semántica suficiente, año fuera de serie o valor nulo.
- **Anti-inyección:** `guard.py` detecta instrucciones en fuentes; se marcan y excluyen; en el
  prompt del LLM las fuentes van en `<fuente>` y el prompt prohíbe obedecerlas.
- **Control humano:** transiciones válidas, persona obligatoria, no se aprueba con evidencia
  insuficiente; aprobar como borrador ≠ publicar.
- **Privacidad:** sin datos personales; el servidor no registra consultas.
- **Derechos:** se guardan metadatos (titular, URL, fecha); no cuerpos completos ni imágenes.
- **Secretos:** `.env` fuera del repositorio; test que busca claves en el código.

## Documentar en Notion (Diseño de solución)
Modelo/proveedor y versión, prompts (`prompts/brief_v1.md`), parámetros (temperatura 0,
umbrales de `config.py`), costo medido por consulta (tokens si hay API; 0 en local) y límites.
