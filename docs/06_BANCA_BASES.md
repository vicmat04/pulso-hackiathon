# 06 · Banca: base preparada, fuera de esta vuelta

Las bases admiten banca "como alternativa o extensión, sin exigir dos productos completos" y
recomiendan "limitarse a una modalidad". Por eso esta vuelta es **solo TVN**.

## Qué pediría la modalidad bancaria (bases)
- Usuario: analista de estudios económicos o riesgo sectorial.
- CU-05: "¿Qué señales públicas del entorno logístico debo revisar?" → contexto sectorial,
  **no** un score de clientes ni una alerta regulatoria definitiva.
- Salida: boletín de entorno ≤250 palabras, sectores potencialmente relacionados, horizonte
  temporal, evidencia y 3 preguntas; separar observación de hipótesis de impacto.
- Prohibido: recomendar compra/venta, inferir pérdidas, impagos o exposición de una cartera
  inexistente; usar datos de clientes; presentar análisis propio como opinión de la SBP.
- Datos D (opcional): 12 informes mensuales de la Superintendencia de Bancos de Panamá con
  período, unidad y página de origen.

## Qué queda listo en el código
| Pieza | Estado |
|---|---|
| `config.MODALIDAD` y `config.VERTICALS["banca"] = False` | Desactivado; test lo verifica |
| `pulso/verticals/banca/` con interfaz `Vertical` | Contrato definido, métodos lanzan `NotImplementedError` |
| Núcleo reutilizable | Carga, agrupación, procedencias, contexto Banco Mundial, puntaje, revisión: sirven igual |
| `Ficha.modalidad` | Ya existe en el contrato de `fichas.jsonl` |

## Cuando se active (próxima vuelta)
1. `pulso/verticals/banca/bulletin.py`: boletín con secciones Observaciones (hechos citados),
   Hipótesis de impacto (marcadas), Sectores, Horizonte, 3 preguntas.
2. Cargador de series SBP (`sbp.csv`: periodo, serie, valor, unidad, url, pagina).
3. Pesos de puntaje propios por modalidad (nueva versión de reglas, documentada).
4. Pruebas: el boletín nunca contiene verbos de recomendación ("comprar", "vender",
   "reducir exposición") ni cifras de clientes.
