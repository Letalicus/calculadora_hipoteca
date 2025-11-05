# ============================================================
# 🏠 Calculadora Hipotecaria Profesional
# Versión: 1.1.0
# Fecha: 2025-11-05
# Autor: Letalicus
#
# 📌 Resumen de cambios en esta versión:
# - Unificación de la validación con función centralizada `es_viable()`:
#   • Criterio único: cuota ≤ cuota máx., LTV ≤ LTV máx., DTI visible ≤ 35 %
#   • Aplicado coherentemente en 🔎 Descubrir mi precio máximo, 🏠 Comprobar una vivienda concreta,
#     escenarios de interés, resúmenes y consejos
# - Eliminación del antiguo “parche visual” ligado al precio máximo de 🔎 Descubrir
# - Reescritura de bloques:
#   • Escenarios de interés (ambos modos) ahora usan `es_viable()`
#   • 🧮 Resumen compacto muestra veredicto claro (✅/❌) y aviso pedagógico en el límite de 35,00 %
#   • 💡 Consejos alineados con `es_viable()` y aviso específico cuando el DTI visible = 35,00 %
# - Guías actualizadas:
#   • 🏠 Comprobar una vivienda concreta incluye nota sobre el límite del precio de 🔎 Descubrir
#   • 🔎 Descubrir mi precio máximo aclara que el resultado es una referencia aproximada
#     y recomienda dejar un margen de seguridad
# - Limpieza y coherencia visual del DTI:
#   • `pct_dti` y `dti_visible` sincronizados (ceil a 2 decimales) para evitar contradicciones
# ============================================================








import streamlit as st
from math import isclose

# =========================
# Umbrales globales de DTI
# =========================
DTI_WARN = 0.30   # ≤ 30% → Seguro
DTI_FAIL = 0.35   # ≤ 35% → Moderado; > 35% → Arriesgado


# =========================
# Configuración inicial
# =========================
st.set_page_config(page_title="Calculadora Hipotecaria Profesional", page_icon="🏠", layout="wide")
st.title("🏠 Calculadora Hipotecaria Profesional")



# =========================
# Utilidades de formato
# =========================
import math

def eur(x):
    if x is None:
        return "—"
    return f"{x:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(x):
    if x is None:
        return "—"
    return f"{x*100:.2f}%".replace(".", ",")

def pct_dti(dti_val):
    """Muestra el DTI redondeado hacia arriba a 2 decimales para evitar contradicciones visuales."""
    if dti_val is None:
        return "—"
    # Ceil a dos decimales en porcentaje: 0.35000004 → 35.01 %
    val = math.ceil(dti_val * 10000) / 100
    return f"{val:.2f}%".replace(".", ",")

def dti_visible(dti_val):
    """Devuelve el DTI visible como proporción (0–1) alineada con pct_dti."""
    if dti_val is None:
        return None
    val_pct = math.ceil(dti_val * 10000) / 100  # ej. 35.01 (%)
    return val_pct / 100  # 0.3501

def semaforo_dti(dti_val):
    """Clasifica el DTI en Seguro, Moderado o Arriesgado con coherencia visual."""
    dv = round(dti_val, 4)  # valor lógico interno
    if dv <= DTI_WARN:
        return f"🟢 {pct_dti(dv)} (Seguro)"
    elif dv <= DTI_FAIL:
        return f"🟡 {pct_dti(dv)} (Moderado)"
    else:
        return f"🔴 {pct_dti(dv)} (Arriesgado)"

def es_viable(cuota, cuota_max, ltv_val, ltv_max, dti_val):
    """
    Valida la operación usando los mismos criterios que ve el usuario:
    - Cuota ≤ cuota máxima
    - LTV ≤ LTV máximo
    - DTI visible (redondeado hacia arriba a 2 decimales) ≤ 35 %
    """
    return (
        cuota <= cuota_max
        and ltv_val <= ltv_max
        and dti_visible(dti_val) <= DTI_FAIL
    )



# =========================
# Escenarios de interés (2% a 5% en pasos de 0,5%)
# =========================
ESCENARIOS_INTERES_PCT = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]  # porcentaje mostrado al usuario


# =========================
# Cálculos financieros
# =========================
def cuota_prestamo(capital, interes_anual, anos):
    n = int(anos * 12)
    if n <= 0 or capital is None or capital <= 0:
        return None
    r = interes_anual / 12.0
    if isclose(r, 0.0, abs_tol=1e-12):
        return capital / n
    return capital * (r / (1 - (1 + r) ** (-n)))

def cuota_maxima(sueldo_neto_mensual, deudas_mensuales, ratio=0.35):
    return max(0.0, sueldo_neto_mensual * ratio - deudas_mensuales)

def dti(cuota_hipoteca, deudas_mensuales, sueldo_neto_mensual):
    if sueldo_neto_mensual <= 0:
        return 0.0
    val = (cuota_hipoteca + deudas_mensuales) / sueldo_neto_mensual
    return round(val, 6)  # redondeamos a 6 decimales para evitar errores de precisión



# =========================
# Presets fiscales (simplificados y coherentes)
# =========================
PRESETS_IMPUESTOS = {
    "Madrid": {"nuevo": {"iva": 0.10, "ajd": 0.007}, "segunda": {"itp": 0.06}},
    "Cataluña": {"nuevo": {"iva": 0.10, "ajd": 0.015}, "segunda": {"itp": 0.10}},
    "Andalucía": {"nuevo": {"iva": 0.10, "ajd": 0.015}, "segunda": {"itp": 0.08}},
    "Comunidad Valenciana": {"nuevo": {"iva": 0.10, "ajd": 0.015}, "segunda": {"itp": 0.10}},
    "País Vasco": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.04}},
    "Navarra": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.06}},
    "Galicia": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.09}},
    "Castilla y León": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Castilla-La Mancha": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.09}},
    "Murcia": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "La Rioja": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.07}},
    "Cantabria": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.10}},
    "Aragón": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Asturias": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Illes Balears": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Extremadura": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Ceuta y Melilla": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.06}},
    "Canarias": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.06}},  # simplificado
}

def tipo_impuesto_por_ccaa(ccaa, estado):
    data = PRESETS_IMPUESTOS.get(ccaa, PRESETS_IMPUESTOS["Madrid"])
    if estado == "Nuevo":
        return data["nuevo"]["iva"] + data["nuevo"]["ajd"]
    else:
        return data["segunda"]["itp"]

# =========================
# Explicaciones fiscales (alineadas con presets)
# =========================
EXPLICACION_IMPUESTOS = {
    ("Madrid", "Nuevo"): "En Madrid (obra nueva) se aplica IVA 10% + AJD 0,7%.",
    ("Madrid", "Segunda mano"): "En Madrid (segunda mano) se aplica ITP 6%.",
    ("Cataluña", "Nuevo"): "En Cataluña (obra nueva) se aplica IVA 10% + AJD 1,5%.",
    ("Cataluña", "Segunda mano"): "En Cataluña (segunda mano) se aplica ITP 10%.",
    ("Andalucía", "Nuevo"): "En Andalucía (obra nueva) se aplica IVA 10% + AJD 1,5%.",
    ("Andalucía", "Segunda mano"): "En Andalucía (segunda mano) se aplica ITP 8%.",
    ("Comunidad Valenciana", "Nuevo"): "En C. Valenciana (obra nueva) IVA 10% + AJD 1,5%.",
    ("Comunidad Valenciana", "Segunda mano"): "En C. Valenciana (segunda mano) ITP 10%.",
    ("País Vasco", "Nuevo"): "En País Vasco (obra nueva) IVA 10% + AJD 1,0%.",
    ("País Vasco", "Segunda mano"): "En País Vasco (segunda mano) ITP 4%.",
    ("Navarra", "Nuevo"): "En Navarra (obra nueva) IVA 10% + AJD 1,0%.",
    ("Navarra", "Segunda mano"): "En Navarra (segunda mano) ITP 6%.",
    ("Galicia", "Nuevo"): "En Galicia (obra nueva) IVA 10% + AJD 1,0%.",
    ("Galicia", "Segunda mano"): "En Galicia (segunda mano) ITP 9%.",
    ("Castilla y León", "Nuevo"): "En Castilla y León (obra nueva) IVA 10% + AJD 1,0%.",
    ("Castilla y León", "Segunda mano"): "En Castilla y León (segunda mano) ITP 8%.",
    ("Castilla-La Mancha", "Nuevo"): "En Castilla-La Mancha (obra nueva) IVA 10% + AJD 1,0%.",
    ("Castilla-La Mancha", "Segunda mano"): "En Castilla-La Mancha (segunda mano) ITP 9%.",
    ("Murcia", "Nuevo"): "En Murcia (obra nueva) IVA 10% + AJD 1,0%.",
    ("Murcia", "Segunda mano"): "En Murcia (segunda mano) ITP 8%.",
    ("La Rioja", "Nuevo"): "En La Rioja (obra nueva) IVA 10% + AJD 1,0%.",
    ("La Rioja", "Segunda mano"): "En La Rioja (segunda mano) ITP 7%.",
    ("Cantabria", "Nuevo"): "En Cantabria (obra nueva) IVA 10% + AJD 1,0%.",
    ("Cantabria", "Segunda mano"): "En Cantabria (segunda mano) ITP 10%.",
    ("Aragón", "Nuevo"): "En Aragón (obra nueva) IVA 10% + AJD 1,0%.",
    ("Aragón", "Segunda mano"): "En Aragón (segunda mano) ITP 8%.",
    ("Asturias", "Nuevo"): "En Asturias (obra nueva) IVA 10% + AJD 1,0%.",
    ("Asturias", "Segunda mano"): "En Asturias (segunda mano) ITP 8%.",
    ("Illes Balears", "Nuevo"): "En Illes Balears (obra nueva) IVA 10% + AJD 1,0%.",
    ("Illes Balears", "Segunda mano"): "En Illes Balears (segunda mano) ITP 8%.",
    ("Extremadura", "Nuevo"): "En Extremadura (obra nueva) IVA 10% + AJD 1,0%.",
    ("Extremadura", "Segunda mano"): "En Extremadura (segunda mano) ITP 8%.",
    ("Ceuta y Melilla", "Nuevo"): "En Ceuta y Melilla (obra nueva) IVA 10% + AJD 1,0%.",
    ("Ceuta y Melilla", "Segunda mano"): "En Ceuta y Melilla (segunda mano) ITP 6%.",
    ("Canarias", "Nuevo"): "En Canarias (obra nueva) IVA 10% + AJD 1,0% (simplificación).",
    ("Canarias", "Segunda mano"): "En Canarias (segunda mano) ITP 6% (simplificación).",
}


