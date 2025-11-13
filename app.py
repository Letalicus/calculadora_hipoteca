# ============================================================
# 🏠 Calculadora Hipotecaria Profesional
# Versión: 1.4.0
# Fecha: 2025-11-10
# Autor: Letalicus
#
# 🎉 Mejoras en esta versión:
# - 🆕 **Nuevas características**:
#   - Guía de usuario mejorada y más intuitiva
#   - Sección de ayuda expandible para cada modo de la calculadora
#   - Mejor organización de la información en secciones lógicas
# 
# - 🎨 **Mejoras en la interfaz de usuario**:
#   - Rediseño del sistema de navegación
#   - Iconografía actualizada y consistente
#   - Textos más claros y concisos
#   - Mejor estructura visual de la información
# 
# - 🐛 **Correcciones de errores**:
#   - Solucionado problema con la persistencia del estado entre actualizaciones
#   - Mejor manejo de valores por defecto
#   - Corregida la organización de los parámetros en las instrucciones
# 
# - 📱 **Optimizaciones móviles**:
#   - Mejora en la visualización en pantallas pequeñas
#   - Contenido más accesible y fácil de leer
#   - Navegación más intuitiva en dispositivos táctiles
# ============================================================





import datetime
import html
from math import isclose

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd

# --- INICIO: SEO / robots / sitemap dinámico ---
# URL pública de la app (tu dominio Streamlit)
SITE_URL = "https://calculadorahipotecapro.streamlit.app"

# Sustituye estos por los códigos que Google/Bing te den en Search Console / Bing Webmaster
GOOGLE_SITE_VERIFICATION = "dxyq3A1a8_xoOr2UUrIg5liMyVTHOZc-GeyoHkOdmKA"
BING_SITE_VERIFICATION = "A447AEA571A2277C69045692A1777B84"

# Detectar query params al inicio para servir robots / sitemap de forma dinámica
_query_params = st.query_params

# Servir robots.txt en: https://.../?robots=1
if "robots" in _query_params:
    robots_txt = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {SITE_URL}?sitemap=1\n"
        "\n"
        "# Nota: si prefieres, publica sitemap.xml en GitHub Pages y cambia la URL aquí."
    )
    # Se muestra plain text para que los bots puedan leerlo
    st.text(robots_txt)
    st.stop()

# Servir sitemap.xml en: https://.../?sitemap=1
if "sitemap" in _query_params:
    lastmod = datetime.date.today().isoformat()
    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{html.escape(SITE_URL)}</loc>
    <lastmod>{lastmod}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""
    # Mostramos el XML en texto plano
    st.text(sitemap_xml)
    st.stop()

# Meta tags + OpenGraph + JSON-LD (se inyectan en el body; Streamlit permite esto mediante unsafe_allow_html)
_meta_html = f"""
<!-- SEO basico -->
<meta name="description" content="Calculadora Hipotecaria Profesional — simula cuotas, LTV, DTI e impuestos rápidamente. Ideal para comparar escenarios de hipoteca en España.">
<meta name="keywords" content="calculadora hipoteca, simulador hipoteca, LTV, DTI, hipoteca España, calculadora hipoteca online">
<link rel="canonical" href="{SITE_URL}">
<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">
<meta name="msvalidate.01" content="{BING_SITE_VERIFICATION}">

<!-- Open Graph (Facebook / Social preview) -->
<meta property="og:title" content="Calculadora Hipotecaria Profesional">
<meta property="og:description" content="Simula cuotas, LTV y DTI. Compara hipotecas reales y planifica tu compra.">
<meta property="og:url" content="{SITE_URL}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Calculadora Hipoteca Pro">

<!-- JSON-LD básico (Organization + WebSite) -->
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Calculadora Hipotecaria Profesional",
  "url": "{SITE_URL}",
  "description": "Herramienta online para simular hipotecas y estimar viabilidad (LTV, DTI, gastos)."
}}
</script>
"""
# Inyectar los metadatos en la página (Streamlit los insertará en el body, eso es suficiente para verificación SEO)
st.markdown(_meta_html, unsafe_allow_html=True)
# --- FIN: SEO / robots / sitemap dinámico ---


