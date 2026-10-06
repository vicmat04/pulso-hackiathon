# 07 · Notion: estructura obligatoria y cómo llenarla

Notion es **condición de admisión** y además puntúa 15/100. `make notion` genera en
`out/notion/` archivos importables (Notion → Importar → CSV crea bases de datos; Markdown crea
páginas). La carga manual es válida; la automatización es opcional.

| Página o base (bases §5) | Qué poner | Fuente en el kit |
|---|---|---|
| Inicio del reto | Equipo, modalidad TVN, problema, usuario, alcance, criterios de éxito, enlaces a repo y demo | `02_PRODUCTO.md` |
| Plan y decisiones | Base de datos de tareas (≥8) con responsable, estado, fecha; base de decisiones (≥3) con motivo | `05_PLAN_TRABAJO.md`, `DECISIONES.md` |
| Catálogo de datos | Fuente, URL, fecha de extracción, cobertura, campos, licencia, transformaciones, SHA-256 | `Catalogo_de_datos.csv` (completar URL y cobertura) |
| Diseño de solución | Arquitectura, modelo de datos, reglas, modelos, prompts, versiones, límites | `03_ARQUITECTURA.md`, `prompts/` |
| Casos y evidencias | ≥5 fichas con IDs, fuentes, puntaje desglosado, estado de evidencia, borrador, persona revisora | `Casos_y_evidencias.csv`, `fichas/*.md` |
| Pruebas y métricas | Matriz T01–T10 (caso, entrada, esperado, observado, evidencia, corrección) + métricas | `Pruebas_T01_T10.csv`, `Benchmark.md` |
| Riesgos y ética | Privacidad, derechos, sesgos, ataques al agente, controles, fuera de alcance | sección de abajo |
| Presentación al jurado | Problema → solución → demo → IA y evidencias → resultados → límites → próximos pasos | guion en `02_PRODUCTO.md` |

## Evidencias mínimas para ser admitidos (checklist)
- [ ] URL de Notion accesible al jurado al cierre.
- [ ] ≥8 tareas y ≥3 decisiones justificadas, **con fechas durante el evento**.
- [ ] Catálogo completo de todas las fuentes usadas.
- [ ] ≥5 fichas trazables, al menos una con evidencia insuficiente (el kit genera varias).
- [ ] Matriz con T01–T10 y métricas de la ejecución final.
- [ ] Pitch de 10 min presentado desde Notion, con enlaces a prototipo y GitHub.

## Bitácora (para "muéstrame una prueba fallida y su corrección")
Crear una base "Bitácora" con: fecha y hora, qué se probó, resultado, qué se cambió, commit.
Ejemplo real del desarrollo de este kit, utilizable como primera entrada:
- **Fallo:** las dos notas del agua (30 mil vs 8 mil usuarios) se fusionaban en una sola
  procedencia por titulares casi idénticos, y la contradicción desaparecía.
- **Corrección:** una nota solo se considera copia si el titular es casi idéntico **y** las cifras
  coinciden (`provenance.py`). T05 pasa.

## Riesgos y ética (texto base)
- **Privacidad:** no se almacenan datos personales; no se crean perfiles ni listas de personas.
  Acusaciones se muestran como declaraciones atribuidas.
- **Derechos:** se guardan titulares, URL y fechas; no cuerpos, imágenes ni videos. TVN RSS y GDELT
  no otorgan licencia de republicación.
- **Sesgos:** el impacto base por tema es un supuesto editorial documentado; medios con más
  volumen no suben el puntaje porque los duplicados no suman.
- **Ataques al agente:** contenido de fuentes tratado como dato; detección de instrucciones;
  consultas que piden revelar instrucciones se rechazan (T07, benchmark adversarial).
- **Controles:** estados de revisión, persona responsable, bloqueo de aprobación sin evidencia.
- **Fuera de alcance:** verdad/falsedad, fraude, riesgo de crédito, audiencia, publicación.
- **Secretos:** `.env` excluido; test de secretos; nada de tokens en capturas o Notion.
