/* PULSO · interfaz offline. Lee window.PULSO_SNAPSHOT (generado por `pulso build`).
   Con `pulso serve` las consultas usan /api/ask (motor completo). Abierto como archivo,
   usa un respaldo por reglas que también se abstiene. Ningún recurso remoto. */
(function () {
  "use strict";
  const S = window.PULSO_SNAPSHOT;
  const $ = (id) => document.getElementById(id);
  const esc = (t) => String(t ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  // Todo contenido interpolado se escapa antes de pasar por este renderizador local.
  function render(el, markup) {
    const parsed = new DOMParser().parseFromString(`<body>${markup}</body>`, "text/html");
    el.replaceChildren(...parsed.body.childNodes);
  }
  if (!S) {
    render(document.querySelector(".main"), '<div class="panel"><h2>No hay snapshot</h2><p>Ejecuta <code>uv run pulso build</code> y recarga.</p></div>');
    return;
  }
  const TOPIC = { economia: "Economía", logistica_canal: "Logística / Canal", turismo: "Turismo", servicios_publicos: "Servicios públicos", eventos_naturales: "Eventos naturales", regulacion: "Regulación", otros: "Otros" };
  const EV = { insuficiente: "Evidencia insuficiente", parcial: "Evidencia parcial", suficiente_para_borrador: "Suficiente para el borrador" };
  const REV = { nuevo: "Nuevo", en_revision: "En revisión", requiere_evidencia: "Requiere evidencia", aprobado_como_borrador: "Aprobado como borrador", descartado: "Descartado" };
  const TRANS = { nuevo: ["en_revision", "descartado"], en_revision: ["requiere_evidencia", "aprobado_como_borrador", "descartado"], requiere_evidencia: ["en_revision", "descartado"], aprobado_como_borrador: ["en_revision"], descartado: ["en_revision"] };
  const COMP = { R: "Relevancia", I: "Impacto potencial", U: "Urgencia", N: "Novedad", E: "Evidencia disponible" };
  const TIPO = { hecho: "Hecho", declaracion: "Declaración", inferencia: "Inferencia", hipotesis: "Hipótesis" };
  const pa = (iso, opts) => iso ? new Date(iso).toLocaleString("es-PA", Object.assign({ timeZone: "America/Panama" }, opts || { dateStyle: "medium", timeStyle: "short" })) : "sin fecha";
  const fichas = S.fichas;
  const byNews = Object.fromEntries(S.noticias.map((n) => [n.id_noticia, n]));
  let current = fichas[0];

  // ---- estado de revisión local (registro exportable) ----
  const KEY = "pulso-revisiones-" + S.meta.fecha_corte_UTC;
  let log = [];
  try { log = JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (_) { log = []; }
  const save = () => { try { localStorage.setItem(KEY, JSON.stringify(log)); } catch (_) {} };
  const stateOf = (f) => { const l = log.filter((r) => r.id_caso === f.id_caso).pop(); return l ? l.estado : f.estado_revision; };

  // ---- cabecera ----
  $("synthetic").hidden = !S.meta.sintetico;
  $("subtitle").textContent = `Corte ${pa(S.meta.fecha_corte_UTC)} (hora de Panamá) · ${S.meta.noticias_validas} noticias válidas agrupadas en ${S.meta.eventos} casos`;
  $("rules").textContent = `${S.meta.version_reglas} · modalidad ${S.meta.modalidad.toUpperCase()}`;
  const stat = (n, l) => `<div class="stat"><div class="n">${n}</div><div class="l">${l}</div></div>`;
  const afirmaciones = fichas.flatMap((f) => f.respaldado || []);
  const afirmacionesCitadas = afirmaciones.filter((a) => (a.citas || []).length).length;
  const coberturaCitas = afirmaciones.length ? Math.round((afirmacionesCitadas / afirmaciones.length) * 100) : 0;
  render($("stats"),
    stat(S.meta.noticias_validas, "Noticias procesadas") +
    stat(fichas.length, "Eventos agrupados") +
    stat(fichas.reduce((n, f) => n + f.fuentes_independientes, 0), "Procedencias en los casos") +
    stat(`${coberturaCitas}%`, "Afirmaciones respaldadas con cita"));
  render($("status"), `<b>Snapshot local</b>Funciona sin internet.<br>Agrupación: ${esc(S.meta.embedder)}<br>Indicadores: ${S.meta.indicadores} · Sismos: ${S.meta.sismos}`);
  const W = S.meta.pesos;
  $("formula").textContent = `P = ${Object.keys(COMP).map((k) => `${W[k]}${k}`).join(" + ")} · bajo <40 · medio 40–69 · alto ≥70 · empate: urgencia, luego ID`;

  // ---- bandeja ----
  const alertCategory = (alerta) => {
    const texto = norm(alerta || "");
    if (/(contradic|incompatibl)/.test(texto)) return { tone: "red", label: "Contradicción" };
    if (/(eco|repetici|replica|procedencia)/.test(texto)) return { tone: "purple", label: "Eco informativo" };
    if (/(contexto|histor|fecha)/.test(texto)) return { tone: "orange", label: "Contexto por verificar" };
    if (/(anomali|inusual)/.test(texto)) return { tone: "blue", label: "Anomalía" };
    if (/(falta|vacio|insuficien|pendiente)/.test(texto)) return { tone: "gray", label: "Verificación pendiente" };
    return { tone: "gray", label: "Alerta" };
  };

  function renderCases() {
    render($("cases"), fichas.map((f) => {
      const category = alertCategory(f.alertas[0]);
      return `<li><button class="case" data-id="${f.id_caso}" aria-pressed="${f === current}">
        <span class="p ${f.banda}">${f.puntaje}<small>${f.banda}</small></span>
        <span><h3>${esc(f.titulo)}</h3><span class="chips">
          <span class="chip">${TOPIC[f.tema]}</span>
          <span class="chip ev-${f.estado_evidencia}">${EV[f.estado_evidencia]}</span>
          <span class="chip">${f.fuentes_independientes} procedencia(s) · ${f.ids_fuente.length} nota(s)</span>
        </span></span>
        <span class="badge ${category.tone}" title="${esc(f.alertas[0] || "Sin alerta específica")}">${category.label}</span>
      </button></li>`;
    }).join(""));
  }
  $("cases").addEventListener("click", (e) => { const b = e.target.closest(".case"); if (b) select(b.dataset.id, true); });

  const cites = (cs) => (cs || []).map((c) => `<span class="cite" title="campo: ${esc(c.campo)}">${esc(c.evidencia_id)}</span>`).join("");
  const claim = (a) => `<li><span class="tag t-${a.tipo}">${TIPO[a.tipo]}</span>${esc(a.texto)}${cites(a.citas)}</li>`;

  function renderDashboard(f) {
    const score = Math.max(0, Math.min(100, Number(f.puntaje) || 0));
    const alerts = f.alertas || [];
    const nodes = Object.entries(f.procedencias || {});
    const notas = nodes.reduce((total, [, ids]) => total + ids.length, 0);
    $("hero-title").textContent = f.titulo;
    $("hero-copy").textContent = f.que_se_reporta || "Sin resumen disponible para el caso seleccionado.";
    render($("hero-badges"), alerts.length
      ? alerts.map((a) => { const c = alertCategory(a); return `<span class="badge ${c.tone}" title="${esc(a)}">${c.label}</span>`; }).join("")
      : '<span class="badge gray">Sin alerta específica</span>');
    $("hero-score").textContent = score;
    $("score-ring").style.setProperty("--score", score);
    $("score-ring").setAttribute("aria-label", `Puntaje de prioridad del caso seleccionado: ${score}, banda ${f.banda}`);

    $("mission-score").textContent = `PULSO ${score}`;
    $("mission-intro").textContent = `Antes de preparar contenido sobre este caso, completa las verificaciones pendientes.`;
    render($("mission-list"), (f.falta_comprobar.length ? f.falta_comprobar : ["No hay verificaciones pendientes registradas."])
      .map((item) => `<li>${esc(item)}</li>`).join(""));
    $("mission-evidence").className = `chip ev-${f.estado_evidencia}`;
    $("mission-evidence").textContent = EV[f.estado_evidencia];

    render($("devil-stats"),
      stat((f.respaldado || []).length, "Respaldadas") +
      stat((f.falta_comprobar || []).length, "Por verificar") +
      stat(alerts.length, "Alertas"));
    $("devil-advice").textContent = f.estado_evidencia === "suficiente_para_borrador"
      ? "La evidencia permite un borrador, pero la revisión humana sigue siendo obligatoria."
      : "Recomendación: no aprobar todavía el borrador hasta resolver la evidencia pendiente.";

    $("map-title").textContent = `Mapa de evidencia — ${TOPIC[f.tema] || "caso seleccionado"}`;
    $("map-summary").textContent = `${notas} publicación(es) · ${f.fuentes_independientes} procedencia(s)`;
    render($("evidence-map"), nodes.length ? nodes.map(([source, ids]) => `<li class="node"><b>${esc(source.replace("agencia:", "Agencia: ").replace("medio:", "Medio: "))}</b>${ids.map((id) => `<span class="cite">${esc(id)}</span>`).join("")}</li>`).join("") : '<li class="node">Sin procedencias registradas.</li>');
    $("map-legend").textContent = `${notas} publicación(es) registradas en ${f.fuentes_independientes} procedencia(s) independiente(s).`;
  }

  function select(id, scroll) {
    current = fichas.find((f) => f.id_caso === id) || fichas[0];
    renderCases();
    const f = current;
    renderDashboard(f);
    $("ficha-id").textContent = f.id_caso;
    $("f-title").textContent = f.titulo;
    render($("f-chips"), `<span class="chip">${TOPIC[f.tema]}</span><span class="chip ev-${f.estado_evidencia}">${EV[f.estado_evidencia]}</span><span class="chip">Primera: ${pa(f.fecha_primera)}</span>`);
    render($("f-alerts"), f.alertas.map((a) => `<p>${esc(a)}</p>`).join(""));
    $("f-que").textContent = f.que_se_reporta;
    $("f-quien").textContent = f.quien_lo_reporta.join(", ") || "Ninguna fuente confiable";
    render($("f-resp"), f.respaldado.length ? `<ul class="claims">${f.respaldado.map(claim).join("")}</ul>` : "Nada respaldado todavía.");
    render($("f-falta"), f.falta_comprobar.length ? `<ul>${f.falta_comprobar.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>` : "Nada pendiente.");
    $("f-accion").textContent = f.accion_recomendada;
    const nNotas = Object.values(f.procedencias).reduce((a, v) => a + v.length, 0);
    $("f-proc-sum").textContent = `${nNotas} publicación(es) → ${f.fuentes_independientes} procedencia(s) independiente(s). La repetición no es corroboración.`;
    render($("f-procs"), Object.entries(f.procedencias).map(([k, ids]) => `<li><b>${esc(k.replace("agencia:", "Agencia: ").replace("medio:", "Medio: "))}</b>
      <div class="ids">${ids.map((i) => `${esc(byNews[i]?.medio || i)} · ${pa(byNews[i]?.fecha_publicacion || byNews[i]?.fecha_deteccion)} <span class="cite">${esc(i)}</span>`).join("<br>")}</div></li>`).join(""));
    render($("f-contra"), f.contradicciones.map((c) => `<div class="box contra"><b>Versiones incompatibles</b> · no se elige ninguna<br>
      ${esc(c.a_medio)}: ${c.a_valor.toLocaleString("es-PA")} ${esc(c.unidad)} <span class="cite">${esc(c.a_id)}</span><br>
      ${esc(c.b_medio)}: ${c.b_valor.toLocaleString("es-PA")} ${esc(c.unidad)} <span class="cite">${esc(c.b_id)}</span></div>`).join(""));
    render($("f-ctx"), f.contexto_oficial.map((c) => c.tipo === "indicador"
      ? `<div class="box"><b>Contexto oficial · Banco Mundial</b> · ${esc(c.indicador)} (${esc(c.pais)}) · unidad: ${esc(c.unidad)} ${c.evidencia_id ? `<span class="cite">${esc(c.evidencia_id)}</span>` : ""}
         ${c.serie ? `<table><tr><th>Año</th>${c.serie.map((s) => `<td>${s[0]}</td>`).join("")}</tr><tr><th>Valor</th>${c.serie.map((s) => `<td>${s[1] === null ? "nulo" : s[1]}</td>`).join("")}</tr></table>` : ""}
         <p class="muted small">${c.limitaciones.map(esc).join(" ")}</p></div>`
      : `<div class="box"><b>Contexto oficial · USGS</b> · M${c.magnitud} · ${esc(c.lugar)} · ${pa(c.fecha)} <span class="cite">${esc(c.evidencia_id)}</span>
         <p class="muted small">${c.limitaciones.map(esc).join(" ")}</p></div>`).join(""));

    $("p-big").textContent = `P ${f.puntaje} · ${f.banda}`;
    render($("breakdown"), Object.keys(COMP).map((k) => `<div><dt>${k} · ${COMP[k]}</dt><dd><i style="width:${Math.round(f.componentes[k] * 100)}%"></i></dd><span>${f.componentes[k].toFixed(2)}</span><p>${esc(f.componentes.justificacion[k] || "")}</p></div>`).join(""));
    renderDraft("brief");
    renderReview();
    if (scroll) document.getElementById("ficha").scrollIntoView({ block: "start" });
  }

  function renderDraft(tab) {
    document.querySelectorAll(".tabs button").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.tab === tab)));
    const b = current.borrador;
    if (!b) {
      $("b-gen").textContent = "abstención";
      render($("b-body"), `<div class="banner">No se genera borrador: ${esc(EV[current.estado_evidencia].toLowerCase())}. Antes, resolver:</div><ul>${current.falta_comprobar.map((x) => `<li>${esc(x)}</li>`).join("")}</ul>`);
      return;
    }
    $("b-gen").textContent = `generado por ${b.generado_por}`;
    const banner = b.aviso_alcance ? `<div class="banner">${esc(b.aviso_alcance)}</div>` : "";
    if (tab === "brief") {
      render($("b-body"), `${banner}<p><b>Título propuesto:</b> ${esc(b.titulo_propuesto)}</p><p><b>Enfoque de interés público:</b> ${esc(b.enfoque_interes_publico)}</p>
        <ul class="claims">${b.brief.map(claim).join("")}</ul>
        <h4>Preguntas de investigación</h4><ol>${b.preguntas.map((q) => `<li>${esc(q)}</li>`).join("")}</ol>
        <h4>Verificaciones pendientes</h4><ul>${b.verificaciones_pendientes.map((q) => `<li>${esc(q)}</li>`).join("")}</ul>
        <h4>Fuentes</h4><ul class="muted small">${b.fuentes.map((q) => `<li>${esc(q)}</li>`).join("")}</ul>`);
    } else if (tab === "guion") {
      render($("b-body"), `${banner}<p class="muted">Duración estimada: ${b.guion_segundos_estimados} s (objetivo 45–60 s, ~150 palabras/min). Sin entrevistas, citas ni imágenes inventadas.</p><ul class="claims">${b.guion.map(claim).join("")}</ul>`);
    } else {
      const n = b.copy_digital.split(/\s+/).filter(Boolean).length;
      render($("b-body"), `${banner}<p>${esc(b.copy_digital)}</p><p class="muted">${n} de 80 palabras máximo.</p>`);
    }
  }
  document.querySelector(".tabs").addEventListener("click", (e) => { if (e.target.dataset.tab) renderDraft(e.target.dataset.tab); });

  // ---- revisión ----
  function renderReview() {
    const st = stateOf(current);
    $("r-state").textContent = REV[st];
    render($("r-actions"), TRANS[st].map((t) => {
      const blocked = t === "aprobado_como_borrador" && current.estado_evidencia === "insuficiente";
      return `<button type="button" class="${t === "descartado" ? "ghost" : ""}" data-to="${t}" ${blocked ? 'disabled title="Evidencia insuficiente: no se puede aprobar"' : ""}>${REV[t]}</button>`;
    }).join(""));
    render($("r-log"), log.filter((r) => r.id_caso === current.id_caso).map((r) => `<li>${pa(r.fecha_UTC)} · ${esc(r.revisor)}: ${REV[r.de]} → ${REV[r.estado]}${r.nota ? " · " + esc(r.nota) : ""}</li>`).join(""));
  }
  $("r-actions").addEventListener("click", (e) => {
    const to = e.target.dataset.to;
    if (!to) return;
    const who = $("revisor").value.trim();
    if (!who) { $("r-msg").textContent = "Indica la persona revisora responsable."; $("revisor").focus(); return; }
    const decision = to === "descartado" ? "descarte" : to === "aprobado_como_borrador" ? "aceptacion" : "correccion";
    log.push({ id_caso: current.id_caso, de: stateOf(current), estado: to, revisor: who, decision, nota: $("nota").value.trim(), puntaje: current.puntaje, version_reglas: current.version_reglas, fecha_UTC: new Date().toISOString().replace(/\.\d+Z$/, "Z") });
    save();
    $("nota").value = "";
    $("r-msg").textContent = `Registrado: ${REV[to]}.`;
    renderCases(); renderReview();
  });
  $("r-export").addEventListener("click", () => {
    const blob = new Blob([log.map((r) => JSON.stringify(r)).join("\n") + "\n"], { type: "application/x-ndjson" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob); a.download = "revisiones_pulso.jsonl"; a.click();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });

  // ---- consultas ----
  const served = location.protocol === "http:" || location.protocol === "https:";
  $("chat-mode").textContent = served ? "motor local completo" : "modo archivo: respuestas precalculadas y reglas";
  const norm = (t) => t.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
  const normPy = (t) => norm(t).replace(/\s+/g, " ").trim();
  function fallback(q) {
    const qn = norm(q);
    const pre = (S.respuestas || {})[normPy(q)];
    if (pre) return pre;
    if (/(revela|muestra|dime).*(prompt|instrucciones|clave|token|secreto)|ignora.*(reglas|instrucciones)|(marca|declara).*(falsa|verdadera)/.test(qn))
      return { respuesta: "No puedo revelar instrucciones ni cambiar reglas, y no etiqueto noticias como verdaderas o falsas.", citas: [], abstencion: true };
    if (/(cinco temas|5 temas|agenda|priorid|merecen)/.test(qn))
      return { respuesta: fichas.slice(0, 5).map((f, i) => `${i + 1}. ${f.titulo} — P${f.puntaje} (${f.banda}), ${EV[f.estado_evidencia].toLowerCase()}. Falta: ${f.falta_comprobar[0] || "nada"}`).join("\n"), citas: fichas.slice(0, 5).map((f) => f.id_caso), abstencion: false };
    // palabras distintivas: se ignoran las que aparecen en muchos casos (p. ej. "panama")
    const df = (w) => fichas.filter((f) => norm(f.titulo + " " + TOPIC[f.tema]).includes(w)).length;
    const terms = qn.split(/[^a-z0-9ñ]+/).filter((w) => w.length > 4 && df(w) > 0 && df(w) <= Math.max(1, fichas.length * 0.3));
    let best = null, bestScore = 0;
    for (const f of fichas) {
      const t = norm(f.titulo + " " + TOPIC[f.tema]);
      const s = terms.filter((w) => t.includes(w)).length;
      if (s > bestScore) { best = f; bestScore = s; }
    }
    if (!best || bestScore < 1) return { respuesta: "No tengo evidencia en el corpus para responder eso. En modo archivo solo busco por palabras; usa `pulso serve` para el motor completo.", citas: [], abstencion: true };
    select(best.id_caso, false);
    return { respuesta: `${best.titulo} — ${EV[best.estado_evidencia]}. Falta: ${best.falta_comprobar.slice(0, 2).join("; ") || "nada"}`, citas: [best.id_caso], abstencion: false };
  }
  function bubble(cls, markup) { const d = document.createElement("div"); d.className = "bubble " + cls; render(d, markup); $("chatlog").appendChild(d); $("chatlog").scrollTop = $("chatlog").scrollHeight; }
  async function ask(q) {
    if (!q.trim()) return;
    bubble("q", esc(q));
    let r;
    if (served) {
      try { r = await (await fetch("/api/ask?q=" + encodeURIComponent(q))).json(); } catch (_) { r = fallback(q); }
    } else r = fallback(q);
    const cs = (r.citas || []).map((c) => `<span class="cite">${esc(c)}</span>`).join("");
    bubble("a" + (r.abstencion ? " abst" : ""), `${esc(r.respuesta)}<small>${r.abstencion ? "Abstención" : "Citas:"} ${cs}${r.ms !== undefined ? ` · ${r.ms} ms` : ""}</small>`);
    const hit = (r.citas || []).find((c) => fichas.some((f) => f.id_caso === c));
    if (hit && !/(cinco|agenda|priorid)/.test(norm(q))) select(hit, false);
  }
  $("ask-form").addEventListener("submit", (e) => { e.preventDefault(); ask($("q").value); $("q").value = ""; });
  const SUG = Object.keys(S.respuestas || {}).length ? S.meta.sugeridas : [];
  render($("suggest"), SUG.map((t) => `<button type="button">${esc(t)}</button>`).join(""));
  $("suggest").addEventListener("click", (e) => { if (e.target.tagName === "BUTTON") ask(e.target.textContent); });

  // ---- calidad ----
  render($("quality-body"), Object.entries(S.calidad).map(([arch, q]) => `<div class="qfile"><b>${esc(arch)}</b>: ${q.validas}/${q.leidas} válidas · ${q.errores.length} con error
    ${Object.keys(q.nulos).length ? ` · nulos conservados: ${esc(Object.entries(q.nulos).map(([k, v]) => `${k} ${v}`).join(", "))}` : ""}
    ${q.errores.length ? `<ul>${q.errores.map((e) => `<li>Fila ${e.fila}: ${esc(e.motivo)} ${esc(e.id || "")}</li>`).join("")}</ul>` : ""}</div>`).join(""));

  document.querySelectorAll(".nav a").forEach((a) => a.addEventListener("click", () => document.querySelectorAll(".nav a").forEach((x) => x.classList.toggle("active", x === a))));
  select(fichas[0].id_caso, false);
})();