# Estilos CSS personalizados para mejorar la legibilidad
st.markdown("""
<style>
    /* Mejora de contraste para títulos en modo oscuro */
    .stApp[data-theme="dark"] h1,
    .stApp[data-theme="dark"] h2,
    .stApp[data-theme="dark"] h3,
    .stApp[data-theme="dark"] h4,
    .stApp[data-theme="dark"] h5,
    .stApp[data-theme="dark"] h6 {
        color: #FFFFFF !important;
    }
    
    /* Mejora de contraste para texto en tooltips */
    .stTooltip {
        color: #000000 !important;
    }
    
    /* Mejora de contraste para etiquetas de gráficos */
    .stPlotlyChart .svg-container text {
        fill: currentColor !important;
    }
    
    /* Asegurar contraste en modo oscuro */
    [data-theme="dark"] .stPlotlyChart .svg-container text {
        fill: #FFFFFF !important;
        opacity: 0.9 !important;
    }
    
    /* Mejorar visibilidad de ejes y etiquetas */
    [data-theme="dark"] .xtick text, 
    [data-theme="dark"] .ytick text {
        fill: #E0E0E0 !important;
    }
    
    /* Asegurar que los contenedores de gráficos tengan el mismo tamaño */
    .stPlotlyChart {
        width: 100% !important;
        height: auto !important;
    }
    
    /* Asegurar que los indicadores de medidor (gauges) se muestren correctamente */
    .js-plotly-plot {
        display: flex !important;
        justify-content: center !important;
    }
    
    /* Asegurar que los contenedores de columnas tengan el mismo ancho */
    .st-emotion-cache-ocqkz7 {
        flex: 1 1 0% !important;
        width: 50% !important;
    }
    
    /* Mejorar visibilidad de leyendas */
    [data-theme="dark"] .legendtext {
        fill: #FFFFFF !important;
    }

    /* Fondo y borde de leyendas en modo oscuro */
    [data-theme="dark"] .stPlotlyChart .legend .bg,
    [data-theme="dark"] .stPlotlyChart .legendbg {
        fill: rgba(22, 26, 33, 0.92) !important;
        stroke: rgba(148, 163, 184, 0.35) !important;
    }

    /* Tooltips para modo oscuro */
    [data-theme="dark"] .stPlotlyChart .hovertext,
    [data-theme="dark"] .stPlotlyChart .hoverlayer text {
        fill: #0F172A !important;
    }
    
    /* Encabezado del tooltip (año) */
    [data-theme="dark"] .stPlotlyChart .hovertext > g:nth-child(1) > text {
        fill: #0F172A !important;
        font-weight: 700 !important;
        opacity: 1 !important;
    }

    [data-theme="dark"] .stPlotlyChart .hoverlayer path.bg,
    [data-theme="dark"] .stPlotlyChart .hoverlayer rect.bg {
        fill: rgba(22, 26, 33, 0.95) !important;
        stroke: rgba(148, 163, 184, 0.45) !important;
    }
    
    /* Estilos específicos para la leyenda del gráfico de donut */
    [data-theme="dark"] .stPlotlyChart .legend .bg,
    [data-theme="dark"] .stPlotlyChart .legend .legendbox,
    [data-theme="dark"] .stPlotlyChart .legend .legendfill {
        fill: rgba(15, 23, 42, 0.98) !important;
        stroke: rgba(100, 116, 139, 0.5) !important;
    }
    
    [data-theme="dark"] .stPlotlyChart .legend .legendtext {
        fill: #FFFFFF !important;
    }
    
    /* Forzar estilos para la leyenda del gráfico de donut */
    [data-theme="dark"] .stPlotlyChart .legend .scrollbox {
        background-color: rgba(15, 23, 42, 0.98) !important;
        border: 1px solid rgba(100, 116, 139, 0.5) !important;
    }
    
    [data-theme="dark"] .stPlotlyChart .legend .legendtoggle {
        cursor: default !important;
        pointer-events: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Código JavaScript para forzar estilos en tooltips
st.markdown("""
<script>
// Aplicar estilos a tooltips después de que se renderice el gráfico
setTimeout(function() {
    // Seleccionar todos los textos de tooltips
    const tooltipTexts = document.querySelectorAll('.hovertext text');
    
    // Aplicar estilos a cada elemento
    tooltipTexts.forEach(function(el) {
        el.style.fill = '#0F172A';
        el.style.fontWeight = '700';
        el.style.opacity = '1';
    });
    
    // Observar cambios en el DOM para aplicar estilos a nuevos tooltips
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1) {
                    const newTooltips = node.querySelectorAll('.hovertext text');
                    newTooltips.forEach(function(tooltip) {
                        tooltip.style.fill = '#0F172A';
                        tooltip.style.fontWeight = '700';
                        tooltip.style.opacity = '1';
                    });
                }
            });
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
}, 1000); // Esperar 1 segundo
</script>
""", unsafe_allow_html=True)

# Función auxiliar para manejar temas en los gráficos
def get_chart_theme():
    """
    Obtiene la configuración de tema actual de Streamlit y devuelve los colores correspondientes.
    """
    base = None
    background = None
    secondary = None

    # Intentar API moderna de Streamlit
    try:
        theme_obj = st.get_theme()  # type: ignore[attr-defined]
        base = getattr(theme_obj, "base", None) or (theme_obj.get("base") if isinstance(theme_obj, dict) else None)
        background = getattr(theme_obj, "backgroundColor", None) or (theme_obj.get("backgroundColor") if isinstance(theme_obj, dict) else None)
        secondary = getattr(theme_obj, "secondaryBackgroundColor", None) or (theme_obj.get("secondaryBackgroundColor") if isinstance(theme_obj, dict) else None)
    except AttributeError:
        # API alternativa para versiones anteriores
        base = st.get_option("theme.base") or base
        background = st.get_option("theme.backgroundColor") or background
        secondary = st.get_option("theme.secondaryBackgroundColor") or secondary
    except Exception:
        pass

    def parse_color_to_rgb(color: str | None):
        if not color:
            return None
        color = color.strip()
        if color.startswith("rgba") or color.startswith("rgb"):
            values = color[color.find("(") + 1:color.rfind(")")].split(",")
            try:
                r, g, b = [float(v.strip()) for v in values[:3]]
                return (r, g, b)
            except ValueError:
                return None
        if color.startswith("#"):
            hex_color = color.lstrip('#')
            if len(hex_color) == 3:
                hex_color = ''.join(c * 2 for c in hex_color)
            if len(hex_color) >= 6:
                try:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return (float(r), float(g), float(b))
                except ValueError:
                    return None
        return None

    def luminance(color: str | None) -> float | None:
        rgb = parse_color_to_rgb(color)
        if not rgb:
            return None
        r, g, b = rgb
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    # Inferir si es modo oscuro cuando base no está disponible o no refleja el toggle dinámico
    base_lum = luminance(background) if background else None
    secondary_lum = luminance(secondary) if secondary else None

    if base in {"dark", "light"}:
        is_dark = base == "dark"
    elif base_lum is not None:
        is_dark = base_lum < 0.45
    elif secondary_lum is not None:
        is_dark = secondary_lum < 0.45
    else:
        is_dark = False

    if is_dark:
        pio.templates.default = "plotly_dark"
        return {
            'dark': True,
            'text_color': '#E5E7EB',
            'title_color': '#FFFFFF',
            'subtitle_color': '#D1D5DB',
            'axis_label_color': '#E5E7EB',
            'tick_color': '#D1D5DB',
            'bg_color': background or '#0E1117',
            'secondary_bg': secondary or '#1E1E1E',
            'grid_color': 'rgba(255, 255, 255, 0.15)',
            'colors': [
                '#4C78A8',
                '#F58518',
                '#54A24B',
                '#E45756',
                '#B279A2',
                '#9D755D',
                '#EECA3B',
                '#BAB0AC',
                '#17BECF',
                '#FF9DA6'
            ]
        }
    else:
        pio.templates.default = "plotly_white"
        return {
            'dark': False,
            'text_color': '#1A1A1A',
            'title_color': '#000000',
            'subtitle_color': '#4B5563',
            'axis_label_color': '#2D3748',
            'tick_color': '#4A5568',
            'bg_color': background or '#FFFFFF',
            'secondary_bg': secondary or '#F0F2F6',
            'grid_color': 'rgba(0, 0, 0, 0.15)',
            'colors': [
                '#1F77B4',
                '#FF7F0E',
                '#2CA02C',
                '#D62728',
                '#9467BD',
                '#8C564B',
                '#E377C2',
                '#7F7F7F',
                '#BCBD22',
                '#17BECF'
            ]
        }



def color_with_alpha(color: str | None, alpha: float) -> str:
    """Convierte un color hex/rgb(a) en rgba con la opacidad indicada."""
    if not color:
        return f"rgba(0, 0, 0, {alpha})"

    color = color.strip()

    if color.startswith("rgba"):
        values = color[color.find("(") + 1:color.rfind(")")].split(",")
        r, g, b = [v.strip() for v in values[:3]]
        return f"rgba({r}, {g}, {b}, {alpha})"

    if color.startswith("rgb"):
        values = color[color.find("(") + 1:color.rfind(")")].split(",")
        r, g, b = [int(float(v.strip())) for v in values[:3]]
        return f"rgba({r}, {g}, {b}, {alpha})"

    if color.startswith("#"):
        hex_color = color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join(c * 2 for c in hex_color)
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return f"rgba({r}, {g}, {b}, {alpha})"
        except ValueError:
            pass

    # Fallback: devolver color original si no se pudo interpretar
    return color


# =========================
# Umbrales globales de DTI
# =========================
DTI_WARN = 0.30   # ≤ 30% → Seguro
DTI_FAIL = 0.35   # ≤ 35% → Moderado; > 35% → Arriesgado


# =========================
# Configuración inicial
# =========================
st.set_page_config(page_title="Calculadora Hipotecaria Profesional", page_icon="🏠", layout="wide")
st.title("🏡 Calculadora Hipotecaria Profesional")



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
    """Devuelve el DTI visible como proporción (0–1) alineada con pct_dti.
    Usa ceil para mostrar el valor más conservador al usuario."""
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



def get_theme_colors():
    """Obtiene los colores según el tema actual de Streamlit."""
    theme = get_chart_theme()
    if theme.get('dark'):
        return {
            'background': 'rgba(30, 41, 59, 0.5)',
            'text': '#F8FAFC',
            'grid': 'rgba(255, 255, 255, 0.1)',
            'border': 'rgba(100, 116, 139, 0.5)',
            'line_colors': ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
        }
    else:
        return {
            'background': 'rgba(255, 255, 255, 0.7)',
            'text': '#1E293B',
            'grid': 'rgba(0, 0, 0, 0.1)',
            'border': 'rgba(203, 213, 225, 0.8)',
            'line_colors': ['#2563EB', '#059669', '#D97706', '#DC2626', '#7C3AED', '#DB2777']
        }

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
    """Calcula DTI con precisión de 6 decimales internamente."""
    if sueldo_neto_mensual is None or sueldo_neto_mensual <= 0:
        return 0.0
    if cuota_hipoteca is None or cuota_hipoteca < 0:
        cuota_hipoteca = 0.0
    if deudas_mensuales is None or deudas_mensuales < 0:
        deudas_mensuales = 0.0
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

# Manejar cambio de opciones en el selector de modo
opciones_modo = [
    "📚 Guía Completa",
    "🔎 Descubrir mi precio máximo",
    "🏠 Comprobar una vivienda concreta"
]

# Si el modo guardado no está en las opciones actuales, lo reseteamos
if 'modo' in st.session_state and st.session_state.modo not in opciones_modo:
    st.session_state.modo = opciones_modo[0]

# === Claves controladas ===
KEYS_WIDGETS = list(DEFAULTS.keys())

# =========================
# ⚙️ Selección de modo
# =========================
st.sidebar.header("⚙️ Selección de modo")

modo = st.sidebar.radio(
    "Selecciona el modo",
    opciones_modo,
    key="modo",
    help="Elige si quieres leer la guía, calcular tu precio máximo o comprobar una vivienda concreta."
)


# =========================
# Renderizado según modo
# =========================
if modo == "📚 Guía Completa":
    # Pantalla inicial de bienvenida con instrucciones y glosario
    st.header("📚 Guía Completa")
    
    with st.expander("🌟 Introducción", expanded=True):
        st.markdown("""
        ### 📊 Analiza tu Capacidad de Compra
        
        Esta herramienta te permite analizar con precisión tu capacidad de compra y simular diferentes escenarios hipotecarios. Con un enfoque profesional y detallado, te ayuda a tomar decisiones informadas sobre tu futura vivienda.
        """)
    
    with st.expander("🔍 Modos de Uso", expanded=True):
        st.markdown("""
        ### 🔎 1. Descubrir mi precio máximo
        **¿Para qué sirve?**  
        Calcula el precio máximo de vivienda que puedes permitirte según tu capacidad económica actual.
        
        **Características principales:**
        - Calcula automáticamente el precio máximo basado en tus ingresos y ahorros
        - Valida los criterios bancarios (DTI ≤ 35% y LTV ≤ 80%)
        - Muestra un desglose detallado de la operación
        - Permite ajustar todos los parámetros de la hipoteca
        
        ### 🏠 2. Comprobar una vivienda concreta
        **¿Para qué sirve?**  
        Analiza la viabilidad de una vivienda específica con un precio determinado.
        
        **Características principales:**
        - Simulación detallada de pagos mensuales
        - Tabla de amortización completa
        - Análisis de diferentes escenarios de tipos de interés
        - Desglose de todos los gastos asociados
        - Cálculo de impuestos y tasas
        """)
    
    with st.expander("📊 Conceptos Clave", expanded=True):
        st.markdown("""
        ### 💰 Términos financieros importantes
        
        **DTI (Deuda sobre Ingresos)**  
        Porcentaje de tus ingresos mensuales que se destina al pago de deudas. 
        - **Límite recomendado:** 35%
        - **Cálculo:** (Cuota hipoteca + Otras deudas) / Ingresos netos mensuales
        
        **LTV (Préstamo sobre Valor de la vivienda)**  
        Porcentaje del valor de la vivienda que financia el banco.
        - **Habitual:** 80% (hasta 100% en casos excepcionales)
        - **Cálculo:** (Importe del préstamo / Valor de tasación) × 100
        
        **Tipo de Hipoteca**
        - **Fija:** Cuota constante durante toda la vida del préstamo
        - **Variable:** Cuota que varía según la evolución del índice de referencia (normalmente Euríbor)
        - **Mixta:** Combina un período inicial a tipo fijo con otro a tipo variable
        """)
    
    with st.expander("💡 Consejos Prácticos", expanded=True):
        st.markdown("""
        ### 📝 Recomendaciones para usar la calculadora
        
        1. **Ingresos realistas**
           - Incluye pagas extras en el cálculo de ingresos mensuales
           - Considera solo ingresos estables y recurrentes
        
        2. **Gastos adicionales**
           - Recuerda incluir: notaría, registro, gestoría, tasación, seguros
           - Considera gastos de reforma o acondicionamiento
        
        3. **Margen de seguridad**
           - Busca viviendas por debajo de tu límite máximo calculado
           - Prevé posibles subidas de tipos de interés
        
        4. **Compara ofertas**
           - Usa la calculadora para comparar diferentes condiciones hipotecarias
           - Prueba con distintos plazos y tipos de interés
        """)
    
    with st.expander("❓ Preguntas Frecuentes", expanded=False):
        st.markdown("""
        ### ❔ ¿Cómo se calcula el precio máximo?
        El precio máximo se calcula considerando:
        - Tu capacidad de pago mensual (DTI ≤ 35%)
        - El valor de la vivienda (LTV ≤ 80%)
        - Tus ahorros disponibles para la entrada
        
        ### ❔ ¿Qué incluyen los gastos de compra?
        - Impuestos (ITP o IVA + AJD)
        - Gastos de notaría y registro
        - Gestoría y tasación
        - Seguros iniciales
        
        ### ❔ ¿Cómo afecta el tipo de hipoteca a mis pagos?
        - **Fija:** Pagos estables, ideal si prefieres seguridad
        - **Variable:** Pagos pueden bajar o subir según el Euríbor
        - **Mixta:** Combina estabilidad inicial con flexibilidad posterior
        """)
    
    st.markdown("""
    ---
    *ℹ️ Recuerda que esta calculadora proporciona estimaciones. Para una valoración exacta, consulta con un asesor financiero.*
    """)

    with st.expander("📖 Glosario de términos"):
        st.markdown("""
        ▸ **Entrada** → dinero que aportas al inicio de la compra.  
        ▸ **Capital financiado** → cantidad que te presta el banco.  
        ▸ **LTV (Loan To Value)** → % del valor de la vivienda que financia el banco.  
        ▸ **DTI (Debt To Income)** → % de tus ingresos destinado a deudas.  
        ▸ **Hipoteca Fija** → tipo de interés constante durante toda la vida del préstamo.  
        ▸ **Hipoteca Variable** → tipo de interés que varía según las revisiones periódicas (Euríbor + diferencial).  
        ▸ **Hipoteca Mixta** → combina un período inicial con tipo fijo y luego variable.  
        ▸ **TIN (Tipo Interés Nominal)** → tipo de interés del préstamo sin incluir gastos ni comisiones.  
        ▸ **TAE (Tasa Anual Equivalente)** → tipo de interés efectivo anual incluyendo todos los gastos y comisiones.  
        ▸ **Euríbor** → índice de referencia para hipotecas variables en Europa.  
        ▸ **Diferencial** → margen fijo que se suma al Euríbor en hipotecas variables.  
        ▸ **Cuota mensual** → pago fijo que realizas cada mes (capital + intereses).  
        ▸ **Principal** → cantidad de capital que amortizas en cada cuota.  
        ▸ **Intereses** → coste financiero que pagas al banco por el dinero prestado.  
        ▸ **Tabla de amortización** → desglose de cada pago mostrando capital e intereses.  
        ▸ **Amortización anticipada** → devolución parcial o total del préstamo antes de tiempo.  
        ▸ **Comisión de apertura** → porcentaje que cobra el banco al formalizar la hipoteca.  
        ▸ **Comisión de amortización anticipada** → coste por devolver parte del préstamo antes de tiempo.  
        ▸ **Período de carencia** → tiempo en el que solo pagas intereses sin amortizar capital.  
        ▸ **Notaría** → coste de la escritura pública de compraventa e hipoteca.  
        ▸ **Registro de la Propiedad** → inscripción de la vivienda y la hipoteca en el registro público.  
        ▸ **Gestoría** → gestión administrativa de los trámites de la hipoteca.  
        ▸ **Tasación** → valoración oficial de la vivienda realizada por un tasador autorizado.  
        ▸ **Seguro de hogar** → seguro obligatorio que cubre daños en la vivienda.  
        ▸ **Seguro de vida** → seguro opcional que cubre el pago de la hipoteca en caso de fallecimiento.  
        ▸ **IVA** → impuesto sobre viviendas nuevas (habitualmente 10%).  
        ▸ **ITP (Impuesto de Transmisiones Patrimoniales)** → impuesto en viviendas de segunda mano.  
        ▸ **AJD (Actos Jurídicos Documentados)** → impuesto sobre escrituras notariales.  
        ▸ **Bonificación fiscal** → reducción en impuestos para ciertos colectivos (jóvenes, familias numerosas, etc.).  
        ▸ **Vivienda habitual** → residencia principal que da derecho a mejores condiciones fiscales.  
        ▸ **Segunda residencia** → vivienda no principal con condiciones fiscales menos favorables.  
        ▸ **Subrogación** → cambiar tu hipoteca de banco manteniendo las mismas condiciones.  
        ▸ **Novación** → modificar las condiciones de tu hipoteca con el mismo banco.  
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
    help="Coste de la escritura pública en notaría, según extensión y complejidad (aprox. 600–1.500 €)."
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

    ltv_real = (capital_final / precio) if (precio is not None and precio > 0) else 0.0
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
    with st.expander("ℹ️ Instrucciones de uso (haz clic para plegar/desplegar)", expanded=True):
        st.markdown("""
        ### Cómo funciona esta calculadora
        
        Esta herramienta te ayuda a determinar el **precio máximo de vivienda** que puedes permitirte basado en tu situación financiera y las condiciones hipotecarias.
        
        ### 📋 Parámetros necesarios
        
        **Datos personales:**
        - Ingresos netos mensuales (calcula la media mensual de tu sueldo neto anual, incluyendo pagas extras)
        - Deudas mensuales (tarjetas, préstamos, etc.)
        - Ahorros disponibles para la entrada
        
        **Condiciones de la hipoteca:**
        - Plazo del préstamo (años)
        - Tipo de hipoteca (Fija, Variable o Mixta)
        - Interés correspondiente según el tipo seleccionado
        
        ### 🔍 Criterios de viabilidad
        
        El cálculo valida automáticamente:
        - **DTI ≤ 35%** (Deuda sobre Ingresos) - Relación entre tu deuda total y tus ingresos netos mensuales
        - **LTV ≤ 80%** (Préstamo sobre Valor de la vivienda) - Algunas entidades pueden ofrecer hasta el 100% en casos excepcionales
        
        ### 💡 Recomendaciones
        
        - El precio mostrado es un **límite teórico máximo**
        - Se recomienda buscar viviendas **por debajo** de este valor para mayor tranquilidad
        - Considera gastos adicionales como reformas, muebles o imprevistos
        
        ⚠️ **Importante**: Las condiciones reales pueden variar según la entidad financiera y tu perfil de riesgo.
        """)

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
    with st.expander("ℹ️ Instrucciones de uso (haz clic para plegar/desplegar)", expanded=True):
        st.markdown("""
        ### Cómo funciona esta herramienta
        
        Analiza la viabilidad de una vivienda específica que ya tengas en mente, mostrándote todos los detalles financieros de la operación.
        
        ### 📋 Parámetros necesarios
        
        **Datos de la vivienda:**
        - Precio de la vivienda (€)
        
        **Tus datos personales:**
        - Ingresos netos mensuales
        - Entrada que puedes aportar
        - Otras deudas mensuales (tarjetas, préstamos, etc.)
        
        **Condiciones de la hipoteca:**
        - Plazo del préstamo (años)
        - Tipo de hipoteca (Fija, Variable o Mixta)
        - Interés correspondiente según el tipo seleccionado
        
        ### 📊 Información que obtendrás
        
        - **Análisis de viabilidad** (DTI, LTV)
        - Coste total de la operación
        - Tabla de amortización detallada
        - Escenarios de tipos de interés
        - Desglose de gastos e impuestos
        - Recomendaciones personalizadas
        
        ⚠️ **Nota importante:** Si introduces el precio exacto calculado en **🔎 Descubrir mi precio máximo**, podría aparecer como no viable por pequeños redondeos o porque el DTI supere mínimamente el 35%.
        """)

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
                if (1 + com_apertura_pct) <= 0:
                    capital_preliminar_aprox = 0.0
                else:
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
        # 📊 Dashboard de Viabilidad (Gauges)
        # =========================
        st.subheader("📊 Dashboard de Viabilidad")
        
        if not sin_hipoteca and cuota_estimada > 0:
            theme = get_chart_theme()
            
            # Definir colores basados en el tema
            if theme.get('dark'):
                bg_color = 'rgba(30, 41, 59, 0.5)'
                border_color = 'rgba(100, 116, 139, 0.5)'
                text_color = '#F8FAFC'
                grid_color = 'rgba(255, 255, 255, 0.1)'
            else:
                bg_color = 'rgba(255, 255, 255, 0.7)'
                border_color = 'rgba(203, 213, 225, 0.8)'
                text_color = '#1E293B'
                grid_color = 'rgba(0, 0, 0, 0.1)'
            
            # Crear columnas con el mismo ancho
            col1, col2 = st.columns(2, gap="medium")
            
            with col1:
                # Gráfico DTI
                fig_dti = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = dti_val * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {
                        'text': "Ratio de Endeudamiento (DTI)",
                        'font': {'size': 16, 'color': text_color}
                    },
                    gauge = {
                        'axis': {
                            'range': [None, 50],
                            'tickwidth': 1,
                            'tickcolor': text_color,
                            'tickfont': {'color': text_color, 'size': 10},
                            'tickformat': '.0f%',
                            'tick0': 0,
                            'dtick': 10
                        },
                        'bar': {'color': '#3B82F6'},
                        'bgcolor': bg_color,
                        'borderwidth': 1,
                        'bordercolor': border_color,
                        'steps': [
                            {'range': [0, 30], 'color': '#10B981'},  # Verde
                            {'range': [30, 35], 'color': '#F59E0B'}, # Amarillo
                            {'range': [35, 50], 'color': '#EF4444'}  # Rojo
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': dti_val * 100
                        }
                    },
                    number = {
                        'suffix': "%", 
                        'font': {'size': 28, 'color': text_color},
                        'valueformat': '.1f'
                    }
                ))
                
                # Configuración mínima necesaria
                fig_dti.update_layout(
                    margin=dict(l=20, r=20, t=60, b=20),
                    height=280,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=text_color, size=12)
                )
                
                # Configuración responsive para el gráfico DTI
                fig_dti.update_layout(
                    margin=dict(l=10, r=10, t=30, b=10),
                    autosize=True,
                    font=dict(size=12)
                )
                st.plotly_chart(
                    fig_dti, 
                    use_container_width=True, 
                    config={
                        'displayModeBar': True,
                        'responsive': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'select'],
                        'staticPlot': False
                    }
                )
                
                # Interpretación DTI
                with st.container(height=90):
                    if dti_val <= DTI_WARN:
                        st.markdown("<div style='background-color: #f0fdf4; color: #166534; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;'>✅ <strong>DTI Saludable</strong> - Endeudamiento seguro</div>", unsafe_allow_html=True)
                    elif dti_val <= DTI_FAIL:
                        st.markdown("<div style='background-color: #fffbeb; color: #854d0e; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;'>⚠️ <strong>DTI Moderado</strong> - Zona de atención</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='background-color: #fef2f2; color: #991b1b; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;'>❌ <strong>DTI Alto</strong> - Riesgo de rechazo</div>", unsafe_allow_html=True)
            
            with col2:
                # Gráfico LTV
                fig_ltv = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = ltv_val * 100,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {
                        'text': f"Ratio de Financiación (LTV) - Máx. {ltv_max*100:.0f}%",
                        'font': {'size': 16, 'color': text_color}
                    },
                    gauge = {
                        'axis': {
                            'range': [None, 100],
                            'tickwidth': 1,
                            'tickcolor': text_color,
                            'tickfont': {'color': text_color, 'size': 10},
                            'tickformat': '.0f%',
                            'tick0': 0,
                            'dtick': 20
                        },
                        'bar': {'color': '#8B5CF6'},
                        'bgcolor': bg_color,
                        'borderwidth': 1,
                        'bordercolor': border_color,
                        'steps': [
                            {'range': [0, 60], 'color': '#10B981'},  # Verde
                            {'range': [60, 80], 'color': '#F59E0B'}, # Amarillo
                            {'range': [80, 100], 'color': '#EF4444'}  # Rojo
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': ltv_val * 100
                        }
                    },
                    number = {
                        'suffix': "%", 
                        'font': {'size': 28, 'color': text_color},
                        'valueformat': '.1f'
                    }
                ))
                
                # Configuración mínima necesaria
                fig_ltv.update_layout(
                    margin=dict(l=20, r=20, t=60, b=20),
                    height=280,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=text_color, size=12)
                )
                
                # Configuración responsive para el gráfico LTV
                fig_ltv.update_layout(
                    margin=dict(l=10, r=10, t=30, b=10),
                    autosize=True,
                    font=dict(size=12)
                )
                st.plotly_chart(
                    fig_ltv, 
                    use_container_width=True, 
                    config={
                        'displayModeBar': True,
                        'responsive': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'select'],
                        'staticPlot': False
                    }
                )
                
                # Interpretación LTV
                with st.container(height=90):
                    if ltv_val <= 0.60:
                        st.markdown("<div style='background-color: #f0fdf4; color: #166534; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;'>✅ <strong>LTV Excelente</strong> - Buena posición de negociación</div>", unsafe_allow_html=True)
                    elif ltv_val <= ltv_max:
                        st.markdown("<div style='background-color: #eff6ff; color: #1e40af; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;'>ℹ️ <strong>LTV Estándar</strong> - Dentro de límites bancarios</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='background-color: #fef2f2; color: #991b1b; padding: 0.5rem; border-radius: 0.5rem; margin: 0.25rem 0;'>❌ <strong>LTV Alto</strong> - Requiere más entrada</div>", unsafe_allow_html=True)
            
            # Resumen de viabilidad
            st.markdown("---")
            
            # Determinar el estado general de viabilidad
            if dti_val <= DTI_WARN and ltv_val <= ltv_max:
                viability_status = "🟢 ÓPTIMA"
                viability_help = "Ambos indicadores están en zona verde. La operación es financieramente saludable."
            elif dti_val <= DTI_FAIL and ltv_val <= ltv_max:
                viability_status = "🟡 ACEPTABLE"
                viability_help = "Algún indicador está en zona amarilla. Revisa los detalles y considera ajustar los parámetros."
            else:
                viability_status = "🔴 RIESGO"
                viability_help = "Uno o ambos indicadores están en zona roja. Se recomienda revisar a fondo la operación."
            
            # Mostrar métricas en un layout de 3 columnas
            col_a, col_b, col_c = st.columns([1, 1, 1])
            
            with col_a:
                st.metric("📊 Estado", viability_status, help=viability_help)
            
            with col_b:
                st.metric("🏠 Cuota/Máx", f"{eur(cuota_estimada)} / {eur(cuota_max)}")
            
            with col_c:
                margen_viability = (cuota_max - cuota_estimada) if cuota_max > 0 else 0
                st.metric("💰 Margen seguridad", f"{eur(margen_viability)}")
            
            st.caption("💡 **Consejo:** Los indicadores verdes indican una posición cómoda, los amarillos requieren atención y los rojos indican la necesidad de ajustar parámetros.")
        
        elif sin_hipoteca:
            st.info("ℹ️ No se requieren indicadores de viabilidad para una compra al contado.")
        else:
            st.warning("⚠️ No se pueden generar los indicadores: faltan datos de la operación.")

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

        # =========================
        # 📊 Dashboard Visual de Costes (Gráfico de Donut)
        # =========================
        st.subheader("📊 Dashboard Visual de Costes")
        
        if precio > 0:
            # Preparar datos para el gráfico
            datos_costes = []
            etiquetas_costes = []
            
            # Precio de la vivienda
            if precio > 0:
                datos_costes.append(precio)
                etiquetas_costes.append(f"🏠 Precio vivienda<br>{eur(precio)}")
            
            # Impuestos
            if impuestos_total > 0:
                datos_costes.append(impuestos_total)
                etiquetas_costes.append(f"🧾 Impuestos<br>{eur(impuestos_total)}")
            
            # Gastos de formalización
            if gastos_formalizacion_total > 0:
                datos_costes.append(gastos_formalizacion_total)
                etiquetas_costes.append(f"📋 Gastos formalización<br>{eur(gastos_formalizacion_total)}")
            
            # Comisión de apertura (si no está financiada)
            if com_apertura_val > 0 and com_incluida_en_gastos:
                datos_costes.append(com_apertura_val)
                etiquetas_costes.append(f"🏦 Comisión apertura<br>{eur(com_apertura_val)}")
            
            # Intereses totales
            if intereses_totales > 0:
                datos_costes.append(intereses_totales)
                etiquetas_costes.append(f"💸 Intereses totales<br>{eur(intereses_totales)}")
            
            theme = get_chart_theme()
            subtitle_color = theme.get('subtitle_color', theme['text_color'])
            
            # Configuración de colores para tooltips y leyenda
            if theme.get('dark'):
                # Configuración de colores para tooltips y leyenda
                hover_bg = 'rgba(15, 23, 42, 0.98)'  # Fondo oscuro
                hover_border = 'rgba(100, 116, 139, 0.5)'
                hover_text_color = '#FFFFFF'  # Texto blanco
                legend_bg = 'rgba(15, 23, 42, 0.98)'  # Fondo oscuro
                legend_text_color = '#FFFFFF'  # Texto blanco
                plotly_template = 'plotly_dark'  # Usar tema oscuro de Plotly
                
                # Ajustes específicos para móviles
                text_size = 12  # Tamaño de fuente más pequeño para móviles
            else:
                # Para modo claro
                hover_bg = color_with_alpha(theme.get('secondary_bg', '#FFFFFF'), 0.98)
                hover_border = color_with_alpha(theme.get('axis_label_color', theme['text_color']), 0.3)
                hover_text_color = theme.get('text_color', '#1A1A1A')
                legend_bg = 'rgba(255, 255, 255, 0.95)'
                legend_text_color = theme.get('text_color', '#1A1A1A')
                plotly_template = 'plotly_white'
                
                # Ajustes específicos para móviles
                text_size = 12  # Tamaño de fuente más pequeño para móviles
                
            donut_colors = [theme['colors'][i % len(theme['colors'])] for i in range(len(datos_costes))]
            # Crear gráfico donut con mejor visibilidad
            fig_costes = go.Figure(data=[go.Pie(
                labels=etiquetas_costes,
                values=datos_costes,
                hole=0.4,
                marker=dict(colors=donut_colors),
                textinfo='percent+label',  # Mostrar porcentaje y etiqueta
                textposition='outside',
                texttemplate='<b>%{percent:.1%}</b>',  # Porcentaje en negrita
                insidetextorientation='radial',
                textfont=dict(
                    color=theme['text_color'],
                    size=text_size,  # Usar tamaño de fuente responsive
                    family='Arial, sans-serif'
                ),
                hovertemplate=(
                    f'<b style="color:{hover_text_color}">%{{label}}</b><br>'
                    f'<span style="color:{hover_text_color}">Importe: %{{value:,.2f}} €</span><br>'
                    f'<span style="color:{hover_text_color}">Porcentaje: %{{percent:.1%}}</span><extra></extra>'
                ),
                pull=[0.02] * len(datos_costes),  # Separación uniforme para todas las secciones
                outsidetextfont=dict(
                    color=theme['text_color'],
                    size=text_size,  # Usar tamaño de fuente responsive
                    family='Arial, sans-serif'
                ),
                direction='clockwise',
                sort=False
            )])
            
            fig_costes.update_layout(
                title={
                    'text': "<b>Distribución del Coste Total</b>",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {
                        'color': theme.get('title_color', theme['text_color']),
                        'family': 'Arial, sans-serif',
                        'size': 18
                    },
                    'y': 0.99
                },
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=10, r=10, t=60, b=20),  # Márgenes optimizados para móviles
                uniformtext_minsize=12,  # Tamaño mínimo de texto más grande
                uniformtext_mode='hide',  # Ocultar textos que no quepan
                font=dict(size=14, color=theme['text_color']),
                # Configuración de la leyenda (fuera de la pantalla)
                legend=dict(
                    orientation="v",
                    yanchor="top",
                    y=1.5,  # Mover la leyenda fuera de la pantalla
                    xanchor="left",
                    x=1.05,
                    bgcolor='rgba(0,0,0,0)',
                    bordercolor='rgba(0,0,0,0)',
                    borderwidth=0,
                    font=dict(
                        color='rgba(0,0,0,0)',
                        family='Arial, sans-serif',
                        size=1  # Tamaño mínimo permitido
                    ),
                    itemclick=False,
                    itemdoubleclick=False,
                    traceorder='normal',
                    itemsizing='constant'
                ),
                annotations=[
                    dict(
                        x=0.5,
                        y=1.0,
                        xref='paper',
                        yref='paper',
                        text=eur(coste_total),
                        showarrow=False,
                        font=dict(
                            size=14,
                            color='#F0F0F0' if theme['dark'] else theme.get('subtitle_color', theme['text_color']),
                            family='Arial, sans-serif, Segoe UI'
                        ),
                        xanchor='center',
                        yanchor='bottom',
                        yshift=4,
                        opacity=0.95
                    )
                ],
                hoverlabel=dict(
                    bgcolor='rgba(15, 23, 42, 0.95)' if theme['dark'] else hover_bg,
                    bordercolor='rgba(100, 116, 139, 0.5)',
                    font=dict(
                        color='#FFFFFF' if theme['dark'] else hover_text_color, 
                        size=12, 
                        family="sans-serif"
                    ),
                    align="left"
                ),
                height=600,
                showlegend=False  # Desactivar la leyenda nativa
            )  # Cierre de update_layout
            
            # Configuración para el gráfico responsive
            fig_costes.update_layout(
                autosize=True,
                margin=dict(
                    l=20,  # Reducir margen izquierdo
                    r=20,  # Reducir margen derecho
                    t=60,  # Reducir margen superior
                    b=20,  # Reducir margen inferior
                    pad=5  # Padding pequeño
                ),
                height=400,  # Altura fija más pequeña para móviles
                font=dict(size=12)  # Tamaño de fuente base para mejor legibilidad
            )
            
            # Configuración para el contenedor del gráfico
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Mostrar el gráfico con configuración responsive
                st.plotly_chart(
                    fig_costes,
                    use_container_width=True,  # Usar el ancho del contenedor
                    config={
                        'displayModeBar': True,
                        'staticPlot': False,
                        'displaylogo': False,
                        'responsive': True,  # Hacer el gráfico responsive
                        'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'select'],
                    }
                )
            
            # Estilos CSS globales para todos los gráficos
            st.markdown("""
            <style>
                /* Estilos para móviles */
                @media (max-width: 768px) {
                    .stPlotlyChart {
                        width: 100% !important;
                        max-width: 100% !important;
                    }
                    .js-plotly-plot .plotly .main-svg text {
                        font-size: 12px !important;
                    }
                    .plotly .legend {
                        font-size: 10px !important;
                    }
                }
                
                /* Ajustes para tablets */
                @media (min-width: 769px) and (max-width: 1024px) {
                    .stPlotlyChart {
                        width: 100% !important;
                    }
                    .js-plotly-plot .plotly .main-svg text {
                        font-size: 11px !important;
                    }
                }
                
                /* Ajustes generales para todos los gráficos */
                .stPlotlyChart {
                    transition: all 0.3s ease;
                }
                
                /* Mejorar la legibilidad en modo oscuro */
                [data-testid="stAppViewContainer"] .js-plotly-plot .plotly .main-svg {
                    background: transparent !important;
                }
                
                /* Ajustar el tamaño de los tooltips */
                .svg-container {
                    margin: 0 auto;
                }
            </style>
            """, unsafe_allow_html=True)
            
            with col2:
                # Inyectar JavaScript para detectar el tema
                st.markdown("""
                <script>
                // Función para detectar el tema actual
                function getCurrentTheme() {
                    // Verificar si está en modo oscuro
                    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                        return 'dark';
                    }
                    return 'light';
                }
                
                // Aplicar tema al cargar
                document.addEventListener('DOMContentLoaded', function() {
                    updateThemeStyles();
                    
                    // Escuchar cambios de tema
                    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', updateThemeStyles);
                });
                
                // Actualizar estilos basado en el tema
                function updateThemeStyles() {
                    const theme = getCurrentTheme();
                    const root = document.documentElement;
                    
                    if (theme === 'dark') {
                        root.style.setProperty('--legend-bg', 'rgba(30, 41, 59, 0.95)');
                        root.style.setProperty('--legend-border', 'rgba(51, 65, 85, 0.5)');
                        root.style.setProperty('--legend-text', '#F8FAFC');
                        root.style.setProperty('--legend-value', '#CBD5E1');
                        root.style.setProperty('--legend-divider', 'rgba(51, 65, 85, 0.5)');
                    } else {
                        root.style.setProperty('--legend-bg', 'rgba(255, 255, 255, 0.95)');
                        root.style.setProperty('--legend-border', 'rgba(203, 213, 225, 0.8)');
                        root.style.setProperty('--legend-text', '#1E293B');
                        root.style.setProperty('--legend-value', '#475569');
                        root.style.setProperty('--legend-divider', 'rgba(203, 213, 225, 0.8)');
                    }
                }
                </script>
                
                <style>
                /* Variables CSS para los temas */
                :root {
                    --legend-bg: rgba(255, 255, 255, 0.95);
                    --legend-border: rgba(0, 0, 0, 0.1);
                    --legend-text: #1E293B;
                    --legend-value: #475569;
                    --legend-divider: #E2E8F0;
                    --legend-hover-bg: rgba(0, 0, 0, 0.03);
                }
                
                /* Ocultar solo la leyenda nativa del gráfico de donut */
                div[data-testid="stPlotlyChart"]:has(> div > div > svg > g.infolayer > g.legend) .legend,
                div[data-testid="stPlotlyChart"]:has(> div > div > svg > g.infolayer > g.legend) .legends,
                div[data-testid="stPlotlyChart"]:has(> div > div > svg > g.infolayer > g.legend) .legendgroup,
                div[data-testid="stPlotlyChart"]:has(> div > div > svg > g.infolayer > g.legend) .legendtext,
                div[data-testid="stPlotlyChart"]:has(> div > div > svg > g.infolayer > g.legend) .legendtoggle,
                div[data-testid="stPlotlyChart"]:has(> div > div > svg > g.infolayer > g.legend) .legendtitle,
                div[data-testid="stPlotlyChart"]:has(> div > div > svg > g.infolayer > g.legend) .legendpoints {
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                    width: 0 !important;
                    height: 0 !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    border: none !important;
                }}
                
                .legend-item:hover {
                    background-color: var(--legend-hover-bg);
                    border: 1px solid var(--legend-border);
                    border-radius: 8px;
                /* Estilos para los elementos de la leyenda */
                .legend-item {
                    display: flex;
                    align-items: center;
                    margin-bottom: 8px;
                    padding: 4px 8px;
                    border-radius: 4px;
                    transition: all 0.3s ease;
                    line-height: 1.4;
                    color: var(--legend-text);
                }
                
                .legend-color {
                    width: 16px;
                    height: 16px;
                    min-width: 16px;
                    min-height: 16px;
                    border-radius: 4px;
                    margin-right: 10px;
                    display: inline-block;
                    vertical-align: middle;
                    flex-shrink: 0;
                    border: 1px solid var(--legend-border);
                    box-sizing: border-box;
                }
                
                .legend-label {
                    color: var(--legend-text);
                    font-weight: 500;
                }
                
                .legend-value {
                    color: var(--legend-value);
                    margin-left: 4px;
                    font-weight: 500;
                    font-size: 0.9em;
                    opacity: 0.9;
                }
                
                /* Efecto hover sutil */
                .legend-item:hover {
                    background-color: var(--legend-hover-bg);
                }
                        width: 16px;
                        height: 16px;
                        border-radius: 4px;
                        margin-right: 10px;
                        flex-shrink: 0;
                        border: 1px solid {hover_border};
                    }}
                    
                    .legend-value {{
                        margin-left: 4px;
                        font-weight: 500;
                        color: var(--legend-value);
                        opacity: 0.9;
                        font-size: 0.9em;
                        transition: color 0.3s ease;
                    }}
                    
                    /* Los estilos específicos ahora se manejan con JavaScript y variables CSS */
                    
                    /* Asegurar que los colores se actualicen suavemente */
                    @media (prefers-color-scheme: dark) {
                        /* Valores iniciales para modo oscuro */
                        :root {
                            --legend-bg: rgba(30, 41, 59, 0.95);
                            --legend-border: rgba(51, 65, 85, 0.5);
                            --legend-text: #F8FAFC;
                            --legend-value: #CBD5E1;
                            --legend-divider: rgba(51, 65, 85, 0.5);
                        }
                    }
                    
                    @media (prefers-color-scheme: light) {
                        /* Valores iniciales para modo claro */
                        :root {
                            --legend-bg: rgba(255, 255, 255, 0.95);
                            --legend-border: rgba(203, 213, 225, 0.8);
                            --legend-text: #1E293B;
                            --legend-value: #475569;
                            --legend-divider: rgba(203, 213, 225, 0.8);
                        }
                    }}
                </style>
                """, unsafe_allow_html=True)
                
                # Iniciar el contenedor de la leyenda sin título
                st.markdown("""
                <div class="custom-legend" id="custom-legend-container">
                """, unsafe_allow_html=True)
                
                # Añadir ítems a la leyenda con valores y colores del donut
                for i, (label, color, value) in enumerate(zip(etiquetas_costes, donut_colors, datos_costes)):
                    # Extraer solo el texto sin el HTML para la leyenda
                    label_text = label.split('<br>')[0]
                    # Formatear el valor con separadores de miles y 2 decimales
                    formatted_value = f"{value:,.2f} €"
                    
                    # Usar el sistema de temas existente y añadir solo el cuadrado de color
                    st.markdown(f"""
                    <div class="legend-item">
                        <div style="width: 16px; height: 16px; background-color: {color}; 
                                 border: 1px solid var(--legend-border); border-radius: 4px; 
                                 margin-right: 10px; display: inline-block; vertical-align: middle;"></div>
                        <span class="legend-label">{label_text} <span class="legend-value">({formatted_value})</span></span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Calcular el total sumando los valores de datos_costes
                total = sum(datos_costes)
                formatted_total = f"{total:,.2f} €"
                st.markdown(f"""
                <div style="margin-top: 12px; padding-top: 10px; border-top: 1px solid {hover_border};">
                    <div class="legend-item" style="font-weight: 600;">
                        <div style="width: 16px; margin-right: 10px;"></div>
                        <span>Total: <span class="legend-value">{formatted_total}</span></span>
                    </div>
                </div>
                </div>
                """, unsafe_allow_html=True)
            st.caption("📊 Este gráfico muestra la distribución visual de todos los costes de la operación. "
                      "El tamaño de cada porción representa el peso porcentual de cada concepto en el coste total.")
        else:
            st.warning("⚠️ No se puede generar el gráfico de costes porque falta el precio de la vivienda.")

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
        
        # Estilos CSS compatibles con tema claro y oscuro
        st.markdown("""
        <style>
            /* Estilos base que funcionan en ambos temas */
            .consejo-container {
                border-left: 4px solid;
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 0 8px 8px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
            
            /* Estilos específicos para tema claro */
            @media (prefers-color-scheme: light) {
                .consejo-container {
                    background-color: #f8f9fa;
                    border-left-color: #4CAF50;
                    color: #333;
                }
                .opcion-consejo {
                    background-color: #f0f7ff;
                    border-left: 4px solid #2196F3;
                    color: #1a1a1a;
                }
                .advertencia {
                    background-color: #fff3e0 !important;
                    border-left-color: #ff9800 !important;
                }
                .financiacion {
                    background-color: #e8f5e9 !important;
                    border-left-color: #4caf50 !important;
                }
            }
            
            /* Estilos específicos para tema oscuro */
            @media (prefers-color-scheme: dark) {
                .consejo-container {
                    background-color: #1e1e1e;
                    border-left-color: #4CAF50;
                    color: #f0f0f0;
                }
                .opcion-consejo {
                    background-color: #2a3b4d;
                    border-left: 4px solid #4d8ff9;
                    color: #f0f0f0;
                }
                .advertencia {
                    background-color: #3e2c16 !important;
                    border-left-color: #ff9800 !important;
                }
                .financiacion {
                    background-color: #1a3a1a !important;
                    border-left-color: #4caf50 !important;
                }
            }
            
            /* Estilos comunes para opciones de consejo */
            .opcion-consejo {
                margin: 0.5rem 0;
                padding: 0.75rem;
                border-radius: 6px;
                transition: all 0.3s ease;
            }
            
            .opcion-consejo:hover {
                transform: translateX(5px);
                opacity: 0.9;
            }
            
            /* Asegurar que el texto sea legible en ambos temas */
            .opcion-consejo p, 
            .consejo-container p, 
            .consejo-container h3,
            .opcion-consejo h3 {
                color: inherit !important;
            }
        </style>
        """, unsafe_allow_html=True)
        
        def mostrar_consejo(tipo, mensaje, es_html=False):
            if tipo == 'advertencia':
                st.markdown(f'<div class="consejo-container advertencia">{mensaje if not es_html else mensaje}</div>', unsafe_allow_html=True)
            elif tipo == 'financiacion':
                st.markdown(f'<div class="consejo-container financiacion">{mensaje if not es_html else mensaje}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="consejo-container">{mensaje if not es_html else mensaje}</div>', unsafe_allow_html=True)
        
        if sin_hipoteca:
            st.info("ℹ️ No se generan consejos: no se requiere hipoteca.")
        else:
            if tipo_hipoteca == "Mixta":
                interes_variable_total = euribor + diferencial
                cuota_fijo_total = cuota_prestamo(capital_hipoteca, interes_fijo, anos_plazo) or 0.0
                cuota_var_total  = cuota_prestamo(capital_hipoteca, interes_variable_total, anos_plazo) or 0.0

                dti_fijo = dti(cuota_fijo_total, deudas_mensuales, sueldo_neto)
                dti_variable = dti(cuota_var_total, deudas_mensuales, sueldo_neto)
                dti_peor = max(dti_fijo, dti_variable)
                cuota_peor = max(cuota_fijo_total, cuota_var_total)

                dti_peor_visible = dti_visible(dti_peor)
                
                if not es_viable(cuota_peor, cuota_max, ltv_val, ltv_max, dti_peor):
                    if dti_peor_visible and dti_peor_visible > DTI_FAIL:
                        with st.container():
                            st.markdown("### 🔍 Opciones de financiación y asesoramiento")
                            st.markdown('<div class="opcion-consejo">👉 Aumenta la entrada inicial para reducir el importe a financiar.</div>', unsafe_allow_html=True)
                            st.markdown('<div class="opcion-consejo">👉 Negocia un tipo de interés más bajo con el banco.</div>', unsafe_allow_html=True)
                            st.markdown('<div class="opcion-consejo">👉 Considera ampliar el plazo del préstamo para reducir la cuota mensual.</div>', unsafe_allow_html=True)
                    
                    elif dti_peor_visible and DTI_WARN < dti_peor_visible <= DTI_FAIL:
                        with st.container():
                            st.markdown("### ⚠️ Capacidad de endeudamiento en el límite")
                            st.markdown("Tu capacidad de endeudamiento está cerca del límite. Te recomendamos:")
                            st.markdown('<div class="opcion-consejo">• Aportar más dinero para la entrada inicial</div>', unsafe_allow_html=True)
                            st.markdown('<div class="opcion-consejo">• Reducir el precio objetivo de la vivienda</div>', unsafe_allow_html=True)
                            st.markdown('<div class="opcion-consejo">• Incorporar un avalista que mejore la evaluación bancaria</div>', unsafe_allow_html=True)
                    
                    if ltv_val > ltv_max:
                        with st.container():
                            if ltv_val > 0.8:  # Si supera el 80% de financiación
                                st.markdown("### 📊 Límite de financiación elevado")
                                st.markdown(f"El banco suele financiar hasta el 80% del valor de la vivienda (solicitado: {ltv_val*100:.1f}%).")
                                st.markdown("**Opciones para mejorar la viabilidad:**")
                                st.markdown(f'<div class="opcion-consejo">• Aportar un {((ltv_val - ltv_max)*100):.1f}% adicional de entrada</div>', unsafe_allow_html=True)
                                st.markdown('<div class="opcion-consejo">• Consultar con otros bancos por condiciones especiales</div>', unsafe_allow_html=True)
                                st.markdown('<div class="opcion-consejo">• Valorar un avalista o garantías adicionales</div>', unsafe_allow_html=True)
                                st.markdown('<div class="opcion-consejo">• Buscar una propiedad con un precio más ajustado</div>', unsafe_allow_html=True)
                            else:
                                st.markdown("### 📊 Financiación dentro de los límites")
                                st.markdown(f"El banco financia hasta el {ltv_max*100:.0f}% del valor de la vivienda (solicitado: {ltv_val*100:.1f}%).")
                else:
                    st.success("✅ Tu operación es viable con los parámetros actuales (considerando ambos tramos).")

            else:  # Fija/Variable
                dti_dashboard = dti_val
                dti_dashboard_visible = dti_visible(dti_dashboard)
                
                if not es_viable(cuota_estimada, cuota_max, ltv_val, ltv_max, dti_dashboard):
                    if dti_dashboard_visible and dti_dashboard_visible > DTI_FAIL:
                        with st.container():
                            st.markdown("### 🔍 Opciones de financiación y asesoramiento")
                            st.markdown('<div class="opcion-consejo">👉 Aumenta la entrada inicial para reducir el importe a financiar.</div>', unsafe_allow_html=True)
                            st.markdown('<div class="opcion-consejo">👉 Negocia un tipo de interés más bajo con el banco.</div>', unsafe_allow_html=True)
                            st.markdown('<div class="opcion-consejo">👉 Considera ampliar el plazo del préstamo para reducir la cuota mensual.</div>', unsafe_allow_html=True)
                    
                    elif dti_dashboard_visible and DTI_WARN < dti_dashboard_visible <= DTI_FAIL:
                        with st.container():
                            st.markdown("### ⚠️ Capacidad de endeudamiento en el límite")
                            st.markdown("Tu capacidad de endeudamiento está cerca del límite. Te recomendamos:")
                            st.markdown('<div class="opcion-consejo">• Aportar más dinero para la entrada inicial</div>', unsafe_allow_html=True)
                            st.markdown('<div class="opcion-consejo">• Reducir el precio objetivo de la vivienda</div>', unsafe_allow_html=True)
                            st.markdown('<div class="opcion-consejo">• Incorporar un avalista que mejore la evaluación bancaria</div>', unsafe_allow_html=True)
                    
                    if ltv_val > ltv_max:
                        with st.container():
                            if ltv_val > 0.8:  # Si supera el 80% de financiación
                                st.markdown("### 📊 Límite de financiación elevado")
                                st.markdown(f"El banco suele financiar hasta el 80% del valor de la vivienda (solicitado: {ltv_val*100:.1f}%).")
                                st.markdown("**Opciones para mejorar la viabilidad:**")
                                st.markdown(f'<div class="opcion-consejo">• Aportar un {((ltv_val - ltv_max)*100):.1f}% adicional de entrada</div>', unsafe_allow_html=True)
                                st.markdown('<div class="opcion-consejo">• Consultar con otros bancos por condiciones especiales</div>', unsafe_allow_html=True)
                                st.markdown('<div class="opcion-consejo">• Valorar un avalista o garantías adicionales</div>', unsafe_allow_html=True)
                                st.markdown('<div class="opcion-consejo">• Buscar una propiedad con un precio más ajustado</div>', unsafe_allow_html=True)
                            else:
                                st.markdown("### 📊 Financiación dentro de los límites")
                                st.markdown(f"El banco financia hasta el {ltv_max*100:.0f}% del valor de la vivienda (solicitado: {ltv_val*100:.1f}%).")
                else:
                    st.success("✅ Tu operación es viable con los parámetros actuales.")

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
                        denominador_log = cuota_estimada - nuevo_capital * r_mensual
                        if denominador_log <= 0 or (1 + r_mensual) <= 0:
                            nuevo_plazo_meses = 0
                        else:
                            nuevo_plazo_meses = math.log(
                                cuota_estimada / denominador_log
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
                    st.caption("En hipotecas fijas la cuota se mantiene estable; en variables puede cambiar según el Euríbor. En ambos casos, cada año disminuye la parte de intereses y aumenta la de capital.")

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
                    st.caption("En el tramo fijo, la cuota se calcula con el plazo total de la hipoteca, quedando capital pendiente para el tramo variable.")

                    # Tramo variable (plazo restante)
                    plazo_var = max(0, anos_plazo - anios_fijo)
                    if plazo_var > 0 and capital_pendiente > 0:
                        data_var = []
                        r_var = interes_variable / 12 if interes_variable else 0.0
                        cuota_mensual_var = cuota_prestamo(capital_pendiente, interes_variable, plazo_var) if plazo_var > 0 else 0.0

                        for anio in range(1, plazo_var + 1):
                            intereses_anio = 0.0
                            capital_anio = 0.0
                            for mes in range(12):
                                if dti_peor_visible and dti_peor_visible > DTI_FAIL:
                                    mensaje_dti = (
                                        "📊 **Capacidad de endeudamiento superada**\n\n"
                                        f"Tu ratio DTI ({dti_peor_visible*100:.1f}%) supera el máximo recomendado ({DTI_FAIL*100:.0f}%).\n\n"
                                        "🔹 **Opciones para mejorar tu perfil financiero:**\n"
                                        "   • Aumenta la entrada inicial para reducir el importe a financiar\n"
                                        "   • Considera ampliar el plazo del préstamo para reducir la cuota mensual\n"
                                        "   • Reduce el precio objetivo de la vivienda\n"
                                        "   • Mejora tus ingresos o reduce otras deudas"
                                    )
                                    consejos.append(mensaje_dti)
                                elif dti_peor_visible and DTI_WARN < dti_peor_visible <= DTI_FAIL:
                                    mensaje_dti = (
                                        "⚠️ **Atención: Límite de endeudamiento cercano**\n\n"
                                        f"Tu ratio DTI ({dti_peor_visible*100:.1f}%) se acerca al máximo recomendado ({DTI_FAIL*100:.0f}%).\n\n"
                                        "🔹 **Recomendaciones para mejorar tu perfil:**\n"
                                        "   • Aporta más dinero para la entrada si es posible\n"
                                        "   • Valora reducir el precio de la vivienda objetivo\n"
                                        "   • Considera la opción de un avalista\n"
                                        "   • Revisa si puedes reducir otras deudas existentes"
                                    )
                                    consejos.append(mensaje_dti)
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
                        st.caption("En el tramo variable, la cuota se recalcula con el nuevo tipo de interés y el plazo restante.")
                    else:
                        st.info("ℹ️ El capital quedó totalmente amortizado en el tramo fijo o no hay plazo restante.")

        # =========================
        # 📈 Evolución del Capital (Gráfico de Área)
        # =========================
        st.subheader("📈 Evolución del Capital e Intereses")
        
        if not sin_hipoteca and cuota_estimada > 0 and capital_hipoteca > 0:
            # Generar datos para el gráfico de evolución
            if tipo_hipoteca in ["Fija", "Variable"]:
                evolucion_data = []
                capital_pendiente = capital_hipoteca
                r = interes_anual / 12 if interes_anual else 0.0
                cuota_mensual = cuota_estimada

                intereses_acumulados = 0.0
                capital_amortizado_acumulado = 0.0
                
                for anio in range(1, anos_plazo + 1):
                    intereses_anio = 0.0
                    capital_anio = 0.0
                    
                    for mes in range(12):
                        if capital_pendiente <= 0:
                            break
                        interes_mes = capital_pendiente * r
                        amortizacion_mes = cuota_mensual - interes_mes
                        intereses_anio += interes_mes
                        capital_anio += amortizacion_mes
                        capital_pendiente -= amortizacion_mes
                    
                    intereses_acumulados += intereses_anio
                    capital_amortizado_acumulado += capital_anio
                    
                    evolucion_data.append({
                        "Año": anio,
                        "Capital Pendiente": max(0, capital_pendiente),
                        "Intereses Acumulados": intereses_acumulados,
                        "Capital Amortizado": capital_amortizado_acumulado,
                        "Intereses Anuales": intereses_anio,
                        "Capital Anual": capital_anio
                    })
                    
                    if capital_pendiente <= 0:
                        break
                
                # Crear DataFrame
                df_evolucion = pd.DataFrame(evolucion_data)
                
                # =========================
                # Sistema de Tabs para Evolución del Capital
                # =========================
                tab1, tab2 = st.tabs(["📈 Evolución del Capital", "💰 Distribución de Pagos"])
                
                with tab1:
                    # Obtener configuración de tema
                    theme = get_chart_theme()
                    # Configuración de colores para tooltips
                    if theme.get('dark'):
                        hover_bg = 'rgba(255, 255, 255, 0.96)'  # Fondo blanco para mejor contraste
                        hover_border = 'rgba(100, 116, 139, 0.5)'
                        hover_text_color = '#1A1A1A'  # Texto oscuro para mejor legibilidad
                    else:
                        hover_bg = color_with_alpha(theme.get('secondary_bg', '#F0F2F6'), 0.96)
                        hover_border = color_with_alpha(theme.get('axis_label_color', theme['text_color']), 0.3)
                        hover_text_color = theme.get('text_color', '#1A1A1A')
                    tooltip_color = hover_text_color
                    
                    # Crear figura con tema adaptativo
                    fig_capital = go.Figure()
                    
                    # Añadir trazo con colores del tema
                    fig_capital.add_trace(
                        go.Scatter(
                            x=df_evolucion["Año"],
                            y=df_evolucion["Capital Pendiente"],
                            fill='tozeroy',
                            mode='lines+markers',
                            name='Capital Pendiente',
                            line=dict(color=theme['colors'][0], width=3),
                            fillcolor=f"rgba({int(theme['colors'][0].lstrip('#')[0:2], 16)}, "
                                    f"{int(theme['colors'][0].lstrip('#')[2:4], 16)}, "
                                    f"{int(theme['colors'][0].lstrip('#')[4:6], 16)}, 0.3)",
                            hovertemplate=(
                                f"<b style='color:{tooltip_color}'>Año %{{x}}</b><br>"
                                f"<span style='color:{tooltip_color}'>Capital pendiente: %{{y:,.2f}} €</span><extra></extra>"
                            )
                        )
                    )
                    
                    # Configuración de diseño adaptativo con automargin
                    fig_capital.update_layout(
                        title={
                            'text': "<b>Evolución del Capital Pendiente</b>",
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {
                                'color': theme.get('title_color', theme['text_color']),
                                'family': 'Arial, sans-serif',
                                'size': 18
                            },
                            'pad': {'b': 10, 't': 20}  # Espaciado interno para el título
                        },
                        annotations=[
                            dict(
                                x=0.5,
                                y=1.0,
                                xref='paper',
                                yref='paper',
                                text=f"Plazo: {anos_plazo} años | Capital inicial: {eur(capital_hipoteca)}",
                                showarrow=False,
                                font=dict(
                                    size=14,
                                    color='#F0F0F0' if theme['dark'] else theme.get('subtitle_color', theme['text_color']),
                                    family='Arial, sans-serif, Segoe UI'
                                ),
                                xanchor='center',
                                yanchor='bottom',
                                yshift=10,
                                opacity=0.95
                            )
                        ],
                        height=540,
                        margin=dict(l=80, r=80, t=90, b=80),  # Margen superior aumentado
                        font=dict(
                            size=14,
                            color=theme['text_color']
                        ),
                        showlegend=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(
                            gridcolor=theme['grid_color'],
                            linecolor=theme.get('axis_label_color', theme['text_color']),
                            zerolinecolor=theme.get('axis_label_color', theme['text_color']),
                            showgrid=True,
                            tickfont=dict(
                                color=theme.get('tick_color', theme['text_color']),
                                size=12
                            ),
                            title_font=dict(
                                color=theme.get('axis_label_color', theme['text_color']),
                                size=13
                            )
                        ),
                        yaxis=dict(
                            gridcolor=theme['grid_color'],
                            linecolor=theme.get('axis_label_color', theme['text_color']),
                            zerolinecolor=theme.get('axis_label_color', theme['text_color']),
                            showgrid=True,
                            tickformat=',.0f',
                            tickprefix='€',
                            tickfont=dict(
                                color=theme.get('tick_color', theme['text_color']),
                                size=12
                            ),
                            title_font=dict(
                                color=theme.get('axis_label_color', theme['text_color']),
                                size=13
                            )
                        ),
                        hoverlabel=dict(
                            bgcolor=hover_bg,
                            bordercolor=hover_border,
                            font=dict(color=hover_text_color, size=12, family="sans-serif"),
                            align="left"
                        ),
                        # Forzar estilos de tooltip
                        hoverlabel_font_color=hover_text_color,
                        hoverlabel_bgcolor=hover_bg,
                        hoverlabel_bordercolor=hover_border,
                        # Configuración adicional para tooltips
                        hoverlabel_namelength=-1,  # Mostrar el nombre completo
                        # Estilos para el contenedor del tooltip
                        hoverlabel_align='left',
                        # Asegurar que el tema oscuro se aplique correctamente
                        template='plotly_dark' if theme['dark'] else 'plotly'
                    )
                    
                    fig_capital.update_xaxes(title_text="Año", tickfont=dict(size=12))
                    fig_capital.update_yaxes(title_text="Capital Pendiente (€)", tickfont=dict(size=12))
                    
                    # Configuración responsive para el gráfico de capital
                    fig_capital.update_layout(
                        autosize=True,
                        font=dict(size=12)
                    )
                    # Habilitar automargin para ejes
                    fig_capital.update_xaxes(automargin=True)
                    fig_capital.update_yaxes(automargin=True)
                    st.plotly_chart(
                        fig_capital, 
                        use_container_width=True,
                        config={
                            'displayModeBar': True,
                            'responsive': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'select'],
                            'staticPlot': False
                        }
                    )
                    
                    st.markdown("""
                    **📊 ¿Qué muestra este gráfico?**
                    - La línea azul representa tu deuda restante cada año
                    - El área sombreada muestra la magnitud de la deuda
                    - Al final del plazo, la deuda llega a cero
                    
                    **💡 Información clave:**
                    - Los primeros años se reduce más lentamente (pagas más intereses)
                    - Los últimos años se reduce más rápido (pagas más capital)
                    """)
                
                with tab2:
                    theme = get_chart_theme()
                    subtitle_color = theme.get('subtitle_color', theme['text_color'])
                    # Configuración de colores para tooltips
                    if theme.get('dark'):
                        hover_bg = 'rgba(255, 255, 255, 0.96)'  # Fondo blanco para mejor contraste
                        hover_border = 'rgba(100, 116, 139, 0.5)'
                        hover_text_color = '#1A1A1A'  # Texto oscuro para mejor legibilidad
                    else:
                        hover_bg = color_with_alpha(theme.get('secondary_bg', '#F0F2F6'), 0.96)
                        hover_border = color_with_alpha(theme.get('axis_label_color', theme['text_color']), 0.3)
                        hover_text_color = theme.get('text_color', '#1A1A1A')
                    tooltip_color = hover_text_color
                    fig_pagos = go.Figure()
                    
                    fig_pagos.add_trace(
                        go.Bar(
                            x=df_evolucion["Año"],
                            y=df_evolucion["Capital Anual"],
                            name='Capital Amortizado',
                            marker_color=theme['colors'][2],
                            hovertemplate=(
                                f"<b style='color:{tooltip_color}'>Año %{{x}}</b><br>"
                                f"<span style='color:{tooltip_color}'>Capital: %{{y:,.2f}} €</span><extra></extra>"
                            )
                        )
                    )
                    
                    fig_pagos.add_trace(
                        go.Bar(
                            x=df_evolucion["Año"],
                            y=df_evolucion["Intereses Anuales"],
                            name='Intereses Pagados',
                            marker_color=theme['colors'][3],
                            hovertemplate=(
                                f"<b style='color:{tooltip_color}'>Año %{{x}}</b><br>"
                                f"<span style='color:{tooltip_color}'>Intereses: %{{y:,.2f}} €</span><extra></extra>"
                            )
                        )
                    )
                    
# No es necesario volver a definir las variables, ya están definidas arriba
                    
                    fig_pagos.update_layout(
                        title={
                            'text': "<b>Distribución Anual de Pagos</b>",
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {
                                'color': theme.get('title_color', theme['text_color']),
                                'family': 'Arial, sans-serif',
                                'size': 18
                            },
                            'pad': {'b': 10, 't': 20}  # Espaciado interno para el título
                        },
                        annotations=[
                            dict(
                                x=0.5,
                                y=1.0,
                                xref='paper',
                                yref='paper',
                                text="Capital vs Intereses por año",
                                showarrow=False,
                                font=dict(
                                    size=14,
                                    color='#F0F0F0' if theme['dark'] else theme.get('subtitle_color', theme['text_color']),
                                    family='Arial, sans-serif, Segoe UI'
                                ),
                                xanchor='center',
                                yanchor='bottom',
                                yshift=10,
                                opacity=0.95
                            )
                        ],
                        height=520,
                        barmode='stack',
                        margin=dict(l=80, r=80, t=100, b=160),  # Margen superior aumentado
                        font=dict(size=14, color=theme['text_color']),
                        legend=dict(
                            orientation="h",
                            yanchor="top",
                            y=-0.22,
                            xanchor="center",
                            x=0.5,
                            bgcolor='rgba(0,0,0,0)',
                            bordercolor='rgba(0,0,0,0)',
                            borderwidth=0,
                            font=dict(color=theme['text_color'], size=12),
                            title=dict(text="")
                        ),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(
                            gridcolor=theme['grid_color'],
                            linecolor=theme.get('axis_label_color', theme['text_color']),
                            zerolinecolor=theme.get('axis_label_color', theme['text_color']),
                            showgrid=True,
                            tickfont=dict(
                                color=theme.get('tick_color', theme['text_color']),
                                size=12
                            ),
                            title_font=dict(
                                color=theme.get('axis_label_color', theme['text_color']),
                                size=13
                            )
                        ),
                        yaxis=dict(
                            gridcolor=theme['grid_color'],
                            linecolor=theme.get('axis_label_color', theme['text_color']),
                            zerolinecolor=theme.get('axis_label_color', theme['text_color']),
                            showgrid=True,
                            tickfont=dict(
                                color=theme.get('tick_color', theme['text_color']),
                                size=12
                            ),
                            title_font=dict(
                                color=theme.get('axis_label_color', theme['text_color']),
                                size=13
                            )
                        ),
                        hoverlabel=dict(
                            bgcolor=hover_bg,
                            bordercolor=hover_border,
                            font=dict(color=hover_text_color, size=12, family="sans-serif"),
                            align="left"
                        ),
                        hovermode='x unified',
                        # Forzar estilos de tooltip
                        hoverlabel_font_color=hover_text_color,
                        hoverlabel_bgcolor=hover_bg,
                        hoverlabel_bordercolor=hover_border,
                        # Configuración adicional para tooltips
                        hoverlabel_namelength=-1,  # Mostrar el nombre completo
                        # Estilos para el contenedor del tooltip
                        hoverlabel_align='left',
                        # Asegurar que el tema oscuro se aplique correctamente
                        template='plotly_dark' if theme['dark'] else 'plotly'
                    )
                    
                    # Configuración de tooltips para las barras
                    fig_pagos.update_traces(
                        hoverlabel=dict(
                            bgcolor=hover_bg,
                            bordercolor=hover_border,
                            font=dict(color=hover_text_color, size=12, family="sans-serif"),
                            align='left',
                            namelength=0
                        ),
                        hovertemplate=(
                            "<span style='color:%s;'><b>Año %%{x}</b><br>"
                            "%%{data.name}: %%{y:,.2f} €</span><extra></extra>" % hover_text_color
                        )
                    )
                    fig_pagos.update_xaxes(title_text="Año")
                    fig_pagos.update_yaxes(title_text="Pago Anual (€)" )
                    
                    # Configuración responsive para el gráfico de pagos
                    fig_pagos.update_layout(
                        autosize=True,
                        font=dict(size=12)
                    )
                    # Habilitar automargin para ejes
                    fig_pagos.update_xaxes(automargin=True)
                    fig_pagos.update_yaxes(automargin=True)
                    st.plotly_chart(
                        fig_pagos, 
                        use_container_width=True,
                        config={
                            'displayModeBar': True,
                            'responsive': True,
                            'displaylogo': False,
                            'modeBarButtonsToRemove': ['select2d', 'lasso2d', 'select'],
                            'staticPlot': False
                        }
                    )
                    
                    st.markdown("""
                    **📊 ¿Qué muestra este gráfico?**
                    - **Barras verdes:** Capital que reduces de tu deuda (dinero "tuyo")
                    - **Barras rojas:** Intereses que pagas al banco (coste financiero)
                    - La altura total es tu cuota anual
                    
                    **💡 Información clave:**
                    - Al principio: barras rojas más grandes (pagas más intereses)
                    - Al final: barras verdes más grandes (pagas más capital)
                    - Esta es la razón por la que las amortizaciones anticipadas son más efectivas al principio
                    """)
                
            elif tipo_hipoteca == "Mixta":
                st.info("ℹ️ El gráfico de evolución detallado para hipotecas mixtas no está disponible. "
                       "Puedes ver la evolución en las tablas de amortización de los tramos fijo y variable.")
        else:
            if sin_hipoteca:
                st.info("No hay gráfico de evolución: no existe hipoteca (compra al contado).")
            else:
                st.warning("No se puede generar el gráfico de evolución porque faltan parámetros válidos.")

        # =========================
        # Resumen compacto
        # =========================
        st.divider()
        st.subheader("Resumen compacto")

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
# 🧪 Validador profesional completo de coherencia hipotecaria
# ============================================================

MODO_VALIDACION = False           # ⬅️ Actívalo a "True" para ejecutar el validador; "False" para desactivarlo.

if MODO_VALIDACION:
    import statistics as stats
    import random
    
    st.header("🧪 VALIDACIÓN PROFESIONAL COMPLETA")
    st.markdown("**Validando coherencia matemática y lógica en todos los escenarios hipotecarios**")
    
    # --- Umbrales alineados con la app ---
    DTI_WARN = 0.30
    DTI_FAIL = 0.35
    LTV_MAX = 0.80
    
    # --- Funciones de validación ---
    def validar_escenario(tipo_hipoteca, escenario_id, params):
        """Valida un escenario específico y devuelve resultados"""
        errores = []
        advertencias = []
        
        try:
            # Parámetros básicos
            precio = params["precio"]
            entrada = params["entrada"]
            sueldo = params["sueldo"]
            deudas = params["deudas"]
            plazo = params["plazo"]
            
            # Cálculos básicos
            capital_hipoteca = max(0, precio - entrada)
            ltv_real = (capital_hipoteca / precio) if precio > 0 else 0.0
            cuota_maxima_user = cuota_maxima(sueldo, deudas, DTI_FAIL)
            
            # Validaciones básicas
            if capital_hipoteca < 0:
                errores.append("Capital hipoteca negativo")
            if ltv_real < 0 or ltv_real > 1:
                errores.append("LTV fuera de rango válido")
            if cuota_maxima_user < 0:
                errores.append("Cuota máxima negativa")
            
            # Cálculos específicos por tipo
            if tipo_hipoteca == "Fija":
                interes = params["interes"]
                cuota = cuota_prestamo(capital_hipoteca, interes, plazo)
                dti_calc = dti(cuota, deudas, sueldo) if cuota else 0.0
                
                if cuota is None or cuota <= 0:
                    errores.append("Cuota fija inválida")
                if dti_calc < 0 or dti_calc > 1:
                    errores.append("DTI fuera de rango")
                    
            elif tipo_hipoteca == "Variable":
                interes = params["interes"]
                cuota = cuota_prestamo(capital_hipoteca, interes, plazo)
                dti_calc = dti(cuota, deudas, sueldo) if cuota else 0.0
                
                if cuota is None or cuota <= 0:
                    errores.append("Cuota variable inválida")
                if dti_calc < 0 or dti_calc > 1:
                    errores.append("DTI fuera de rango")
                    
            elif tipo_hipoteca == "Mixta":
                interes_fijo = params["interes_fijo"]
                interes_var = params["interes_var"]
                anios_fijo = params.get("anios_fijo", 5)
                
                # Para hipotecas mixtas, calculamos la cuota como si fuera el plazo total
                # pero usando el interés más alto para el peor escenario
                cuota_fija = cuota_prestamo(capital_hipoteca, interes_fijo, plazo)
                cuota_variable = cuota_prestamo(capital_hipoteca, interes_var, plazo)
                
                dti_fijo = dti(cuota_fija, deudas, sueldo) if cuota_fija else 0.0
                dti_variable = dti(cuota_variable, deudas, sueldo) if cuota_variable else 0.0
                
                # Validaciones específicas mixta
                if cuota_fija is None or cuota_fija <= 0:
                    errores.append("Cuota fija inválida en mixta")
                if cuota_variable is None or cuota_variable <= 0:
                    errores.append("Cuota variable inválida en mixta")
                if dti_fijo < 0 or dti_fijo > 1 or dti_variable < 0 or dti_variable > 1:
                    errores.append("DTI fuera de rango en mixta")
                    
                # Coherencia del peor tramo
                cuota_peor = max(cuota_fija, cuota_variable)
                tramo_peor = "FIJO" if cuota_peor == cuota_fija else "VARIABLE"
                
                if tramo_peor == "FIJO" and cuota_fija < cuota_variable:
                    advertencias.append("Inconsistencia en identificación peor tramo")
                
                cuota = cuota_peor
                dti_calc = max(dti_fijo, dti_variable)
            
            # Validaciones de coherencia general
            if cuota and cuota > 0:
                if dti_calc > DTI_FAIL and es_viable(cuota, cuota_maxima_user, ltv_real, LTV_MAX, dti_calc):
                    advertencias.append("DTI > 35% pero operación marcada como viable")
                    
                if ltv_real > LTV_MAX and es_viable(cuota, cuota_maxima_user, ltv_real, LTV_MAX, dti_calc):
                    advertencias.append("LTV > 80% pero operación marcada como viable")
            
            # Validaciones matemáticas
            if capital_hipoteca > 0 and sueldo > 0:
                ratio_endeudamiento = (deudas / sueldo) if sueldo > 0 else 0.0
                if ratio_endeudamiento > DTI_FAIL:
                    advertencias.append("Ratio de endeudamiento base ya supera 35%")
        
        except Exception as e:
            errores.append(f"Error en cálculo: {str(e)}")
        
        return {
            "escenario_id": escenario_id,
            "tipo_hipoteca": tipo_hipoteca,
            "errores": errores,
            "advertencias": advertencias,
            "viable": len(errores) == 0,
            "ltv": ltv_real,
            "dti": dti_calc if 'dti_calc' in locals() else 0.0,
            "cuota": cuota if 'cuota' in locals() else 0.0
        }
    
    # --- Escenarios de prueba completos ---
    escenarios_prueba = [
        # Hipoteca Fija
        {"tipo": "Fija", "id": "FJ-01", "precio": 200000, "entrada": 40000, "interes": 0.025, "plazo": 20, "sueldo": 2500, "deudas": 0},
        {"tipo": "Fija", "id": "FJ-02", "precio": 300000, "entrada": 60000, "interes": 0.035, "plazo": 25, "sueldo": 3000, "deudas": 200},
        {"tipo": "Fija", "id": "FJ-03", "precio": 150000, "entrada": 30000, "interes": 0.020, "plazo": 15, "sueldo": 2000, "deudas": 100},
        
        # Hipoteca Variable
        {"tipo": "Variable", "id": "VR-01", "precio": 250000, "entrada": 50000, "interes": 0.030, "plazo": 20, "sueldo": 2800, "deudas": 0},
        {"tipo": "Variable", "id": "VR-02", "precio": 350000, "entrada": 70000, "interes": 0.040, "plazo": 30, "sueldo": 4000, "deudas": 300},
        {"tipo": "Variable", "id": "VR-03", "precio": 180000, "entrada": 36000, "interes": 0.025, "plazo": 25, "sueldo": 2200, "deudas": 150},
        
        # Hipoteca Mixta
        {"tipo": "Mixta", "id": "MX-01", "precio": 280000, "entrada": 56000, "interes_fijo": 0.025, "interes_var": 0.035, "anios_fijo": 5, "plazo": 25, "sueldo": 3200, "deudas": 100},
        {"tipo": "Mixta", "id": "MX-02", "precio": 400000, "entrada": 80000, "interes_fijo": 0.030, "interes_var": 0.045, "anios_fijo": 10, "plazo": 30, "sueldo": 4500, "deudas": 200},
        {"tipo": "Mixta", "id": "MX-03", "precio": 200000, "entrada": 40000, "interes_fijo": 0.022, "interes_var": 0.032, "anios_fijo": 3, "plazo": 20, "sueldo": 2500, "deudas": 0},
        
        # Casos límite
        {"tipo": "Fija", "id": "LM-01", "precio": 100000, "entrada": 20000, "interes": 0.050, "plazo": 30, "sueldo": 1500, "deudas": 100},
        {"tipo": "Variable", "id": "LM-02", "precio": 500000, "entrada": 100000, "interes": 0.020, "plazo": 15, "sueldo": 6000, "deudas": 500},
        {"tipo": "Mixta", "id": "LM-03", "precio": 150000, "entrada": 30000, "interes_fijo": 0.015, "interes_var": 0.025, "anios_fijo": 2, "plazo": 10, "sueldo": 1800, "deudas": 50},
    ]
    
    # ============================================================
    # 🔍 Ejecutar validación completa
    # ============================================================
    # --- Ejecutar validación de todos los escenarios ---
    resultados = []
    errores_criticos = []
    advertencias = []
    
    for escenario in escenarios_prueba:
        resultado = validar_escenario(
            escenario["tipo"], 
            escenario["id"], 
            escenario
        )
        resultados.append(resultado)
        
        if resultado["errores"]:
            errores_criticos.extend([
                f"{resultado['escenario_id']}: {error}" 
                for error in resultado["errores"]
            ])
        
        if resultado["advertencias"]:
            advertencias.extend([
                f"{resultado['escenario_id']}: {warning}" 
                for warning in resultado["advertencias"]
            ])
    
    # --- Métricas generales ---
    total_escenarios = len(resultados)
    escenarios_exitosos = sum(1 for r in resultados if r["viable"])
    tasa_exito = (escenarios_exitosos / total_escenarios * 100) if total_escenarios > 0 else 0
    
    # --- Resumen por tipo de hipoteca ---
    fijas = [r for r in resultados if r["tipo_hipoteca"] == "Fija"]
    variables = [r for r in resultados if r["tipo_hipoteca"] == "Variable"]
    mixtas = [r for r in resultados if r["tipo_hipoteca"] == "Mixta"]
    
    st.subheader("📊 Métricas generales")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Escenarios probados", total_escenarios)
    col2.metric("Errores críticos", len(errores_criticos))
    col3.metric("Advertencias", len(advertencias))
    col4.metric("Tasa éxito", f"{tasa_exito:.1f}%")
    
    # --- Veredicto final ---
    if not errores_criticos and not advertencias:
        st.success("✅ **VEREDICTO: Todo correcto** - La calculadora funciona perfectamente en todos los escenarios")
    elif errores_criticos:
        st.error(f"❌ **VEREDICTO: Problemas detectados** - {len(errores_criticos)} errores críticos encontrados")
    else:
        st.warning(f"⚠️ **VEREDICTO: Precaución** - {len(advertencias)} advertencias encontradas")
    
    # --- Detalles por tipo ---
    st.subheader("📈 Resumen por tipo de hipoteca")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🟦 Hipoteca Fija**")
        st.write(f"Escenarios: {len(fijas)}")
        st.write(f"Éxitos: {sum(1 for r in fijas if r['viable'])}")
        st.write(f"Errores: {sum(len(r['errores']) for r in fijas)}")
    
    with col2:
        st.markdown("**🟧 Hipoteca Variable**")
        st.write(f"Escenarios: {len(variables)}")
        st.write(f"Éxitos: {sum(1 for r in variables if r['viable'])}")
        st.write(f"Errores: {sum(len(r['errores']) for r in variables)}")
    
    with col3:
        st.markdown("**🟩 Hipoteca Mixta**")
        st.write(f"Escenarios: {len(mixtas)}")
        st.write(f"Éxitos: {sum(1 for r in mixtas if r['viable'])}")
        st.write(f"Errores: {sum(len(r['errores']) for r in mixtas)}")
    
    # --- Detalles de errores y advertencias ---
    if errores_criticos:
        st.subheader("❌ Errores críticos detectados")
        for error in errores_criticos:
            st.error(error)
    
    if advertencias:
        st.subheader("⚠️ Advertencias detectadas")
        for warning in advertencias:
            st.warning(warning)
    
    # --- Detalles de escenarios ---
    with st.expander("📋 Ver detalles de todos los escenarios"):
        for resultado in resultados:
            st.markdown(f"**{resultado['escenario_id']} - {resultado['tipo_hipoteca']}**")
            col1, col2, col3, col4 = st.columns(4)
            col1.write(f"LTV: {pct(resultado['ltv'])}")
            col2.write(f"DTI: {pct(resultado['dti'])}")
            col3.write(f"Cuota: {eur(resultado['cuota'])}")
            col4.write(f"Estado: {'✅ OK' if resultado['viable'] else '❌ Error'}")
            
            if resultado['errores']:
                st.error("Errores: " + ", ".join(resultado['errores']))
            if resultado['advertencias']:
                st.warning("Advertencias: " + ", ".join(resultado['advertencias']))








# =========================
# Pie de transparencia
# =========================
st.divider()
st.caption("""
**Autor:** Letalicus  
**Versión:** 1.4.0  
**Fecha de actualización:** Noviembre 2025
""")
