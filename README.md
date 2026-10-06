# PULSO · De la señal a la decisión

PULSO es un copiloto editorial offline-first para la sala de TVN en el reto hackIAthon 2026. Ordena señales de noticias públicas y datos oficiales para que una persona editora pueda decidir qué investigar: prioriza temas, muestra una ficha trazable y prepara un borrador responsable; no reemplaza el juicio humano ni publica contenido.

> **Importante:** `data/sample/` contiene datos sintéticos para desarrollo y las pruebas T01–T10. Sus métricas son exclusivamente de desarrollo: **no son resultados oficiales de la competencia**.

## Inicio rápido

**Requisito:** Python 3.11+ y [uv](https://docs.astral.sh/uv/). El proyecto usa dependencias fijadas en `uv.lock`; no necesita red después de sincronizar las dependencias para su recorrido base.

### PowerShell (Windows)

```powershell
uv sync
uv run pulso calidad
uv run pulso manifest
uv run pulso build
uv run pulso serve
```

Abra `http://127.0.0.1:8000` en el navegador. Para comprobar el proyecto:

```powershell
uv run pytest -q
uv run ruff check pulso tests
```

### Bash (macOS/Linux)

```bash
uv sync
uv run pulso calidad
uv run pulso manifest
uv run pulso build
uv run pulso serve
```

En otra terminal, ejecute las comprobaciones:

```bash
uv run pytest -q
uv run ruff check pulso tests
```

También puede abrir `web/index.html` directamente para el modo archivo con respuestas precalculadas. Para quien tenga `make`, los atajos equivalentes son `make test`, `make lint`, `make build`, `make demo` y `make serve`; en Windows se recomiendan los comandos directos con `uv run`.

## Qué resuelve

Las redacciones reciben señales dispersas que pueden repetir la misma procedencia y que no siempre tienen respaldo suficiente. PULSO convierte un paquete de datos congelado en una bandeja de temas, sin presentar la repetición como corroboración. Cada caso conserva procedencias, citas y vacíos de evidencia para que la decisión permanezca en manos de la persona editora.

El dashboard funcional reproduce el recorrido editorial del mockup con datos del snapshot: bandeja priorizada, radar de caso, ficha trazable, misión, alertas, mapa plano de procedencias, borrador, revisión, consultas y calidad de datos. Es una aplicación local de HTML, CSS y JavaScript, sin recursos remotos.

## Flujo editorial

1. **Cargar:** valida IDs, URLs, fechas, campos obligatorios y nulos; los nulos se conservan.
2. **Organizar:** agrupa temas y procedencias sin inferir relaciones de copia no demostradas.
3. **Contextualizar:** relaciona datos del Banco Mundial cuando corresponde; USGS respalda únicamente hechos sísmicos.
4. **Priorizar:** ordena la bandeja mediante una regla fija y explicable.
5. **Explicar y producir:** entrega ficha, faltantes y borrador con citas o abstención explícita.
6. **Revisar:** una persona responsable registra la decisión; aprobar un borrador no equivale a publicar.

### Puntaje y evidencia son independientes

La prioridad usa la fórmula fija **P = 30R + 25I + 20U + 15N + 10E** (`R`, relevancia; `I`, impacto; `U`, urgencia; `N`, novedad; `E`, evidencia). Las bandas son bajo `<40`, medio `<70` y alto `≥70`; los empates se resuelven por `U` y luego por ID. Los pesos, bandas y desempate pertenecen a `reglas-v1.0` y no se ajustan sin una nueva versión y decisión documentada.

El estado de evidencia se calcula aparte: `insuficiente`, `parcial` o `suficiente_para_borrador`. Un puntaje alto no convierte una fuente en prueba ni autoriza un borrador; las contradicciones se muestran y la falta de respaldo produce abstención.

## Datos: demo, pruebas y paquete oficial

El paquete predeterminado es `data/sample/`. No lo edite durante pruebas locales. Si necesita experimentar con una copia, cree y seleccione `data/prueba/`; esta carpeta local está ignorada por Git:

**PowerShell**

```powershell
Copy-Item -Recurse data/sample data/prueba
$env:PULSO_DATA = "data/prueba"
uv run pulso calidad
uv run pulso build
```

**Bash**

```bash
cp -R data/sample data/prueba
export PULSO_DATA=data/prueba
uv run pulso calidad
uv run pulso build
```

Así se conserva intacto `data/sample/`. Antes de trabajar con el paquete autorizado, sitúelo en `data/oficial/` con el contrato de archivos esperado (`noticias.csv`, `indicadores.csv`, `eventos.geojson` y `manifest.json`) y selecciónelo explícitamente:

```powershell
$env:PULSO_DATA = "data/oficial"
uv run pulso calidad
uv run pulso build
```

```bash
export PULSO_DATA=data/oficial
uv run pulso calidad
uv run pulso build
```

El paquete oficial, su validación humana y las métricas finales siguen pendientes; no se sustituyen por el set sintético.

## Comandos clave

| Comando | Uso |
|---|---|
| `uv run pulso calidad` | Valida el paquete y reporta errores y nulos. |
| `uv run pulso manifest` | Calcula hashes, filas y licencias del paquete. |
| `uv run pulso build` | Genera fichas, prioridad, borradores y el snapshot local. |
| `uv run pulso serve` | Sirve la interfaz local y `/api/ask`. |
| `uv run pulso ask "¿…?"` | Responde con citas o una abstención explícita. |
| `uv run pulso ficha CASO-…` | Muestra la ficha JSON de un caso. |
| `uv run pulso revisar CASO-… --estado en_revision --revisor "Nombre"` | Registra una revisión humana válida. |
| `uv run pulso importar-revisiones archivo.jsonl` | Valida e importa decisiones descargadas de la interfaz. |
| `uv run pulso aceptacion` | Ejecuta la matriz T01–T10 y actualiza su reporte local. |
| `uv run pulso bench` | Produce el benchmark de desarrollo. |
| `uv run pulso fetch` | Requiere red; es la única ruta de extracción. |

La verificación esperada del estado actual es **20 pruebas**, incluidas las pruebas de aceptación **T01–T10**, y un lint limpio con Ruff.

## Arquitectura y controles

```text
paquete local → validación → organización → contexto oficial → prioridad
              → fichas y borradores → revisión humana → snapshot/dashboard local
```

- **Carga y calidad:** Pydantic valida el contrato; fechas en UTC y presentación en hora de Panamá.
- **Organización:** TF-IDF y agrupación aglomerativa funcionan sin descargas; embeddings multilingües son opcionales y deben descargarse previamente.
- **Trazabilidad:** toda afirmación de hecho o declaración incluye `evidencia_id` y `campo`; los hechos provienen solo de datos oficiales.
- **Seguridad editorial:** no inventa hechos, cifras, entrevistas, citas, causas, imágenes ni fuentes. Con solo titulares avisa «Basado únicamente en titular/metadatos».
- **Anti-inyección:** el texto de fuentes se trata como dato, se envuelve antes de llegar a un modelo y se excluye del borrador si contiene instrucciones.
- **Control humano:** los estados son `nuevo`, `en_revision`, `requiere_evidencia`, `aprobado_como_borrador` y `descartado`; no se aprueba evidencia insuficiente.
- **Privacidad y derechos:** se conservan metadatos, no cuerpos completos ni imágenes; el servidor local no registra consultas.

## Operación sin internet

La demo se ejecuta con un snapshot y dependencias locales: carga, validación, agrupación, puntaje, plantillas, consultas y dashboard operan sin red. `pulso fetch` es la excepción y debe ejecutarse antes, con red. Si un LLM por API no está disponible, el flujo cae a una plantilla determinista; si falta un modelo de embeddings, usa TF-IDF. Consulte el plan de fallback antes de una demostración.

## Estado y límites

PULSO es un prototipo funcional basado en el mockup para una demo local. No determina verdad o falsedad, no publica, no mide audiencia, no evalúa clientes, no lee contenido tras paywall ni perfila personas. La vertical de banca permanece desactivada.

No están completos el paquete oficial, la validación humana, las métricas finales, la entrega en Notion ni la preparación para producción. Los próximos pasos son cargar y validar el paquete oficial, recalibrar y medir con etiquetas humanas, documentar decisiones y evidencia real en Notion, y ensayar el flujo offline con la sala editorial.

## Estructura del repositorio

```text
pulso/          núcleo Python, CLI, reglas y controles
web/            dashboard local y snapshot publicable
data/sample/    paquete sintético versionado para desarrollo
data/prueba/    copia local ignorada para experimentar
data/oficial/   destino previsto del paquete autorizado (pendiente)
tests/          pruebas unitarias y T01–T10
docs/           producto, arquitectura, operación y decisiones
reports/        reportes publicables de desarrollo
```

## Documentación

- [Auditoría frente a las bases](docs/01_AUDITORIA.md)
- [Producto y recorrido editorial](docs/02_PRODUCTO.md)
- [Arquitectura, IA y controles](docs/03_ARQUITECTURA.md)
- [Operación offline y fallbacks](docs/04_OFFLINE.md)
- [Plan de trabajo](docs/05_PLAN_TRABAJO.md)
- [Decisiones](docs/DECISIONES.md)
- [Preguntas para la organización](docs/09_PREGUNTAS_ORGANIZACION.md)
