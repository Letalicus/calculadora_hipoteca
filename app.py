# ============================================================
# 🏠 Calculadora Hipotecaria Profesional
# Versión: 1.1.5
# Fecha: 2025-11-06
# Autor: Letalicus
#
# 📌 Resumen de cambios en esta versión:
# - Ajustada la lógica de entrada y capital financiado:
#   ahora se distingue correctamente entre hipoteca normal,
#   hipoteca reducida y compra al contado.
# - Evita mostrar "No disponible" cuando la entrada cubre
#   el precio completo de la vivienda (se indica que no se
#   requiere hipoteca).
# - Mensajes más claros y pedagógicos en todos los escenarios
#   de entrada, LTV y DTI.
# - Integración completa en el Modo 2: escenarios de interés,
#   consejos de viabilidad, amortización anticipada y resumen
#   compacto coherentes incluso sin hipoteca.
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

def cuota_mixta_peor_tramo(capital, plazo_anios, interes_fijo_pct, euribor_pct, diferencial_pct):
    """
    Calcula ambas cuotas (fijo y variable) sobre el plazo total y devuelve:
    (cuota_peor, cuota_fija, cuota_variable, tramo_peor)
    """
    if capital is None or capital <= 0 or plazo_anios <= 0:
        return None, None, None, None

    r_fijo = (interes_fijo_pct or 0.0)
    r_var  = ((euribor_pct or 0.0) + (diferencial_pct or 0.0))

    cuota_fija = cuota_prestamo(capital, r_fijo, plazo_anios) or 0.0
    cuota_var  = cuota_prestamo(capital, r_var,  plazo_anios) or 0.0

    cuota_peor = max(cuota_fija, cuota_var)
    tramo_peor = "FIJO" if cuota_peor == cuota_fija else "VARIABLE"
    return cuota_peor, cuota_fija, cuota_var, tramo_peor


# =========================
# Presets fiscales (simplificados y coherentes)
# =========================
PRESETS_IMPUESTOS = {
    "Andalucía": {"nuevo": {"iva": 0.10, "ajd": 0.015}, "segunda": {"itp": 0.08}},
    "Aragón": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Asturias": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Baleares": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},  # antes "Illes Balears"
    "Canarias": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.06}},  # simplificado
    "Cantabria": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.10}},
    "Castilla-La Mancha": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.09}},
    "Castilla y León": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Cataluña": {"nuevo": {"iva": 0.10, "ajd": 0.015}, "segunda": {"itp": 0.10}},
    "Ceuta y Melilla": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.06}},
    "Extremadura": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Galicia": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.09}},
    "La Rioja": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.07}},
    "Madrid": {"nuevo": {"iva": 0.10, "ajd": 0.007}, "segunda": {"itp": 0.06}},
    "Murcia": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.08}},
    "Navarra": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.06}},
    "País Vasco": {"nuevo": {"iva": 0.10, "ajd": 0.010}, "segunda": {"itp": 0.04}},
    "Valencia": {"nuevo": {"iva": 0.10, "ajd": 0.015}, "segunda": {"itp": 0.10}},  # antes "Comunidad Valenciana"
}


# =========================
# Lista de comunidades (ordenada alfabéticamente)
# =========================
comunidades = sorted(PRESETS_IMPUESTOS.keys())



def tipo_impuesto_por_ccaa(ccaa, estado):
    data = PRESETS_IMPUESTOS.get(ccaa, PRESETS_IMPUESTOS["Madrid"])
    if estado == "Nuevo":
        return data["nuevo"]["iva"] + data["nuevo"]["ajd"]
    else:
        return data["segunda"]["itp"]

# =========================
# Explicaciones fiscales (alineadas con presets simplificados)
# =========================
EXPLICACION_IMPUESTOS = {
    ("Madrid", "Nuevo"): "En Madrid (obra nueva) se aplica IVA 10% + AJD 0,7%.",
    ("Madrid", "Segunda mano"): "En Madrid (segunda mano) se aplica ITP 6%.",

    ("Cataluña", "Nuevo"): "En Cataluña (obra nueva) se aplica IVA 10% + AJD 1,5%.",
    ("Cataluña", "Segunda mano"): "En Cataluña (segunda mano) se aplica ITP 10%.",

    ("Andalucía", "Nuevo"): "En Andalucía (obra nueva) se aplica IVA 10% + AJD 1,5%.",
    ("Andalucía", "Segunda mano"): "En Andalucía (segunda mano) se aplica ITP 8%.",

    ("Valencia", "Nuevo"): "En Valencia (obra nueva) se aplica IVA 10% + AJD 1,5%.",
    ("Valencia", "Segunda mano"): "En Valencia (segunda mano) se aplica ITP 10%.",

    ("País Vasco", "Nuevo"): "En País Vasco (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("País Vasco", "Segunda mano"): "En País Vasco (segunda mano) se aplica ITP 4%.",

    ("Navarra", "Nuevo"): "En Navarra (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Navarra", "Segunda mano"): "En Navarra (segunda mano) se aplica ITP 6%.",

    ("Galicia", "Nuevo"): "En Galicia (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Galicia", "Segunda mano"): "En Galicia (segunda mano) se aplica ITP 9%.",

    ("Castilla y León", "Nuevo"): "En Castilla y León (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Castilla y León", "Segunda mano"): "En Castilla y León (segunda mano) se aplica ITP 8%.",

    ("Castilla-La Mancha", "Nuevo"): "En Castilla-La Mancha (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Castilla-La Mancha", "Segunda mano"): "En Castilla-La Mancha (segunda mano) se aplica ITP 9%.",

    ("Murcia", "Nuevo"): "En Murcia (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Murcia", "Segunda mano"): "En Murcia (segunda mano) se aplica ITP 8%.",

    ("La Rioja", "Nuevo"): "En La Rioja (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("La Rioja", "Segunda mano"): "En La Rioja (segunda mano) se aplica ITP 7%.",

    ("Cantabria", "Nuevo"): "En Cantabria (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Cantabria", "Segunda mano"): "En Cantabria (segunda mano) se aplica ITP 10%.",

    ("Aragón", "Nuevo"): "En Aragón (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Aragón", "Segunda mano"): "En Aragón (segunda mano) se aplica ITP 8%.",

    ("Asturias", "Nuevo"): "En Asturias (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Asturias", "Segunda mano"): "En Asturias (segunda mano) se aplica ITP 8%.",

    ("Baleares", "Nuevo"): "En Baleares (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Baleares", "Segunda mano"): "En Baleares (segunda mano) se aplica ITP 8%.",

    ("Extremadura", "Nuevo"): "En Extremadura (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Extremadura", "Segunda mano"): "En Extremadura (segunda mano) se aplica ITP 8%.",

    ("Ceuta y Melilla", "Nuevo"): "En Ceuta y Melilla (obra nueva) se aplica IVA 10% + AJD 1,0%.",
    ("Ceuta y Melilla", "Segunda mano"): "En Ceuta y Melilla (segunda mano) se aplica ITP 6%.",

    ("Canarias", "Nuevo"): "En Canarias (obra nueva) IVA 10% + AJD 1,0% (simplificación).",
    ("Canarias", "Segunda mano"): "En Canarias (segunda mano) ITP 6% (simplificación).",
}



# =========================
# Sidebar completo (reordenado con tooltips restaurados)
# =========================

# === Valores por defecto ===
DEFAULTS = {
    "modo": "📘 Instrucciones",
    "edad": 18,
    "sueldo": 0.0,
    "deudas": 0.0,
    "entrada": 0.0,
    "ratio_dti": 35,
    "ltv": 80,
    "plazo": 30,
    "tipo_hipoteca": "Fija",
    "interes_fijo": 4.0,
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
    "Comunidad autónoma", comunidades, key="ccaa",
    help="La fiscalidad de la compra varía por CCAA. Impacta en IVA/ITP y AJD, afectando la entrada necesaria."
)

# Recuperamos los presets fiscales de la comunidad seleccionada
presets = PRESETS_IMPUESTOS[ccaa]


