# Benchmark (dev) · reglas-v1.0

| Métrica | Resultado |
|---|---|
| Aciertos | 14/14 (1.0) |
| Abstención correcta (sin respuesta) | 4/4 (1.0) |
| Rechazo adversarial | 2/2 (1.0) |
| Abstención incorrecta en respondibles | 0/8 (0.0) |
| Cobertura de citas (respuestas emitidas) | 8/8 (1.0) |
| Latencia mediana / p95 (ms) | 0.1 / 0.5 |


## IA vs baseline

Etiquetas: 18 · embedder: tfidf-char3-5

| Tarea | IA | Baseline |
|---|---|---|
| Clasificación temática (macro-F1) | 0.937 | 1.0 |
| Agrupación (precisión / recall por pares) | 1.0 / 0.833 | 1.0 / 1.0 |
