# Dashboard funcional basado en el mockup

## Objetivo
Convertir `docs/mockup_original.html` en la referencia visual de la aplicación web, manteniendo toda la funcionalidad real de PULSO: bandeja, ficha trazable, borrador, revisión humana, consultas y calidad de datos.

## Problema
La interfaz actual funciona y cumple los controles del reto, pero su composición visual no refleja el mockup original. Faltan la portada tipo radar, el anillo de puntaje, la misión periodística, el abogado del diablo, los badges semánticos y un mapa de evidencia visual.

## Por qué
El mockup expresa la identidad y el recorrido editorial deseados. El rediseño debe recuperar esa experiencia sin degradar trazabilidad, citas, abstención, separación entre prioridad y evidencia, funcionamiento offline ni control humano.

## Alcance
- Usar el mockup como dashboard principal funcional.
- Conservar las secciones de detalle existentes y hacerlas navegables desde la portada.
- Mostrar el puntaje circular para el caso seleccionado, sin inventar un promedio global.
- Representar procedencias de forma plana, sin afirmar relaciones de copia no demostradas.
- Colorear alertas con categorías derivadas de datos existentes y un fallback neutral.
- Mantener HTML, CSS y JavaScript locales, sin dependencias remotas.

## Restricciones
- Interfaz y mensajes en español.
- El estado de evidencia permanece independiente del puntaje.
- Todas las afirmaciones y procedencias conservan sus citas e identificadores.
- No se inventan relaciones direccionales entre medios o agencias.
- La revisión humana, exportación JSONL y consultas deben seguir funcionando.
- T01–T10 y las 20 pruebas deben permanecer en verde.
- El usuario autorizó explícitamente crear commits y publicar todo el proyecto en `https://github.com/vicmat04/pulso-hackiathon.git`.
- La memoria Engram se conserva en el proveedor de memoria del proyecto; no se publica su contenido interno en GitHub.

## Estrategia de entrega
- Estrategia: `ask-on-risk` para cambios posteriores.
- Pronóstico del rediseño: 300–400 líneas modificadas, excluyendo archivos generados.
- Publicación inicial: importación completa de un repositorio previamente sin commits; por definición excede el presupuesto normal de revisión y se publicará como base inicial porque el usuario pidió subir todo a un remoto vacío.
- Ruta: escritor delegado obligatorio para el rediseño multiarchivo; README e higiene del repositorio forman la unidad de publicación autorizada.
- Excepción TDD: no hay una prueba visual determinista existente con un RED significativo. Se usarán comprobaciones estructurales, pruebas existentes y recorrido funcional con navegador.

## Secuencia de commits revisables
El usuario eligió dividir la importación inicial después de que el candidato completo excediera el presupuesto nativo. Se hará una sola partición honesta, preservando el árbol final:

1. `chore: add project scaffolding` — metadatos, README, configuración y prompts (~373 líneas).
2. `docs: document product architecture and mockup` — auditoría, producto, arquitectura, offline y mockup (~480 líneas).
3. `docs: add delivery and governance guides` — plan, Notion, redes, preguntas y decisiones (~196 líneas).
4. `feat(core): add data contracts and loading` — configuración, modelos, texto y carga (~461 líneas).
5. `feat(core): add analysis and scoring` — contexto, embeddings, procedencias, organización, guardas y puntaje (~285 líneas).
6. `feat(core): add drafting pipeline` — borradores, LLM, manifiesto y pipeline (~435 líneas).
7. `feat(core): add acceptance and querying` — aceptación, consultas, benchmark y revisión (~475 líneas).
8. `feat(cli): add operational adapters` — CLI, fetch, Notion, servidor y verticales (~474 líneas).
9. `test: add synthetic acceptance fixtures` — datos sintéticos y pruebas (~270 líneas).
10. `feat(web): add dashboard structure and styles` — HTML y CSS (~337 líneas).
11. `feat(web): connect dashboard interactions` — JavaScript funcional (~258 líneas).
12. `chore: add development reports and snapshot` — artefactos generados (~406 líneas).
13. `chore: lock dependencies` — `uv.lock` generado (~1880 líneas, sobrepresupuesto inevitable e indivisible).
14. `docs: record implementation evidence` — documento ODD actualizado.

Cada candidato autorado se revisará contra su predecesor. El lockfile se mantendrá aislado porque partirlo dañaría su integridad.

## Tareas

### UI-1 · Portar la estructura visual del dashboard
- [x] Adaptar `web/index.html` para incorporar sidebar, radar, métricas, misión y abogado del diablo.
- [x] Adaptar `web/styles.css` con la composición, tarjetas, anillo, badges y diseño responsive del mockup.
- [x] Conservar todas las regiones funcionales actuales y sus identificadores DOM.
- Ruta: delegada por regla de escritura multiarchivo.
- Cierre: implementación incluida en el commit inicial reescrito `7728d0e`; verificación visual independiente pendiente.

### UI-2 · Conectar el dashboard con datos reales
- [x] Actualizar `web/app.js` para poblar métricas, puntaje circular, misión, alertas y mapa plano de procedencias.
- [x] Mantener selección de casos, citas, borrador, revisión, consultas y calidad.
- [x] Evitar inferir relaciones de réplica no presentes en los datos.
- Ruta: delegada dentro del mismo escritor acotado para preservar coherencia entre DOM y JavaScript.
- Cierre: implementación incluida en el commit inicial reescrito `7728d0e`; verificación visual independiente pendiente.