estado_vivienda = st.sidebar.radio(
    "Estado", ["Nuevo", "Segunda mano"], key="estado_vivienda",
    help="Obra nueva: IVA + AJD. Segunda mano: ITP. Cambia el coste fiscal y la entrada mínima necesaria."
)


# 👇 NUEVO BLOQUE: Uso de la vivienda
uso_vivienda = st.sidebar.radio(
    "Uso de la vivienda",
    ["🏠 Vivienda habitual", "🏖️ Segunda residencia / inversión"],
    key="uso_vivienda",
    help=(
        "Los bancos suelen ofrecer hasta el 80 % de financiación y plazos de hasta 30–35 años "
        "para vivienda habitual.\n\n"
        "Para segunda residencia/inversión, lo habitual es un 60–70 % de financiación y plazos "
        "de 20–25 años, con tipos de interés algo más altos."
    )
)

# --- Inicializar memoria del último uso seleccionado ---
if "uso_vivienda_prev" not in st.session_state:
    st.session_state["uso_vivienda_prev"] = uso_vivienda

# --- Aplicar presets SOLO si el usuario cambia de opción ---
if uso_vivienda != st.session_state["uso_vivienda_prev"]:
    if uso_vivienda == "🏠 Vivienda habitual":
        st.session_state["ltv"] = 80
        st.session_state["plazo"] = 30
    elif uso_vivienda == "🏖️ Segunda residencia / inversión":
        st.session_state["ltv"] = 70
        st.session_state["plazo"] = 25

# --- Actualizar el valor previo ---
st.session_state["uso_vivienda_prev"] = uso_vivienda

# 👇 Continúa con la parte de impuestos
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

