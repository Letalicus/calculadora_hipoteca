# 📑 CHANGELOG — Calculadora Hipotecaria Profesional

## [1.1.2] - 2025-11-05
### Changed
- Lista de comunidades autónomas homogeneizada (ej. “Illes Balears” → “Baleares”, “Comunidad Valenciana” → “Valencia”).
- Desplegable de CCAA ahora ordenado alfabéticamente.
- Eliminado selector duplicado en la parte superior; ahora solo aparece en el sidebar.



## [1.1.1] — 2025-11-05
### Mejoras y cambios principales
- **Nueva opción de uso de la vivienda en el sidebar:**
  - 🏠 Vivienda habitual → mantiene LTV máx. 80 % y plazo máx. 30 años.
  - 🏖️ Segunda residencia / inversión → ajusta LTV máx. a 70 % y plazo máx. a 25 años.
  - Se aplica como **preset inicial**, pero el usuario puede modificar libremente los sliders después.
- **Mensaje contextual en pantalla principal:**
  - Explica las diferencias de condiciones bancarias entre vivienda habitual y segunda residencia.
  - Refuerza la pedagogía para que el usuario entienda por qué cambian los parámetros.
- **Conservadas todas las mejoras de la versión 1.1.0:**
  - Validación unificada con `es_viable()` en todos los modos.
  - Escenarios de interés, resúmenes y consejos alineados con la validación centralizada.
  - Avisos pedagógicos en el límite del 35,00 % de DTI.
  - Guías actualizadas y coherencia visual en ratios DTI/LTV.

---

## [1.1.0] — 2025-11-05
### Mejoras y cambios principales
- **Unificación de validación con `es_viable()`:**
  - Criterio único: cuota ≤ cuota máx., LTV ≤ LTV máx., DTI visible ≤ 35 %.
  - Aplicado coherentemente en 🔎 Descubrir mi precio máximo, 🏠 Comprobar una vivienda concreta, escenarios de interés, resúmenes y consejos.
- **Eliminación de parches antiguos:**
  - Retirado el “parche visual” que forzaba verde cuando el precio coincidía con el máximo de 🔎 Descubrir.
- **Reescritura de bloques clave:**
  - Escenarios de interés (ambos modos) ahora usan `es_viable()`.
  - 🧮 Resumen compacto muestra siempre veredicto claro (✅/❌) y añade aviso pedagógico en el límite exacto del 35,00 %.
  - 💡 Consejos alineados con `es_viable()` y con aviso específico cuando el DTI visible = 35,00 %.
- **Guías actualizadas:**
  - 🏠 Comprobar una vivienda concreta incluye nota sobre el límite del precio de 🔎 Descubrir.
  - 🔎 Descubrir mi precio máximo aclara que el resultado es una referencia aproximada y recomienda dejar un margen de seguridad.
- **Coherencia visual del DTI:**
  - `pct_dti` y `dti_visible` sincronizados (ceil a 2 decimales) para evitar contradicciones entre lo mostrado y lo evaluado.

---

## [1.0.0] — 2025-11-04
### Publicación inicial en repositorio limpio (fase privada)
- Se establece esta versión como baseline (v1.0.0).
- Incluye todas las funcionalidades actuales:
  - Cálculo de precio máximo de vivienda.
  - Comprobación de viabilidad de una vivienda concreta.
  - Evaluación conjunta de ratios LTV y DTI.
  - Escenarios de tipos de interés (fijo, variable, mixto).
  - Cálculo de impuestos y gastos por CCAA.
- A partir de aquí, el changelog reflejará solo nuevas mejoras.