### UI-3 · Verificar el recorrido funcional y visual
- [x] Ejecutar las pruebas automatizadas.
- [ ] Verificar la interfaz en navegador: portada, selección de caso, navegación, borrador, revisión, consulta y calidad.
- [ ] Confirmar visualmente el funcionamiento responsive.
- [x] Confirmar estructuralmente la ausencia de recursos remotos.
- Ruta: evaluación nativa no disponible por ausencia de una base Git rastreada; el verificador independiente falló antes de ejecutar herramientas.

### UI-4 · Preparar la publicación en GitHub
- [x] Actualizar `README.md` para instalación reproducible en Windows y Unix, demo sintética, arquitectura, controles, estado y límites.
- [x] Ajustar la higiene del repositorio para excluir artefactos locales y datos de prueba duplicados sin ocultar evidencia útil.
- [x] Ejecutar pruebas, lint, escaneo de secretos y comprobaciones funcionales disponibles.
- Ruta: escritor delegado completó README e higiene; verificación propia en verde. La evaluación nativa siguió no evaluable sin una base Git y el verificador independiente volvió a fallar antes de ejecutar herramientas.
- Cierre: README e higiene incluidos en el commit inicial reescrito `7728d0e`.

### UI-5 · Crear la base Git y publicar
- [x] Crear un commit inicial convencional con el proyecto completo autorizado.
- [ ] Reescribir la importación inicial como la secuencia de commits revisables elegida.
- [ ] Configurar `origin` con el remoto vacío autorizado.
- [ ] Publicar la rama principal y verificar el estado remoto.
- Ruta: entrega explícitamente autorizada por el usuario; no se creará PR ni se hará merge adicional.

### UI-6 · Persistir memoria del proyecto
- [ ] Actualizar el espejo Engram con el estado final, commit, remoto, verificaciones y próximos pasos.
- [ ] Mantener la memoria interna fuera del repositorio público.
- Ruta: memoria del proyecto, no artefacto de GitHub.

## Criterios de aceptación
1. La primera pantalla reproduce claramente la composición e identidad del mockup original.
2. El dashboard usa los datos actuales del snapshot, no cifras fijas del mockup.
3. Puntaje y estado de evidencia se muestran como conceptos separados.
4. El mapa de evidencia conserva procedencias y citas sin inventar causalidad.
5. Ficha, borrador, revisión, consultas y calidad siguen accesibles y funcionales.
6. La aplicación continúa funcionando offline.
7. T01–T10 y la suite existente pasan.
8. El recorrido principal funciona en escritorio y ancho móvil.

## Progreso y evidencia
- 2026-10-06: comparación visual y estructural completada entre `docs/mockup_original.html` y `web/`.
- 2026-10-06: el usuario eligió “Mockup como portada funcional”.
- 2026-10-06: el escritor delegado actualizó `web/index.html`, `web/styles.css` y `web/app.js` dentro de las superficies autorizadas.
- Verificación del escritor: `uv run pytest -q` → 20 pruebas pasaron; verificación estructural → `ui-structure-ok`; `uv run ruff check pulso tests` → sin hallazgos.
- Lectura estructural del padre: identificadores funcionales presentes, dashboard conectado a `PULSO_SNAPSHOT` y sin errores LSP confirmados en dos archivos; un servidor LSP no pudo confirmar limpio el tercer archivo.
- Evaluación nativa: no evaluable porque el repositorio completo continúa sin archivos rastreados ni una base Git.
- Verificador independiente: falló antes de ejecutar herramientas; la verificación visual y responsive permanece pendiente.
- 2026-10-06: el usuario autorizó crear commits, corregir README, publicar el proyecto completo en `vicmat04/pulso-hackiathon` y guardar la memoria del proyecto en Engram.
- Remoto inspeccionado: no contiene ramas, por lo que la publicación será una importación inicial.
- README e higiene: escritor delegado completó `README.md` y `.gitignore`; 20 pruebas pasaron, Ruff pasó, estructura README validada y exclusiones locales confirmadas.
- Revisión del padre: 69 archivos serían rastreados; `.venv/`, `out/`, `data/prueba/` y caches permanecen ignorados; `data/sample/`, `reports/` y `web/snapshot.js` se conservan publicables.
- Verificador independiente: nuevo intento falló antes de ejecutar herramientas; no se atribuye el fallo al código del proyecto.
- Historial reescrito con autorización: base vacía `43a7c95` y commit de proyecto `7728d0e`; el árbol del proyecto coincide exactamente con el commit anterior `0768929`.
- Preflight nativo con base explícita `43a7c95`: detenido con `lens_context_budget_exceeded`; no se creó autoridad y reintentar el mismo candidato completo no puede funcionar.
- Publicación remota: pendiente de decidir entre dividir la importación en candidatos más pequeños o publicar con la revisión nativa pendiente.

## Próximo paso
Reconstruir la rama desde `43a7c95` usando la secuencia acordada, verificar que el árbol final coincide y revisar cada candidato aplicable antes del push.
