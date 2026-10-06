"""Exporta artefactos para importar en Notion (bases, sección 5). Notion importa CSV como bases
de datos y Markdown como páginas: Configuración → Importar. La carga manual es válida."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from . import config


def _csv(path: Path, header: list[str], rows: list[list]):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def export(snap: dict, out: Path, bench: dict | None = None, ev: dict | None = None) -> list[Path]:
    out.mkdir(parents=True, exist_ok=True)
    files = []
    p = out / "Casos_y_evidencias.csv"
    _csv(p, ["ID caso", "Título", "Tema", "IDs fuente", "Procedencias", "Puntaje", "Banda", "R", "I", "U", "N", "E",
             "Versión reglas", "Estado evidencia", "Falta comprobar", "Acción", "Alertas", "Brief (resumen)",
             "Estado revisión", "Persona revisora"],
         [[f["id_caso"], f["titulo"], config.TOPIC_LABEL[f["tema"]], ", ".join(f["ids_fuente"]),
           f["fuentes_independientes"], f["puntaje"], f["banda"], *[f["componentes"][k] for k in "RIUNE"],
           f["version_reglas"], f["estado_evidencia"], " | ".join(f["falta_comprobar"]), f["accion_recomendada"],
           " | ".join(f["alertas"]),
           " ".join(a["texto"] for a in (f["borrador"] or {}).get("brief", [])) or "Sin borrador: evidencia insuficiente",
           f["estado_revision"], f.get("revisor") or ""] for f in snap["fichas"]])
    files.append(p)

    m = json.loads((config.DATA_DIR / "manifest.json").read_text(encoding="utf-8")) if (config.DATA_DIR / "manifest.json").exists() else {}
    p = out / "Catalogo_de_datos.csv"
    rows = []
    for name, info in m.get("archivos", {}).items():
        rows.append([name, m.get("version"), m.get("fecha_corte_UTC"), info["filas"],
                     m.get("licencia_condiciones", {}).get(name, "COMPLETAR"), info["sha256"],
                     "; ".join(m.get("transformaciones", [])), "COMPLETAR: URL de la fuente", "COMPLETAR: cobertura efectiva",
                     "ver docs/03_ARQUITECTURA.md (contrato)"])
    _csv(p, ["Archivo", "Versión", "Fecha corte UTC", "Filas", "Licencia/condiciones", "SHA-256",
             "Transformaciones", "URL", "Cobertura", "Campos"], rows)
    files.append(p)

    calidad = snap["calidad"]
    p = out / "Reporte_de_calidad.md"
    lines = ["# Reporte de calidad de carga", ""]
    for arch, q in calidad.items():
        lines += [f"## {arch}", f"Leídas {q['leidas']} · válidas {q['validas']} · errores {len(q['errores'])}", ""]
        lines += [f"- Fila {e['fila']}: {e['motivo']} {e.get('id', '')}" for e in q["errores"]]
        if q["nulos"]:
            lines.append(f"- Nulos conservados: {q['nulos']}")
        lines.append("")
    p.write_text("\n".join(lines), encoding="utf-8")
    files.append(p)

    if bench:
        from .bench import to_markdown
        p = out / "Benchmark.md"
        p.write_text(to_markdown(bench, ev), encoding="utf-8")
        files.append(p)

    acc = config.ROOT / "reports" / "aceptacion.json"
    if acc.exists():
        p = out / "Pruebas_T01_T10.csv"
        data = json.loads(acc.read_text(encoding="utf-8"))
        _csv(p, ["ID", "Prueba", "Entrada", "Resultado esperado", "Resultado observado", "Estado", "Evidencia de ejecución", "Corrección"],
             [[t["id"], t["prueba"], t["entrada"], t["esperado"], t["observado"], t["estado"],
               f"pytest {t['test']} · {data['fecha_UTC']}", t.get("correccion", "")] for t in data["pruebas"]])
        files.append(p)

    for f in snap["fichas"][:10]:
        b = f["borrador"]
        lines = [f"# {f['id_caso']} · {f['titulo']}", "",
                 f"**Puntaje** {f['puntaje']} ({f['banda']}) · R {f['componentes']['R']} · I {f['componentes']['I']} · "
                 f"U {f['componentes']['U']} · N {f['componentes']['N']} · E {f['componentes']['E']} · {f['version_reglas']}",
                 f"**Estado de evidencia** {f['estado_evidencia']} · **Revisión** {f['estado_revision']}", "",
                 "## Qué se reporta", f["que_se_reporta"], "", "## Quién lo reporta", ", ".join(f["quien_lo_reporta"]), "",
                 "## Procedencias", *[f"- {k}: {', '.join(v)}" for k, v in f["procedencias"].items()], "",
                 "## Qué falta comprobar", *[f"- {x}" for x in f["falta_comprobar"]], "",
                 "## Acción recomendada", f["accion_recomendada"], ""]
        if f["alertas"]:
            lines += ["## Alertas", *[f"- {x}" for x in f["alertas"]], ""]
        if b:
            lines += ["## Borrador", f"**Título propuesto:** {b['titulo_propuesto']}", "",
                      f"**Enfoque de interés público:** {b['enfoque_interes_publico']}", ""]
            if b.get("aviso_alcance"):
                lines += [f"> {b['aviso_alcance']}", ""]
            lines += ["### Brief"] + [f"- [{a['tipo']}] {a['texto']} " + " ".join(f"`{c['evidencia_id']}·{c['campo']}`" for c in a["citas"]) for a in b["brief"]]
            lines += ["", "### Preguntas", *[f"{i}. {q}" for i, q in enumerate(b["preguntas"], 1)], "",
                      f"### Guion (~{b['guion_segundos_estimados']} s)"] + [f"- {a['texto']}" for a in b["guion"]]
            lines += ["", "### Copy digital", b["copy_digital"], "", "### Fuentes", *[f"- {x}" for x in b["fuentes"]]]
        else:
            lines += ["## Borrador", "No se genera: evidencia insuficiente. El sistema se abstiene y lista lo que falta."]
        lines += ["", "## Registro de revisión", "| Fecha (Panamá) | Persona | Decisión | Estado | Nota |", "|---|---|---|---|---|", "| | | | | |"]
        p = out / "fichas" / f"{f['id_caso']}.md"
        p.parent.mkdir(exist_ok=True)
        p.write_text("\n".join(lines), encoding="utf-8")
        files.append(p)
    return files