# =========================
# Sidebar completo (reordenado con tooltips restaurados)
# =========================

# === Valores por defecto ===
DEFAULTS = {
    "modo": "📘 Instrucciones",
    "edad": 40,
    "sueldo": 2000.0,
    "deudas": 0.0,
    "entrada": 85000.0,
    "ratio_dti": 35,
    "ltv": 80,
    "plazo": 30,
    "tipo_hipoteca": "Fija",
    "interes_fijo": 3.0,
    "euribor": 2.0,
    "diferencial": 1.0,
    "anios_fijo": 5,
    "interes_fijo_mixta": 2.0,
    "euribor_mixta": 2.0,
    "diferencial_mixta": 1.0,
    "financiar_comision": False,
    "notario": 1500.0,
    "registro": 500.0,
    "gestoria": 500.0,
    "tasacion": 400.0,
    "seguro_inicial": 300.0,
    "com_apertura": 1.0,
    "ccaa": "Madrid",
    "estado_vivienda": "Segunda mano",
    "usar_manual": False,
    "iva_itp": 10.0,
    "ajd": 1.0,
    "precio_comp": 0.0
}

# === Inicialización de valores por defecto solo si no existen ===
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# === Claves controladas ===
KEYS_WIDGETS = list(DEFAULTS.keys())

# =========================
# ⚙️ Selección de modo
# =========================
st.sidebar.header("⚙️ Selección de modo")

modo = st.sidebar.radio(
    "Selecciona el modo",
    [
        "📘 Instrucciones",
        "🔎 Descubrir mi precio máximo",
        "🏠 Comprobar una vivienda concreta"
    ],
    key="modo",
    help="Elige si quieres leer la guía, calcular tu precio máximo o comprobar una vivienda concreta."
)


# =========================
# Renderizado según modo
# =========================
if modo == "📘 Instrucciones":
    # Pantalla inicial de bienvenida con instrucciones y glosario
    st.header("ℹ️ Guía de uso")
    st.markdown("""
    Bienvenido a la **Calculadora Hipotecaria Profesional**.  
    Esta herramienta te ayuda a entender cuánto puedes permitirte al comprar una vivienda y qué implicaciones tiene tu hipoteca.

    ### 🔧 Modos de uso
    - **🔎 Descubrir mi precio máximo**: calcula el mayor precio de vivienda que puedes permitir con tu entrada, tu cuota máxima (DTI) y el LTV máximo permitido.
    - **🏠 Comprobar una vivienda concreta**: introduce un precio y comprueba si tu operación es viable, con desglose de gastos, escenarios de interés y tabla de amortización.
    - **🔄 Resetear**: restablece todos los valores a los predeterminados.

    ### 📌 Notas importantes
    - La **entrada** cubre primero los **impuestos y gastos de compra**; el excedente reduce el capital de la hipoteca.
    - Se validan dos ratios clave:
      - **LTV (Loan To Value):** porcentaje del valor de la vivienda que financia el banco.
      - **DTI (Debt To Income):** porcentaje de tus ingresos destinado a deudas.
    - Los valores en el apartado **⚖️ Gastos asociados** son una **media de lo que cuesta actualmente en España** cada concepto (notaría, registro, gestoría, tasación, seguro).  
      Puedes ajustarlos si conoces la cifra exacta.
    - En hipotecas **variables** y **mixtas**, la cuota puede variar según la evolución futura del Euríbor.
    """)

    with st.expander("📖 Glosario de términos"):
        st.markdown("""
        **Entrada** → dinero que aportas al inicio de la compra.  
        **Capital financiado** → cantidad que te presta el banco.  
        **LTV (Loan To Value)** → % del valor de la vivienda que financia el banco.  
        **DTI (Debt To Income)** → % de tus ingresos destinado a deudas.  
        **Euríbor** → índice de referencia para hipotecas variables en Europa.  
        **Diferencial** → margen fijo que se suma al Euríbor en hipotecas variables.  
        **Amortización anticipada** → devolución parcial o total del préstamo antes de tiempo.  
        **Comisión de apertura** → porcentaje que cobra el banco al formalizar la hipoteca.  
        **AJD (Actos Jurídicos Documentados)** → impuesto sobre escrituras notariales.  
        **ITP (Impuesto de Transmisiones Patrimoniales)** → impuesto en viviendas de segunda mano.  
        **IVA** → impuesto sobre viviendas nuevas (habitualmente 10%).  
        """)


# Botón reset
st.sidebar.markdown("")
if st.sidebar.button("🔄 Resetear calculadora"):
    for key in KEYS_WIDGETS:
        if key != "modo":
            st.session_state[key] = DEFAULTS[key]
    st.toast("✅ Calculadora restablecida a valores por defecto", icon="🏠")
    st.rerun()

st.sidebar.markdown("---")

# === Datos del inmueble ===
st.sidebar.header("🏠 Datos del inmueble")
ccaa = st.sidebar.selectbox(
    "Comunidad autónoma", list(PRESETS_IMPUESTOS.keys()), key="ccaa",
    help="La fiscalidad de la compra varía por CCAA. Impacta en IVA/ITP y AJD, afectando la entrada necesaria."
)
estado_vivienda = st.sidebar.radio(
    "Estado", ["Nuevo", "Segunda mano"], key="estado_vivienda",
    help="Obra nueva: IVA + AJD. Segunda mano: ITP. Cambia el coste fiscal y la entrada mínima necesaria."
)
usar_manual = st.sidebar.checkbox(
    "Introducir impuestos manualmente", key="usar_manual",
    help="Marca esta casilla si quieres introducir manualmente IVA/ITP y AJD."
)
if usar_manual:
    iva_itp_pct = st.sidebar.number_input(
        "IVA/ITP (%)", 0.0, 20.0, step=0.1, key="iva_itp",
        help="Obra nueva: IVA (habitualmente 10%). Segunda mano: ITP (varía por CCAA y perfil). Ajusta según normativa local y bonificaciones."
    ) / 100
    ajd_pct = st.sidebar.number_input(
        "AJD (%)", 0.0, 2.0, step=0.1, key="ajd",
        help="Impuesto de Actos Jurídicos Documentados. Depende de CCAA y tipo de operación. Añade coste sobre escritura e hipoteca."
    ) / 100
    tipo_impuesto = iva_itp_pct + ajd_pct
else:
    tipo_impuesto = tipo_impuesto_por_ccaa(ccaa, estado_vivienda)

# 👇 Campo de precio de la vivienda: siempre visible, editable solo en Modo 2
if modo == "🏠 Comprobar una vivienda concreta":
    precio = st.sidebar.number_input(
        "Precio de la vivienda (€)",
        min_value=0.0,
        step=1000.0,
        key="precio_comp",
        help="Precio del inmueble que quieres comprobar."
    )
else:
    precio = st.sidebar.number_input(
        "Precio de la vivienda (€)",
        min_value=0.0,
        step=1000.0,
        key="precio_comp",
        help="Este campo solo se usa en el modo 'Comprobar una vivienda concreta'.",
        disabled=True
    )

explicacion = EXPLICACION_IMPUESTOS.get((ccaa, estado_vivienda))
if explicacion:
    st.sidebar.info(explicacion)

st.sidebar.markdown("---")

# === Datos personales y financieros ===
st.sidebar.header("👤 Datos personales y financieros")
edad = st.sidebar.number_input(
    "Edad", 18, 75, step=1, key="edad",
    help="Tu edad actual. Los bancos limitan el plazo para que la hipoteca termine antes de una edad objetivo (suele ser 70–75 años)."
)
sueldo_neto = st.sidebar.number_input(
    "Sueldo neto mensual (€)", 0.0, step=100.0, key="sueldo",
    help="Ingresos netos mensuales (tras impuestos y retenciones). Se usan para calcular tu capacidad de endeudamiento (DTI)."
)
deudas_mensuales = st.sidebar.number_input(
    "Otras deudas mensuales (€)", 0.0, step=50.0, key="deudas",
    help="Pagos fijos de otros préstamos, tarjetas o financiación. Se restan de tu capacidad de endeudamiento."
)
entrada_usuario = st.sidebar.number_input(
    "Entrada aportada (€)", 0.0, step=1000.0, key="entrada",
    help="Dinero que realmente aportas a la compra. Primero cubre impuestos y gastos; el excedente reduce el capital a financiar."
)

st.sidebar.markdown("---")

# === Parámetros de la hipoteca ===
st.sidebar.header("📊 Parámetros de la hipoteca")
ratio_dti_pct = st.sidebar.slider(
    "Ratio máximo DTI (%)", 20, 50, step=1, key="ratio_dti",
    help="DTI (Debt To Income): porcentaje de tus ingresos destinado a deudas. Lo habitual es un máximo del 35% salvo excepciones (ingresos altos, perfil muy solvente, avales)."
)
ratio_dti = ratio_dti_pct / 100

ltv_max_pct = st.sidebar.slider(
    "LTV máximo permitido (%)", 50, 100, step=1, key="ltv",
    help="LTV (Loan To Value): % del valor de la vivienda que el banco financia. Lo habitual es 80%; en condiciones especiales puede llegar al 90% o 100% (por ejemplo, viviendas de banco, avales o perfiles muy solventes)."
)
ltv_max = ltv_max_pct / 100

anos_plazo = st.sidebar.slider(
    "Plazo (años)", 5, 40, step=1, key="plazo",
    help="Duración del préstamo. A mayor plazo, menor cuota mensual pero más intereses totales. Suele limitarse por edad (fin de préstamo antes de los 70–75 años)."
)

tipo_hipoteca = st.sidebar.radio(
    "Tipo de hipoteca", ["Fija", "Variable", "Mixta"], key="tipo_hipoteca",
    help="Elige Fija (cuota estable), Variable (Euríbor + diferencial) o Mixta (tramo fijo y luego variable). La estabilidad del pago depende del tipo elegido."
)

if tipo_hipoteca == "Fija":
    interes_anual = st.sidebar.number_input(
        "Interés fijo (%)", 0.0, 10.0, step=0.1, key="interes_fijo",
        help="Tipo nominal anual fijo. Mantiene cuota estable durante todo el plazo. Si baja el tipo, puedes intentar subrogación o novación."
    ) / 100

