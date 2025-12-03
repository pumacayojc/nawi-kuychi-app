import math
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from io import BytesIO

# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================
st.set_page_config(
    page_title="NAWI KUYCHI - Muestreo MIL-STD-414",
    page_icon="🧶",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CONSTANTES Y CONFIGURACIONES
# ============================================================
COLORES = {
    'primary': '#800000',
    'secondary': '#E9C46A',
    'accent1': '#2A9D8F',
    'accent2': '#E76F51',
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# ============================================================
# CLASES DE DATOS
# ============================================================
class PlanMuestreo:
    """Clase para gestionar el plan de muestreo"""
    
    RANGOS_LOTE = [
        (3, 8,     {'I': 'B', 'II': 'B', 'III': 'B', 'IV': 'B', 'V': 'C'}),
        (9, 15,    {'I': 'B', 'II': 'B', 'III': 'B', 'IV': 'B', 'V': 'D'}),
        (16, 25,   {'I': 'B', 'II': 'B', 'III': 'B', 'IV': 'C', 'V': 'E'}),
        (26, 40,   {'I': 'B', 'II': 'B', 'III': 'B', 'IV': 'D', 'V': 'F'}),
        (41, 65,   {'I': 'B', 'II': 'B', 'III': 'C', 'IV': 'E', 'V': 'G'}),
        (66, 110,  {'I': 'B', 'II': 'B', 'III': 'D', 'IV': 'F', 'V': 'H'}),
        (111, 180, {'I': 'B', 'II': 'C', 'III': 'E', 'IV': 'G', 'V': 'I'}),
        (181, 300, {'I': 'B', 'II': 'D', 'III': 'F', 'IV': 'H', 'V': 'J'}),
        (301, 500, {'I': 'C', 'II': 'E', 'III': 'G', 'IV': 'I', 'V': 'K'}),
        (501, 800, {'I': 'D', 'II': 'F', 'III': 'H', 'IV': 'J', 'V': 'L'}),
        (801, 1300,{'I': 'E', 'II': 'G', 'III': 'I', 'IV': 'K', 'V': 'L'}),
        (1301, 3200,{'I': 'F', 'II': 'H', 'III': 'J', 'IV': 'L', 'V': 'M'}),
        (3201, 8000,{'I': 'G', 'II': 'I', 'III': 'L', 'IV': 'M', 'V': 'N'}),
        (8001, 22000,{'I': 'H', 'II': 'J', 'III': 'M', 'IV': 'N', 'V': 'O'}),
        (22001, 110000,{'I': 'I', 'II': 'K', 'III': 'N', 'IV': 'O', 'V': 'P'}),
        (110001, 550000,{'I': 'I', 'II': 'K', 'III': 'O', 'IV': 'P', 'V': 'Q'}),
        (550001, float('inf'),{'I': 'I', 'II': 'K', 'III': 'P', 'IV': 'Q', 'V': 'Q'}),
    ]
    
    AQL_KEYS = ["0.04", "0.065", "0.1", "0.15", "0.25", "0.4", "0.65", "1",
                "1.5", "2.5", "4", "6.5", "10", "15"]
    
    TABLA_K = {
        "B": {"muestra": 3, "0.04": None, "0.065": None, "0.1": None, "0.15": None, "0.25": None, "0.4": None, "0.65": None, "1": None, "1.5": None, "2.5": 7.59, "4": 18.86, "6.5": 26.94, "10": 33.69, "15": 40.47},
        "C": {"muestra": 4, "0.04": None, "0.065": None, "0.1": None, "0.15": None, "0.25": None, "0.4": None, "0.65": None, "1": 1.53, "1.5": 5.5, "2.5": 10.92, "4": 16.45, "6.5": 22.86, "10": 29.45, "15": 36.9},
        "D": {"muestra": 5, "0.04": None, "0.065": None, "0.1": None, "0.15": None, "0.25": None, "0.4": None, "0.65": None, "1": 1.33, "1.5": 5.83, "2.5": 9.8, "4": 14.39, "6.5": 20.19, "10": 26.56, "15": 33.99},
        "E": {"muestra": 7, "0.04": None, "0.065": None, "0.1": None, "0.15": None, "0.25": 0.422, "0.4": 1.06, "0.65": 2.14, "1": 3.55, "1.5": 5.35, "2.5": 8.4, "4": 12.2, "6.5": 17.35, "10": 23.29, "15": 30.5},
        "F": {"muestra": 10, "0.04": None, "0.065": None, "0.1": None, "0.15": 0.349, "0.25": 0.716, "0.4": 1.3, "0.65": 2.17, "1": 3.26, "1.5": 4.77, "2.5": 7.29, "4": 10.54, "6.5": 15.17, "10": 20.74, "15": 27.57},
        "G": {"muestra": 15, "0.04": 0.099, "0.065": 0.099, "0.1": 0.312, "0.15": 0.503, "0.25": 0.818, "0.4": 1.31, "0.65": 2.11, "1": 3.05, "1.5": 4.31, "2.5": 6.56, "4": 9.46, "6.5": 13.71, "10": 18.94, "15": 25.61},
        "H": {"muestra": 20, "0.04": 0.135, "0.065": 0.135, "0.1": 0.365, "0.15": 0.544, "0.25": 0.846, "0.4": 1.29, "0.65": 2.05, "1": 2.95, "1.5": 4.09, "2.5": 6.17, "4": 8.92, "6.5": 12.99, "10": 18.03, "15": 24.53},
        "I": {"muestra": 25, "0.04": 0.155, "0.065": 0.156, "0.1": 0.38, "0.15": 0.551, "0.25": 0.877, "0.4": 1.29, "0.65": 2, "1": 2.86, "1.5": 3.97, "2.5": 5.97, "4": 8.63, "6.5": 12.57, "10": 17.51, "15": 23.97},
        "J": {"muestra": 30, "0.04": 0.179, "0.065": 0.179, "0.1": 0.413, "0.15": 0.581, "0.25": 0.879, "0.4": 1.29, "0.65": 1.98, "1": 2.83, "1.5": 3.91, "2.5": 5.86, "4": 8.47, "6.5": 12.36, "10": 17.24, "15": 23.58},
        "K": {"muestra": 35, "0.04": 0.17, "0.065": 0.17, "0.1": 0.388, "0.15": 0.535, "0.25": 0.847, "0.4": 1.23, "0.65": 1.87, "1": 2.68, "1.5": 3.7, "2.5": 5.57, "4": 8.1, "6.5": 11.87, "10": 16.65, "15": 22.91},
        "L": {"muestra": 40, "0.04": 0.179, "0.065": 0.179, "0.1": 0.401, "0.15": 0.566, "0.25": 0.873, "0.4": 1.26, "0.65": 1.88, "1": 2.71, "1.5": 3.72, "2.5": 5.58, "4": 8.09, "6.5": 11.85, "10": 16.61, "15": 22.86},
        "M": {"muestra": 50, "0.04": 0.163, "0.065": 0.163, "0.1": 0.363, "0.15": 0.503, "0.25": 0.789, "0.4": 1.17, "0.65": 1.71, "1": 2.49, "1.5": 3.45, "2.5": 5.2, "4": 7.61, "6.5": 11.23, "10": 15.87, "15": 22},
        "N": {"muestra": 75, "0.04": 1.147, "0.065": 0.147, "0.1": 0.33, "0.15": 0.467, "0.25": 0.72, "0.4": 1.07, "0.65": 1.6, "1": 2.29, "1.5": 3.2, "2.5": 4.87, "4": 7.15, "6.5": 10.63, "10": 15.13, "15": 21.11},
        "O": {"muestra": 100, "0.04": 0.145, "0.065": 0.145, "0.1": 0.317, "0.15": 0.447, "0.25": 0.689, "0.4": 1.02, "0.65": 1.53, "1": 2.2, "1.5": 3.07, "2.5": 4.69, "4": 6.91, "6.5": 10.32, "10": 14.75, "15": 20.66},
        "P": {"muestra": 150, "0.04": 0.134, "0.065": 0.134, "0.1": 0.293, "0.15": 0.413, "0.25": 0.638, "0.4": 0.949, "0.65": 1.43, "1": 2.05, "1.5": 2.89, "2.5": 4.43, "4": 6.57, "6.5": 9.88, "10": 14.2, "15": 20.02},
        "Q": {"muestra": 200, "0.04": 0.135, "0.065": 0.135, "0.1": 0.294, "0.15": 0.414, "0.25": 0.637, "0.4": 0.945, "0.65": 1.42, "1": 2.04, "1.5": 2.87, "2.5": 4.4, "4": 6.53, "6.5": 9.81, "10": 14.12, "15": 19.92}
    }
    
    @classmethod
    def obtener_letra(cls, nivel: str, tam_lote: int) -> str:
        """Obtiene la letra del plan según nivel y tamaño de lote"""
        for minimo, maximo, letras in cls.RANGOS_LOTE:
            if minimo <= tam_lote <= maximo:
                return letras[nivel]
        return None
    
    @classmethod
    def obtener_plan(cls, letra: str, aql: str) -> dict:
        """Obtiene el plan completo para una letra y AQL dados"""
        fila = cls.TABLA_K.get(letra)
        if not fila:
            return None
        
        return {
            'n': fila['muestra'],
            'k': fila.get(aql),
            'letra': letra,
            'aql': aql
        }

# ============================================================
# FUNCIONES UTILITARIAS
# ============================================================
def normal_cdf(z: float) -> float:
    """Función de distribución acumulada de N(0,1)"""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))

