import math
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
)

# Configuración de colores
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
# COMPONENTES DE INTERFAZ - HEADER MEJORADO
# ============================================================
def mostrar_header():
    """Muestra el encabezado con logo y título"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("""
        <div style="text-align: center;">
            <svg width="120" height="120" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" stroke="#E9C46A" stroke-width="4" fill="none"/>
                <path d="M25 40 C35 30,45 25,60 35" stroke="#2A9D8F" stroke-width="2" fill="none"/>
                <path d="M30 50 C40 40,50 35,65 45" stroke="#2A9D8F" stroke-width="2" fill="none"/>
                <path d="M35 60 C45 50,55 45,70 55" stroke="#E76F51" stroke-width="2" fill="none"/>
                <path d="M30 35 C45 30,55 35,65 45" stroke="#E76F51" stroke-width="2" fill="none"/>
                <path d="M40 70 C50 60,60 55,75 65" stroke="#E9C46A" stroke-width="2" fill="none"/>
                <path d="M40 60 C55 55,70 40,85 35" stroke="#2A9D8F" stroke-width="3" fill="none"/>
                <path d="M45 65 C60 60,75 50,90 45" stroke="#E9C46A" stroke-width="3" fill="none"/>
                <path d="M50 70 C65 65,80 60,95 55" stroke="#E76F51" stroke-width="3" fill="none"/>
            </svg>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="padding-left: 20px;">
            <h1 style="color: {COLORES['primary']}; margin-bottom: 5px; font-size: 2.8em;">NAWI KUYCHI</h1>
            <h3 style="color: {COLORES['secondary']}; margin-top: 0; margin-bottom: 10px;">
                Sistema de Muestreo MIL-STD-414
            </h3>
            <p style="color: {COLORES['dark']}; font-size: 1.1em;">
                <strong>Medimos para crear valor</strong> · Control de calidad en pesado de ovillos
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

