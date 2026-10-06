"""CLI de PULSO: `uv run pulso --help`. Todo funciona sin internet salvo `fetch`."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from . import config

app = typer.Typer(help="PULSO · de la señal a la decisión (offline-first)", no_args_is_help=True)


def _snap():
    from .ask import load_snapshot

    p = config.OUT_DIR / "snapshot.json"
    if not p.exists():
        typer.secho("No hay snapshot. Ejecuta `pulso build`.", fg="red")
        raise typer.Exit(1)
    return load_snapshot(p)


@app.command()
def calidad(data: Path = typer.Option(None, help="Carpeta del paquete")):
    """Etapa 1: valida el paquete y muestra el reporte de calidad (T01)."""
    from .load import load_corpus, quality_report

    rep = quality_report(load_corpus(data))
    for arch, q in rep.items():
        typer.echo(f"{arch}: {q['validas']}/{q['leidas']} válidas · {len(q['errores'])} errores · nulos {q['nulos']}")
        for e in q["errores"]:
            typer.secho(f"   fila {e['fila']}: {e['motivo']} {e.get('id', '')}", fg="yellow")


@app.command()
def manifest(data: Path = typer.Option(None)):
    """Genera manifest.json (SHA-256, filas, licencias) del paquete."""
    from . import manifest as m

    typer.echo(json.dumps(m.build(data)["archivos"], indent=1))


@app.command()
def build(data: Path = typer.Option(None)):
    """Etapas 1–6: carga, organiza, contextualiza, prioriza, explica y produce borradores."""
    from . import pipeline

    snap = pipeline.build(data)
    out = pipeline.write_outputs(snap)
    typer.secho(f"OK {len(snap['fichas'])} casos · embedder {snap['meta']['embedder']} · {out}", fg="green")
    for f in snap["fichas"][:5]:
        typer.echo(f"  P{f['puntaje']:>3} {f['banda']:<5} {f['estado_evidencia']:<24} {f['titulo'][:60]}")


@app.command()
def ask(pregunta: str):
    """Consulta en español con citas o abstención."""
    from .ask import ask as _ask

    r = _ask(pregunta, _snap())
    typer.echo(r["respuesta"])
    typer.secho(f"\ncitas: {r['citas']} · abstención: {r['abstencion']} · {r['ms']} ms", dim=True)


@app.command()
def ficha(id_caso: str):
    """Muestra una ficha completa (JSON)."""
    f = next((x for x in _snap()["fichas"] if x["id_caso"] == id_caso), None)
    if not f:
        raise typer.BadParameter("ID no encontrado")
    typer.echo(json.dumps(f, ensure_ascii=False, indent=1))


@app.command()
def revisar(
    id_caso: str,
    estado: str = typer.Option(..., help=" | ".join(config.REVIEW_STATES)),
    revisor: str = typer.Option(...),
    decision: str = typer.Option("correccion", help="aceptacion | correccion | descarte"),
    nota: str = typer.Option(""),
):
    """Etapa 7: registra la decisión humana (copiar luego a Notion)."""
    from . import review

    f = next((x for x in _snap()["fichas"] if x["id_caso"] == id_caso), None)
    if not f:
        raise typer.BadParameter("ID no encontrado")
    try:
        r = review.record(f, estado, revisor, decision, nota)
    except ValueError as e:
        typer.secho(f"[X] {e}", fg="red")
        raise typer.Exit(1) from e
    typer.secho(f"[OK] {r['id_caso']}: {r['de']} -> {r['estado']} por {r['revisor']}", fg="green")


@app.command("importar-revisiones")
def importar_revisiones(archivo: Path):
    """Importa el registro descargado de la interfaz, validando cada transición."""
    from . import review

    snap = _snap()
    by_id = {f["id_caso"]: f for f in snap["fichas"]}
    ok = 0
    for line in archivo.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError as e:
            typer.secho(f"[X] Linea JSON invalida: {e}", fg="red")
            continue
        f = by_id.get(r["id_caso"])
        if not f:
            typer.secho(f"[X] {r['id_caso']}: no existe en el snapshot", fg="red")
            continue
        try:
            review.record(f, r["estado"], r["revisor"], r.get("decision", "correccion"), r.get("nota", ""))
            ok += 1
        except ValueError as e:
            typer.secho(f"[X] {r['id_caso']}: {e}", fg="red")
    typer.secho(f"[OK] {ok} decisiones registradas en {config.REVIEW_LOG}", fg="green")


@app.command()
def aceptacion():
    """Ejecuta T01–T10 y guarda reports/aceptacion.json."""
    from .acceptance import run

    rep = run(_snap())
    for t in rep["pruebas"]:
        typer.secho(f"{t['id']} {t['estado']:<5} {t['prueba']}", fg="green" if t["estado"] == "pasa" else "red")


@app.command()
def bench(
    split: str = "dev",
    archivo: Path = typer.Option(config.ROOT / "data" / "benchmark" / "benchmark_dev.jsonl"),
    etiquetas: Path = typer.Option(None),
):
    """Benchmark + IA vs baseline. Guarda reports/bench_<split>.json y .md."""
    from .bench import evaluate_labels, run_benchmark, to_markdown

    snap = _snap()
    b = run_benchmark(snap, archivo, split)
    lab = etiquetas or config.DATA_DIR / "etiquetas.csv"
    ev = evaluate_labels(snap, lab) if lab.exists() else None
    (config.ROOT / "reports").mkdir(exist_ok=True)
    (config.ROOT / "reports" / f"bench_{split}.json").write_text(
        json.dumps({"benchmark": b, "evaluacion": ev}, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    md = to_markdown(b, ev)
    (config.ROOT / "reports" / f"bench_{split}.md").write_text(md, encoding="utf-8")
    typer.echo(md)


@app.command("export-notion")
def export_notion():
    """Genera CSV/MD importables en Notion en out/notion/."""
    from . import notion

    snap = _snap()
    bp = config.ROOT / "reports" / "bench_dev.json"
    b = {}
    if bp.exists():
        try:
            b = json.loads(bp.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            typer.secho(f"[!] Advertencia: benchmark JSON invalido: {e}", fg="yellow")
    files = notion.export(snap, config.OUT_DIR / "notion", b.get("benchmark"), b.get("evaluacion"))
    typer.secho(f"[OK] {len(files)} archivos en {config.OUT_DIR / 'notion'}", fg="green")


@app.command()
def serve(port: int = 8000):
    """Interfaz + /api/ask en http://127.0.0.1:8000 (sin internet)."""
    from .server import serve as _serve

    _serve(port)


@app.command()
def fetch(destino: Path = typer.Option(config.ROOT / "data" / "raw"), fuentes: str = "worldbank,usgs"):
    """[REQUIERE RED] Receta de extracción si no hay paquete oficial. Ver docs/04."""
    from . import fetch as f

    destino.mkdir(parents=True, exist_ok=True)
    if "worldbank" in fuentes:
        typer.echo(f"Banco Mundial: {f.worldbank(destino)} filas (con nulos explícitos)")
    if "usgs" in fuentes:
        typer.echo(f"USGS: {f.usgs(destino)} eventos")
    typer.echo("Noticias: usa fetch.rss()/fetch.gdelt() con la URL verificada del RSS de TVN y ventanas de fechas.")


if __name__ == "__main__":
    app()
