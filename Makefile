.PHONY: install test lint build demo bench aceptacion notion serve models check-offline

install:          ## dependencias base (sin descargas de modelos)
	uv sync

test:             ## pytest: unidades + T01–T10
	uv run pytest -q

lint:
	uv run ruff check pulso tests

build:            ## manifest + etapas 1–6 → out/ y web/snapshot.js
	uv run pulso manifest
	uv run pulso build

bench:            ## benchmark dev + IA vs baseline → reports/
	uv run pulso bench

aceptacion:       ## matriz T01–T10 → reports/aceptacion.json
	uv run pulso aceptacion

notion:           ## CSV/MD importables en Notion → out/notion/
	uv run pulso export-notion

demo: build bench aceptacion notion   ## todo lo necesario para la presentación

serve:            ## interfaz con motor completo en http://127.0.0.1:8000
	uv run pulso serve

models:           ## CON RED: descarga el modelo de embeddings para uso offline
	uv sync --group nlp
	HF_HUB_OFFLINE=0 TRANSFORMERS_OFFLINE=0 uv run python -c "import os; from sentence_transformers import SentenceTransformer as S; S(os.environ['PULSO_ST_MODEL'])"

check-offline: demo test   ## ensayo de víspera (luego apaga el wifi y repite `make serve`)
	@echo "Apaga el wifi, ejecuta 'make serve' y recorre el guion de docs/02_PRODUCTO.md"