# ============================================================
# TABLAS DE DATOS MIL-STD-414
# ============================================================
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
    "B": {"muestra": 3, "0.04": None, "0.065": None, "0.1": None, "0.15": None,
          "0.25": None, "0.4": None, "0.65": None, "1": None, "1.5": None,
          "2.5": 7.59, "4": 18.86, "6.5": 26.94, "10": 33.69, "15": 40.47},
    "C": {"muestra": 4, "0.04": None, "0.065": None, "0.1": None, "0.15": None,
          "0.25": None, "0.4": None, "0.65": None, "1": 1.53, "1.5": 5.5,
          "2.5": 10.92, "4": 16.45, "6.5": 22.86, "10": 29.45, "15": 36.9},
    "D": {"muestra": 5, "0.04": None, "0.065": None, "0.1": None, "0.15": None,
          "0.25": None, "0.4": None, "0.65": None, "1": 1.33, "1.5": 5.83,
          "2.5": 9.8, "4": 14.39, "6.5": 20.19, "10": 26.56, "15": 33.99},
    "E": {"muestra": 7, "0.04": None, "0.065": None, "0.1": None, "0.15": None,
          "0.25": 0.422, "0.4": 1.06, "0.65": 2.14, "1": 3.55, "1.5": 5.35,
          "2.5": 8.4, "4": 12.2, "6.5": 17.35, "10": 23.29, "15": 30.5},
    "F": {"muestra": 10, "0.04": None, "0.065": None, "0.1": None,
          "0.15": 0.349, "0.25": 0.716, "0.4": 1.3, "0.65": 2.17, "1": 3.26,
          "1.5": 4.77, "2.5": 7.29, "4": 10.54, "6.5": 15.17, "10": 20.74, "15": 27.57},
    "G": {"muestra": 15, "0.04": 0.099, "0.065": 0.099, "0.1": 0.312,
          "0.15": 0.503, "0.25": 0.818, "0.4": 1.31, "0.65": 2.11, "1": 3.05,
          "1.5": 4.31, "2.5": 6.56, "4": 9.46, "6.5": 13.71, "10": 18.94, "15": 25.61},
    "H": {"muestra": 20, "0.04": 0.135, "0.065": 0.135, "0.1": 0.365,
          "0.15": 0.544, "0.25": 0.846, "0.4": 1.29, "0.65": 2.05, "1": 2.95,
          "1.5": 4.09, "2.5": 6.17, "4": 8.92, "6.5": 12.99, "10": 18.03, "15": 24.53},
    "I": {"muestra": 25, "0.04": 0.155, "0.065": 0.156, "0.1": 0.38,
          "0.15": 0.551, "0.25": 0.877, "0.4": 1.29, "0.65": 2, "1": 2.86,
          "1.5": 3.97, "2.5": 5.97, "4": 8.63, "6.5": 12.57, "10": 17.51, "15": 23.97},
    "J": {"muestra": 30, "0.04": 0.179, "0.065": 0.179, "0.1": 0.413,
          "0.15": 0.581, "0.25": 0.879, "0.4": 1.29, "0.65": 1.98, "1": 2.83,
          "1.5": 3.91, "2.5": 5.86, "4": 8.47, "6.5": 12.36, "10": 17.24, "15": 23.58},
    "K": {"muestra": 35, "0.04": 0.17, "0.065": 0.17, "0.1": 0.388,
          "0.15": 0.535, "0.25": 0.847, "0.4": 1.23, "0.65": 1.87, "1": 2.68,
          "1.5": 3.7, "2.5": 5.57, "4": 8.1, "6.5": 11.87, "10": 16.65, "15": 22.91},
    "L": {"muestra": 40, "0.04": 0.179, "0.065": 0.179, "0.1": 0.401,
          "0.15": 0.566, "0.25": 0.873, "0.4": 1.26, "0.65": 1.88, "1": 2.71,
          "1.5": 3.72, "2.5": 5.58, "4": 8.09, "6.5": 11.85, "10": 16.61, "15": 22.86},
    "M": {"muestra": 50, "0.04": 0.163, "0.065": 0.163, "0.1": 0.363,
          "0.15": 0.503, "0.25": 0.789, "0.4": 1.17, "0.65": 1.71, "1": 2.49,
          "1.5": 3.45, "2.5": 5.2, "4": 7.61, "6.5": 11.23, "10": 15.87, "15": 22},
    "N": {"muestra": 75, "0.04": 1.147, "0.065": 0.147, "0.1": 0.33,
          "0.15": 0.467, "0.25": 0.72, "0.4": 1.07, "0.65": 1.6, "1": 2.29,
          "1.5": 3.2, "2.5": 4.87, "4": 7.15, "6.5": 10.63, "10": 15.13, "15": 21.11},
    "O": {"muestra": 100, "0.04": 0.145, "0.065": 0.145, "0.1": 0.317,
          "0.15": 0.447, "0.25": 0.689, "0.4": 1.02, "0.65": 1.53, "1": 2.2,
          "1.5": 3.07, "2.5": 4.69, "4": 6.91, "6.5": 10.32, "10": 14.75, "15": 20.66},
    "P": {"muestra": 150, "0.04": 0.134, "0.065": 0.134, "0.1": 0.293,
          "0.15": 0.413, "0.25": 0.638, "0.4": 0.949, "0.65": 1.43, "1": 2.05,
          "1.5": 2.89, "2.5": 4.43, "4": 6.57, "6.5": 9.88, "10": 14.2, "15": 20.02},
    "Q": {"muestra": 200, "0.04": 0.135, "0.065": 0.135, "0.1": 0.294,
          "0.15": 0.414, "0.25": 0.637, "0.4": 0.945, "0.65": 1.42, "1": 2.04,
          "1.5": 2.87, "2.5": 4.4, "4": 6.53, "6.5": 9.81, "10": 14.12, "15": 19.92}
}

# ============================================================
# FUNCIONES UTILITARIAS
# ============================================================
def normal_cdf(z: float) -> float:
    """Función de distribución acumulada de N(0,1)"""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))

