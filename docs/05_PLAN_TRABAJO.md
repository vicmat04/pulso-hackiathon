# 05 · Plan de trabajo (evento de 3 días)

Copiar esta tabla como base de datos **Plan y decisiones** en Notion (≥8 tareas exigidas) y
actualizar estado y responsable durante el evento, no al final.

## Antes del evento
| ID | Tarea | Hecho cuando |
|---|---|---|
| P0.1 | Enviar las preguntas de `09_PREGUNTAS_ORGANIZACION.md` | Respuestas anotadas en Notion |
| P0.2 | Confirmar acceso Notion Business para equipo y jurado | Invitaciones aceptadas, permisos probados |
| P0.3 | `uv sync && make demo && make test` en todos los portátiles | 20 pruebas en verde en cada equipo |
| P0.4 | Crear repositorio GitHub con acceso al jurado | URL en Inicio del reto |

## Día 1 · Datos y diseño (≈35%)
| ID | Tarea | Responsable | Hecho cuando |
|---|---|---|---|
| D1.1 | Copiar paquete oficial a `data/oficial/`, `PULSO_DATA=data/oficial`, `pulso manifest` | Datos | SHA-256 en Catálogo de datos |
| D1.2 | `pulso calidad` y revisar errores | Datos | Reporte de calidad en Notion |
| D1.3 | Etiquetar ≥50 noticias (tema y evento) en `etiquetas.csv` con método declarado | Editorial | Archivo + método en Notion |
| D1.4 | Ajustar `TOPIC_KEYWORDS`, `IMPACT_BASE`, `AGENCIES` al corpus real | Producto | Decisión registrada |
| D1.5 | Calibrar `PULSO_CLUSTER_DISTANCE` con etiquetas (mejor F1 de pares) | IA | Decisión con números |
| D1.6 | Probar `PULSO_EMBED=st` con un modelo multilingüe y comparar con TF-IDF | IA | Tabla IA vs baseline |
| D1.7 | Crear las 8 páginas de Notion (`07_NOTION.md`) | Coordinación | Estructura visible |

## Día 2 · Producto funcional (≈40%)
| ID | Tarea | Hecho cuando |
|---|---|---|
| D2.1 | `pulso build` con datos oficiales; revisar top 10 con la persona editorial | Notas de revisión |
| D2.2 | Revisar contexto oficial: ningún dato anual presentado como de hoy | T04 pasa con datos reales |
| D2.3 | (Opcional) LLM para reescribir brief; medir validez vs plantilla | Tabla con costo y tokens |
| D2.4 | Revisar ≥5 fichas en la interfaz, una con evidencia insuficiente; registrar decisiones | 5 fichas en Casos y evidencias |
| D2.5 | Publicación diaria en LinkedIn (`08_REDES.md`) | Enlace en Notion |

## Día 3 · Pruebas y cierre (≈25%)
| ID | Tarea | Hecho cuando |
|---|---|---|
| D3.1 | `pulso aceptacion` y `pulso bench` con datos oficiales y benchmark de desarrollo (40) | Matriz T01–T10 y métricas en Notion |
| D3.2 | Registrar al menos una prueba fallida real y su corrección | Fila en Pruebas y métricas |
| D3.3 | Validez de sustento: persona revisa ≥30 afirmaciones | Numerador/denominador |
| D3.4 | Precision@5 con selección independiente de la persona editorial | Valor o "exploratoria" |
| D3.5 | Medir tiempo manual vs asistido en una tarea equivalente (n declarado) | Tabla |
| D3.6 | `make notion`, importar CSV/MD, completar pitch | Pitch navegable |
| D3.7 | Ensayo con wifi apagado (`04_OFFLINE.md`) | Evidencia T10 en Notion |

## Prompts para tu agente de CLI
1. "Lee CLAUDE.md y docs/. Ejecuta `make demo` y `make test` y resume el estado."
2. "Tengo el paquete oficial en data/oficial. Ejecuta `pulso calidad` con PULSO_DATA=data/oficial,
   explica cada tipo de error y propone si alguno es un problema del cargador, sin cambiar reglas."
3. "Con data/oficial/etiquetas.csv, prueba PULSO_CLUSTER_DISTANCE entre 0.6 y 0.9 en pasos de
   0.02 y dame precisión/recall por pares. No cambies el valor por defecto; escribe la tabla en
   reports/calibracion.md."
4. "Activa PULSO_EMBED=st con el modelo de PULSO_ST_MODEL, repite `pulso bench` y compara con
   tfidf en una tabla. Si el modelo no está descargado, detente y dímelo."
5. "Un caso de prueba falló: <describir>. Reprodúcelo con un test, corrígelo y deja la
   explicación en docs/DECISIONES.md."
