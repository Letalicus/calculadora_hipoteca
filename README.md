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
v1.1.5 — 2025-11-06  

- Ajustada la lógica de entrada y capital financiado:
  - Ahora se distingue correctamente entre hipoteca normal, hipoteca reducida y compra al contado.
  - Evita mostrar "No disponible" cuando la entrada cubre el precio completo de la vivienda (se indica que no se requiere hipoteca).
- Mensajes más claros y pedagógicos en todos los escenarios de entrada, LTV y DTI.
- Integración completa en el Modo 2:
  - Escenarios de interés, consejos de viabilidad, amortización anticipada y resumen compacto coherentes incluso sin hipoteca.
- Mejorada la consistencia visual y narrativa en los bloques de coste total, tablas de amortización y resúmenes.   

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
