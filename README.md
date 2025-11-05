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
👉 [https://calculadorahipotecapro.streamlit.app/](https://calculadorahipotecapro.streamlit.app/)

---

## 🚀 Cómo usarla

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
👉 [http://localhost:8501](http://localhost:8501)

---

## 🌐 Versión online

También puedes desplegarla fácilmente en **Streamlit Cloud** y acceder desde cualquier navegador.  
Solo necesitas tener una cuenta gratuita en 👉 [https://streamlit.io/cloud](https://streamlit.io/cloud)

---

📌 Versiones

Versión actual: v1.1.1 — Uso de vivienda habitual vs. segunda residencia

Nueva opción en el sidebar para indicar si la vivienda es habitual o segunda residencia/inversión.

Ajuste automático de parámetros iniciales:

🏠 Vivienda habitual → LTV máx. 80 %, plazo máx. 30 años.

🏖️ Segunda residencia → LTV máx. 70 %, plazo máx. 25 años.

Mensaje contextual explicando las diferencias de condiciones bancarias.

Conservadas todas las mejoras de la versión 1.1.0.

📌 Versión anterior: v1.1.0 — Validación unificada y mejoras pedagógicas

Validación centralizada con es_viable() en todos los modos y escenarios.

🧮 Resumen compacto con veredicto claro (✅/❌) y aviso pedagógico en el límite del 35,00 %.

💡 Consejos coherentes con es_viable() y aviso específico en el 35,00 %.

Guías actualizadas en 🔎 Descubrir mi precio máximo y 🏠 Comprobar una vivienda concreta para explicar el límite y recomendar margen de seguridad.

Coherencia visual del DTI garantizada (pct_dti y dti_visible sincronizados).

📌 Versión inicial: v1.0.0 — Publicación inicial en repositorio limpio (fase privada)

Baseline inicial con todas las funcionalidades principales.

Repositorio privado hasta futura publicación pública.

---

## 👤 Autor

**Letalicus**  
📍 *España*