def obtener_letra_muestreo(nivel, tam_lote):
    """Obtiene la letra del plan según nivel y tamaño de lote"""
    for minimo, maximo, letras in RANGOS_LOTE:
        if minimo <= tam_lote <= maximo:
            return letras[nivel]
    return None

def generar_pesos_aleatorios(n, nominal, lim_inf, lim_sup):
    """Genera pesos aleatorios con distribución normal"""
    if lim_sup > lim_inf:
        sigma = (lim_sup - lim_inf) / 6.0
    else:
        sigma = max(0.1, abs(nominal) * 0.01)
    
    pesos = []
    for _ in range(n):
        valor = random.gauss(nominal, sigma)
        # Asegurarnos de que el valor sea razonable
        valor = max(nominal - 3*sigma, min(nominal + 3*sigma, valor))
        pesos.append(round(valor, 2))
    
    return pesos

def crear_grafico_matplotlib(pesos, nominal, lim_inf, lim_sup, media, desviacion):
    """Crea un gráfico de calidad profesional con Matplotlib"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Gráfico 1: Distribución de puntos
    n = len(pesos)
    x_positions = np.arange(1, n + 1)
    
    # Colores según posición relativa a límites
    colors = []
    for peso in pesos:
        if peso < lim_inf:
            colors.append(COLORES['danger'])
        elif peso > lim_sup:
            colors.append(COLORES['warning'])
        else:
            colors.append(COLORES['success'])
    
    ax1.scatter(x_positions, pesos, c=colors, s=100, edgecolors='black', alpha=0.7)
    
    # Líneas de referencia
    ax1.axhline(y=nominal, color=COLORES['accent1'], linestyle='--', linewidth=2, label='Nominal')
    ax1.axhline(y=lim_inf, color=COLORES['danger'], linestyle='-', linewidth=1.5, label='Lím. Inferior')
    ax1.axhline(y=lim_sup, color=COLORES['danger'], linestyle='-', linewidth=1.5, label='Lím. Superior')
    ax1.axhline(y=media, color=COLORES['primary'], linestyle='-', linewidth=2, label='Media')
    
    # Área de especificación
    ax1.fill_between([0, n+1], lim_inf, lim_sup, alpha=0.1, color=COLORES['accent1'])
    
    # Configuración del gráfico 1
    ax1.set_title('Distribución de Pesos de la Muestra', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlabel('Número de Muestra', fontsize=12)
    ax1.set_ylabel('Peso', fontsize=12)
    ax1.set_xticks(x_positions)
    ax1.set_xlim(0.5, n + 0.5)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')
    
    # Añadir etiquetas de valores
    for i, peso in enumerate(pesos, 1):
        ax1.annotate(f'{peso:.2f}', (i, peso), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9, fontweight='bold')
    
    # Gráfico 2: Histograma y distribución normal
    if n > 1 and desviacion > 0:
        # Histograma
        ax2.hist(pesos, bins=min(10, n), alpha=0.7, color=COLORES['accent1'], 
                edgecolor='black', density=True, label='Distribución Muestral')
        
        # Curva normal teórica
        x_min = min(pesos) - desviacion
        x_max = max(pesos) + desviacion
        x = np.linspace(x_min, x_max, 100)
        y = (1/(desviacion * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - media)/desviacion)**2)
        ax2.plot(x, y, color=COLORES['primary'], linewidth=2, label='Distribución Normal')
        
        # Líneas de límites en histograma
        ax2.axvline(x=lim_inf, color=COLORES['danger'], linestyle='--', linewidth=2, label='Límites')
        ax2.axvline(x=lim_sup, color=COLORES['danger'], linestyle='--', linewidth=2)
        ax2.axvline(x=nominal, color=COLORES['accent1'], linestyle='-', linewidth=2, label='Nominal')
        
        ax2.set_title('Distribución de Frecuencias', fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel('Peso', fontsize=12)
        ax2.set_ylabel('Densidad', fontsize=12)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    else:
        ax2.text(0.5, 0.5, 'No hay suficientes datos\npara el histograma', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=12)
        ax2.set_title('Distribución de Frecuencias', fontsize=14, fontweight='bold', pad=15)
    
    plt.tight_layout()
    return fig

# ============================================================
# INICIALIZACIÓN DEL ESTADO
# ============================================================
def inicializar_estado():
    """Inicializa el estado de la sesión"""
    if 'plan_calculado' not in st.session_state:
        st.session_state.plan_calculado = False
    if 'n' not in st.session_state:
        st.session_state.n = 0
    if 'k' not in st.session_state:
        st.session_state.k = None
    if 'pesos' not in st.session_state:
        st.session_state.pesos = []
    if 'pesos_input' not in st.session_state:
        st.session_state.pesos_input = {}
    if 'analisis_realizado' not in st.session_state:
        st.session_state.analisis_realizado = False
    if 'resultados' not in st.session_state:
        st.session_state.resultados = None

# ============================================================
# COMPONENTES PRINCIPALES
# ============================================================
def mostrar_panel_configuracion():
    """Muestra el panel de configuración del plan"""
    st.markdown("### ⚙️ Configuración del Plan de Muestreo")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nivel = st.selectbox(
                "Nivel de Inspección",
                ["I", "II", "III", "IV", "V"],
                index=1,
                help="Nivel de rigurosidad de la inspección"
            )
        
        with col2:
            tam_lote = st.number_input(
                "Tamaño del Lote",
                min_value=3,
                value=1000,
                step=1,
                help="Cantidad total de unidades en el lote"
            )
        
        with col3:
            aql = st.selectbox(
                "NCA (AQL)",
                AQL_KEYS,
                index=AQL_KEYS.index("1"),
                help="Nivel de Calidad Aceptable"
            )
    
    # Botón para calcular plan
    if st.button("📊 Calcular Plan de Muestreo", type="primary", use_container_width=True):
        with st.spinner("Calculando plan de muestreo..."):
            letra = obtener_letra_muestreo(nivel, tam_lote)
            if letra is None:
                st.error("❌ No se encontró un rango de lote para esos datos.")
            else:
                fila = TABLA_K.get(letra)
                if fila is None:
                    st.error(f"❌ Letra {letra} no está definida en la tabla.")
                else:
                    n = fila["muestra"]
                    k = fila.get(aql)
                    
                    st.session_state.plan_calculado = True
                    st.session_state.n = n
                    st.session_state.k = k
                    
                    # Reiniciar pesos
                    st.session_state.pesos = [0.0] * n
                    st.session_state.pesos_input = {f"peso_{i}": 0.0 for i in range(n)}
                    st.session_state.analisis_realizado = False
                    st.session_state.resultados = None
                    
                    st.success(f"✅ Plan calculado exitosamente!")
                    
                    # Mostrar resumen
                    st.markdown(f"""
                    **Resumen del Plan:**
                    - **Letra del plan:** {letra}
                    - **Tamaño de muestra (n):** {n}
                    - **Valor M (k):** {k if k is not None else "No disponible"}
                    - **NCA (AQL):** {aql}%
                    - **Nivel de inspección:** {nivel}
                    """)

def mostrar_panel_especificaciones():
    """Muestra el panel de especificaciones técnicas"""
    st.markdown("### 🎯 Especificaciones Técnicas")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            nominal = st.number_input(
                "Peso Nominal",
                value=100.0,
                step=0.01,
                format="%.2f",
                help="Peso objetivo del ovillo"
            )
        
        with col2:
            lim_inf = st.number_input(
                "Límite Inferior",
                value=98.0,
                step=0.01,
                format="%.2f",
                help="Peso mínimo aceptable"
            )
        
        with col3:
            lim_sup = st.number_input(
                "Límite Superior",
                value=102.0,
                step=0.01,
                format="%.2f",
                help="Peso máximo aceptable"
            )
    
    return nominal, lim_inf, lim_sup

def mostrar_panel_pesos(nominal, lim_inf, lim_sup):
    """Muestra el panel para ingreso de pesos"""
    if not st.session_state.plan_calculado:
        st.warning("⚠️ Primero calcule el plan de muestreo para continuar")
        return
    
    n = st.session_state.n
    
    st.markdown(f"### ⚖️ Registro de Pesos (n={n})")
    
    # Dividir en pestañas para diferentes métodos de entrada
    tab1, tab2 = st.tabs(["📝 Entrada Manual", "🎲 Generación Automática"])
    
    with tab1:
        # Entrada manual
        st.markdown("Ingrese los pesos individualmente:")
        
        # Organizar en columnas dinámicas
        num_cols = 4 if n > 8 else (3 if n > 4 else 2)
        cols = st.columns(num_cols)
        
        pesos_manual = []
        pesos_actualizados = False
        
        for i in range(n):
            col_idx = i % num_cols
            with cols[col_idx]:
                key = f"peso_manual_{i}"
                
                # Obtener valor actual o usar 0.0
                valor_actual = st.session_state.pesos[i] if i < len(st.session_state.pesos) else 0.0
                
                nuevo_valor = st.number_input(
                    f"P{i+1}",
                    key=key,
                    value=float(valor_actual),
                    step=0.01,
                    format="%.2f",
                    label_visibility="visible"
                )
                
                pesos_manual.append(nuevo_valor)
                
                # Verificar si el valor cambió
                if nuevo_valor != valor_actual:
                    pesos_actualizados = True
        
        # Botón para guardar pesos manuales
        if st.button("💾 Guardar Pesos Manuales", use_container_width=True):
            st.session_state.pesos = pesos_manual
            st.success(f"✅ {len(pesos_manual)} pesos guardados exitosamente")
            st.rerun()
    
    with tab2:
        # Generación automática
        st.markdown("Configure la generación de pesos aleatorios:")
        
        col1, col2 = st.columns(2)
        with col1:
            sigma = st.slider(
                "Variabilidad (σ)",
                min_value=0.1,
                max_value=2.0,
                value=0.5,
                step=0.1,
                help="Desviación estándar para la generación"
            )
        
        with col2:
            if st.button("🎯 Generar Pesos Aleatorios", use_container_width=True):
                # CORRECCIÓN CRÍTICA: Generar y actualizar correctamente
                nuevos_pesos = generar_pesos_aleatorios(n, nominal, lim_inf, lim_sup)
                st.session_state.pesos = nuevos_pesos
                
                # Actualizar también los inputs individuales
                for i in range(n):
                    key = f"peso_manual_{i}"
                    if key in st.session_state:
                        st.session_state[key] = nuevos_pesos[i]
                
                st.success(f"✅ {n} pesos aleatorios generados exitosamente!")
                
                # Mostrar vista previa
                df_preview = pd.DataFrame({
                    'Muestra': range(1, n+1),
                    'Peso (g)': nuevos_pesos,
                    'Desviación': [f"{p - nominal:+.2f}" for p in nuevos_pesos]
                })
                
                st.dataframe(
                    df_preview,
                    use_container_width=True,
                    height=min(300, n * 35)
                )
                
                st.rerun()
    
    # Mostrar resumen de pesos actuales
    if st.session_state.pesos and any(p != 0 for p in st.session_state.pesos):
        st.markdown("---")
        st.markdown("**📋 Resumen de Pesos Ingresados:**")
        
        df_resumen = pd.DataFrame({
            'Estadístico': ['Cantidad', 'Mínimo', 'Máximo', 'Promedio', 'Rango'],
            'Valor': [
                f"{n} muestras",
                f"{min(st.session_state.pesos):.2f}",
                f"{max(st.session_state.pesos):.2f}",
                f"{np.mean(st.session_state.pesos):.2f}",
                f"{max(st.session_state.pesos) - min(st.session_state.pesos):.2f}"
            ]
        })
        
        st.table(df_resumen)

def realizar_analisis(pesos, nominal, lim_inf, lim_sup, k):
    """Realiza el análisis estadístico completo"""
    n = len(pesos)
    
    # Verificar datos válidos
    if n < 2:
        return {
            'error': True,
            'mensaje': 'Se requieren al menos 2 pesos para el análisis'
        }
    
    if all(p == 0 for p in pesos):
        return {
            'error': True,
            'mensaje': 'Todos los pesos son cero. Ingrese valores válidos.'
        }
    
    # Calcular estadísticas básicas
    X_bar = np.mean(pesos)
    S = np.std(pesos, ddof=1)
    
    if S == 0:
        return {
            'error': True,
            'mensaje': 'La desviación estándar es cero (sin variación)'
        }
    
    # Calcular índices Z
    Z_ES = (lim_sup - X_bar) / S
    Z_EI = (X_bar - lim_inf) / S
    
    # Calcular porcentajes fuera de especificación
    pi = (1 - normal_cdf(Z_EI)) * 100
    ps = (1 - normal_cdf(Z_ES)) * 100
    p_total = pi + ps
    
    # Determinar decisión
    if k is None:
        decision = "Indeterminado (valor k no definido)"
        color = COLORES['warning']
        icono = "⚠️"
    elif p_total <= k:
        decision = f"ACEPTAR EL LOTE (p={p_total:.2f}% ≤ k={k})"
        color = COLORES['success']
        icono = "✅"
    else:
        decision = f"RECHAZAR EL LOTE (p={p_total:.2f}% > k={k})"
        color = COLORES['danger']
        icono = "❌"
    
    return {
        'error': False,
        'n': n,
        'media': X_bar,
        'desviacion': S,
        'Z_ES': Z_ES,
        'Z_EI': Z_EI,
        'pi': pi,
        'ps': ps,
        'p_total': p_total,
        'k': k,
        'decision': decision,
        'color': color,
        'icono': icono
    }

def mostrar_panel_analisis(nominal, lim_inf, lim_sup):
    """Muestra el panel de análisis estadístico"""
    if not st.session_state.pesos or all(p == 0 for p in st.session_state.pesos):
        st.info("📝 Ingrese pesos en la pestaña anterior para realizar el análisis")
        return
    
    st.markdown("### 📈 Análisis Estadístico")
    
    # Botón para realizar análisis
    if st.button("🔍 Realizar Análisis Completo", type="primary", use_container_width=True):
        with st.spinner("Calculando estadísticas..."):
            resultados = realizar_analisis(
                st.session_state.pesos,
                nominal,
                lim_inf,
                lim_sup,
                st.session_state.k
            )
            
            st.session_state.resultados = resultados
            st.session_state.analisis_realizado = True
    
    # Mostrar resultados si están disponibles
    if st.session_state.analisis_realizado and st.session_state.resultados:
        resultados = st.session_state.resultados
        
        if resultados['error']:
            st.error(f"❌ {resultados['mensaje']}")
            return
        
        # Mostrar decisión destacada
        st.markdown(f"""
        <div style="
            background-color: {resultados['color']}20;
            border-left: 5px solid {resultados['color']};
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        ">
            <h3 style="color: {resultados['color']}; margin: 0;">
                {resultados['icono']} {resultados['decision']}
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tamaño Muestra", resultados['n'])
        
        with col2:
            st.metric("Media", f"{resultados['media']:.3f}")
        
        with col3:
            st.metric("Desviación", f"{resultados['desviacion']:.3f}")
        
        with col4:
            k_val = resultados['k'] if resultados['k'] else "N/A"
            st.metric("Valor k", f"{k_val}")
        
        # Estadísticas detalladas
        st.markdown("---")
        st.markdown("#### 📊 Estadísticas Detalladas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Índices Z:**
            - Z Inferior: **{resultados['Z_EI']:.4f}**
            - Z Superior: **{resultados['Z_ES']:.4f}**
            
            **Porcentajes fuera de especificación:**
            - p Inferior: **{resultados['pi']:.3f}%**
            - p Superior: **{resultados['ps']:.3f}%**
            """)
        
        with col2:
            st.markdown(f"""
            **Cálculos de aceptación:**
            - p Total: **{resultados['p_total']:.3f}%**
            - Valor k: **{resultados['k'] if resultados['k'] else 'No definido'}**
            - Diferencia: **{resultados['p_total'] - resultados['k']:.3f}%** 
              {"(a favor)" if resultados['p_total'] <= resultados['k'] else "(en contra)"}
            """)
        
        # Gráficos
        st.markdown("---")
        st.markdown("#### 📈 Visualización de Datos")
        
        fig = crear_grafico_matplotlib(
            st.session_state.pesos,
            nominal,
            lim_inf,
            lim_sup,
            resultados['media'],
            resultados['desviacion']
        )
        
        st.pyplot(fig)
        
        # Opciones de exportación
        st.markdown("---")
        st.markdown("#### 💾 Exportar Resultados")
        
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Exportar CSV de datos
            df_datos = pd.DataFrame({
                'Muestra': range(1, len(st.session_state.pesos) + 1),
                'Peso': st.session_state.pesos,
                'Desviacion_Media': [p - resultados['media'] for p in st.session_state.pesos]
            })
            
            csv = df_datos.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Datos (CSV)",
                data=csv,
                file_name=f"datos_nawi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_exp2:
            # Exportar resumen
            df_resumen = pd.DataFrame({
                'Parámetro': ['Decisión', 'p Total (%)', 'Valor k', 'Media', 'Desviación', 'Z Inferior', 'Z Superior'],
                'Valor': [
                    resultados['decision'],
                    f"{resultados['p_total']:.3f}",
                    f"{resultados['k'] if resultados['k'] else 'N/A'}",
                    f"{resultados['media']:.3f}",
                    f"{resultados['desviacion']:.3f}",
                    f"{resultados['Z_EI']:.3f}",
                    f"{resultados['Z_ES']:.3f}"
                ]
            })
            
            csv_resumen = df_resumen.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Descargar Resumen (CSV)",
                data=csv_resumen,
                file_name=f"resumen_nawi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ============================================================
# APLICACIÓN PRINCIPAL
# ============================================================
def main():
    """Función principal de la aplicación"""
    # Inicializar estado
    inicializar_estado()
    
    # Mostrar header
    mostrar_header()
    
    # Panel de configuración
    with st.expander("⚙️ CONFIGURACIÓN DEL PLAN", expanded=True):
        mostrar_panel_configuracion()
    
    st.markdown("---")
    
    # Panel de especificaciones técnicas
    with st.expander("🎯 ESPECIFICACIONES TÉCNICAS", expanded=True):
        nominal, lim_inf, lim_sup = mostrar_panel_especificaciones()
    
    st.markdown("---")
    
    # Panel de ingreso de datos
    if st.session_state.plan_calculado:
        with st.expander(f"⚖️ REGISTRO DE PESOS (n={st.session_state.n})", expanded=True):
            mostrar_panel_pesos(nominal, lim_inf, lim_sup)
        
        st.markdown("---")
        
        # Panel de análisis
        with st.expander("📈 ANÁLISIS ESTADÍSTICO", expanded=True):
            mostrar_panel_analisis(nominal, lim_inf, lim_sup)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: {COLORES['dark']}; padding: 20px;">
        <p style="margin: 0;">
            <strong>NAWI KUYCHI</strong> · Sistema de Control de Calidad MIL-STD-414
        </p>
        <p style="margin: 5px 0; font-size: 0.9em;">
            Versión 2.0 · © 2024 · Medimos para crear valor
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Botón de reinicio en sidebar si existe
    try:
        with st.sidebar:
            if st.button("🔄 Reiniciar Aplicación", type="secondary", use_container_width=True):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    except:
        pass

# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    main()