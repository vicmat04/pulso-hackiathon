# 📡 PULSO · De la señal a la decisión

**PULSO** es un copiloto editorial *offline-first* para la sala de redacción de **TVN Media**, desarrollado para el reto **hackIAthon 2026** («De la señal a la decisión»).

Ordena señales de noticias públicas y datos oficiales para que una persona editora pueda decidir qué investigar: **prioriza temas**, muestra una **ficha trazable** y prepara un **borrador responsable**. No reemplaza el juicio humano ni publica contenido automáticamente.

> [!WARNING]  
> **Importante:** El directorio `data/sample/` contiene **datos sintéticos** exclusivos para desarrollo y pruebas de aceptación (T01–T10). Sus métricas son estrictamente referenciales y **no representan resultados oficiales de la competencia**.

---

## 🚀 Inicio rápido

**Requisitos mínimos:** Python 3.11+ y [uv](https://docs.astral.sh/uv/).  
El proyecto utiliza dependencias fijadas en `uv.lock`. Una vez sincronizado, **no requiere conexión a internet** para su recorrido base.

### 💻 PowerShell (Windows)

```powershell
uv sync
uv run pulso calidad
uv run pulso manifest
uv run pulso build
uv run pulso serve
```

Abra `http://127.0.0.1:8000` en su navegador. Para comprobar la salud del proyecto:

```powershell
uv run pytest -q
uv run ruff check pulso tests
```

### 🐧 Bash (macOS/Linux)

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

> [!TIP]  
> También puede abrir `web/index.html` directamente en su navegador para visualizar el modo archivo con respuestas precalculadas. Si cuenta con `make`, los atajos equivalentes son `make test`, `make lint`, `make build`, `make demo` y `make serve`. (En Windows se recomiendan los comandos directos con `uv run`).

---

## 🎯 Qué resuelve

Las redacciones reciben un alud de señales dispersas que suelen repetir la misma procedencia, a menudo sin respaldo suficiente. PULSO convierte un paquete de datos congelado en una **bandeja de temas organizada**, cuidando de **no presentar la repetición como corroboración**. Cada caso conserva sus procedencias, citas y vacíos de evidencia, dejando la decisión final en manos de la persona editora.

El **dashboard funcional** reproduce el recorrido editorial del mockup original utilizando datos reales del *snapshot*: bandeja priorizada, radar de caso, ficha trazable, misión, alertas, mapa plano de procedencias, borrador, revisión, consultas y calidad de datos. Es una aplicación local (HTML, CSS y JS puro) **sin recursos remotos**.

---

## ⚙️ Flujo editorial

1. 📥 **Cargar:** Valida IDs, URLs, fechas, campos obligatorios y nulos (los nulos se conservan).
2. 🧩 **Organizar:** Agrupa temas y procedencias sin inferir relaciones de copia que no estén demostradas.
3. 🔎 **Contextualizar:** Relaciona datos del Banco Mundial cuando corresponde (USGS respalda **únicamente** hechos sísmicos).
4. 📈 **Priorizar:** Ordena la bandeja mediante una regla algorítmica fija y explicable.
5. 📝 **Explicar y producir:** Entrega una ficha, señala faltantes y genera un borrador con citas directas (o emite una abstención explícita).
6. 🧑‍⚖️ **Revisar:** Una persona responsable registra la decisión. *Aprobar un borrador no equivale a publicarlo*.

### ⚖️ Puntaje y Evidencia (Variables independientes)

La prioridad utiliza la fórmula oficial:
**`P = 30R + 25I + 20U + 15N + 10E`**
*(**R**: relevancia; **I**: impacto; **U**: urgencia; **N**: novedad; **E**: evidencia)*

Las bandas operan en: Bajo `<40` | Medio `<70` | Alto `≥70`.  
Los empates se resuelven por `U` y luego por `ID`. Todos los pesos pertenecen a `reglas-v1.0` y no se ajustan sin una decisión documentada.

El **estado de evidencia** se calcula por separado (`insuficiente`, `parcial`, `suficiente_para_borrador`). Un puntaje alto no convierte un rumor en prueba ni autoriza un borrador automáticamente. Si falta respaldo, el sistema produce una abstención.

---

## 📂 Datos: Demo, pruebas y paquete oficial

El paquete predeterminado es `data/sample/`. **No lo edite durante pruebas locales**. Si necesita experimentar, cree una copia aislada (ignorada por Git):

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

Cuando reciba el **paquete oficial** autorizado, colóquelo en `data/oficial/` asegurando el contrato esperado (`noticias.csv`, `indicadores.csv`, `eventos.geojson`, `manifest.json`) y selecciónelo:

```powershell
$env:PULSO_DATA = "data/oficial"
uv run pulso build
```

> [!NOTE]  
> La evaluación de métricas finales y validación humana quedan pendientes hasta operar con el paquete oficial. No deben sustituirse por el set sintético.

---

## 🛠️ Comandos clave

| Comando | Acción |
|---|---|
| `uv run pulso calidad` | Valida el paquete y reporta errores y valores nulos. |
| `uv run pulso manifest` | Calcula hashes (SHA-256), filas y licencias del paquete. |
| `uv run pulso build` | Genera fichas, prioridad, borradores y el snapshot local. |
| `uv run pulso serve` | Sirve la interfaz local y habilita la ruta `/api/ask`. |
| `uv run pulso ask "¿…?"` | Responde una consulta con citas o emite una abstención explícita. |
| `uv run pulso ficha CASO-…` | Imprime la ficha JSON completa de un caso. |
| `uv run pulso revisar CASO-…` | Registra una decisión humana válida. (Soporta `--estado` y `--revisor`). |
| `uv run pulso importar-revisiones file.jsonl` | Valida e importa el log de decisiones descargado desde la interfaz. |
| `uv run pulso aceptacion` | Ejecuta la matriz de pruebas T01–T10 y actualiza el reporte local. |
| `uv run pulso bench` | Produce el benchmark de desarrollo. |
| `uv run pulso fetch` | **Requiere red:** única ruta de extracción remota (APIs de terceros). |

La verificación base consta de **20 pruebas** (que incluyen las pruebas de aceptación de bases **T01–T10**) y un análisis estático limpio con `ruff`.

---

## 🏗️ Arquitectura y controles

```text
paquete local → validación → organización → contexto oficial → prioridad
              → fichas y borradores → revisión humana → snapshot/dashboard local
```

- **Carga y calidad:** Pydantic valida estrictamente el contrato; manejo de fechas en UTC y visualización en hora de Panamá.
- **Organización:** TF-IDF y agrupación aglomerativa (operan sin descargas). Embeddings multilingües son opcionales y de descarga previa.
- **Trazabilidad:** Toda afirmación de hecho o declaración emite su propio `evidencia_id` y `campo`. Hechos extraídos estrictamente de datos oficiales.
- **Seguridad editorial:** Bloqueo de alucinaciones. Si solo dispone de titulares avisa de forma obligatoria: *«Basado únicamente en titular/metadatos»*.
- **Anti-inyección:** Todo texto de fuentes externas se esteriliza y aísla antes del LLM. Se excluye si incluye comandos maliciosos.
- **Control humano:** Rutas cerradas de estado: `nuevo`, `en_revision`, `requiere_evidencia`, `aprobado_como_borrador` y `descartado`.
- **Privacidad:** Retención exclusiva de metadatos. El servidor local no registra consultas.

---

## 🔌 Operación sin internet (Offline-First)

La demostración se ejecuta con un snapshot pre-calculado y dependencias locales. Tareas pesadas como validación, agrupación, puntaje, plantillas, consultas y dashboard operan **sin acceso a red**. 
La excepción es `pulso fetch`, pensada para la etapa previa. Si el modelo LLM por API falla, el flujo recurre suavemente a una plantilla determinista.

---

## ⚠️ Estado y límites

PULSO es un prototipo funcional diseñado para una demostración local interactiva. 
**Limitaciones intencionales:** No determina verdad absoluta o falsedad, no publica en gestores de contenido, no mide audiencias, no evalúa clientes, no lee detrás de muros de pago (*paywalls*) ni perfila personas. La vertical bancaria permanece desactivada temporalmente.

Próximos pasos orientados a producción:
1. Cargar el **paquete oficial**.
2. Recalibrar y evaluar contra **etiquetas humanas** reales.
3. Documentar en **Notion** hallazgos, decisiones y métricas finales.

---

## 🗂️ Estructura del repositorio

```text
pulso/          Núcleo Python, CLI, reglas y controles de motor
web/            Dashboard local (HTML/CSS/JS) y snapshot publicable
data/sample/    Paquete sintético versionado para pruebas continuas
data/prueba/    Copia local ignorada por Git para experimentación
data/oficial/   Directorio destino para el paquete autorizado (pendiente)
tests/          Pruebas unitarias y matriz de cumplimiento T01–T10
docs/           Definición de producto, arquitectura, operación y decisiones
reports/        Métricas y reportes publicables de desarrollo
```

---

## 📚 Documentación adicional

- 📋 [Auditoría frente a las bases](docs/01_AUDITORIA.md)
- 🗺️ [Producto y recorrido editorial](docs/02_PRODUCTO.md)
- 🏛️ [Arquitectura, IA y controles](docs/03_ARQUITECTURA.md)
- 🚫 [Operación offline y fallbacks](docs/04_OFFLINE.md)
- 🗓️ [Plan de trabajo](docs/05_PLAN_TRABAJO.md)
- 💡 [Decisiones de diseño](docs/DECISIONES.md)
- ❓ [Preguntas para la organización](docs/09_PREGUNTAS_ORGANIZACION.md)
