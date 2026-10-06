# 02 · Producto: PULSO, de la señal a la decisión

## En una frase
PULSO convierte noticias públicas e indicadores oficiales en una **bandeja priorizada de temas
para la sala de TVN**, cada uno con una **ficha de evidencia trazable** y un **borrador
responsable**, y deja la decisión a una persona editora.

## Modalidad y usuario
- **Modalidad:** TVN · principal (editor/a y periodista). TVN · digital se cubre con el copy de
  ≤80 palabras. **Banca:** solo base técnica (`06_BANCA_BASES.md`).
- **Usuario primario:** editor/a de turno que arma la agenda del día.
- **Trabajo que resuelve:** pasar de fuentes dispersas a un tema investigable sabiendo qué está
  respaldado, qué falta y qué hacer.

## Recorrido de extremo a extremo (las 7 etapas)
| Etapa | En PULSO | Comando / pantalla |
|---|---|---|
| 1 Cargar | Valida IDs, URLs, fechas, obligatorios, nulos; reporte de calidad | `pulso calidad` · panel Calidad |
| 2 Organizar | Tema por similitud semántica; agrupa notas del mismo evento | `pulso build` |
| 3 Contextualizar | Une con Banco Mundial (período, unidad, limitaciones) o USGS; no fuerza | Ficha · Contexto oficial |
| 4 Priorizar | P = 30R+25I+20U+15N+10E con justificación; banda; desempate | Bandeja · Puntaje desglosado |
| 5 Explicar | Qué se reporta, quién, qué está respaldado, qué falta, acción | Ficha |
| 6 Producir | Brief, título, enfoque, 3 preguntas, guion, copy, citas por afirmación | Borrador |
| 7 Revisar | Aceptar, corregir o descartar con persona responsable | Revisión · `pulso revisar` · Notion |

## Casos de uso
| CU | Cómo se demuestra |
|---|---|
| CU-01 cinco temas | Consulta sugerida 1: ranking con P, banda, evidencia y vacío principal |
| CU-02 tema económico + serie | Caso desempleo: dato anual 2023 con unidad; 2024 nulo no se rellena |
| CU-03 repetición vs corroboración | Cruceros: 5 notas de Agencia X → 1 procedencia |
| CU-04 cifra inexistente / contradicción | "precio del bitcoin" → abstención; agua: 30 mil vs 8 mil sin elegir |
| CU-05 banca | Fuera de esta vuelta; base preparada |

## Guion del pitch (10 minutos, desde Notion)
| Min | Contenido | Qué se ve |
|---|---|---|
| 0–1 | Problema: 5 medios repiten una agencia y parece confirmado | Página Inicio del reto |
| 1–2 | Solución y alcance; datos públicos usados | Catálogo de datos (SHA-256) |
| 2–6 | **Demo**: consulta CU-01 → ficha del agua (contradicción) → borrador económico con cita y año → abstención (bitcoin) → inyección rechazada. **Wifi apagado.** | Prototipo (enlace desde Notion) |
| 6–8 | Arquitectura, IA usada, baseline y métricas reales con numerador/denominador | Diseño de solución · Pruebas y métricas |
| 8–9 | Valor: tiempo manual vs asistido en una tarea equivalente (medirlo) o hipótesis declarada | Casos y evidencias |
| 9–10 | Riesgos, límites, próximos pasos (embeddings multilingües, banca) | Riesgos y ética |

## Respuestas preparadas para las pruebas dinámicas del jurado
- **"¿De dónde viene esta cifra y de qué año es?"** → clic en la cita `ind:PAN:SL.UEM.TOTL.ZS:2023`:
  país, año, unidad, URL de fuente y limitación "dato anual".
- **"Si cinco medios replican la misma agencia, ¿cuántas fuentes independientes?"** → Una. Caso
  cruceros: 5 notas → `agencia:Agencia X (5)`; evidencia insuficiente; no se genera borrador.
- **"¿Y si no hay evidencia o una fuente intenta cambiar instrucciones?"** → Abstención explícita
  (T06) y caso N060 marcado "contenido no confiable", excluido del borrador (T07).
- **"Muéstrame una decisión, una prueba fallida y su corrección en Notion"** → tenerlas
  registradas de verdad durante el evento (ver `07_NOTION.md`, sección "Bitácora").

## Qué no hace (y se dice en el pitch)
No detecta noticias falsas, no etiqueta verdadero/falso, no publica, no mide audiencia, no lee
contenido tras paywall, no perfila personas, no inventa entrevistas, citas ni imágenes.