# === Mensaje contextual en pantalla principal ===
if uso_vivienda == "🏖️ Segunda residencia / inversión":
    st.info(
        "ℹ️ Has seleccionado **segunda residencia/inversión**. "
        "Ten en cuenta que los bancos suelen limitar la financiación al 60–70 % del valor "
        "y reducir el plazo máximo a 20–25 años, aplicando además tipos de interés algo más altos. "
        "Esto se refleja en los valores iniciales de LTV y plazo, aunque puedes ajustarlos libremente."
    )



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
        f"✅ El cálculo valida automáticamente que el **DTI ≤ {int(DTI_FAIL*100)} %** y que el **LTV ≤ LTV máximo**, "
        "por lo que el resultado mostrado es siempre viable bajo criterios bancarios habituales.\n\n"
        "⚠️ **Nota importante:** el precio máximo mostrado aquí debe entenderse como una **referencia aproximada del límite**. "
        "Conviene dejar un pequeño margen de seguridad por debajo de este valor."
    )

    # Validación de parámetros mínimos
    if sueldo_neto <= 0:
        st.error("⚠️ Debes introducir un sueldo neto mensual mayor que 0 para calcular el precio máximo de vivienda.")
    elif entrada_usuario <= 0:
        st.error("⚠️ Debes introducir una entrada aportada mayor que 0.")
    else:
        # --- Cálculo de cuota máxima ---
        cuota_max = cuota_maxima(sueldo_neto, deudas_mensuales, ratio=ratio_dti)

        # --- Búsqueda binaria del precio máximo viable ---
        low, high = 0.0, 2_000_000.0
        precio_maximo = 0.0
        for _ in range(50):
            mid = (low + high) / 2

            r_mid = calcular_capital_y_gastos(
                mid, entrada_usuario, params,
                ltv_max=ltv_max, financiar_comision=financiar_comision
            )
            capital_mid = r_mid["capital_final"]
            ltv_ok = r_mid["ltv_ok"]
            entrada_ok = entrada_usuario >= r_mid["gastos_puros"]

            # Cuota según tipo de hipoteca
            if tipo_hipoteca in ["Fija", "Variable"] and interes_anual:
                cuota_mid = cuota_prestamo(capital_mid, interes_anual, anos_plazo) or 0.0
                dti_mid = dti(cuota_mid, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0

            elif tipo_hipoteca == "Mixta" and (interes_fijo is not None) and (euribor is not None) and (diferencial is not None):
                interes_variable_mid = euribor + diferencial
                cuota_mid_fijo = cuota_prestamo(capital_mid, interes_fijo, anos_plazo) or 0.0
                cuota_mid_var  = cuota_prestamo(capital_mid, interes_variable_mid, anos_plazo) or 0.0
                cuota_mid = max(cuota_mid_fijo, cuota_mid_var)
                dti_mid = dti(cuota_mid, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0

            else:
                cuota_mid = 0.0
                dti_mid = 0.0

            cuota_ok = cuota_mid <= cuota_max
            dti_ok = dti_visible(dti_mid) <= DTI_FAIL

            if entrada_ok and ltv_ok and dti_ok and cuota_ok:
                precio_maximo = mid
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

        # Guardamos en sesión
        st.session_state["precio_max_modo1"] = precio_maximo

        
        
        # =========================
        # 📌 Resultado del modo Descubrir
        # =========================
        st.header("📌 Resultado del modo Descubrir")
        c1, c2, c3 = st.columns(3)

        # Mostrar siempre la cuota máxima
        c1.metric("💶 Cuota máxima mensual", eur(cuota_max))

        # Mostrar siempre el bloque de precio máximo, pero con "No disponible" si es 0
        if precio_maximo <= 0:
            c2.metric("🏠 Precio máximo vivienda", "No disponible")
            st.warning("⚠️ Con los parámetros introducidos no es posible calcular un precio máximo de vivienda viable. "
                    "Revisa tu sueldo neto, entrada aportada y plazo de hipoteca.")
        else:
            c2.metric("🏠 Precio máximo vivienda", eur(precio_maximo))

        # Mostrar el tipo de interés según hipoteca
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
                interes_variable_esc = interes_var_esc + diferencial
                cuota_fijo_esc = cuota_prestamo(capital_hipoteca, interes_fijo, anos_plazo) or 0.0
                cuota_var_esc  = cuota_prestamo(capital_hipoteca, interes_variable_esc, anos_plazo) or 0.0
                cuota_peor_esc = max(cuota_fijo_esc, cuota_var_esc)
                dti_peor_esc = dti(cuota_peor_esc, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0
                tramo_peor = "FIJO" if cuota_fijo_esc >= cuota_var_esc else "VARIABLE"
                if es_viable(cuota_peor_esc, cuota_max, ltv_val, ltv_max, dti_peor_esc):
                    st.success(
                        f"✅ fijo {pct(interes_fijo)} / var {pct(interes_variable_esc)} → peor tramo {tramo_peor}: "
                        f"cuota {eur(cuota_peor_esc)} | DTI {semaforo_dti(dti_peor_esc)}"
                    )
                else:
                    st.error(
                        f"❌ fijo {pct(interes_fijo)} / var {pct(interes_variable_esc)} → peor tramo {tramo_peor}: "
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
        "- Precio de la vivienda (€).\n"
        "- Sueldo neto mensual.\n"
        "- Otras deudas mensuales.\n"
        "- Entrada aportada.\n"
        "- Plazo de la hipoteca.\n"
        "- Tipo de hipoteca e interés correspondiente.\n\n"
        "ℹ️ Con estos datos, la calculadora mostrará: LTV, DTI, coste total de la operación, "
        "escenarios de interés, consejos de viabilidad y tablas de amortización.\n\n"
        "⚠️ Nota importante: si introduces aquí exactamente el precio máximo del Modo 1, "
        "puede aparecer como **no viable** por redondeos o porque el DTI real supere mínimamente el 35 %."
    )

    # ✅ Validación de parámetros mínimos
    if precio <= 0:
        st.error("⚠️ Debes introducir un precio de vivienda mayor que 0.")
    elif sueldo_neto <= 0:
        st.error("⚠️ Debes introducir un sueldo neto mensual mayor que 0.")
    elif entrada_usuario <= 0:
        st.error("⚠️ Debes introducir una entrada aportada mayor que 0.")
    else:
        # --- Cálculo de capital y gastos (usa tu función existente) ---
        r = calcular_capital_y_gastos(
            precio,
            entrada_usuario,
            params,
            ltv_max=ltv_max,
            financiar_comision=financiar_comision
        )

        gastos_puros = r["gastos_puros"]                # impuestos + trámites
        diferencia_entrada = r["diferencia_entrada"]    # entrada - gastos_puros (puede ser negativa)
        excedente = r["excedente"]                      # sobrante aplicado al precio o préstamo
        capital_hipoteca = r["capital_final"]           # capital a financiar tras aplicar excedente
        ltv_val = r["ltv"]                              # capital_final/precio
        ltv_ok = r.get("ltv_ok", True)

        cuota_max = cuota_maxima(sueldo_neto, deudas_mensuales, ratio=ratio_dti)

        # --- Determinar si hay hipoteca (compra al contado si capital=0) ---
        sin_hipoteca = (capital_hipoteca <= 0 and diferencia_entrada >= precio)

        # --- Cuota estimada según tipo (solo si hay hipoteca) ---
        cuota_estimada = 0.0
        tramo_peor = None
        if not sin_hipoteca:
            if tipo_hipoteca in ["Fija", "Variable"] and interes_anual:
                cuota_estimada = cuota_prestamo(capital_hipoteca, interes_anual, anos_plazo) or 0.0
            elif (
                tipo_hipoteca == "Mixta"
                and (interes_fijo is not None)
                and (euribor is not None)
                and (diferencial is not None)
            ):
                interes_variable_total = euribor + diferencial
                cuota_fijo_total = cuota_prestamo(capital_hipoteca, interes_fijo, anos_plazo) or 0.0
                cuota_variable_total = cuota_prestamo(capital_hipoteca, interes_variable_total, anos_plazo) or 0.0
                cuota_estimada = max(cuota_fijo_total, cuota_variable_total)
                tramo_peor = "FIJO" if cuota_estimada == cuota_fijo_total else "VARIABLE"

        # --- DTI (solo sentido si hay hipoteca y sueldo > 0) ---
        dti_val = round(dti(cuota_estimada, deudas_mensuales, sueldo_neto), 4) if (sueldo_neto > 0 and not sin_hipoteca) else 0.0
        # =========================
        # 📌 Resumen de la vivienda
        # =========================
        st.header("📌 Resumen de la vivienda")
        c1, c2, c3, c4 = st.columns(4)

        c1.metric("💰 Precio vivienda", eur(precio))
        c2.metric("🧾 Impuestos y gastos", eur(gastos_puros) if gastos_puros > 0 else "No disponible")
        c3.metric("🏦 Capital a financiar", eur(capital_hipoteca) if capital_hipoteca > 0 else ("0,00 €" if sin_hipoteca else "No disponible"))
        c4.metric("💵 Capital no financiado", eur(excedente) if excedente > 0 else (eur(0) if diferencia_entrada >= 0 else "No disponible"))

        st.divider()

        # =========================
        # 1️⃣ Entrada
        # =========================
        st.subheader("1️⃣ Entrada")
        st.write(f"Entrada aportada: **{eur(entrada_usuario)}**")
        st.write(f"Gastos de compra (impuestos + trámites): **{eur(gastos_puros) if gastos_puros > 0 else 'No disponible'}**")

        if diferencia_entrada < 0:
            st.error(f"❌ Entrada insuficiente. Te faltan: {eur(-diferencia_entrada)}")
        elif sin_hipoteca:
            st.success("✅ Entrada suficiente. No se requiere hipoteca: la entrada cubre el precio completo de la vivienda.")
        elif diferencia_entrada >= 0:
            st.success(f"✅ Entrada suficiente. El excedente se aplica al precio de la vivienda, reduciendo el préstamo necesario: {eur(excedente)}")



        # --- Texto aclaratorio ratios (solo aplica si hay hipoteca) ---
        st.info(
            "ℹ️ En este modo se muestran explícitamente los ratios clave: **DTI (endeudamiento)** y **LTV (porcentaje financiado)**. "
            "Un DTI ≤ 35 % y LTV ≤ 80 % suelen considerarse dentro de rangos aceptables."
        )

        # =========================
        # 📑 Impuestos y comisión de apertura (pre-cálculo)
        # =========================
        if usar_manual:
            iva_itp_pct = st.session_state.get("iva_itp", 0.0) / 100
            ajd_pct = st.session_state.get("ajd", 0.0) / 100
            if estado_vivienda == "Nuevo":
                iva_itp_label = "IVA"
                iva_itp_val = precio * iva_itp_pct if precio > 0 else 0.0
                ajd_val = precio * ajd_pct if precio > 0 else 0.0
            else:
                iva_itp_label = "ITP"
                iva_itp_val = precio * iva_itp_pct if precio > 0 else 0.0
                ajd_val = 0.0
        else:
            preset = PRESETS_IMPUESTOS.get(ccaa, PRESETS_IMPUESTOS.get("Madrid", {}))
            if estado_vivienda == "Nuevo":
                iva_itp_label = "IVA"
                iva_itp_pct = preset.get("nuevo", {}).get("iva", 0.0)
                ajd_pct = preset.get("nuevo", {}).get("ajd", 0.0)
                iva_itp_val = precio * iva_itp_pct if precio > 0 else 0.0
                ajd_val = precio * ajd_pct if precio > 0 else 0.0
            else:
                iva_itp_label = "ITP"
                iva_itp_pct = preset.get("segunda", {}).get("itp", 0.0)
                ajd_pct = 0.0
                iva_itp_val = precio * iva_itp_pct if precio > 0 else 0.0
                ajd_val = 0.0

        # Comisión de apertura (si existe)
        if com_apertura_pct > 0 and not sin_hipoteca:
            if financiar_comision:
                capital_preliminar_aprox = capital_hipoteca / (1 + com_apertura_pct) if capital_hipoteca > 0 else 0.0
                com_apertura_val = max(0.0, capital_hipoteca - capital_preliminar_aprox)
                com_label = "Comisión apertura (financiada)"
                com_incluida_en_gastos = False
            else:
                capital_preliminar_aprox = capital_hipoteca
                com_apertura_val = capital_preliminar_aprox * com_apertura_pct if capital_preliminar_aprox > 0 else 0.0
                com_label = "Comisión apertura (pagada al inicio)"
                com_incluida_en_gastos = True
        else:
            com_apertura_val = 0.0
            com_label = "Sin comisión de apertura"
            com_incluida_en_gastos = False
        # =========================
        # 2️⃣ Hipoteca
        # =========================
        st.header("2️⃣ Hipoteca")

        c1, c2, c3 = st.columns(3)
        c1.metric("📉 LTV", (pct(ltv_val) if ltv_val > 0 else ("0,00%" if sin_hipoteca else "No disponible")))
        c2.metric("📅 Plazo", f"{anos_plazo} años" if anos_plazo > 0 else "No disponible")
        c3.metric("💶 Cuota máxima permitida", eur(cuota_max) if cuota_max > 0 else "No disponible")

        if sin_hipoteca:
            st.write("**Cuota mensual estimada:** 0,00 €")
            st.info("ℹ️ No se requiere hipoteca: la entrada cubre el precio completo de la vivienda.")
        else:
            if tipo_hipoteca == "Mixta" and tramo_peor and cuota_estimada > 0:
                st.write(f"**Cuota mensual estimada (peor tramo {tramo_peor}):** {eur(cuota_estimada)}")
            else:
                st.write(f"**Cuota mensual estimada:** {eur(cuota_estimada) if cuota_estimada > 0 else 'No disponible'}")

            # Evaluación combinada (solo si hay hipoteca)
            if cuota_estimada > 0 and es_viable(cuota_estimada, cuota_max, ltv_val, ltv_max, dti_val):
                if dti_val <= DTI_WARN:
                    st.success(
                        f"DTI estimado: 🟢 {pct_dti(dti_val)} (Seguro)\n\n"
                        "Con endeudamiento y LTV dentro de límite, la operación se considera solvente."
                    )
                else:
                    st.warning(
                        f"DTI estimado: 🟡 {pct_dti(dti_val)} (Moderado)\n\n"
                        "La operación es viable, aunque podrían analizar estabilidad, avales o perfil de riesgo."
                    )
            else:
                if not ltv_ok and dti_visible(dti_val) > DTI_FAIL:
                    st.error(
                        f"❌ LTV real {pct(ltv_val)} (máx. {pct(ltv_max)}) y DTI {pct_dti(dti_val)}.\n\n"
                        "La operación no es viable: supera tanto el límite de financiación (LTV) como el endeudamiento (DTI)."
                    )
                elif not ltv_ok:
                    st.error(
                        f"⚠️ El LTV real ({pct(ltv_val)}) supera el máximo permitido ({pct(ltv_max)}).\n\n"
                        f"Aunque el DTI es {pct_dti(dti_val)} y estaría dentro de rango, la operación no sería viable."
                    )
                elif dti_visible(dti_val) > DTI_FAIL:
                    st.error(
                        f"⚠️ El LTV real ({pct(ltv_val)}) está dentro del límite ({pct(ltv_max)}), "
                        f"pero el DTI es {pct_dti(dti_val)} (Arriesgado).\n\n"
                        "Por encima del 35 % los bancos suelen rechazar la operación salvo condiciones excepcionales."
                    )

        st.caption("DTI = (Cuota hipoteca + otras deudas) / Ingresos netos")

        # =========================
        # 💵 Coste total de la operación
        # =========================
        import pandas as pd

        st.subheader("💵 Coste total de la operación")

        impuestos_total = (iva_itp_val + ajd_val) if precio > 0 else 0.0
        gastos_formalizacion_total = (notario + registro + gestoria + tasacion + seguro_inicial)
        gastos_compra_total = impuestos_total + gastos_formalizacion_total + (com_apertura_val if com_incluida_en_gastos else 0.0)
        coste_inicial_total = (precio + gastos_compra_total) if precio > 0 else 0.0

        # Pagos al banco (si hay hipoteca)
        if not sin_hipoteca and tipo_hipoteca in ["Fija", "Variable"] and cuota_estimada > 0 and capital_hipoteca > 0:
            pagos_totales = cuota_estimada * anos_plazo * 12
            intereses_totales = max(0.0, pagos_totales - capital_hipoteca)
            capital_amortizado = capital_hipoteca
        elif not sin_hipoteca and tipo_hipoteca == "Mixta" and cuota_estimada > 0 and capital_hipoteca > 0:
            cuota_fijo = cuota_prestamo(capital_hipoteca, interes_fijo, anios_fijo) or 0.0
            pagos_fijo = cuota_fijo * anios_fijo * 12
            plazo_var = max(0, anos_plazo - anios_fijo)
            cuota_var = cuota_prestamo(capital_hipoteca, interes_variable, plazo_var) if plazo_var > 0 else 0.0
            pagos_var = cuota_var * plazo_var * 12
            pagos_totales = pagos_fijo + pagos_var
            intereses_totales = max(0.0, pagos_totales - capital_hipoteca)
            capital_amortizado = capital_hipoteca
        else:
            pagos_totales = 0.0
            intereses_totales = 0.0
            capital_amortizado = 0.0

        coste_total = (coste_inicial_total + intereses_totales) if precio > 0 else 0.0

        # --- Tabla resumen ---
        tabla_resumen = pd.DataFrame([
            ["⚖️ Coste inicial (precio + impuestos + gastos)", eur(coste_inicial_total) if coste_inicial_total > 0 else "No disponible"],
            ["➕ Intereses totales (pagados al banco)", (eur(intereses_totales) if intereses_totales > 0 else ("0,00 €" if sin_hipoteca else "No disponible"))],
            ["➡️ Coste total con hipoteca", eur(coste_total) if coste_total > 0 else "No disponible"]
        ], columns=["Concepto", "Importe"])

        def resaltar_resumen(row):
            if "Coste total" in row["Concepto"]:
                return ["background-color: #14532d; color: white; font-weight: bold"] * len(row)
            return [""] * len(row)

        st.dataframe(
            tabla_resumen.style
                .apply(resaltar_resumen, axis=1)
                .set_properties(**{"text-align": "left", "white-space": "nowrap"}),
            width="stretch",
            hide_index=True
        )
        st.caption("El coste inicial incluye precio, impuestos y gastos de compra. "
                   "Los pagos al banco incluyen solo capital e intereses. "
                   "El coste total con hipoteca es la suma de ambos mundos.")

        # --- Expander con el desglose completo ---
        with st.expander("📊 Ver desglose completo"):
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
                    return ["background-color: #1e3a8a; color: white; font-weight: bold"] * len(row)
                return [""] * len(row)

            st.dataframe(
                tabla_compra.style
                    .apply(resaltar_totales, axis=1)
                    .set_properties(**{"text-align": "left", "white-space": "nowrap"}),
                width="stretch",
                hide_index=True
            )
            st.caption("Este bloque refleja lo que cuesta formalizar la compra: precio, impuestos y gastos iniciales. No incluye las cuotas al banco.")

            tabla_banco = pd.DataFrame([
                ["Capital amortizado (devuelto al banco)", eur(capital_amortizado) if capital_amortizado > 0 else ("0,00 €" if sin_hipoteca else "No disponible")],
                ["Intereses totales (coste financiero)", eur(intereses_totales) if intereses_totales > 0 else ("0,00 €" if sin_hipoteca else "No disponible")],
                ["Pagos totales al banco (todas las cuotas)", eur(pagos_totales) if pagos_totales > 0 else ("0,00 €" if sin_hipoteca else "No disponible")]
            ], columns=["Concepto", "Importe"])

            def resaltar_banco(row):
                if "Pagos totales" in row["Concepto"]:
                    return ["background-color: #7c2d12; color: white; font-weight: bold"] * len(row)
                return [""] * len(row)

            st.dataframe(
                tabla_banco.style
                    .apply(resaltar_banco, axis=1)
                    .set_properties(**{"text-align": "left", "white-space": "nowrap"}),
                width="stretch",
                hide_index=True
            )
            st.caption("Este bloque refleja lo que pagarás en cuotas al banco: capital + intereses. No incluye impuestos ni gastos iniciales.")
        # =========================
        # 📊 Escenarios de interés (2%–5%)
        # =========================
        st.subheader("📊 Escenarios de interés (2%–5%)")
        st.caption("Simulación de la cuota mensual en distintos escenarios de tipo de interés, validando LTV + DTI.")

        if sin_hipoteca:
            st.info("ℹ️ No se simulan escenarios porque no se requiere hipoteca.")
        else:
            if capital_hipoteca <= 0 or sueldo_neto <= 0:
                st.warning("⚠️ No se pueden simular escenarios porque faltan parámetros mínimos (sueldo o capital a financiar).")
            else:
                if tipo_hipoteca == "Fija":
                    for interes_pct in ESCENARIOS_INTERES_PCT:
                        interes_decimal = interes_pct / 100
                        cuota_esc = cuota_prestamo(capital_hipoteca, interes_decimal, anos_plazo) or 0.0
                        dti_esc = dti(cuota_esc, deudas_mensuales, sueldo_neto)
                        if es_viable(cuota_esc, cuota_max, ltv_val, ltv_max, dti_esc):
                            st.success(f"✅ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")
                        else:
                            st.error(f"❌ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")

                elif tipo_hipoteca == "Variable":
                    for interes_pct in ESCENARIOS_INTERES_PCT:
                        interes_decimal = interes_pct / 100
                        cuota_esc = cuota_prestamo(capital_hipoteca, interes_decimal, anos_plazo) or 0.0
                        dti_esc = dti(cuota_esc, deudas_mensuales, sueldo_neto)
                        if es_viable(cuota_esc, cuota_max, ltv_val, ltv_max, dti_esc):
                            st.success(f"✅ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")
                        else:
                            st.error(f"❌ {pct(interes_decimal)} → cuota {eur(cuota_esc)} | DTI {semaforo_dti(dti_esc)}")

                elif tipo_hipoteca == "Mixta":
                    for interes_pct in ESCENARIOS_INTERES_PCT:
                        interes_variable_esc = (interes_pct / 100) + diferencial
                        cuota_fijo_esc = cuota_prestamo(capital_hipoteca, interes_fijo, anos_plazo) or 0.0
                        cuota_var_esc  = cuota_prestamo(capital_hipoteca, interes_variable_esc, anos_plazo) or 0.0
                        cuota_peor_esc = max(cuota_fijo_esc, cuota_var_esc)
                        dti_peor_esc = dti(cuota_peor_esc, deudas_mensuales, sueldo_neto)
                        tramo_peor_esc = "FIJO" if cuota_fijo_esc >= cuota_var_esc else "VARIABLE"
                        if es_viable(cuota_peor_esc, cuota_max, ltv_val, ltv_max, dti_peor_esc):
                            st.success(
                                f"✅ fijo {pct(interes_fijo)} / var {pct(interes_variable_esc)} → peor tramo {tramo_peor_esc}: "
                                f"cuota {eur(cuota_peor_esc)} | DTI {semaforo_dti(dti_peor_esc)}"
                            )
                        else:
                            st.error(
                                f"❌ fijo {pct(interes_fijo)} / var {pct(interes_variable_esc)} → peor tramo {tramo_peor_esc}: "
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

        if sin_hipoteca:
            st.info("ℹ️ No se generan consejos: no se requiere hipoteca.")
        else:
            if cuota_estimada <= 0 or precio <= 0 or sueldo_neto <= 0 or entrada_usuario <= 0:
                st.warning("⚠️ No se pueden generar consejos porque faltan parámetros mínimos.")
            else:
                if tipo_hipoteca == "Mixta":
                    interes_variable_total = euribor + diferencial
                    cuota_fijo_total = cuota_prestamo(capital_hipoteca, interes_fijo, anos_plazo) or 0.0
                    cuota_var_total  = cuota_prestamo(capital_hipoteca, interes_variable_total, anos_plazo) or 0.0

                    dti_fijo = dti(cuota_fijo_total, deudas_mensuales, sueldo_neto)
                    dti_variable = dti(cuota_var_total, deudas_mensuales, sueldo_neto)
                    dti_peor = max(dti_fijo, dti_variable)
                    cuota_peor = max(cuota_fijo_total, cuota_var_total)

                    if not es_viable(cuota_peor, cuota_max, ltv_val, ltv_max, dti_peor):
                        if dti_visible(dti_peor) > DTI_FAIL:
                            consejos.append("👉 Aporta más entrada, amplía el plazo o negocia condiciones.")
                        elif DTI_WARN < dti_visible(dti_peor) <= DTI_FAIL:
                            consejos.append("👉 DTI en zona límite. Revisa estabilidad o avales.")
                        if ltv_val > ltv_max:
                            consejos.append("👉 Reduce LTV aportando más entrada o ajustando el precio.")

                    if not consejos:
                        st.success("✅ Tu operación es viable con los parámetros actuales (considerando ambos tramos).")
                    else:
                        for c in consejos:
                            st.warning(c)

                else:  # Fija/Variable
                    dti_dashboard = dti_val
                    if not es_viable(cuota_estimada, cuota_max, ltv_val, ltv_max, dti_dashboard):
                        if dti_visible(dti_dashboard) > DTI_FAIL:
                            consejos.append("👉 Aumenta entrada o reduce el precio.")
                            consejos.append("👉 Negocia un interés más bajo.")
                            consejos.append("👉 Amplía el plazo para bajar la cuota mensual.")
                        elif DTI_WARN < dti_visible(dti_dashboard) <= DTI_FAIL:
                            consejos.append("👉 Estás en zona límite de DTI. Considera ampliar plazo o negociar condiciones.")
                        if ltv_val > ltv_max:
                            consejos.append("👉 Reduce LTV aportando más entrada o ajustando el precio.")

                    if not consejos:
                        st.success("✅ Tu operación es viable con los parámetros actuales.")
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

        if simular_amortizacion:
            if sin_hipoteca:
                st.info("ℹ️ No aplica amortización anticipada: no hay hipoteca.")
            elif tipo_hipoteca == "Mixta":
                st.warning("⚠️ La simulación solo está disponible para hipotecas Fijas o Variables.")
            elif cuota_estimada <= 0 or capital_hipoteca <= 0:
                st.warning("⚠️ No se puede simular: faltan parámetros válidos.")
            else:
                anio_extra = st.number_input("Año de amortización anticipada", min_value=1, max_value=anos_plazo, value=5, step=1)
                pago_extra = st.number_input("Cantidad del pago extra (€)", min_value=0.0, step=1000.0, value=5000.0)
                mantener_cuota = st.radio("¿Qué prefieres tras amortizar?", ["Reducir plazo", "Reducir cuota"], index=0)

                n_total = anos_plazo * 12
                n_transcurridos = anio_extra * 12
                r_mensual = interes_anual / 12 if interes_anual else 0.0

                if r_mensual > 0 and cuota_estimada > 0:
                    capital_pendiente = capital_hipoteca * (
                        ((1 + r_mensual) ** n_total - (1 + r_mensual) ** n_transcurridos)
                        / ((1 + r_mensual) ** n_total - 1)
                    )
                else:
                    capital_pendiente = capital_hipoteca * (1 - n_transcurridos / n_total)

                nuevo_capital = max(0.0, capital_pendiente - pago_extra)

                if mantener_cuota == "Reducir plazo":
                    import math
                    if r_mensual > 0 and cuota_estimada > 0:
                        nuevo_plazo_meses = math.log(
                            cuota_estimada / (cuota_estimada - nuevo_capital * r_mensual)
                        ) / math.log(1 + r_mensual)
                        nuevo_plazo_anios = max(0, nuevo_plazo_meses / 12)
                    else:
                        nuevo_plazo_anios = 0
                    st.info(
                        f"📉 Con amortización anticipada de {eur(pago_extra)} en el año {anio_extra}, "
                        f"reduces el plazo a **{nuevo_plazo_anios:.1f} años** manteniendo la misma cuota."
                    )
                else:
                    nuevo_plazo_restante = max(1, anos_plazo - anio_extra)
                    nueva_cuota = cuota_prestamo(nuevo_capital, interes_anual, nuevo_plazo_restante) or 0.0
                    st.info(
                        f"📉 Con amortización anticipada de {eur(pago_extra)} en el año {anio_extra}, "
                        f"tu nueva cuota sería de **{eur(nueva_cuota)}** manteniendo el plazo original."
                    )

        # =========================
        # 📊 Tabla de amortización simplificada (por años)
        # =========================
        st.divider()
        st.subheader("📊 Tabla de amortización simplificada (por años)")

        if sin_hipoteca:
            st.info("ℹ️ No hay tabla de amortización: no existe hipoteca.")
        else:
            if cuota_estimada <= 0 or capital_hipoteca <= 0:
                st.warning("⚠️ No se puede generar la tabla de amortización porque faltan parámetros válidos.")
            else:
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
                    st.dataframe(df_amort, width="stretch")
                    st.caption("En hipotecas fijas o variables, la cuota se mantiene estable y cada año disminuye capital e intereses.")

                elif tipo_hipoteca == "Mixta":
                    # Tramo fijo (cuota calculada con plazo total)
                    data_fijo = []
                    capital_pendiente = capital_hipoteca
                    r_fijo = interes_fijo / 12 if interes_fijo else 0.0
                    cuota_mensual_fijo = cuota_prestamo(capital_pendiente, interes_fijo, anos_plazo) or 0.0

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
                    st.dataframe(pd.DataFrame(data_fijo), width="stretch")
                    st.caption("Durante el tramo fijo, la cuota se calcula con el plazo total pactado; queda capital para el tramo variable.")

                    # Tramo variable (plazo restante)
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
                        st.dataframe(pd.DataFrame(data_var), width="stretch")
                        st.caption("En el tramo variable, la cuota se recalcula con el nuevo tipo y el plazo restante.")
                    else:
                        st.info("ℹ️ El capital quedó totalmente amortizado en el tramo fijo o no hay plazo restante.")
        # =========================
        # 🧮 Resumen compacto (dashboard rápido)
        # =========================
        st.divider()
        st.subheader("🧮 Resumen compacto")

        if sin_hipoteca:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("DTI", "No aplica")
            col2.metric("LTV", "0,00%")
            col3.metric("Cuota máx.", eur(cuota_max) if cuota_max > 0 else "No disponible")
            col4.metric("Cuota estimada", "0,00 €")
            st.info("ℹ️ Resumen: No se requiere hipoteca (compra al contado).")
        else:
            if tipo_hipoteca == "Mixta":
                interes_variable_total = (euribor + diferencial) if (euribor is not None and diferencial is not None) else None
                cuota_fijo_total = cuota_prestamo(capital_hipoteca, interes_fijo, anos_plazo) if (capital_hipoteca > 0 and interes_fijo) else 0.0
                cuota_var_total  = cuota_prestamo(capital_hipoteca, interes_variable_total, anos_plazo) if (capital_hipoteca > 0 and interes_variable_total) else 0.0

                dti_fijo = dti(cuota_fijo_total, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0
                dti_variable = dti(cuota_var_total, deudas_mensuales, sueldo_neto) if sueldo_neto > 0 else 0.0
                dti_peor = max(dti_fijo, dti_variable)
                cuota_peor = max(cuota_fijo_total, cuota_var_total)
                tramo_peor = "FIJO" if cuota_peor == cuota_fijo_total else "VARIABLE"

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("DTI (peor tramo)", semaforo_dti(dti_peor) if dti_peor > 0 else "No disponible")
                col2.metric("LTV", pct(ltv_val) if ltv_val > 0 else "No disponible")
                col3.metric("Cuota máx.", eur(cuota_max) if cuota_max > 0 else "No disponible")
                col4.metric("Cuota estimada (peor tramo)", eur(cuota_peor) if cuota_peor > 0 else "No disponible")

                st.caption(f"Evaluado en tramo: {tramo_peor}")
                st.caption("DTI = (Cuota hipoteca + otras deudas) / Ingresos netos")

                if cuota_peor > 0 and es_viable(cuota_peor, cuota_max, ltv_val, ltv_max, dti_peor):
                    st.success("✅ Resumen: Operación viable (LTV y DTI dentro de rango).")
                    if abs(dti_visible(dti_peor) - DTI_FAIL) < 1e-9:
                        st.info("ℹ️ Estás en el límite exacto del 35 %. Cualquier variación mínima podría hacerla no viable.")
                else:
                    if precio <= 0 or sueldo_neto <= 0 or entrada_usuario <= 0 or capital_hipoteca <= 0:
                        st.warning("⚠️ Resumen no evaluable: faltan parámetros mínimos.")
                    else:
                        st.error("❌ Resumen: Operación no viable (supera LTV o DTI).")

            else:
                cuota_dashboard = cuota_estimada or 0.0
                dti_dashboard = dti_val or 0.0

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("DTI", semaforo_dti(dti_dashboard) if dti_dashboard > 0 else "No disponible")
                col2.metric("LTV", pct(ltv_val) if ltv_val > 0 else "No disponible")
                col3.metric("Cuota máx.", eur(cuota_max) if cuota_max > 0 else "No disponible")
                col4.metric("Cuota estimada", eur(cuota_dashboard) if cuota_dashboard > 0 else "No disponible")

                st.caption("DTI = (Cuota hipoteca + otras deudas) / Ingresos netos")

                if cuota_dashboard > 0 and es_viable(cuota_dashboard, cuota_max, ltv_val, ltv_max, dti_dashboard):
                    st.success("✅ Resumen: Operación viable (LTV y DTI dentro de rango).")
                    if abs(dti_visible(dti_dashboard) - DTI_FAIL) < 1e-9:
                        st.info("ℹ️ Estás en el límite exacto del 35 %. Cualquier variación mínima podría hacerla no viable.")
                else:
                    if precio <= 0 or sueldo_neto <= 0 or entrada_usuario <= 0 or capital_hipoteca <= 0:
                        st.warning("⚠️ Resumen no evaluable: faltan parámetros mínimos.")
                    else:
                        st.error("❌ Resumen: Operación no viable (supera LTV o DTI).")



 


# ============================================================
# 🧪 Validador profesional dual (modos: rápida / intensa)
# ============================================================

MODO_VALIDACION = False           # ⬅️ Actívalo a "True" para ejecutar el validador; "False" para desactivarlo.
TIPO_VALIDACION = "intensa"       # opciones: "rápida" o "intensa"

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
        if dti_visible(d) <= THRESHOLDS["DTI_warn"]:
            return "🟢"
        elif dti_visible(d) <= THRESHOLDS["DTI_fail"]:
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

    def is_viable_joint(cuota, cuota_max, ltv_val, ltv_max, dti_val, entrada_ok):
        """Usa la misma lógica que la app: entrada suficiente + es_viable()."""
        return entrada_ok and es_viable(cuota, cuota_max, ltv_val, ltv_max, dti_val)

    def assert_coherencia(fallos, escenario_id, etiqueta, condicion):
        if not condicion:
            fallos.append((escenario_id, etiqueta))
    # --- Escenarios base ---
    OPERACIONES_BASE = [
        {"precio": 200000, "entrada": 40000, "ccaa": "Madrid",    "estado": "Segunda mano", "financiar": False},
        {"precio": 260000, "entrada": 30000, "ccaa": "Cataluña",  "estado": "Segunda mano", "financiar": True},
        {"precio": 180000, "entrada": 20000, "ccaa": "Andalucía", "estado": "Segunda mano", "financiar": False},
    ]

    # --- Combinaciones de prueba ---
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
    
    
    # ============================================================
    # 🔎 Validación rápida
    # ============================================================
    if TIPO_VALIDACION == "rápida":
        st.subheader("⚡ Validación rápida")

        fallos = []

        escenario_id = 0
        for op in OPERACIONES_BASE:
            for combo in COMBOS_FIJA:
                escenario_id += 1
                # --- Preparar parámetros ---
                r = calcular_capital_y_gastos(
                    op["precio"], op["entrada"], params,
                    ltv_max=ltv_max, financiar_comision=op["financiar"]
                )
                capital = r["capital_final"]
                ltv_val = r["ltv"]
                entrada_ok = op["entrada"] >= r["gastos_puros"]

                cuota = cuota_para(capital, combo["interes"], combo["plazo"])
                cuota_max = cuota_maxima(combo["sueldo"], combo["deudas"])
                dti_val = dti(cuota, combo["deudas"], combo["sueldo"])

                # --- Validación conjunta ---
                viable = is_viable_joint(cuota, cuota_max, ltv_val, ltv_max, dti_val, entrada_ok)

                # --- Comprobaciones de coherencia ---
                assert_coherencia(fallos, escenario_id, "Entrada insuficiente aceptada", not (not entrada_ok and viable))
                assert_coherencia(fallos, escenario_id, "DTI > 35% aceptado", not (dti_visible(dti_val) > THRESHOLDS["DTI_fail"] and viable))
                assert_coherencia(fallos, escenario_id, "LTV > límite aceptado", not (ltv_val > ltv_max and viable))

                # --- Mostrar resultados ---
                st.write(
                    f"Escenario {escenario_id}: Precio {eur(op['precio'])}, Entrada {eur(op['entrada'])}, "
                    f"Sueldo {eur(combo['sueldo'])}, Deudas {eur(combo['deudas'])}, "
                    f"Interés {pct(combo['interes'])}, Plazo {combo['plazo']} años → "
                    f"Cuota {eur(cuota)} | DTI {flag_dti(dti_val)} {pct_dti(dti_val)} | "
                    f"LTV {flag_ltv(ltv_val)} {pct(ltv_val)} → "
                    f"{'✅ Viable' if viable else '❌ No viable'}"
                )

        if not fallos:
            st.success("✅ Validación rápida completada sin incoherencias detectadas")
        else:
            st.error(f"❌ Se detectaron {len(fallos)} incoherencias en validación rápida")
            for f in fallos:
                st.write(f"Escenario {f[0]} → {f[1]}")
    
    
    # ============================================================
    # 🔍 Validación intensa (auditoría total)
    # ============================================================
    elif TIPO_VALIDACION == "intensa":
        st.subheader("🔍 Validación intensa (auditoría total)")

        fallos = []
        dti_hist, ltv_hist = [], []
        escenario_id = 0

        # --- Parámetros de sensibilidad y monotonicidad ---
        SENSIBILIDADES_INTERES = [-0.02, -0.01, +0.01, +0.02]   # ±100 pb, ±200 pb
        MONO_INTERESES = [0.02, 0.03, 0.04, 0.05]
        MONO_PLAZOS    = [15, 20, 25, 30]

        # --- Función auxiliar para precio máximo coherente (binaria) ---
        def precio_maximo_coherente(entrada, sueldo, deudas, interes, plazo, ltv_lim, financiar=False):
            low, high = 60000.0, 900000.0
            mejor = 0.0
            for _ in range(25):
                mid = (low + high) / 2
                pipe = calcular_capital_y_gastos(mid, entrada, params, ltv_max=ltv_lim, financiar_comision=financiar)
                capital = pipe["capital_final"]
                ltv_val = pipe["ltv"]
                entrada_ok = entrada >= pipe["gastos_puros"]
                cuota = cuota_para(capital, interes, plazo)
                cuota_max = cuota_maxima(sueldo, deudas)
                dti_val = dti(cuota, deudas, sueldo)
                viable = is_viable_joint(cuota, cuota_max, ltv_val, ltv_lim, dti_val, entrada_ok)
                if viable:
                    mejor = mid
                    low = mid
                else:
                    high = mid
            return mejor

        # --- Bucle principal de operaciones base ---
        for op in OPERACIONES_BASE:
            escenario_id += 1
            st.markdown(f"**OPERACIÓN {escenario_id}: {op['ccaa']} — {op['estado']} — precio {eur(op['precio'])}**")

            pipe = calcular_capital_y_gastos(op["precio"], op["entrada"], params, ltv_max=ltv_max, financiar_comision=op["financiar"])
            capital_final = pipe["capital_final"]
            ltv_val_base = pipe["ltv"]
            entrada_ok = op["entrada"] >= pipe["gastos_puros"]

            # === Hipoteca Fija ===
            st.markdown("### 🟦 Hipoteca fija")
            for c in COMBOS_FIJA:
                cuota = cuota_para(capital_final, c["interes"], c["plazo"])
                cuota_max = cuota_maxima(c["sueldo"], c["deudas"])
                dti_val = dti(cuota, c["deudas"], c["sueldo"])
                viable = is_viable_joint(cuota, cuota_max, ltv_val_base, ltv_max, dti_val, entrada_ok)

                dti_hist.append(dti_val); ltv_hist.append(ltv_val_base)
                st.write(f"Fija {pct(c['interes'])}, {c['plazo']}a → cuota {eur(cuota)} → "
                         f"DTI {flag_dti(dti_val)} {pct_dti(dti_val)} | LTV {flag_ltv(ltv_val_base)} {pct(ltv_val_base)} → "
                         f"{'✅ Viable' if viable else '❌ No viable'}")

                # Coherencias básicas
                assert_coherencia(fallos, escenario_id, "Entrada insuficiente aceptada (Fija)", not (not entrada_ok and viable))
                assert_coherencia(fallos, escenario_id, "DTI > 35% aceptado (Fija)", not (dti_visible(dti_val) > THRESHOLDS["DTI_fail"] and viable))
                assert_coherencia(fallos, escenario_id, "LTV > Límite aceptado (Fija)", not (ltv_val_base > ltv_max and viable))

            # === Hipoteca Variable ===
            st.markdown("### 🟧 Hipoteca variable")
            for c in COMBOS_VARIABLE:
                cuota = cuota_para(capital_final, c["interes"], c["plazo"])
                cuota_max = cuota_maxima(c["sueldo"], c["deudas"])
                dti_val = dti(cuota, c["deudas"], c["sueldo"])
                viable = is_viable_joint(cuota, cuota_max, ltv_val_base, ltv_max, dti_val, entrada_ok)

                dti_hist.append(dti_val); ltv_hist.append(ltv_val_base)
                st.write(f"Variable {pct(c['interes'])}, {c['plazo']}a → cuota {eur(cuota)} → "
                         f"DTI {flag_dti(dti_val)} {pct_dti(dti_val)} | LTV {flag_ltv(ltv_val_base)} {pct(ltv_val_base)} → "
                         f"{'✅ Viable' if viable else '❌ No viable'}")

                assert_coherencia(fallos, escenario_id, "Entrada insuficiente aceptada (Variable)", not (not entrada_ok and viable))
                assert_coherencia(fallos, escenario_id, "DTI > 35% aceptado (Variable)", not (dti_visible(dti_val) > THRESHOLDS["DTI_fail"] and viable))
                assert_coherencia(fallos, escenario_id, "LTV > Límite aceptado (Variable)", not (ltv_val_base > ltv_max and viable))

            # === Hipoteca Mixta (peor tramo) ===
            st.markdown("### 🟩 Hipoteca mixta (peor tramo)")
            for c in COMBOS_MIXTA:
                plazo_var = max(0, c["plazo_total"] - c["fijo_anios"])
                cuota_fijo = cuota_para(capital_final, c["i_fijo"], c["fijo_anios"])
                cuota_var  = cuota_para(capital_final, c["i_var"], plazo_var) if plazo_var > 0 else 0.0
                dti_fijo   = dti(cuota_fijo, c["deudas"], c["sueldo"])
                dti_var    = dti(cuota_var,  c["deudas"], c["sueldo"])
                dti_peor   = max(dti_fijo, dti_var)
                cuota_peor = max(cuota_fijo, cuota_var)
                tramo_peor = "FIJO" if dti_fijo >= dti_var else "VARIABLE"
                cuota_max  = cuota_maxima(c["sueldo"], c["deudas"])

                viable = is_viable_joint(cuota_peor, cuota_max, ltv_val_base, ltv_max, dti_peor, entrada_ok)

                dti_hist.append(dti_peor); ltv_hist.append(ltv_val_base)
                st.write(f"Mixta fijo {pct(c['i_fijo'])} {c['fijo_anios']}a / var {pct(c['i_var'])} {plazo_var}a → peor tramo {tramo_peor}: "
                         f"cuota {eur(cuota_peor)} → DTI {flag_dti(dti_peor)} {pct_dti(dti_peor)} | LTV {flag_ltv(ltv_val_base)} {pct(ltv_val_base)} → "
                         f"{'✅ Viable' if viable else '❌ No viable'}")

                assert_coherencia(fallos, escenario_id, "Entrada insuficiente aceptada (Mixta)", not (not entrada_ok and viable))
                assert_coherencia(fallos, escenario_id, "DTI > 35% aceptado (Mixta)", not (dti_visible(dti_peor) > THRESHOLDS["DTI_fail"] and viable))
                assert_coherencia(fallos, escenario_id, "LTV > Límite aceptado (Mixta)", not (ltv_val_base > ltv_max and viable))

            # === Sensibilidad de interés (sobre un caso representativo) ===
            st.markdown("### 🧪 Sensibilidad de interés (fija 25 años, sueldo 2800, deudas 200)")
            for delta in SENSIBILIDADES_INTERES:
                interes_base = 0.03 + delta
                cuota_sens   = cuota_para(capital_final, interes_base, 25)
                dti_sens     = dti(cuota_sens, 200, 2800)
                cuota_max    = cuota_maxima(2800, 200)
                viable_sens  = is_viable_joint(cuota_sens, cuota_max, ltv_val_base, ltv_max, dti_sens, entrada_ok)

                dti_hist.append(dti_sens); ltv_hist.append(ltv_val_base)
                st.caption(f"Sensibilidad interés {pct(interes_base)} (δ={pct(delta)}): cuota {eur(cuota_sens)} → "
                           f"DTI {flag_dti(dti_sens)} {pct_dti(dti_sens)} | LTV {flag_ltv(ltv_val_base)} {pct(ltv_val_base)} → "
                           f"{'✅ Viable' if viable_sens else '❌ No viable'}")

            # === Monotonicidad de interés: DTI debe crecer al subir el tipo ===
            st.markdown("### 📈 Monotonicidad: interés ↑ ⇒ DTI ↑")
            prev_dti = None
            for i in MONO_INTERESES:
                cuota_mono = cuota_para(capital_final, i, 25)
                dti_mono   = dti(cuota_mono, 200, 2800)
                st.caption(f"Interés {pct(i)} → DTI {pct(dti_mono)}")
                if prev_dti is not None and dti_mono < prev_dti - 1e-9:
                    fallos.append((escenario_id, "DTI no crece con interés creciente"))
                prev_dti = dti_mono
                dti_hist.append(dti_mono); ltv_hist.append(ltv_val_base)

            # === Monotonicidad de plazo: DTI debe bajar al aumentar plazo ===
            st.markdown("### ⏳ Monotonicidad: plazo ↑ ⇒ DTI ↓")
            prev_dti = None
            for p in MONO_PLAZOS:
                cuota_mono = cuota_para(capital_final, 0.03, p)
                dti_mono   = dti(cuota_mono, 200, 2800)
                st.caption(f"Plazo {p} años → DTI {pct(dti_mono)}")
                if prev_dti is not None and dti_mono > prev_dti + 1e-9:
                    fallos.append((escenario_id, "DTI no baja al aumentar plazo"))
                prev_dti = dti_mono
                dti_hist.append(dti_mono); ltv_hist.append(ltv_val_base)

            # === Precio máximo coherente (verificación) ===
            pm = precio_maximo_coherente(
                entrada=op["entrada"], sueldo=2800, deudas=200,
                interes=0.03, plazo=25, ltv_lim=ltv_max, financiar=op["financiar"]
            )
            if pm and pm > 0:
                st.caption(f"Precio máximo estimado coherente: {eur(pm)} (cumple Entrada/LTV/DTI con lógica app)")
            else:
                st.caption("Precio máximo estimado: no encontrado dentro del rango configurado")

        # === Escenarios aleatorios (stress test adicional) ===
        st.subheader("🎲 Stress test aleatorio (6 escenarios)")
        def rnd_ccaa():
            return random.choice(["Madrid", "Cataluña", "Andalucía", "Comunidad Valenciana", "Galicia"])
        def rnd_estado():
            return random.choice(["Nuevo", "Segunda mano"])

        for rnd_idx in range(1, 7):
            precio   = random.choice([130000, 180000, 220000, 300000, 380000])
            entrada  = random.choice([15000, 30000, 50000, 70000])
            ccaa     = rnd_ccaa()
            estado   = rnd_estado()
            financiar = random.choice([True, False])

            st.markdown(f"**Aleatorio {rnd_idx}: {ccaa} — {estado} — precio {eur(precio)} — entrada {eur(entrada)} — financiar comisión {financiar}**")

            # Fiscalidad dinámica para el aleatorio (reutiliza presets actuales)
            tmp_params = dict(params)  # copia superficial de params actuales

            pipe = calcular_capital_y_gastos(precio, entrada, tmp_params, ltv_max=ltv_max, financiar_comision=financiar)
            capital = pipe["capital_final"]
            ltv_rnd = pipe["ltv"]
            entrada_ok_rnd = entrada >= pipe["gastos_puros"]

            # Probamos combinaciones rápida fija/variable/mixta
            cuota_f = cuota_para(capital, 0.03, 25); dti_f = dti(cuota_f, 200, 2800); viable_f = is_viable_joint(cuota_f, cuota_maxima(2800, 200), ltv_rnd, ltv_max, dti_f, entrada_ok_rnd)
            cuota_v = cuota_para(capital, 0.04, 25); dti_v = dti(cuota_v, 150, 2800); viable_v = is_viable_joint(cuota_v, cuota_maxima(2800, 150), ltv_rnd, ltv_max, dti_v, entrada_ok_rnd)

            # Mixta peor tramo
            cuota_mf = cuota_para(capital, 0.02, 10)
            cuota_mv = cuota_para(capital, 0.04, 20)
            dti_mf = dti(cuota_mf, 250, 3200); dti_mv = dti(cuota_mv, 250, 3200)
            dti_m  = max(dti_mf, dti_mv); cuota_m_peor = max(cuota_mf, cuota_mv)
            viable_m = is_viable_joint(cuota_m_peor, cuota_maxima(3200, 250), ltv_rnd, ltv_max, dti_m, entrada_ok_rnd)

            dti_hist.extend([dti_f, dti_v, dti_m]); ltv_hist.extend([ltv_rnd, ltv_rnd, ltv_rnd])

            st.write(f"Fija → DTI {flag_dti(dti_f)} {pct_dti(dti_f)} | LTV {flag_ltv(ltv_rnd)} {pct(ltv_rnd)} → {'✅ Viable' if viable_f else '❌ No viable'}")
            st.write(f"Variable → DTI {flag_dti(dti_v)} {pct_dti(dti_v)} | LTV {flag_ltv(ltv_rnd)} {pct(ltv_rnd)} → {'✅ Viable' if viable_v else '❌ No viable'}")
            st.write(f"Mixta (peor) → DTI {flag_dti(dti_m)} {pct_dti(dti_m)} | LTV {flag_ltv(ltv_rnd)} {pct(ltv_rnd)} → {'✅ Viable' if viable_m else '❌ No viable'}")

            # Señalización de incoherencias evidentes
            assert_coherencia(fallos, rnd_idx, "Entrada insuficiente aceptada (Aleatorio)", not (not entrada_ok_rnd and (viable_f or viable_v or viable_m)))
            assert_coherencia(fallos, rnd_idx, "DTI > 35% aceptado (Aleatorio)", not ((dti_visible(dti_f) > THRESHOLDS["DTI_fail"] and viable_f) or
                                                                                       (dti_visible(dti_v) > THRESHOLDS["DTI_fail"] and viable_v) or
                                                                                       (dti_visible(dti_m) > THRESHOLDS["DTI_fail"] and viable_m)))
            assert_coherencia(fallos, rnd_idx, "LTV > Límite aceptado (Aleatorio)", not (ltv_rnd > ltv_max and (viable_f or viable_v or viable_m)))

        # --- Resumen ejecutivo único ---
        st.subheader("📈 Resumen validación intensa")
        if dti_hist:
            st.write(f"DTI medio: {pct(sum(dti_hist)/len(dti_hist))}")
            st.write(f"DTI máximo: {pct(max(dti_hist))}")
            st.write(f"DTI mínimo: {pct(min(dti_hist))}")
        if ltv_hist:
            st.write(f"LTV medio: {pct(sum(ltv_hist)/len(ltv_hist))}")
            st.write(f"LTV máximo: {pct(max(ltv_hist))}")
            st.write(f"LTV mínimo: {pct(min(ltv_hist))}")

        if fallos:
            st.error(f"❌ Se han detectado {len(fallos)} incoherencias de lógica. Revisa las condiciones indicadas.")
            for esc_id, label in fallos:
                st.error(f"   → Escenario {esc_id}: {label}")
        else:
            st.success("✅ Todo correcto: la calculadora cumple en todos los escenarios. No se han detectado incoherencias.")








# =========================
# Pie de transparencia
# =========================
st.divider()
st.caption("""
**Autor:** Letalicus  
**Fecha de actualización:** Noviembre 2025
""")

