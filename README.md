# 🏠 Calculadora Hipotecaria Profesional

Aplicación interactiva en **Python + Streamlit** para simular hipotecas en España de forma clara y práctica.  

---

## ✨ Qué puedes hacer con esta calculadora

- 🔎 **Descubrir tu precio máximo de vivienda** según sueldo, deudas y entrada.  
- 🏠 **Comprobar una vivienda concreta** y ver si la operación es viable.  
- 📊 **Explorar escenarios de tipos de interés** (fijo, variable o mixto).  
- ✅ **Revisar ratios clave**: LTV (Loan To Value) y DTI (Debt To Income).  
- ⚖️ **Calcular impuestos y gastos** según tu comunidad autónoma.  

---

## 🌐 Probar la aplicación online

Puedes probar la calculadora directamente desde tu navegador, sin necesidad de instalar nada:  
👉 https://calculadorahipotecapro.streamlit.app/

---

## 🚀 Cómo usarla en local

### 1️⃣ Clona el repositorio y entra en la carpeta

```bash
git clone https://github.com/Letalicus/calculadora_hipoteca.git
cd calculadora_hipoteca
```

### 2️⃣ Instala las dependencias

```bash
pip install -r requirements.txt
```

### 3️⃣ Ejecuta la aplicación

```bash
streamlit run app.py
```

Abre en tu navegador la URL que aparece (por defecto):  
👉 http://localhost:8501

---

## 🌐 Versión online

También puedes desplegarla fácilmente en **Streamlit Cloud** y acceder desde cualquier navegador.  
Solo necesitas tener una cuenta gratuita en 👉 https://streamlit.io/cloud

---

📌 Versión actual  
v1.2.0 — 2025-11-08  

### ✨ **Novedades principales**
- 🔧 **Corregido cálculo de hipotecas mixtas**: ahora calcula las cuotas con el plazo completo para ambos tramos, eliminando DTI >100% y haciendo los cálculos matemáticamente coherentes.
- 🧪 **Implementado validador profesional completo**: nueva herramienta de testing automático que valida 12 escenarios hipotecarios (fijos, variables y mixtos) con reporte detallado de errores y advertencias.
- 🧹 **Código limpio y optimizado**: eliminado código obsoleto, depurados errores y optimizado para producción.
- ✅ **Mejoras en coherencia matemática**: DTI y LTV perfectamente alineados en todos los escenarios de uso y tipos de hipoteca.

### 🛠️ **Mejoras técnicas**
- Validación robusta de escenarios hipotecarios
- Precisión mejorada en fórmulas matemáticas
- Código estable y listo para producción   

📖 Consulta el historial completo de cambios en el archivo CHANGELOG.md.

---

## 👤 Autor

**Letalicus**  
📍 España

---

## 📜 Licencia

Este proyecto se distribuye bajo la licencia **MIT**.  
Consulta el archivo LICENSE para más detalles.

---