def calcular_estadisticas(pesos: list, lim_inf: float, lim_sup: float) -> dict:
    """Calcula todas las estadísticas necesarias"""
    n = len(pesos)
    X_bar = np.mean(pesos)
    S = np.std(pesos, ddof=1) if n > 1 else 0
    
    if S == 0:
        return {
            'n': n, 'media': X_bar, 'desviacion': S,
            'Z_ES': None, 'Z_EI': None,
            'pi': 0, 'ps': 0, 'p_total': 0,
            'estado': 'error', 'mensaje': 'Desviación estándar es cero'
        }
    
    Z_ES = (lim_sup - X_bar) / S
    Z_EI = (X_bar - lim_inf) / S
    
    pi = (1 - normal_cdf(Z_EI)) * 100
    ps = (1 - normal_cdf(Z_ES)) * 100
    p_total = pi + ps
    
    return {
        'n': n, 'media': X_bar, 'desviacion': S,
        'Z_ES': Z_ES, 'Z_EI': Z_EI,
        'pi': pi, 'ps': ps, 'p_total': p_total,
        'estado': 'ok'
    }

def generar_pesos_aleatorios(n: int, nominal: float, sigma: float = None, 
                             lim_inf: float = None, lim_sup: float = None) -> list:
    """Genera pesos aleatorios con distribución normal"""
    if sigma is None:
        sigma = (lim_sup - lim_inf) / 6.0 if lim_sup and lim_inf else nominal * 0.02
    
    pesos = []
    for _ in range(n):
        valor = random.gauss(nominal, sigma)
        # Asegurar que esté dentro de límites razonables
        if lim_inf and lim_sup:
            valor = max(lim_inf * 0.9, min(lim_sup * 1.1, valor))
        pesos.append(round(valor, 2))
    
    return pesos

