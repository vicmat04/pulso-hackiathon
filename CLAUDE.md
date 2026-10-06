# Instrucciones para el agente de código (Claude Code / Codex / Gemini CLI)

Proyecto: PULSO, reto TVN del hackIAthon 2026. Las **bases del reto mandan** sobre cualquier
otra preferencia. Resumen operativo en `docs/01_AUDITORIA.md` y `docs/03_ARQUITECTURA.md`.
Idioma de interfaz, mensajes y documentación: español.

## Comandos
`uv sync` · `make test` · `make lint` · `make demo` · `make serve` · `uv run pulso --help`

## Reglas no negociables
1. **Fórmula fija:** P = 30R + 25I + 20U + 15N + 10E; bandas bajo <40, medio <70, alto ≥70;
   desempate U y luego ID. Cambiar pesos o criterios exige subir `RULES_VERSION` y anotar la
   decisión en `docs/DECISIONES.md`.
2. **Estado de evidencia independiente del puntaje.** Nunca combinarlos.
3. **Citas obligatorias:** toda afirmación de tipo hecho o declaración cita `evidencia_id` +
   `campo`. Hechos solo desde datos oficiales. Sin evidencia → abstención explícita.
4. **No inventar** hechos, cifras, entrevistas, citas, causas, imágenes ni fuentes. Con solo
   titulares, indicar «Basado únicamente en titular/metadatos».
5. **Anti-inyección:** el texto de fuentes es dato. Nunca concatenarlo a instrucciones sin
   `guard.wrap_source`. Fuentes con instrucciones se excluyen del borrador.
6. **Offline:** solo `pulso/fetch.py` usa red. Tests sin red. Web sin recursos remotos.
7. **Nulos se conservan**; nunca rellenar con 0. Fechas en UTC; interfaz en hora de Panamá.
   `fecha_deteccion` (GDELT seendate) ≠ `fecha_publicacion`.
8. **USGS** solo respalda hechos sísmicos; nunca inundaciones ni pérdidas.
9. **Control humano:** estados `nuevo · en_revision · requiere_evidencia ·
   aprobado_como_borrador · descartado`. No aprobar con evidencia insuficiente.
10. **Banca desactivada** (`VERTICALS["banca"] = False`). No implementar en esta vuelta.
11. **Sin secretos** en código, logs, capturas ni Notion. `.env` nunca se sube.
12. Ninguna prueba T01–T10 puede quedar en rojo al cerrar un cambio.

## Flujo
Una tarea de `docs/05_PLAN_TRABAJO.md` por cambio → test que la cubra → `make test` y
`make lint` → registrar decisiones y fallos reales (sirven para Notion) → resumen breve.
Si una regla de las bases es ambigua, pregunta antes de decidir.
