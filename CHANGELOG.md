# 📑 CHANGELOG — Calculadora Hipotecaria Profesional

## [Unreleased]

---

## [1.2.0] - 2025-11-08
### Fixed
- 🔧 **Corregido cálculo de hipotecas mixtas**: ahora calcula las cuotas con el plazo completo para ambos tramos, eliminando DTI >100% y haciendo los cálculos matemáticamente coherentes.
- 🧹 **Eliminado código obsoleto del validador dual**: removido completamente el validador antiguo que causaba errores `NameError` y conflictos en la ejecución.

### Added
- 🧪 **Implementado validador profesional completo**: nueva herramienta de testing automático que valida 12 escenarios hipotecarios (fijos, variables y mixtos) con reporte detallado de errores y advertencias.
- ✅ **Mejoras en coherencia matemática**: DTI y LTV perfectamente alineados en todos los escenarios de uso y tipos de hipoteca.
- Reformulado el mensaje de entrada para mayor claridad visual: ahora el excedente se muestra al final del texto.

### Changed
- 🎯 **Optimización para release**: código depurado, estable y listo para producción con validación robusta.
- 📊 **Mejorada precisión en cálculos**: ajustes finos en fórmulas matemáticas para mayor exactitud.

---

## [1.1.5] - 2025-11-06
### Changed
- Ajustada la lógica de entrada y capital financiado:
  - Ahora se distingue correctamente entre hipoteca normal, hipoteca reducida y compra al contado.
  - Evita mostrar "No disponible" cuando la entrada cubre el precio completo de la vivienda (se indica que no se requiere hipoteca).
- Mensajes más claros y pedagógicos en todos los escenarios de entrada, LTV y DTI.
- Integración completa en el Modo 2:
  - Escenarios de interés, consejos de viabilidad, amortización anticipada y resumen compacto coherentes incluso sin hipoteca.
- Mejorada la consistencia visual y narrativa en los bloques de coste total, tablas de amortización y resúmenes.

---

## [1.1.4] - 2025-11-06
### Changed
- Mejorado el contraste de colores en las tablas de coste total, compra y pagos al banco.
- Los resaltados ahora se ven correctamente tanto en tema claro como en tema oscuro.

---

## [1.1.3] - 2025-11-05
### Fixed
- Corregida la **tabla de amortización simplificada en hipotecas mixtas**, que antes mostraba todo el tramo variable con valores a 0 €.
- Ajustado el **cálculo de hipoteca mixta**:
  - El tramo fijo ahora se calcula con el plazo total, evitando amortizar todo el capital en los primeros años.
  - El tramo variable se recalcula correctamente con el capital pendiente al final del tramo fijo y el plazo restante.


---

## [1.1.2] - 2025-11-05
### Changed
- Lista de comunidades autónomas homogeneizada (ej. “Illes Balears” → “Baleares”, “Comunidad Valenciana” → “Valencia”).
- Desplegable de CCAA ahora ordenado alfabéticamente.
- Eliminado selector duplicado en la parte superior; ahora solo aparece en el sidebar.

---

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