def crear_grafico_interactivo(pesos: list, nominal: float, 
                              lim_inf: float, lim_sup: float, 
                              media: float) -> go.Figure:
    """Crea gráfico interactivo con Plotly"""
    fig = go.Figure()
    
    # Añadir puntos de pesos
    fig.add_trace(go.Scatter(
        x=list(range(1, len(pesos) + 1)),
        y=pesos,
        mode='markers+text',
        name='Pesos',
        marker=dict(size=12, color=COLORES['accent1'], line=dict(width=2, color='white')),
        text=[f'{p:.2f}' for p in pesos],
        textposition="top center",
        hovertemplate='Muestra %{x}: %{y:.2f}<extra></extra>'
    ))
    
    # Añadir líneas de referencia
    fig.add_hline(y=nominal, line_dash="dash", line_color=COLORES['success'],
                  annotation_text="Nominal", annotation_position="bottom right")
    fig.add_hline(y=lim_inf, line_dash="dash", line_color=COLORES['danger'],
                  annotation_text="Lím. Inferior", annotation_position="bottom right")
    fig.add_hline(y=lim_sup, line_dash="dash", line_color=COLORES['danger'],
                  annotation_text="Lím. Superior", annotation_position="bottom right")
    fig.add_hline(y=media, line_dash="solid", line_color=COLORES['primary'],
                  annotation_text="Media", annotation_position="top right")
    
    # Área de especificación
    fig.add_hrect(y0=lim_inf, y1=lim_sup, 
                  fillcolor="rgba(42, 157, 143, 0.1)", 
                  line_width=0, annotation_text="Zona de especificación")
    
    # Configurar layout
    fig.update_layout(
        title="Distribución de Pesos de la Muestra",
        xaxis_title="Ítem de Muestra",
        yaxis_title="Peso",
        hovermode="closest",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", size=12, color=COLORES['dark']),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
    
    return fig

# ============================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================
def inicializar_estado():
    """Inicializa todas las variables de estado"""
    estado_default = {
        'plan_calculado': False,
        'n': 0,
        'k': None,
        'pesos': [],
        'historico_analisis': [],
        'ultimo_analisis': None,
        'configuracion': {
            'nivel': 'II',
            'tam_lote': 1000,
            'aql': '1',
            'nominal': 100.0,
            'lim_inf': 98.0,
            'lim_sup': 102.0
        }
    }
    
    for key, value in estado_default.items():
        if key not in st.session_state:
            st.session_state[key] = value

# ============================================================
# COMPONENTES DE INTERFAZ
# ============================================================
def mostrar_header():
    """Muestra el encabezado de la aplicación"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORES['primary']}, {COLORES['accent2']});
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    ">
        <div style="display: flex; align-items: center; gap: 2rem;">
            <div style="flex-shrink: 0;">
                <svg width="80" height="80" viewBox="0 0 100 100">
                    <circle cx="50" cy="50" r="45" stroke="{COLORES['secondary']}" stroke-width="4" fill="none"/>
                    <path d="M25 40 C35 30,45 25,60 35" stroke="{COLORES['accent1']}" stroke-width="2" fill="none"/>
                    <path d="M30 50 C40 40,50 35,65 45" stroke="{COLORES['accent1']}" stroke-width="2" fill="none"/>
                    <path d="M35 60 C45 50,55 45,70 55" stroke="{COLORES['accent2']}" stroke-width="2" fill="none"/>
                    <path d="M40 70 C50 60,60 55,75 65" stroke="{COLORES['secondary']}" stroke-width="2" fill="none"/>
                </svg>
            </div>
            <div style="flex-grow: 1;">
                <h1 style="margin: 0; font-size: 2.8rem; font-weight: 800;">NAWI KUYCHI</h1>
                <p style="margin: 0.5rem 0 0 0; font-size: 1.2rem; opacity: 0.9;">
                    Sistema de Muestreo MIL-STD-414 para Control de Calidad
                </p>
                <p style="margin: 0.5rem 0 0 0; font-size: 1rem; font-weight: 300;">
                    Medimos para crear valor · Precisión en cada ovillo
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Indicadores rápidos
    if st.session_state.plan_calculado:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Muestra (n)", st.session_state.n)
        with col2:
            st.metric("AQL", st.session_state.configuracion['aql'])
        with col3:
            k_val = st.session_state.k if st.session_state.k else "N/A"
            st.metric("Valor M (k)", f"{k_val}")
        with col4:
            estado = "✅ Activo" if st.session_state.plan_calculado else "⏳ Pendiente"
            st.metric("Estado Plan", estado)

def mostrar_panel_configuracion():
    """Muestra el panel de configuración del plan"""
    st.markdown("###⚙️ Configuración del Plan de Muestreo")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nivel = st.selectbox(
                "Nivel de Inspección",
                ["I", "II", "III", "IV", "V"],
                index=["I", "II", "III", "IV", "V"].index(st.session_state.configuracion['nivel']),
                help="Nivel de rigurosidad de la inspección"
            )
        
        with col2:
            tam_lote = st.number_input(
                "Tamaño del Lote",
                min_value=3,
                value=st.session_state.configuracion['tam_lote'],
                step=1,
                help="Cantidad total de unidades en el lote"
            )
        
        with col3:
            aql = st.selectbox(
                "NCA (AQL)",
                PlanMuestreo.AQL_KEYS,
                index=PlanMuestreo.AQL_KEYS.index(st.session_state.configuracion['aql']),
                help="Nivel de Calidad Aceptable"
            )
    
    # Botón para calcular plan
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📊 Calcular Plan", type="primary", use_container_width=True):
            with st.spinner("Calculando plan de muestreo..."):
                letra = PlanMuestreo.obtener_letra(nivel, tam_lote)
                if letra:
                    plan = PlanMuestreo.obtener_plan(letra, aql)
                    if plan:
                        st.session_state.plan_calculado = True
                        st.session_state.n = plan['n']
                        st.session_state.k = plan['k']
                        st.session_state.configuracion.update({
                            'nivel': nivel,
                            'tam_lote': tam_lote,
                            'aql': aql,
                            'letra': letra
                        })
                        st.session_state.pesos = [0.0] * plan['n']
                        st.success(f"✅ Plan calculado: Letra {letra}, n={plan['n']}, k={plan['k'] if plan['k'] else 'N/A'}")
                    else:
                        st.error("No se pudo obtener el plan para esta combinación")
                else:
                    st.error("Tamaño de lote fuera de rango")
    
    # Mostrar resumen si hay plan calculado
    if st.session_state.plan_calculado:
        st.info(f"""
        **Resumen del Plan:** 
        - **Letra:** {st.session_state.configuracion.get('letra', 'N/A')}
        - **Tamaño de muestra:** {st.session_state.n}
        - **Valor M (k):** {st.session_state.k if st.session_state.k else "No disponible"}
        - **Nivel AQL:** {st.session_state.configuracion['aql']}%
        """)

def mostrar_panel_especificaciones():
    """Muestra el panel de especificaciones técnicas"""
    st.markdown("### 🎯 Especificaciones Técnicas")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nominal = st.number_input(
                "Peso Nominal",
                value=st.session_state.configuracion['nominal'],
                step=0.1,
                format="%.2f",
                help="Peso objetivo del ovillo"
            )
        
        with col2:
            lim_inf = st.number_input(
                "Límite Inferior",
                value=st.session_state.configuracion['lim_inf'],
                step=0.1,
                format="%.2f",
                help="Peso mínimo aceptable"
            )
        
        with col3:
            lim_sup = st.number_input(
                "Límite Superior",
                value=st.session_state.configuracion['lim_sup'],
                step=0.1,
                format="%.2f",
                help="Peso máximo aceptable"
            )
    
    # Validación de especificaciones
    if lim_inf >= lim_sup:
        st.warning("⚠️ El límite inferior debe ser menor al límite superior")
    if nominal < lim_inf or nominal > lim_sup:
        st.warning("⚠️ El peso nominal debe estar entre los límites")
    
    st.session_state.configuracion.update({
        'nominal': nominal,
        'lim_inf': lim_inf,
        'lim_sup': lim_sup
    })
    
    # Visualización de tolerancia
    tolerancia = lim_sup - lim_inf
    st.caption(f"📏 Rango de tolerancia: {tolerancia:.2f}")

def mostrar_panel_pesos():
    """Muestra el panel para ingreso de pesos"""
    if not st.session_state.plan_calculado:
        st.warning("Primero configure el plan de muestreo")
        return
    
    n = st.session_state.n
    
    st.markdown(f"### ⚖️ Registro de Pesos (n={n})")
    
    # Opciones de entrada
    tab1, tab2, tab3 = st.tabs(["📝 Entrada Manual", "🎲 Generación Automática", "📁 Carga Masiva"])
    
    with tab1:
        # Entrada manual organizada
        st.markdown("Ingrese los pesos individualmente:")
        
        pesos_manual = []
        cols_per_row = min(5, n)
        cols = st.columns(cols_per_row)
        
        for i in range(n):
            with cols[i % cols_per_row]:
                key = f"peso_manual_{i}"
                valor = st.number_input(
                    f"P{i+1}",
                    key=key,
                    value=float(st.session_state.pesos[i] if i < len(st.session_state.pesos) else 0.0),
                    step=0.01,
                    format="%.2f",
                    label_visibility="visible"
                )
                pesos_manual.append(valor)
        
        if st.button("💾 Guardar Pesos Manuales", type="secondary"):
            st.session_state.pesos = pesos_manual
            st.success(f"✅ {len(pesos_manual)} pesos guardados")
    
    with tab2:
        # Generación automática
        st.markdown("Configure la generación automática de pesos:")
        
        col1, col2 = st.columns(2)
        with col1:
            sigma = st.slider(
                "Variabilidad (σ)",
                min_value=0.1,
                max_value=5.0,
                value=0.5,
                step=0.1,
                help="Desviación estándar para la generación"
            )
        
        with col2:
            if st.button("🎯 Generar Pesos Aleatorios", use_container_width=True):
                pesos_gen = generar_pesos_aleatorios(
                    n,
                    st.session_state.configuracion['nominal'],
                    sigma,
                    st.session_state.configuracion['lim_inf'],
                    st.session_state.configuracion['lim_sup']
                )
                st.session_state.pesos = pesos_gen
                st.success(f"✅ {len(pesos_gen)} pesos generados")
                
                # Mostrar previsualización
                st.dataframe(
                    pd.DataFrame({
                        'Muestra': range(1, n+1),
                        'Peso': pesos_gen,
                        'Desviación': [f"{(p - st.session_state.configuracion['nominal']):+.2f}" for p in pesos_gen]
                    }),
                    use_container_width=True,
                    height=200
                )
    
    with tab3:
        # Carga masiva
        st.markdown("Ingrese pesos separados por comas, espacios o saltos de línea:")
        
        texto_pesos = st.text_area(
            "Pesos (formato libre)",
            value=", ".join([f"{p:.2f}" for p in st.session_state.pesos]),
            height=100,
            help="Ejemplo: 100.5, 99.8, 101.2, 100.0"
        )
        
        if st.button("📥 Procesar Pesos", use_container_width=True):
            try:
                # Parsear pesos del texto
                pesos_texto = []
                for valor in texto_pesos.replace('\n', ',').replace(';', ',').split(','):
                    valor_limpio = valor.strip()
                    if valor_limpio:
                        pesos_texto.append(float(valor_limpio))
                
                if len(pesos_texto) == n:
                    st.session_state.pesos = pesos_texto
                    st.success(f"✅ {len(pesos_texto)} pesos procesados")
                else:
                    st.warning(f"Se esperaban {n} pesos, pero se encontraron {len(pesos_texto)}")
            except ValueError:
                st.error("Formato inválido. Asegúrese de ingresar solo números.")

def mostrar_panel_analisis():
    """Muestra el panel de análisis estadístico"""
    if not st.session_state.pesos or all(p == 0 for p in st.session_state.pesos):
        st.info("Ingrese pesos para realizar el análisis")
        return
    
    if st.button("📈 Realizar Análisis Estadístico", type="primary", use_container_width=True):
        with st.spinner("Calculando estadísticas..."):
            # Calcular estadísticas
            stats = calcular_estadisticas(
                st.session_state.pesos,
                st.session_state.configuracion['lim_inf'],
                st.session_state.configuracion['lim_sup']
            )
            
            if stats['estado'] == 'error':
                st.error(stats['mensaje'])
                return
            
            # Determinar decisión
            k = st.session_state.k
            if k is None:
                decision = "Indeterminado (k no definido)"
                color_decision = COLORES['warning']
                icono = "⚠️"
            elif stats['p_total'] <= k:
                decision = f"ACEPTAR (p={stats['p_total']:.2f}% ≤ k={k})"
                color_decision = COLORES['success']
                icono = "✅"
            else:
                decision = f"RECHAZAR (p={stats['p_total']:.2f}% > k={k})"
                color_decision = COLORES['danger']
                icono = "❌"
            
            # Guardar en histórico
            analisis = {
                'timestamp': datetime.now(),
                'stats': stats,
                'decision': decision,
                'config': st.session_state.configuracion.copy()
            }
            st.session_state.historico_analisis.append(analisis)
            st.session_state.ultimo_analisis = analisis
            
            # Mostrar resultados
            st.markdown("### 📊 Resultados del Análisis")
            
            # Métricas principales
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Media", f"{stats['media']:.3f}")
            with col2:
                st.metric("Desviación", f"{stats['desviacion']:.3f}")
            with col3:
                st.metric("p Total", f"{stats['p_total']:.3f}%")
            with col4:
                st.metric("Valor k", f"{k if k else 'N/A'}")
            
            # Decision
            st.markdown(f"""
            <div style="
                background-color: {color_decision}20;
                border-left: 5px solid {color_decision};
                padding: 1rem;
                border-radius: 5px;
                margin: 1rem 0;
            ">
                <h4 style="margin: 0; color: {color_decision};">{icono} {decision}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Gráfico interactivo
            st.plotly_chart(
                crear_grafico_interactivo(
                    st.session_state.pesos,
                    st.session_state.configuracion['nominal'],
                    st.session_state.configuracion['lim_inf'],
                    st.session_state.configuracion['lim_sup'],
                    stats['media']
                ),
                use_container_width=True
            )
            
            # Tabla detallada
            df_detalle = pd.DataFrame({
                'Estadístico': ['n', 'Media', 'Desviación Estándar', 'Z (Inferior)', 'Z (Superior)', 
                              'p Inferior', 'p Superior', 'p Total', 'Valor k', 'Decisión'],
                'Valor': [
                    stats['n'],
                    f"{stats['media']:.4f}",
                    f"{stats['desviacion']:.4f}",
                    f"{stats['Z_EI']:.4f}" if stats['Z_EI'] else 'N/A',
                    f"{stats['Z_ES']:.4f}" if stats['Z_ES'] else 'N/A',
                    f"{stats['pi']:.4f}%",
                    f"{stats['ps']:.4f}%",
                    f"{stats['p_total']:.4f}%",
                    f"{k if k else 'N/A'}",
                    decision
                ]
            })
            
            st.dataframe(
                df_detalle,
                use_container_width=True,
                hide_index=True
            )
            
            # Exportar opciones
            col_exp1, col_exp2, col_exp3 = st.columns(3)
            
            with col_exp1:
                # Exportar CSV
                csv = df_detalle.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Resultados (CSV)",
                    data=csv,
                    file_name=f"analisis_nawi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_exp2:
                # Exportar datos brutos
                df_pesos = pd.DataFrame({
                    'Muestra': range(1, len(st.session_state.pesos) + 1),
                    'Peso': st.session_state.pesos
                })
                csv_pesos = df_pesos.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Exportar Pesos (CSV)",
                    data=csv_pesos,
                    file_name=f"pesos_nawi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_exp3:
                # Imprimir reporte
                if st.button("🖨️ Generar Reporte PDF", use_container_width=True):
                    st.info("Función de generación de PDF en desarrollo")

def mostrar_sidebar():
    """Muestra la barra lateral con herramientas adicionales"""
    with st.sidebar:
        st.markdown("### 🛠️ Herramientas")
        
        # Historial de análisis
        if st.session_state.historico_analisis:
            st.markdown("#### 📚 Historial")
            for i, analisis in enumerate(reversed(st.session_state.historico_analisis[-5:])):
                with st.expander(f"Análisis {i+1} - {analisis['timestamp'].strftime('%H:%M')}"):
                    st.write(f"**Decisión:** {analisis['decision']}")
                    st.write(f"**p Total:** {analisis['stats']['p_total']:.2f}%")
        
        # Calculadora rápida
        st.markdown("#### 🧮 Calculadora Rápida")
        peso_calc = st.number_input("Peso a evaluar", value=100.0)
        if st.button("Calcular Z-score"):
            nominal = st.session_state.configuracion['nominal']
            desv = (st.session_state.configuracion['lim_sup'] - st.session_state.configuracion['lim_inf']) / 6
            if desv > 0:
                z_score = (peso_calc - nominal) / desv
                st.info(f"Z-score: {z_score:.2f}")
        
        # Información del sistema
        st.markdown("---")
        st.markdown("#### ℹ️ Información")
        st.caption(f"Versión: 2.0.0")
        st.caption(f"Análisis realizados: {len(st.session_state.historico_analisis)}")
        
        # Botón de reinicio
        if st.button("🔄 Reiniciar Todo", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

# ============================================================
# APLICACIÓN PRINCIPAL
# ============================================================
def main():
    """Función principal de la aplicación"""
    # Inicializar estado
    inicializar_estado()
    
    # Mostrar interfaz
    mostrar_header()
    
    # Layout principal
    col_main, col_side = st.columns([4, 1])
    
    with col_main:
        # Pestañas principales
        tab_config, tab_datos, tab_analisis = st.tabs([
            "⚙️ Configuración",
            "📊 Datos",
            "📈 Análisis"
        ])
        
        with tab_config:
            mostrar_panel_configuracion()
            st.markdown("---")
            mostrar_panel_especificaciones()
        
        with tab_datos:
            mostrar_panel_pesos()
        
        with tab_analisis:
            mostrar_panel_analisis()
    
    with col_side:
        mostrar_sidebar()
    
    # Pie de página
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: {COLORES['dark']}; padding: 1rem;">
        <small>
            <strong>NAWI KUYCHI</strong> · Sistema de Control de Calidad · 
            <a href="mailto:soporte@nawikuychi.com" style="color: {COLORES['primary']};">Soporte</a> · 
            v2.0.0 © 2024
        </small>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    main()