elif tipo_hipoteca == "Variable":
    euribor = st.sidebar.number_input(
        "Euríbor actual (%)", -2.0, 10.0,
        value=st.session_state["euribor"], step=0.1, key="euribor",
        help="Índice de referencia del mercado. La cuota se recalcula periódicamente (normalmente cada 6–12 meses) según el Euríbor vigente."
    ) / 100
    diferencial = st.sidebar.number_input(
        "Diferencial (%)", 0.0, 5.0,
        value=st.session_state["diferencial"], step=0.1, key="diferencial",
        help="Margen fijo que el banco añade al Euríbor (ej. Euríbor + 1%). Negociable según perfil, vinculación y condiciones."
    ) / 100
    interes_anual = euribor + diferencial

elif tipo_hipoteca == "Mixta":
    anios_fijo = st.sidebar.number_input(
        "Años tramo fijo", 1, 30,
        value=st.session_state["anios_fijo"], step=1, key="anios_fijo",
        help="Duración del período inicial con tipo fijo. Al terminar, la hipoteca pasa a tipo variable (Euríbor + diferencial)."
    )
    interes_fijo = st.sidebar.number_input(
        "Interés fijo inicial (%)", 0.0, 10.0,
        value=st.session_state["interes_fijo_mixta"], step=0.1, key="interes_fijo_mixta",
        help="Tipo nominal aplicado durante el tramo fijo. Aporta estabilidad al inicio y luego cambia a variable."
    ) / 100
    euribor = st.sidebar.number_input(
        "Euríbor actual (%)", -2.0, 10.0,
        value=st.session_state["euribor_mixta"], step=0.1, key="euribor_mixta",
        help="Referencia para el tramo variable tras el fijo. La cuota futura dependerá de la evolución del Euríbor."
    ) / 100
    diferencial = st.sidebar.number_input(
        "Diferencial (%)", 0.0, 5.0,
        value=st.session_state["diferencial_mixta"], step=0.1, key="diferencial_mixta",
        help="Margen que se suma al Euríbor en el tramo variable. Determina el coste total junto con el índice."
    ) / 100
    interes_variable = euribor + diferencial
    interes_anual = interes_fijo

financiar_comision = st.sidebar.checkbox(
    "Financiar comisión de apertura", key="financiar_comision",
    help="Si se marca, la comisión se suma al capital financiado."
)

st.sidebar.markdown("---")

# === Gastos asociados ===
st.sidebar.header("⚖️ Gastos asociados")
notario = st.sidebar.number_input(
    "Notaría (€)", 0.0, step=50.0, key="notario",
    help="Coste de la escritura pública. Suele rondar 600–1.500 € según complejidad y aranceles."
)
registro = st.sidebar.number_input(
    "Registro (€)", 0.0, step=50.0, key="registro",
    help="Inscripción de la hipoteca y la compraventa en el Registro de la Propiedad (aprox. 400–600 €)."
)
gestoria = st.sidebar.number_input(
    "Gestoría (€)", 0.0, step=50.0, key="gestoria",
    help="Tramitación administrativa de escrituras y liquidaciones. Habitual 300–500 €."
)
tasacion = st.sidebar.number_input(
    "Tasación (€)", 0.0, step=50.0, key="tasacion",
    help="Valoración oficial de la vivienda. Necesaria para fijar el LTV y aprobar la operación (aprox. 300–500 €)."
)
seguro_inicial = st.sidebar.number_input(
    "Seguro inicial (€)", 0.0, step=50.0, key="seguro_inicial",
    help="Seguro de hogar básico. Muchas entidades exigen cobertura mínima; productos adicionales (vida, protección de pagos) pueden afectar el diferencial."
)
com_apertura_pct = st.sidebar.number_input(
    "Comisión apertura (%)", 0.0, 5.0,
    step=0.1, key="com_apertura",
    help="Porcentaje sobre el capital financiado (habitual 0–1%). Puede financiarse o pagarse al inicio según condiciones."
) / 100

# ✅ Parámetros agregados para cálculos posteriores
params = {
    "tipo_impuesto": tipo_impuesto,
    "notario": notario,
    "gestoria": gestoria,
    "registro": registro,
    "tasacion": tasacion,
    "seguro_inicial": seguro_inicial,
    "com_apertura_pct": com_apertura_pct,
}



# =========================
# Función unificada de cálculo
# =========================
def calcular_capital_y_gastos(precio, entrada, params, ltv_max=0.80, financiar_comision=False):
    impuestos_pct = params["tipo_impuesto"]
    impuestos = precio * impuestos_pct
    gastos_puros = impuestos + params["notario"] + params["gestoria"] + params["registro"] + params["tasacion"] + params["seguro_inicial"]

    diferencia_entrada = entrada - gastos_puros
    excedente = max(0.0, diferencia_entrada)
    capital_preliminar = max(0.0, precio - excedente)

    com_apertura = capital_preliminar * params["com_apertura_pct"] if params["com_apertura_pct"] > 0 else 0.0
    if financiar_comision:
        capital_final = capital_preliminar + com_apertura
        gastos_iniciales = gastos_puros
    else:
        capital_final = capital_preliminar
        gastos_iniciales = gastos_puros + com_apertura

    ltv_real = (capital_final / precio) if precio > 0 else 0.0
    ltv_ok = ltv_real <= ltv_max

    return {
        "gastos_puros": gastos_puros,
        "gastos_iniciales": gastos_iniciales,
        "capital_final": capital_final,
        "excedente": excedente,
        "diferencia_entrada": diferencia_entrada,
        "ltv": ltv_real,
        "ltv_ok": ltv_ok
    }


# =========================
# MODO 1: Descubrir mi precio máximo (versión corregida)
# =========================
if modo == "🔎 Descubrir mi precio máximo":
    st.subheader("🔎 Descubrir mi precio máximo")

    # --- Instrucciones específicas para este modo ---
    st.info(
        "En este modo puedes calcular el **precio máximo de vivienda** que puedes permitirte "
        "según tus ingresos, deudas, entrada y parámetros de hipoteca.\n\n"
        "👉 **Parámetros mínimos a configurar:** sueldo neto mensual, deudas mensuales, entrada aportada, "
        "plazo de la hipoteca, tipo de hipoteca **y el Interés fijo (%) que te ofrece el banco**.\n\n"
        "ℹ️ Los valores en el apartado **⚖️ Gastos asociados** son una **media de lo que cuesta actualmente en España** "
        "(notaría, registro, gestoría, tasación, seguro). Puedes ajustarlos si conoces la cifra exacta.\n\n"
        f"✅ El cálculo valida automáticamente que el **DTI ≤ {int(DTI_FAIL*100)} %** y que el **LTV ≤ LTV máximo**, "
        "por lo que el resultado mostrado es siempre viable bajo criterios bancarios habituales.\n\n"
        "⚠️ **Nota importante:** el precio máximo mostrado aquí debe entenderse como una **referencia aproximada del límite**. "
        "Si en la opción **🏠 Comprobar una vivienda concreta** introduces exactamente esa cifra, la operación puede aparecer como "
        "**no viable** debido a redondeos internos o a que el DTI real supere mínimamente el 35 %. "
        "En la práctica, conviene dejar un pequeño margen de seguridad por debajo de este valor."
    )


    # --- Cálculo de cuota máxima ---
    cuota_max = cuota_maxima(sueldo_neto, deudas_mensuales, ratio=ratio_dti)

    # --- Búsqueda binaria del precio máximo viable ---
    low, high = 0.0, 2_000_000.0
    precio_maximo = 0.0  # guardamos el último valor viable
    for _ in range(50):
        mid = (low + high) / 2

        r_mid = calcular_capital_y_gastos(
            mid, entrada_usuario, params,
            ltv_max=ltv_max, financiar_comision=financiar_comision
        )
        capital_mid = r_mid["capital_final"]
        ltv_ok = r_mid["ltv_ok"]
        entrada_ok = entrada_usuario >= r_mid["gastos_puros"]

        # Cuota según tipo de hipoteca: usar peor tramo en Mixta
        if tipo_hipoteca in ["Fija", "Variable"] and interes_anual:
            cuota_mid = cuota_prestamo(capital_mid, interes_anual, anos_plazo) or 0.0
            dti_mid = dti(cuota_mid, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0
        elif tipo_hipoteca == "Mixta" and interes_fijo and interes_variable:
            cuota_mid_fijo = cuota_prestamo(capital_mid, interes_fijo, anios_fijo) or 0.0
            plazo_var_mid = max(0, anos_plazo - anios_fijo)
            cuota_mid_var = cuota_prestamo(capital_mid, interes_variable, plazo_var_mid) if plazo_var_mid > 0 else 0.0
            cuota_mid = max(cuota_mid_fijo, cuota_mid_var)
            dti_mid = dti(cuota_mid, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0
        else:
            cuota_mid = 0.0
            dti_mid = 0.0

        cuota_ok = cuota_mid <= cuota_max
        dti_ok = dti_mid <= DTI_FAIL   # ← usamos el umbral global

        # Criterio combinado: entrada suficiente + LTV dentro + DTI dentro
        if entrada_ok and ltv_ok and dti_ok and cuota_ok:
            precio_maximo = mid   # guardamos el último viable
            low = mid
        else:
            high = mid

    # --- Resultado final ---
    rf = calcular_capital_y_gastos(
        precio_maximo, entrada_usuario, params,
        ltv_max=ltv_max, financiar_comision=financiar_comision
    )
    capital_hipoteca = rf["capital_final"]
    ltv_val = rf["ltv"]
    gastos_puros = rf["gastos_puros"]

    # 🔧 Guardamos el precio máximo en sesión para usarlo en Modo 2 (parche visual)
    st.session_state["precio_max_modo1"] = precio_maximo
    # =========================
    # 📌 Resultado del modo Descubrir
    # =========================
    st.header("📌 Resultado del modo Descubrir")
    c1, c2, c3 = st.columns(3)
    c1.metric("💶 Cuota máxima mensual", eur(cuota_max))
    c2.metric("🏠 Precio máximo vivienda", eur(precio_maximo))
    if tipo_hipoteca == "Fija":
        c3.metric("📈 Interés fijo", pct(interes_anual))
    elif tipo_hipoteca == "Variable":
        c3.metric("📈 Interés variable", pct(interes_anual))
    elif tipo_hipoteca == "Mixta":
        c3.metric("📈 Interés fijo inicial", pct(interes_fijo))

    # =========================
    # 📊 Escenarios de interés (2%–5%)
    # =========================
    st.subheader("📊 Escenarios de interés (2%–5%)")
    st.caption("Simulación de la cuota mensual en distintos escenarios de tipo de interés, validando LTV + DTI.")

    # En Fija
    if tipo_hipoteca == "Fija":
        for interes_pct in ESCENARIOS_INTERES_PCT:
            interes_decimal = interes_pct / 100
            cuota_esc = cuota_prestamo(capital_hipoteca, interes_decimal, anos_plazo) or 0.0
            dti_esc = dti(cuota_esc, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0

            if es_viable(cuota_esc, cuota_max, ltv_val, ltv_max, dti_esc):
                st.success(f"✅ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")
            else:
                st.error(f"❌ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")

    # En Variable
    elif tipo_hipoteca == "Variable":
        for interes_pct in ESCENARIOS_INTERES_PCT:
            interes_decimal = interes_pct / 100
            cuota_esc = cuota_prestamo(capital_hipoteca, interes_decimal, anos_plazo) or 0.0
            dti_esc = dti(cuota_esc, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0

            if es_viable(cuota_esc, cuota_max, ltv_val, ltv_max, dti_esc):
                st.success(f"✅ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")
            else:
                st.error(f"❌ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")

    # En Mixta
    elif tipo_hipoteca == "Mixta":
        for interes_pct in ESCENARIOS_INTERES_PCT:
            interes_var_esc = interes_pct / 100
            cuota_fijo_esc = cuota_prestamo(capital_hipoteca, interes_fijo, anios_fijo) or 0.0
            plazo_var_esc = max(0, anos_plazo - anios_fijo)
            cuota_var_esc = cuota_prestamo(capital_hipoteca, interes_var_esc, plazo_var_esc) if plazo_var_esc > 0 else 0.0

            cuota_peor_esc = max(cuota_fijo_esc, cuota_var_esc)
            dti_peor_esc = dti(cuota_peor_esc, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0
            tramo_peor = "FIJO" if cuota_fijo_esc >= cuota_var_esc else "VARIABLE"

            if es_viable(cuota_peor_esc, cuota_max, ltv_val, ltv_max, dti_peor_esc):
                st.success(
                    f"✅ fijo {pct(interes_fijo)} / var {pct(interes_var_esc)} → peor tramo {tramo_peor}: "
                    f"cuota {eur(cuota_peor_esc)} | DTI {semaforo_dti(dti_peor_esc)}"
                )
            else:
                st.error(
                    f"❌ fijo {pct(interes_fijo)} / var {pct(interes_var_esc)} → peor tramo {tramo_peor}: "
                    f"cuota {eur(cuota_peor_esc)} | DTI {semaforo_dti(dti_peor_esc)}"
                )

        st.caption("En Mixta se valida siempre el tramo más exigente (peor escenario).")

    st.caption("DTI = (Cuota hipoteca + otras deudas) / Ingresos netos")









# =========================
# MODO 2: Comprobar una vivienda concreta
# =========================
elif modo == "🏠 Comprobar una vivienda concreta":
    st.subheader("🏠 Comprobar una vivienda concreta")
    # --- Instrucciones específicas para este modo ---
    st.info(
        "En este modo puedes comprobar la viabilidad de una **vivienda concreta**.\n\n"
        "👉 **Parámetros mínimos a configurar:**\n"
        "- Precio de la vivienda (€) → por defecto aparece en 0, debes introducir el valor real.\n"
        "- Sueldo neto mensual.\n"
        "- Otras deudas mensuales.\n"
        "- Entrada aportada.\n"
        "- Plazo de la hipoteca.\n"
        "- Tipo de hipoteca e interés correspondiente (fijo, variable o mixto).\n\n"
        "ℹ️ Con estos datos, la calculadora mostrará: LTV, DTI, coste total de la operación, "
        "escenarios de interés, consejos de viabilidad y tablas de amortización.\n\n"
        "⚠️ **Nota importante:** el cálculo del *precio máximo* en la opción **🔎 Descubrir mi precio máximo** "
        "se obtiene con una búsqueda matemática muy precisa. Esto significa que si introduces aquí exactamente esa cifra, "
        "la operación puede aparecer como **no viable** debido a redondeos internos o a que el DTI real supera mínimamente el 35 %. "
        "Considera el resultado de **🔎 Descubrir mi precio máximo** como una **referencia aproximada del límite**: "
        "en la práctica, si estás en esa frontera, cualquier variación mínima en ingresos, deudas o interés puede hacer que la operación pase de viable a no viable."
    )



    # 👇 Usamos directamente el precio definido en el sidebar
    r = calcular_capital_y_gastos(
        precio,
        entrada_usuario,
        params,
        ltv_max=ltv_max,
        financiar_comision=financiar_comision
    )

    gastos_puros = r["gastos_puros"]
    gastos_iniciales = r["gastos_iniciales"]
    capital_hipoteca = r["capital_final"]
    excedente = r["excedente"]
    diferencia_entrada = r["diferencia_entrada"]
    ltv_val = r["ltv"]

    cuota_max = cuota_maxima(sueldo_neto, deudas_mensuales, ratio=ratio_dti)

    # Cuota estimada según tipo
    cuota_estimada = 0.0
    if tipo_hipoteca in ["Fija", "Variable"] and interes_anual:
        cuota_estimada = cuota_prestamo(capital_hipoteca, interes_anual, anos_plazo) or 0.0
    elif tipo_hipoteca == "Mixta" and interes_fijo and interes_variable:
        cuota_estimada = cuota_prestamo(capital_hipoteca, interes_fijo, anios_fijo) or 0.0

    # Calcular DTI (redondeado para coherencia)
    dti_val = round(dti(cuota_estimada, deudas_mensuales, sueldo_neto), 4) if sueldo_neto > 0 else 0.0

    # =========================
    # Cálculo de intereses totales y coste total
    # =========================
    intereses_fijo = intereses_variable = 0.0
    if tipo_hipoteca in ["Fija", "Variable"]:
        intereses_totales = (cuota_estimada or 0.0) * anos_plazo * 12 - capital_hipoteca
    elif tipo_hipoteca == "Mixta":
        cuota_fijo = cuota_prestamo(capital_hipoteca, interes_fijo, anios_fijo) or 0.0
        pagos_fijo = cuota_fijo * anios_fijo * 12
        plazo_var = max(0, anos_plazo - anios_fijo)
        cuota_var = cuota_prestamo(capital_hipoteca, interes_variable, plazo_var) if plazo_var > 0 else 0.0
        pagos_var = cuota_var * plazo_var * 12
        # Nota: pagos_fijo y pagos_var incluyen capital+intereses
        intereses_totales = (pagos_fijo + pagos_var) - capital_hipoteca

    coste_inicial_total = precio + gastos_puros
    coste_total = coste_inicial_total + intereses_totales

    # =========================
    # Resumen
    # =========================
    st.header("📌 Resumen de la vivienda")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("💰 Precio vivienda", eur(precio))
    c2.metric("🧾 Impuestos y gastos", eur(gastos_puros))
    c3.metric("🏦 Capital a financiar", eur(capital_hipoteca))
    c4.metric("💵 Capital no financiado", eur(excedente))

    st.divider()


    # =========================
    # 1️⃣ Entrada
    # =========================
    st.subheader("1️⃣ Entrada")
    st.write(f"Entrada aportada: **{eur(entrada_usuario)}**")
    st.write(f"Gastos de compra (impuestos + trámites): **{eur(gastos_puros)}**")
    if diferencia_entrada >= 0:
        st.success(f"✅ Entrada suficiente. Excedente aplicado al préstamo: {eur(excedente)}")
    else:
        st.error(f"❌ Entrada insuficiente. Te faltan: {eur(-diferencia_entrada)}")

    # --- Texto aclaratorio sobre ratios en Modo 2 ---
    st.info(
    "ℹ️ En este modo se muestran explícitamente los ratios clave de la operación: "
    "**DTI (endeudamiento)** y **LTV (porcentaje financiado)**. "
    "Estos son los indicadores que los bancos utilizan para evaluar la viabilidad de la hipoteca. "
    f"Un DTI ≤ {int(DTI_FAIL*100)} % y un LTV ≤ 80 % suelen considerarse dentro de rangos aceptables."
)




    # =========================
    # 2️⃣ Hipoteca
    # =========================
    st.header("2️⃣ Hipoteca")

    c1, c2, c3 = st.columns(3)
    c1.metric("📉 LTV", pct(ltv_val))
    c2.metric("📅 Plazo", f"{anos_plazo} años")
    c3.metric("💶 Cuota máxima permitida", eur(cuota_max))

    st.write(f"**Cuota mensual estimada:** {eur(cuota_estimada)}")

    # --- Evaluación combinada de LTV y DTI con es_viable ---
    if es_viable(cuota_estimada, cuota_max, ltv_val, ltv_max, dti_val):
        # Dentro de rango → matizamos según nivel de DTI
        if dti_val <= DTI_WARN:
            st.success(
                f"DTI estimado: 🟢 {pct_dti(dti_val)} (Seguro)\n\n"
                "Con este nivel de endeudamiento y un LTV dentro del límite, la operación se considera solvente."
            )
        else:  # entre WARN y FAIL
            st.warning(
                f"DTI estimado: 🟡 {pct_dti(dti_val)} (Moderado)\n\n"
                "La operación es viable, aunque podrían analizar estabilidad, avales o perfil de riesgo."
            )
    else:
        # No viable → detallamos el motivo
        if not r["ltv_ok"] and dti_visible(dti_val) > DTI_FAIL:
            st.error(
                f"❌ LTV real {pct(ltv_val)} (máx. {pct(ltv_max)}) y DTI {pct_dti(dti_val)}.\n\n"
                "La operación no es viable: supera tanto el límite de financiación (LTV) como el nivel de endeudamiento (DTI)."
            )
        elif not r["ltv_ok"]:
            st.error(
                f"⚠️ El LTV real ({pct(ltv_val)}) supera el máximo permitido ({pct(ltv_max)}).\n\n"
                f"Aunque el DTI es {pct_dti(dti_val)} y estaría dentro de rango, la operación no sería viable según criterios bancarios habituales. "
                "Algunos bancos pueden aceptar hasta el 90 % o incluso el 100 % en casos especiales, pero no es lo estándar."
            )
        elif dti_visible(dti_val) > DTI_FAIL:
            st.error(
                f"⚠️ El LTV real ({pct(ltv_val)}) está dentro del límite ({pct(ltv_max)}), "
                f"pero el DTI es {pct_dti(dti_val)} (Arriesgado).\n\n"
                "Por encima del 35 % los bancos suelen rechazar la operación salvo condiciones excepcionales."
            )

    st.caption("DTI = (Cuota hipoteca + otras deudas) / Ingresos netos")








    # =========================
    # 💵 Coste total de la operación (con resumen y desglose opcional)
    # =========================
    import pandas as pd

    st.subheader("💵 Coste total de la operación")

    # --- Cálculo de totales previos ---
    if usar_manual:
        iva_itp_pct = st.session_state["iva_itp"] / 100
        ajd_pct = st.session_state["ajd"] / 100
        if estado_vivienda == "Nuevo":
            iva_itp_label = "IVA"
            iva_itp_val = precio * iva_itp_pct
            ajd_val = precio * ajd_pct
        else:
            iva_itp_label = "ITP"
            iva_itp_val = precio * iva_itp_pct
            ajd_val = 0.0
    else:
        preset = PRESETS_IMPUESTOS.get(ccaa, PRESETS_IMPUESTOS["Madrid"])
        if estado_vivienda == "Nuevo":
            iva_itp_label = "IVA"
            iva_itp_pct = preset["nuevo"]["iva"]
            ajd_pct = preset["nuevo"]["ajd"]
            iva_itp_val = precio * iva_itp_pct
            ajd_val = precio * ajd_pct
        else:
            iva_itp_label = "ITP"
            iva_itp_pct = preset["segunda"]["itp"]
            ajd_pct = 0.0
            iva_itp_val = precio * iva_itp_pct
            ajd_val = 0.0

    if com_apertura_pct > 0:
        if financiar_comision:
            capital_preliminar_aprox = capital_hipoteca / (1 + com_apertura_pct)
            com_apertura_val = capital_hipoteca - capital_preliminar_aprox
            com_label = "Comisión apertura (financiada)"
            com_incluida_en_gastos = False
        else:
            capital_preliminar_aprox = capital_hipoteca
            com_apertura_val = capital_preliminar_aprox * com_apertura_pct
            com_label = "Comisión apertura (pagada al inicio)"
            com_incluida_en_gastos = True
    else:
        com_apertura_val = 0.0
        com_label = "Sin comisión de apertura"
        com_incluida_en_gastos = False

    impuestos_total = iva_itp_val + ajd_val
    gastos_formalizacion_total = notario + registro + gestoria + tasacion + seguro_inicial
    gastos_compra_total = impuestos_total + gastos_formalizacion_total + (com_apertura_val if com_incluida_en_gastos else 0.0)
    coste_inicial_total = precio + gastos_compra_total

    # --- Pagos al banco ---
    if tipo_hipoteca in ["Fija", "Variable"]:
        pagos_totales = (cuota_estimada or 0.0) * anos_plazo * 12
        intereses_totales = pagos_totales - capital_hipoteca
        capital_amortizado = capital_hipoteca
    elif tipo_hipoteca == "Mixta":
        cuota_fijo = cuota_prestamo(capital_hipoteca, interes_fijo, anios_fijo) or 0.0
        pagos_fijo = cuota_fijo * anios_fijo * 12
        plazo_var = max(0, anos_plazo - anios_fijo)
        cuota_var = cuota_prestamo(capital_hipoteca, interes_variable, plazo_var) if plazo_var > 0 else 0.0
        pagos_var = cuota_var * plazo_var * 12
        pagos_totales = pagos_fijo + pagos_var
        intereses_totales = pagos_totales - capital_hipoteca
        capital_amortizado = capital_hipoteca

    coste_total = coste_inicial_total + intereses_totales

    # --- Tabla resumen siempre visible ---
    tabla_resumen = pd.DataFrame([
        ["⚖️ Coste inicial (precio + impuestos + gastos)", eur(coste_inicial_total)],
        ["➕ Intereses totales (pagados al banco)", eur(intereses_totales)],
        ["➡️ Coste total con hipoteca", eur(coste_total)]
    ], columns=["Concepto", "Importe"])

    def resaltar_resumen(row):
        if "Coste total" in row["Concepto"]:
            return ["background-color: #b3ffb3; font-weight: bold"] * len(row)
        return [""] * len(row)

    st.dataframe(
        tabla_resumen.style
            .apply(resaltar_resumen, axis=1)
            .set_properties(**{"text-align": "left", "white-space": "nowrap"}),
        use_container_width=True,
        hide_index=True
    )
    st.caption("El coste inicial incluye precio, impuestos y gastos de compra. Los pagos al banco incluyen solo capital e intereses. El coste total con hipoteca es la suma de ambos mundos.")

    # --- Expander con el desglose completo ---
    with st.expander("📊 Ver desglose completo"):
        # Tabla 1: Costes de compra
        tabla_compra = pd.DataFrame([
            ["Precio del inmueble", eur(precio)],
            [f"{iva_itp_label} + AJD" if ajd_val > 0 else iva_itp_label, eur(impuestos_total)],
            ["Notaría", eur(notario)],
            ["Registro", eur(registro)],
            ["Gestoría", eur(gestoria)],
            ["Tasación", eur(tasacion)],
            ["Seguro inicial", eur(seguro_inicial)],
            [com_label, eur(com_apertura_val)],
            ["⚖️ Coste inicial (precio + impuestos + gastos)", eur(coste_inicial_total)]
        ], columns=["Concepto", "Importe"])

        def resaltar_totales(row):
            if "Coste inicial" in row["Concepto"]:
                return ["background-color: #d1ffd1; font-weight: bold"] * len(row)
            return [""] * len(row)

        st.dataframe(
            tabla_compra.style
                .apply(resaltar_totales, axis=1)
                .set_properties(**{"text-align": "left", "white-space": "nowrap"}),
            use_container_width=True,
            hide_index=True
        )
        st.caption("Este bloque refleja lo que cuesta formalizar la compra: precio, impuestos y gastos iniciales. No incluye las cuotas al banco.")

        # Tabla 2: Pagos al banco
        tabla_banco = pd.DataFrame([
            ["Capital amortizado (devuelto al banco)", eur(capital_amortizado)],
            ["Intereses totales (coste financiero)", eur(intereses_totales)],
            ["Pagos totales al banco (todas las cuotas)", eur(pagos_totales)]
        ], columns=["Concepto", "Importe"])

        def resaltar_banco(row):
            if "Pagos totales" in row["Concepto"]:
                return ["background-color: #d1ffd1; font-weight: bold"] * len(row)
            return [""] * len(row)

        st.dataframe(
            tabla_banco.style
                .apply(resaltar_banco, axis=1)
                .set_properties(**{"text-align": "left", "white-space": "nowrap"}),
            use_container_width=True,
            hide_index=True
        )
        st.caption("Este bloque refleja lo que pagarás en cuotas al banco: capital + intereses. No incluye impuestos ni gastos iniciales.")



    # =========================
    # 📊 Escenarios de interés (2%–5%)
    # =========================
    st.subheader("📊 Escenarios de interés (2%–5%)")
    st.caption("Simulación de la cuota mensual en distintos escenarios de tipo de interés, validando LTV + DTI.")

    precio_max_modo1 = st.session_state.get("precio_max_modo1", None)  # 🔧 recuperamos el máximo de Modo 1

    if tipo_hipoteca == "Fija":
        for interes_pct in ESCENARIOS_INTERES_PCT:
            interes_decimal = interes_pct / 100
            cuota_esc = cuota_prestamo(capital_hipoteca, interes_decimal, anos_plazo) or 0.0
            dti_esc = dti(cuota_esc, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0

            if es_viable(cuota_esc, cuota_max, ltv_val, ltv_max, dti_esc):
                st.success(f"✅ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")
            else:
                st.error(f"❌ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")

    elif tipo_hipoteca == "Variable":
        for interes_pct in ESCENARIOS_INTERES_PCT:
            interes_decimal = interes_pct / 100
            cuota_esc = cuota_prestamo(capital_hipoteca, interes_decimal, anos_plazo) or 0.0
            dti_esc = dti(cuota_esc, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0

            if es_viable(cuota_esc, cuota_max, ltv_val, ltv_max, dti_esc):
                st.success(f"✅ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")
            else:
                st.error(f"❌ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")

    elif tipo_hipoteca == "Mixta":
        for interes_pct in ESCENARIOS_INTERES_PCT:
            interes_var_esc = interes_pct / 100
            cuota_fijo_esc = cuota_prestamo(capital_hipoteca, interes_fijo, anios_fijo) or 0.0
            plazo_var_esc = max(0, anos_plazo - anios_fijo)
            cuota_var_esc = cuota_prestamo(capital_hipoteca, interes_var_esc, plazo_var_esc) if plazo_var_esc > 0 else 0.0

            cuota_peor_esc = max(cuota_fijo_esc, cuota_var_esc)
            dti_peor_esc = dti(cuota_peor_esc, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0
            tramo_peor = "FIJO" if cuota_fijo_esc >= cuota_var_esc else "VARIABLE"

            if es_viable(cuota_peor_esc, cuota_max, ltv_val, ltv_max, dti_peor_esc):
                st.success(
                    f"✅ fijo {pct(interes_fijo)} / var {pct(interes_var_esc)} → peor tramo {tramo_peor}: "
                    f"cuota {eur(cuota_peor_esc)} | DTI {semaforo_dti(dti_peor_esc)}"
                )
            else:
                st.error(
                    f"❌ fijo {pct(interes_fijo)} / var {pct(interes_var_esc)} → peor tramo {tramo_peor}: "
                    f"cuota {eur(cuota_peor_esc)} | DTI {semaforo_dti(dti_peor_esc)}"
                )

        st.caption("En Mixta se valida siempre el tramo más exigente (peor escenario).")

    st.caption("DTI = (Cuota hipoteca + otras deudas) / Ingresos netos")







    # =========================
    # 💡 Consejos para mejorar la viabilidad
    # =========================
    st.divider()
    st.subheader("💡 Consejos para mejorar la viabilidad")
    consejos = []

    if tipo_hipoteca == "Mixta":
        # Cálculo coherente de ambos tramos
        cuota_fijo = cuota_prestamo(capital_hipoteca, interes_fijo, anios_fijo) or 0.0
        plazo_var = max(0, anos_plazo - anios_fijo)
        cuota_var = cuota_prestamo(capital_hipoteca, interes_variable, plazo_var) if plazo_var > 0 else 0.0

        dti_fijo = dti(cuota_fijo, deudas_mensuales, sueldo_neto)
        dti_variable = dti(cuota_var, deudas_mensuales, sueldo_neto)
        dti_peor = max(dti_fijo, dti_variable)
        cuota_peor = max(cuota_fijo, cuota_var)
        tramo_peor = "FIJO" if dti_fijo >= dti_variable else "VARIABLE"

        # Evaluación con es_viable
        if not es_viable(cuota_peor, cuota_max, ltv_val, ltv_max, dti_peor):
            if dti_visible(dti_peor) > DTI_FAIL:
                if tramo_peor == "FIJO":
                    consejos.append("👉 El tramo fijo supera el límite de endeudamiento. Considera aportar más entrada, ampliar plazo o negociar condiciones.")
                else:
                    consejos.append("👉 El tramo variable supera el límite de endeudamiento. Considera aportar más entrada, ampliar plazo o negociar condiciones.")
            elif DTI_WARN < dti_visible(dti_peor) <= DTI_FAIL:
                consejos.append("👉 Tu DTI está en zona límite. Revisa estabilidad laboral, avales o considera ampliar plazo para mayor seguridad.")

            if ltv_val > ltv_max:
                consejos.append("👉 Aporta más entrada para reducir el LTV.")
                consejos.append("👉 Considera una vivienda de menor precio.")

        if not consejos:
            st.success("✅ Tu operación es viable con los parámetros actuales (considerando ambos tramos).")
            if abs(dti_visible(dti_peor) - DTI_FAIL) < 1e-9:
                st.info("ℹ️ Estás en el límite exacto del 35 %. Aunque la operación se considera viable, cualquier variación mínima podría hacerla no viable.")
            st.info("ℹ️ Aunque el tramo fijo es asequible, recuerda que el tramo variable puede suponer un esfuerzo mayor a largo plazo.")
        else:
            for c in consejos:
                st.warning(c)
            st.info(f"ℹ️ En hipotecas mixtas, la viabilidad se evalúa en ambos tramos. El tramo más exigente es el **{tramo_peor}**.")

        if plazo_var == 0 or cuota_var == 0.0:
            st.info("ℹ️ El capital quedó totalmente amortizado en el tramo fijo, por lo que no existe tramo variable.")

    else:
        # Fija y Variable
        dti_dashboard = dti_val

        if not es_viable(cuota_estimada, cuota_max, ltv_val, ltv_max, dti_dashboard):
            if dti_visible(dti_dashboard) > DTI_FAIL:
                consejos.append("👉 Aumenta la entrada o reduce el precio de la vivienda.")
                consejos.append("👉 Negocia un interés más bajo con el banco.")
                consejos.append("👉 Amplía el plazo de la hipoteca para reducir la cuota mensual.")
            elif DTI_WARN < dti_visible(dti_dashboard) <= DTI_FAIL:
                consejos.append("👉 Tu DTI está en zona límite. Considera ampliar plazo o negociar condiciones para mayor seguridad.")

            if ltv_val > ltv_max:
                consejos.append("👉 Aporta más entrada para reducir el LTV.")
                consejos.append("👉 Considera una vivienda de menor precio.")

        if not consejos:
            st.success("✅ Tu operación es viable con los parámetros actuales.")
            if abs(dti_visible(dti_dashboard) - DTI_FAIL) < 1e-9:
                st.info("ℹ️ Estás en el límite exacto del 35 %. Aunque la operación se considera viable, cualquier variación mínima podría hacerla no viable.")
        else:
            for c in consejos:
                st.warning(c)








    # =========================
    # 💸 Simulación de amortización anticipada (opcional)
    # =========================
    st.divider()
    st.subheader("💸 Simulación de amortización anticipada (opcional)")
    st.markdown("""
ℹ️ **Cómo funciona**  
- *Año de amortización anticipada*: el año en el que harías un pago extra.  
- *Cantidad del pago extra*: dinero adicional que aportas en ese momento para reducir la deuda.  
- *Reducir plazo*: mantienes la cuota, pero terminas de pagar antes.  
- *Reducir cuota*: mantienes el plazo, pero tu cuota mensual baja.  
""")

    simular_amortizacion = st.checkbox("Activar simulación de amortización anticipada", value=False)
    if simular_amortizacion and cuota_estimada:
        anio_extra = st.number_input("Año de amortización anticipada", min_value=1, max_value=anos_plazo, value=5, step=1)
        pago_extra = st.number_input("Cantidad del pago extra (€)", min_value=0.0, step=1000.0, value=5000.0)
        mantener_cuota = st.radio("¿Qué prefieres tras amortizar?", ["Reducir plazo", "Reducir cuota"], index=0)

        n_total = anos_plazo * 12
        n_transcurridos = anio_extra * 12
        r_mensual = interes_anual / 12 if interes_anual else 0.0

        if r_mensual > 0:
            capital_pendiente = capital_hipoteca * ((1 + r_mensual) ** n_total - (1 + r_mensual) ** n_transcurridos) / ((1 + r_mensual) ** n_total - 1)
        else:
            capital_pendiente = capital_hipoteca * (1 - n_transcurridos / n_total)

        nuevo_capital = max(0.0, capital_pendiente - pago_extra)

        if mantener_cuota == "Reducir plazo":
            import math
            if r_mensual > 0 and cuota_estimada > 0:
                nuevo_plazo_meses = math.log(cuota_estimada / (cuota_estimada - nuevo_capital * r_mensual)) / math.log(1 + r_mensual)
                nuevo_plazo_anios = nuevo_plazo_meses / 12
            else:
                nuevo_plazo_anios = 0
            st.info(f"📉 Con amortización anticipada de {eur(pago_extra)} en el año {anio_extra}, reduces el plazo a **{nuevo_plazo_anios:.1f} años** manteniendo la misma cuota.")
        else:
            nueva_cuota = cuota_prestamo(nuevo_capital, interes_anual, anos_plazo - anio_extra)
            st.info(f"📉 Con amortización anticipada de {eur(pago_extra)} en el año {anio_extra}, tu nueva cuota sería de **{eur(nueva_cuota)}** manteniendo el plazo original.")




    # =========================
    # 📊 Tabla de amortización simplificada (por años)
    # =========================
    st.divider()
    st.subheader("📊 Tabla de amortización simplificada (por años)")

    import pandas as pd

    if cuota_estimada:
        if tipo_hipoteca in ["Fija", "Variable"]:
            data = []
            capital_pendiente = capital_hipoteca
            r = interes_anual / 12 if interes_anual else 0.0
            cuota_mensual = cuota_estimada

            for anio in range(1, anos_plazo + 1):
                intereses_anio = 0.0
                capital_anio = 0.0
                for mes in range(12):
                    interes_mes = capital_pendiente * r
                    amortizacion_mes = cuota_mensual - interes_mes
                    intereses_anio += interes_mes
                    capital_anio += amortizacion_mes
                    capital_pendiente -= amortizacion_mes
                    if capital_pendiente <= 0:
                        capital_pendiente = 0
                        break
                data.append({
                    "Año": anio,
                    "Cuota anual": eur(cuota_mensual * 12),
                    "Intereses pagados": eur(intereses_anio),
                    "Capital amortizado": eur(capital_anio),
                    "Capital pendiente": eur(capital_pendiente)
                })
                if capital_pendiente <= 0:
                    break

            df_amort = pd.DataFrame(data)
            st.dataframe(df_amort, use_container_width=True)

        elif tipo_hipoteca == "Mixta":
            # --- Tramo fijo ---
            data_fijo = []
            capital_pendiente = capital_hipoteca
            r_fijo = interes_fijo / 12 if interes_fijo else 0.0
            cuota_mensual_fijo = cuota_prestamo(capital_pendiente, interes_fijo, anios_fijo) or 0.0

            for anio in range(1, anios_fijo + 1):
                intereses_anio = 0.0
                capital_anio = 0.0
                for mes in range(12):
                    interes_mes = capital_pendiente * r_fijo
                    amortizacion_mes = cuota_mensual_fijo - interes_mes
                    intereses_anio += interes_mes
                    capital_anio += amortizacion_mes
                    capital_pendiente -= amortizacion_mes
                    if capital_pendiente <= 0:
                        capital_pendiente = 0
                        break
                data_fijo.append({
                    "Año": anio,
                    "Cuota anual": eur(cuota_mensual_fijo * 12),
                    "Intereses pagados": eur(intereses_anio),
                    "Capital amortizado": eur(capital_anio),
                    "Capital pendiente": eur(capital_pendiente)
                })
                if capital_pendiente <= 0:
                    break

            st.markdown("### 🟦 Tramo fijo")
            st.dataframe(pd.DataFrame(data_fijo), use_container_width=True)

            # --- Tramo variable ---
            plazo_var = max(0, anos_plazo - anios_fijo)
            if plazo_var > 0 and capital_pendiente > 0:
                data_var = []
                r_var = interes_variable / 12 if interes_variable else 0.0
                cuota_mensual_var = cuota_prestamo(capital_pendiente, interes_variable, plazo_var) or 0.0

                for anio in range(1, plazo_var + 1):
                    intereses_anio = 0.0
                    capital_anio = 0.0
                    for mes in range(12):
                        interes_mes = capital_pendiente * r_var
                        amortizacion_mes = cuota_mensual_var - interes_mes
                        intereses_anio += interes_mes
                        capital_anio += amortizacion_mes
                        capital_pendiente -= amortizacion_mes
                        if capital_pendiente <= 0:
                            capital_pendiente = 0
                            break
                    data_var.append({
                        "Año": anios_fijo + anio,
                        "Cuota anual": eur(cuota_mensual_var * 12),
                        "Intereses pagados": eur(intereses_anio),
                        "Capital amortizado": eur(capital_anio),
                        "Capital pendiente": eur(capital_pendiente)
                    })
                    if capital_pendiente <= 0:
                        break

                st.markdown("### 🟩 Tramo variable")
                st.dataframe(pd.DataFrame(data_var), use_container_width=True)
            else:
                st.markdown("### 🟩 Tramo variable")
                st.info("El capital quedó totalmente amortizado en el tramo fijo, por lo que no existe tramo variable.")



    

    # =========================
    # 🧮 Resumen compacto (dashboard rápido)
    # =========================
    st.divider()
    st.subheader("🧮 Resumen compacto")

    if tipo_hipoteca == "Mixta":
        cuota_fijo = cuota_prestamo(capital_hipoteca, interes_fijo, anios_fijo) or 0.0
        plazo_var = max(0, anos_plazo - anios_fijo)
        cuota_var = cuota_prestamo(capital_hipoteca, interes_variable, plazo_var) if plazo_var > 0 else 0.0

        dti_fijo = dti(cuota_fijo, deudas_mensuales, sueldo_neto)
        dti_variable = dti(cuota_var, deudas_mensuales, sueldo_neto)
        dti_peor = max(dti_fijo, dti_variable)
        cuota_peor = max(cuota_fijo, cuota_var)
        tramo_peor = "FIJO" if dti_fijo >= dti_variable else "VARIABLE"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("DTI (peor tramo)", semaforo_dti(dti_peor))
        col2.metric("LTV", pct(ltv_val))
        col3.metric("Cuota máx.", eur(cuota_max))
        col4.metric("Cuota estimada (peor tramo)", eur(cuota_peor))

        st.caption(f"Evaluado en tramo: {tramo_peor}")
        st.caption("DTI = (Cuota hipoteca + otras deudas) / Ingresos netos")

        if plazo_var > 0 and cuota_var > 0.0:
            st.info("ℹ️ Se muestra el tramo más exigente (peor escenario).")
        else:
            st.info("ℹ️ El capital quedó totalmente amortizado en el tramo fijo, por lo que no existe tramo variable.")

        # --- Evaluación combinada rápida con es_viable ---
        if es_viable(cuota_peor, cuota_max, ltv_val, ltv_max, dti_peor):
            st.success("✅ Resumen: Operación viable (LTV y DTI dentro de rango).")
            if abs(dti_visible(dti_peor) - DTI_FAIL) < 1e-9:
                st.info("ℹ️ Estás en el límite exacto del 35 %. Aunque la operación se considera viable, cualquier variación mínima podría hacerla no viable.")
        else:
            st.error("❌ Resumen: Operación no viable (supera LTV o DTI).")

    else:
        cuota_dashboard = cuota_estimada or 0.0
        dti_dashboard = dti_val or 0.0

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("DTI", semaforo_dti(dti_dashboard))
        col2.metric("LTV", pct(ltv_val))
        col3.metric("Cuota máx.", eur(cuota_max))
        col4.metric("Cuota estimada", eur(cuota_dashboard))

        st.caption("DTI = (Cuota hipoteca + otras deudas) / Ingresos netos")

        # --- Evaluación combinada rápida con es_viable ---
        if es_viable(cuota_dashboard, cuota_max, ltv_val, ltv_max, dti_dashboard):
            st.success("✅ Resumen: Operación viable (LTV y DTI dentro de rango).")
            if abs(dti_visible(dti_dashboard) - DTI_FAIL) < 1e-9:
                st.info("ℹ️ Estás en el límite exacto del 35 %. Aunque la operación se considera viable, cualquier variación mínima podría hacerla no viable.")
        else:
            st.error("❌ Resumen: Operación no viable (supera LTV o DTI).")





 


# ============================================================
# 🧪 Validador profesional dual (modos: rápida / intensa)
# ============================================================

MODO_VALIDACION = False           # ⬅️ Actívalo a True para ejecutar el validador
TIPO_VALIDACION = "intensa"        # opciones: "rápida" o "intensa"

if MODO_VALIDACION:
    import statistics as stats
    import random

    st.header("🧪 VALIDACIÓN PROFESIONAL (dual)")

    # --- Umbrales alineados con la app ---
    THRESHOLDS = {
        "DTI_warn": 0.30,
        "DTI_fail": 0.35,
        "LTV_warn": 0.80,
        "LTV_fail": 0.90,
    }

    # --- Utilidades visuales ---
    def flag_dti(d):
        if d <= THRESHOLDS["DTI_warn"]:
            return "🟢"
        elif d <= THRESHOLDS["DTI_fail"]:
            return "🟡"
        return "🔴"

    def flag_ltv(l):
        if l <= THRESHOLDS["LTV_warn"]:
            return "🟢"
        elif l <= THRESHOLDS["LTV_fail"]:
            return "🟡"
        return "🔴"

    # --- Funciones de apoyo ---
    def cuota_para(capital, interes, plazo):
        return cuota_prestamo(capital, interes, plazo) or 0.0

    def is_viable_joint(dti_val, ltv_val, entrada_ok):
        return entrada_ok and (dti_val <= THRESHOLDS["DTI_fail"]) and (ltv_val <= THRESHOLDS["LTV_warn"])

    def assert_coherencia(fallos, escenario_id, etiqueta, condicion):
        if not condicion:
            fallos.append((escenario_id, etiqueta))

    # --- Escenarios base ---
    OPERACIONES_BASE = [
        {"precio": 200000, "entrada": 40000, "ccaa": "Madrid",    "estado": "Segunda mano", "financiar": False},
        {"precio": 260000, "entrada": 30000, "ccaa": "Cataluña",  "estado": "Segunda mano", "financiar": True},
        {"precio": 180000, "entrada": 20000, "ccaa": "Andalucía", "estado": "Segunda mano", "financiar": False},
    ]

    COMBOS_FIJA = [
        {"interes": 0.02, "plazo": 20, "sueldo": 2500, "deudas": 0},
        {"interes": 0.03, "plazo": 25, "sueldo": 2800, "deudas": 200},
        {"interes": 0.04, "plazo": 30, "sueldo": 3200, "deudas": 300},
    ]

    COMBOS_VARIABLE = [
        {"interes": 0.03, "plazo": 20, "sueldo": 2200, "deudas": 0},
        {"interes": 0.04, "plazo": 25, "sueldo": 2800, "deudas": 150},
    ]

    COMBOS_MIXTA = [
        {"fijo_anios": 5,  "i_fijo": 0.02,  "i_var": 0.03, "plazo_total": 30, "sueldo": 2800, "deudas": 150},
        {"fijo_anios": 10, "i_fijo": 0.018, "i_var": 0.04, "plazo_total": 30, "sueldo": 3200, "deudas": 250},
    ]
    if TIPO_VALIDACION == "rápida":
        st.subheader("⚡ Validación rápida (smoke test)")

        operaciones = OPERACIONES_BASE[:2]  # dos operaciones representativas
        combos_basicos = [
            {"tipo": "Fija",     "interes": 0.03, "plazo": 25, "sueldo": 2800, "deudas": 200},
            {"tipo": "Variable", "interes": 0.04, "plazo": 25, "sueldo": 2800, "deudas": 150},
            {"tipo": "Mixta",    "fijo_anios": 10, "i_fijo": 0.02, "i_var": 0.04,
                                 "plazo_total": 30, "sueldo": 3200, "deudas": 250},
        ]

        dti_vals, ltv_vals = [], []
        fallos_codigo = []
        escenario_id = 0

        for op in operaciones:
            escenario_id += 1
            st.markdown(f"**Operación {escenario_id}: {op['ccaa']} — {op['estado']} — precio {eur(op['precio'])}**")

            pipe = calcular_capital_y_gastos(
                precio=op["precio"], entrada=op["entrada"], params=params,
                ltv_max=THRESHOLDS["LTV_warn"], financiar_comision=op["financiar"]
            )
            capital_final = pipe["capital_final"]
            ltv_val = pipe["ltv"]
            entrada_ok = op["entrada"] >= pipe["gastos_puros"]

            for c in combos_basicos:
                if c["tipo"] == "Fija":
                    cuota = cuota_para(capital_final, c["interes"], c["plazo"])
                    dti_val = dti(cuota, c["deudas"], c["sueldo"])
                    st.write(f"Fija {pct(c['interes'])}, {c['plazo']}a → cuota {eur(cuota)} "
                             f"→ DTI {pct(dti_val)} {flag_dti(dti_val)} | "
                             f"LTV {pct(ltv_val)} {flag_ltv(ltv_val)}")

                elif c["tipo"] == "Variable":
                    cuota = cuota_para(capital_final, c["interes"], c["plazo"])
                    dti_val = dti(cuota, c["deudas"], c["sueldo"])
                    st.write(f"Variable {pct(c['interes'])}, {c['plazo']}a → cuota {eur(cuota)} "
                             f"→ DTI {pct(dti_val)} {flag_dti(dti_val)} | "
                             f"LTV {pct(ltv_val)} {flag_ltv(ltv_val)}")

                else:  # Mixta
                    plazo_var = max(0, c["plazo_total"] - c["fijo_anios"])
                    cuota_fijo = cuota_para(capital_final, c["i_fijo"], c["fijo_anios"])
                    cuota_var = cuota_para(capital_final, c["i_var"], plazo_var) if plazo_var > 0 else 0.0
                    dti_val = max(
                        dti(cuota_fijo, c["deudas"], c["sueldo"]),
                        dti(cuota_var, c["deudas"], c["sueldo"])
                    )
                    st.write(f"Mixta fijo {pct(c['i_fijo'])} {c['fijo_anios']}a / "
                             f"var {pct(c['i_var'])} {plazo_var}a → peor DTI {pct(dti_val)} {flag_dti(dti_val)} | "
                             f"LTV {pct(ltv_val)} {flag_ltv(ltv_val)}")

                # Mostrar viabilidad conjunta
                if not is_viable_joint(dti_val, ltv_val, entrada_ok):
                    st.error("❌ Viabilidad conjunta")
                else:
                    st.success("✅ Viabilidad conjunta")

                dti_vals.append(dti_val)
                ltv_vals.append(ltv_val)

        # --- Resumen final ---
        st.subheader("📈 Resumen validación rápida")
        if dti_vals:
            st.write(f"DTI medio: {pct(stats.mean(dti_vals))} | "
                     f"máx: {pct(max(dti_vals))} | mín: {pct(min(dti_vals))}")
        if ltv_vals:
            st.write(f"LTV medio: {pct(stats.mean(ltv_vals))} | "
                     f"máx: {pct(max(ltv_vals))} | mín: {pct(min(ltv_vals))}")

        if fallos_codigo:
            st.error(f"❌ Se han detectado incoherencias de código en {len(fallos_codigo)} escenarios. Revisa app.py.")
            for esc_id, label in fallos_codigo:
                st.error(f"   → Escenario {esc_id}: {label}")
        else:
            st.success("✅ Todo correcto: la calculadora cumple en todos los escenarios. "
                       "No se han detectado incoherencias de código.")
    elif TIPO_VALIDACION == "intensa":
        st.subheader("🔍 Validación intensa (auditoría total)")

        operaciones = OPERACIONES_BASE  # todas las operaciones base
        dti_vals, ltv_vals = [], []
        fallos_codigo = []
        escenario_id = 0

        # --- Parámetros de sensibilidad y monotonicidad ---
        SENSIBILIDADES = [-0.02, -0.01, +0.01, +0.02]   # ±100 pb, ±200 pb
        MONO_INTERESES = [0.02, 0.03, 0.04, 0.05]
        MONO_PLAZOS    = [15, 20, 25, 30]

        # --- Validación de precio máximo ---
        def validar_precio_maximo(pipe_base, sueldo, deudas, interes, plazo):
            low, high = 60000, 800000
            mejor_precio = None
            for _ in range(20):
                mid = (low + high) // 2
                pipe = calcular_capital_y_gastos(
                    precio=mid, entrada=pipe_base["entrada"], params=params,
                    ltv_max=THRESHOLDS["LTV_warn"], financiar_comision=False
                )
                capital = pipe["capital_final"]
                ltv_mid = pipe["ltv"]
                entrada_ok_mid = pipe_base["entrada"] >= pipe["gastos_puros"]
                cuota_mid = cuota_para(capital, interes, plazo)
                dti_mid = dti(cuota_mid, deudas, sueldo)
                viable_mid = is_viable_joint(dti_mid, ltv_mid, entrada_ok_mid)
                if viable_mid:
                    mejor_precio = mid
                    low = mid + 1000
                else:
                    high = mid - 1000
            return mejor_precio

        # --- Escenarios aleatorios ---
        def generar_escenario_aleatorio():
            precio   = random.choice([130000, 180000, 220000, 300000, 380000])
            entrada  = random.choice([15000, 30000, 50000, 70000])
            ccaa     = random.choice(["Madrid", "Cataluña", "Andalucía", "Valencia", "Galicia"])
            estado   = random.choice(["Obra nueva", "Segunda mano"])
            financiar = random.choice([True, False])
            return {"precio": precio, "entrada": entrada, "ccaa": ccaa, "estado": estado, "financiar": financiar}

        ESCENARIOS_ALEATORIOS = [generar_escenario_aleatorio() for _ in range(6)]
        # --- Bucle principal de operaciones ---
        for op in operaciones:
            escenario_id += 1
            st.subheader(f"OPERACIÓN {escenario_id}: {op['ccaa']} — {op['estado']} — precio {eur(op['precio'])}")

            pipe = calcular_capital_y_gastos(
                precio=op["precio"], entrada=op["entrada"], params=params,
                ltv_max=THRESHOLDS["LTV_warn"], financiar_comision=op["financiar"]
            )

            capital_final = pipe["capital_final"]
            ltv_val = pipe["ltv"]
            entrada_ok = op["entrada"] >= pipe["gastos_puros"]

            # --- Hipoteca Fija ---
            for c in COMBOS_FIJA:
                cuota = cuota_para(capital_final, c["interes"], c["plazo"])
                dti_val = dti(cuota, c["deudas"], c["sueldo"])
                st.write(f"Fija {pct(c['interes'])}, {c['plazo']}a → cuota {eur(cuota)} "
                         f"→ DTI {pct(dti_val)} {flag_dti(dti_val)} | LTV {pct(ltv_val)} {flag_ltv(ltv_val)}")

                if not is_viable_joint(dti_val, ltv_val, entrada_ok):
                    st.error("❌ Viabilidad conjunta (Entrada + LTV + DTI)")
                else:
                    st.success("✅ Viabilidad conjunta")

                dti_vals.append(dti_val)
                ltv_vals.append(ltv_val)

            # --- Hipoteca Variable ---
            for c in COMBOS_VARIABLE:
                cuota = cuota_para(capital_final, c["interes"], c["plazo"])
                dti_val = dti(cuota, c["deudas"], c["sueldo"])
                st.write(f"Variable {pct(c['interes'])}, {c['plazo']}a → cuota {eur(cuota)} "
                         f"→ DTI {pct(dti_val)} {flag_dti(dti_val)} | LTV {pct(ltv_val)} {flag_ltv(ltv_val)}")

                if not is_viable_joint(dti_val, ltv_val, entrada_ok):
                    st.error("❌ Viabilidad conjunta (Entrada + LTV + DTI)")
                else:
                    st.success("✅ Viabilidad conjunta")

                dti_vals.append(dti_val)
                ltv_vals.append(ltv_val)

            # --- Hipoteca Mixta ---
            for c in COMBOS_MIXTA:
                plazo_var = max(0, c["plazo_total"] - c["fijo_anios"])
                cuota_fijo = cuota_para(capital_final, c["i_fijo"], c["fijo_anios"])
                cuota_var  = cuota_para(capital_final, c["i_var"], plazo_var) if plazo_var > 0 else 0.0

                dti_fijo = dti(cuota_fijo, c["deudas"], c["sueldo"])
                dti_var  = dti(cuota_var,  c["deudas"], c["sueldo"])
                dti_peor = max(dti_fijo, dti_var)
                tramo_peor = "FIJO" if dti_fijo >= dti_var else "VARIABLE"

                st.write(f"Mixta fijo {pct(c['i_fijo'])} {c['fijo_anios']}a / "
                         f"var {pct(c['i_var'])} {plazo_var}a → peor {tramo_peor}: "
                         f"DTI {pct(dti_peor)} {flag_dti(dti_peor)} | LTV {pct(ltv_val)} {flag_ltv(ltv_val)}")

                if not is_viable_joint(dti_peor, ltv_val, entrada_ok):
                    st.error("❌ Viabilidad conjunta (Entrada + LTV + DTI peor tramo)")
                else:
                    st.success("✅ Viabilidad conjunta")

                dti_vals.append(dti_peor)
                ltv_vals.append(ltv_val)
            # --- Sensibilidad de interés ---
            for delta in SENSIBILIDADES:
                interes_base = 0.03 + delta
                cuota_sens = cuota_para(capital_final, interes_base, 25)
                dti_sens = dti(cuota_sens, 200, 2800)
                st.caption(f"Sensibilidad interés {pct(interes_base)} (δ={pct(delta)}): "
                           f"cuota {eur(cuota_sens)} → DTI {pct(dti_sens)} {flag_dti(dti_sens)}")
                dti_vals.append(dti_sens)
                ltv_vals.append(ltv_val)

            # --- Monotonicidad de interés ---
            prev_dti = None
            for i in MONO_INTERESES:
                cuota_mono = cuota_para(capital_final, i, 25)
                dti_mono = dti(cuota_mono, 200, 2800)
                st.caption(f"Monotonicidad interés {pct(i)} → DTI {pct(dti_mono)}")
                if prev_dti is not None and dti_mono < prev_dti:
                    fallos_codigo.append((escenario_id, "DTI no crece con interés creciente"))
                prev_dti = dti_mono
                dti_vals.append(dti_mono)
                ltv_vals.append(ltv_val)

            # --- Monotonicidad de plazo ---
            prev_dti = None
            for p in MONO_PLAZOS:
                cuota_mono = cuota_para(capital_final, 0.03, p)
                dti_mono = dti(cuota_mono, 200, 2800)
                st.caption(f"Monotonicidad plazo {p}a → DTI {pct(dti_mono)}")
                if prev_dti is not None and dti_mono > prev_dti:
                    fallos_codigo.append((escenario_id, "DTI no baja al aumentar plazo"))
                prev_dti = dti_mono
                dti_vals.append(dti_mono)
                ltv_vals.append(ltv_val)

            # --- Precio máximo ---
            mejor_precio = validar_precio_maximo(
                pipe_base={"entrada": op["entrada"]},
                sueldo=2800, deudas=200, interes=0.03, plazo=25
            )
            if mejor_precio:
                st.caption(f"Precio máximo estimado coherente: {eur(mejor_precio)} (cumple Entrada/LTV/DTI)")
            else:
                st.caption("Precio máximo estimado: no encontrado dentro del rango configurado")
        # --- Escenarios aleatorios (stress test adicional) ---
        st.subheader("🎲 Stress test aleatorio")
        for rnd_idx, rnd in enumerate(ESCENARIOS_ALEATORIOS, start=1):
            st.markdown(f"**Aleatorio {rnd_idx}: {rnd['ccaa']} — {rnd['estado']} — precio {eur(rnd['precio'])}**")
            pipe = calcular_capital_y_gastos(
                precio=rnd["precio"], entrada=rnd["entrada"], params=params,
                ltv_max=THRESHOLDS["LTV_warn"], financiar_comision=rnd["financiar"]
            )
            capital = pipe["capital_final"]
            ltv_rnd = pipe["ltv"]
            entrada_ok_rnd = rnd["entrada"] >= pipe["gastos_puros"]

            # probamos una combinación rápida fija/variable/mixta
            cuota_f = cuota_para(capital, 0.03, 25); dti_f = dti(cuota_f, 200, 2800)
            cuota_v = cuota_para(capital, 0.04, 25); dti_v = dti(cuota_v, 150, 2800)
            cuota_mf = cuota_para(capital, 0.02, 10); cuota_mv = cuota_para(capital, 0.04, 20)
            dti_m = max(dti(cuota_mf, 250, 3200), dti(cuota_mv, 250, 3200))

            st.write(f"Fija → DTI {pct(dti_f)} {flag_dti(dti_f)} | LTV {pct(ltv_rnd)} {flag_ltv(ltv_rnd)}")
            st.write(f"Variable → DTI {pct(dti_v)} {flag_dti(dti_v)} | LTV {pct(ltv_rnd)} {flag_ltv(ltv_rnd)}")
            st.write(f"Mixta (peor) → DTI {pct(dti_m)} {flag_dti(dti_m)} | LTV {pct(ltv_rnd)} {flag_ltv(ltv_rnd)}")

            for dti_val in (dti_f, dti_v, dti_m):
                if not is_viable_joint(dti_val, ltv_rnd, entrada_ok_rnd):
                    st.error("❌ Viabilidad conjunta")
                else:
                    st.success("✅ Viabilidad conjunta")

                dti_vals.append(dti_val)
                ltv_vals.append(ltv_rnd)

        # --- Resumen ejecutivo único ---
        st.subheader("📈 Resumen validación intensa")
        if dti_vals:
            st.write(f"DTI medio: {pct(stats.mean(dti_vals))}")
            st.write(f"DTI máximo: {pct(max(dti_vals))}")
            st.write(f"DTI mínimo: {pct(min(dti_vals))}")
        if ltv_vals:
            st.write(f"LTV medio: {pct(stats.mean(ltv_vals))}")
            st.write(f"LTV máximo: {pct(max(ltv_vals))}")
            st.write(f"LTV mínimo: {pct(min(ltv_vals))}")

        if fallos_codigo:
            st.error(f"❌ Se han detectado incoherencias de código en {len(fallos_codigo)} escenarios. Revisa app.py.")
            for esc_id, label in fallos_codigo:
                st.error(f"   → Escenario {esc_id}: {label}")
        else:
            st.success("✅ Todo correcto: la calculadora cumple en todos los escenarios. "
                       "No se han detectado incoherencias de código.")







# =========================
# Pie de transparencia
# =========================
st.divider()
st.caption("""
**Autor:** Letalicus  
**Fecha de actualización:** Noviembre 2025
""")

