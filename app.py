import math
import random
import matplotlib.pyplot as plt
import streamlit as st
import numpy as np

# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================
st.set_page_config(
    page_title="NAWI KUYCHI - Muestreo MIL-STD-414",
    page_icon="🧶",
    layout="wide",
)

# Logo y título mejorado
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 10px;">
        <div style="flex: 0 0 auto;">
            <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <circle cx="50" cy="50" r="45" stroke="#E9C46A" stroke-width="4" fill="none"/>
                <path d="M25 40 C35 30, 45 25, 60 35" stroke="#2A9D8F" stroke-width="2" fill="none"/>
                <path d="M30 50 C40 40, 50 35, 65 45" stroke="#2A9D8F" stroke-width="2" fill="none"/>
                <path d="M35 60 C45 50, 55 45, 70 55" stroke="#E76F51" stroke-width="2" fill="none"/>
                <path d="M30 35 C45 30, 55 35, 65 45" stroke="#E76F51" stroke-width="2" fill="none"/>
                <path d="M40 70 C50 60, 60 55, 75 65" stroke="#E9C46A" stroke-width="2" fill="none"/>
                <path d="M40 60 C55 55, 70 40, 85 35" stroke="#2A9D8F" stroke-width="3" fill="none"/>
                <path d="M45 65 C60 60, 75 50, 90 45" stroke="#E9C46A" stroke-width="3" fill="none"/>
                <path d="M50 70 C65 65, 80 60, 95 55" stroke="#E76F51" stroke-width="3" fill="none"/>
            </svg>
        </div>
        <div style="flex: 1 1 auto;">
            <h1 style="color: #800000; margin: 0; font-size: 2.5em; font-weight: 700;">NAWI KUYCHI</h1>
            <p style="color: #E9C46A; font-size: 1.3em; margin: 5px 0 0 0; font-weight: 500;">
                Medimos para crear valor.
            </p>
        </div>
    </div>
    <hr style="border: none; height: 2px; background: linear-gradient(to right, #2A9D8F, #E9C46A, #E76F51); margin: 10px 0 20px 0;">
    """,
    unsafe_allow_html=True
)

st.title("APLICATIVO – Muestreo MIL-STD-414 para pesado de ovillos")

st.markdown(
    """
Esta herramienta permite:
- Seleccionar **nivel de inspección**, **tamaño de lote** y **NCA** (AQL).
- Obtener la **letra del plan**, el tamaño de muestra **n** y el valor **M (k)**.
- Registrar o simular pesos de la muestra.
- Calcular **media, desviación, índices Z**, porcentaje fuera de especificación y decisión de aceptación/rechazo del lote.
"""
)

# ============================================================
# 1. TABLA RANGOS LOTE -> LETRA
# ============================================================
rangos = [
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

def obtener_letra_muestreo(nivel, tam_lote):
    for minimo, maximo, letras in rangos:
        if minimo <= tam_lote <= maximo:
            return letras[nivel]
    return None

# ============================================================
# 2. TABLA LETRA -> n Y k POR NCA (inspección normal)
# ============================================================
aql_keys = ["0.04", "0.065", "0.1", "0.15", "0.25", "0.4", "0.65", "1",
            "1.5", "2.5", "4", "6.5", "10", "15"]

tabla_k = {
    "B": {"muestra": 3,
          "0.04": None, "0.065": None, "0.1": None, "0.15": None,
          "0.25": None, "0.4": None, "0.65": None, "1": None,
          "1.5": None, "2.5": 7.59, "4": 18.86, "6.5": 26.94,
          "10": 33.69, "15": 40.47},
    "C": {"muestra": 4,
          "0.04": None, "0.065": None, "0.1": None, "0.15": None,
          "0.25": None, "0.4": None, "0.65": None,
          "1": 1.53, "1.5": 5.5, "2.5": 10.92, "4": 16.45,
          "6.5": 22.86, "10": 29.45, "15": 36.9},
    "D": {"muestra": 5,
          "0.04": None, "0.065": None, "0.1": None, "0.15": None,
          "0.25": None, "0.4": None, "0.65": None,
          "1": 1.33, "1.5": 5.83, "2.5": 9.8, "4": 14.39,
          "6.5": 20.19, "10": 26.56, "15": 33.99},
    "E": {"muestra": 7,
          "0.04": None, "0.065": None, "0.1": None, "0.15": None,
          "0.25": 0.422, "0.4": 1.06, "0.65": 2.14,
          "1": 3.55, "1.5": 5.35, "2.5": 8.4, "4": 12.2,
          "6.5": 17.35, "10": 23.29, "15": 30.5},
    "F": {"muestra": 10,
          "0.04": None, "0.065": None, "0.1": None,
          "0.15": 0.349, "0.25": 0.716, "0.4": 1.3,
          "0.65": 2.17, "1": 3.26, "1.5": 4.77, "2.5": 7.29,
          "4": 10.54, "6.5": 15.17, "10": 20.74, "15": 27.57},
    "G": {"muestra": 15,
          "0.04": 0.099, "0.065": 0.099, "0.1": 0.312,
          "0.15": 0.503, "0.25": 0.818, "0.4": 1.31, "0.65": 2.11,
          "1": 3.05, "1.5": 4.31, "2.5": 6.56, "4": 9.46,
          "6.5": 13.71, "10": 18.94, "15": 25.61},
    "H": {"muestra": 20,
          "0.04": 0.135, "0.065": 0.135, "0.1": 0.365,
          "0.15": 0.544, "0.25": 0.846, "0.4": 1.29, "0.65": 2.05,
          "1": 2.95, "1.5": 4.09, "2.5": 6.17, "4": 8.92,
          "6.5": 12.99, "10": 18.03, "15": 24.53},
    "I": {"muestra": 25,
          "0.04": 0.155, "0.065": 0.156, "0.1": 0.38,
          "0.15": 0.551, "0.25": 0.877, "0.4": 1.29, "0.65": 2,
          "1": 2.86, "1.5": 3.97, "2.5": 5.97, "4": 8.63,
          "6.5": 12.57, "10": 17.51, "15": 23.97},
    "J": {"muestra": 30,
          "0.04": 0.179, "0.065": 0.179, "0.1": 0.413,
          "0.15": 0.581, "0.25": 0.879, "0.4": 1.29, "0.65": 1.98,
          "1": 2.83, "1.5": 3.91, "2.5": 5.86, "4": 8.47,
          "6.5": 12.36, "10": 17.24, "15": 23.58},
    "K": {"muestra": 35,
          "0.04": 0.17, "0.065": 0.17, "0.1": 0.388,
          "0.15": 0.535, "0.25": 0.847, "0.4": 1.23, "0.65": 1.87,
          "1": 2.68, "1.5": 3.7, "2.5": 5.57, "4": 8.1,
          "6.5": 11.87, "10": 16.65, "15": 22.91},
    "L": {"muestra": 40,
          "0.04": 0.179, "0.065": 0.179, "0.1": 0.401,
          "0.15": 0.566, "0.25": 0.873, "0.4": 1.26, "0.65": 1.88,
          "1": 2.71, "1.5": 3.72, "2.5": 5.58, "4": 8.09,
          "6.5": 11.85, "10": 16.61, "15": 22.86},
    "M": {"muestra": 50,
          "0.04": 0.163, "0.065": 0.163, "0.1": 0.363,
          "0.15": 0.503, "0.25": 0.789, "0.4": 1.17, "0.65": 1.71,
          "1": 2.49, "1.5": 3.45, "2.5": 5.2, "4": 7.61,
          "6.5": 11.23, "10": 15.87, "15": 22},
    "N": {"muestra": 75,
          "0.04": 1.147, "0.065": 0.147, "0.1": 0.33,
          "0.15": 0.467, "0.25": 0.72, "0.4": 1.07, "0.65": 1.6,
          "1": 2.29, "1.5": 3.2, "2.5": 4.87, "4": 7.15,
          "6.5": 10.63, "10": 15.13, "15": 21.11},
    "O": {"muestra": 100,
          "0.04": 0.145, "0.065": 0.145, "0.1": 0.317,
          "0.15": 0.447, "0.25": 0.689, "0.4": 1.02, "0.65": 1.53,
          "1": 2.2, "1.5": 3.07, "2.5": 4.69, "4": 6.91,
          "6.5": 10.32, "10": 14.75, "15": 20.66},
    "P": {"muestra": 150,
          "0.04": 0.134, "0.065": 0.134, "0.1": 0.293,
          "0.15": 0.413, "0.25": 0.638, "0.4": 0.949, "0.65": 1.43,
          "1": 2.05, "1.5": 2.89, "2.5": 4.43, "4": 6.57,
          "6.5": 9.88, "10": 14.2, "15": 20.02},
    "Q": {"muestra": 200,
          "0.04": 0.135, "0.065": 0.135, "0.1": 0.294,
          "0.15": 0.414, "0.25": 0.637, "0.4": 0.945, "0.65": 1.42,
          "1": 2.04, "1.5": 2.87, "2.5": 4.4, "4": 6.53,
          "6.5": 9.81, "10": 14.12, "15": 19.92}
}

# ============================================================
# 3. FUNCIONES AUXILIARES
# ============================================================
def normal_cdf(z: float) -> float:
    """Función de distribución acumulada de N(0,1)."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))

# Inicialización del estado
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

# ============================================================
# 4. PASO 1: SELECCIÓN DE PLAN
# ============================================================
st.subheader("1️⃣ Selección del plan de muestreo")

col1, col2, col3 = st.columns(3)

with col1:
    nivel = st.selectbox("Nivel de inspección", ["I", "II", "III", "IV", "V"], index=1)
with col2:
    tam_lote = st.number_input("Tamaño de lote", min_value=3, value=1000, step=1)
with col3:
    aql = st.selectbox("NCA (AQL)", aql_keys, index=aql_keys.index("1"))

if st.button("Calcular plan", key="calcular_plan"):
    letra = obtener_letra_muestreo(nivel, tam_lote)
    if letra is None:
        st.error("No se encontró un rango de lote para esos datos.")
    else:
        fila = tabla_k.get(letra)
        if fila is None:
            st.error(f"Letra {letra} no está definida en la tabla de n y k.")
        else:
            n = fila["muestra"]
            k = fila.get(aql)
            st.session_state.plan_calculado = True
            st.session_state.n = n
            st.session_state.k = k
            
            # Reiniciar pesos
            st.session_state.pesos = [0.0] * n
            st.session_state.pesos_input = {f"peso_{i}": 0.0 for i in range(n)}
            
            st.success("✅ Plan de muestreo calculado correctamente.")
            st.markdown(
                f"""
**Resultados del plan:**

- Nivel de inspección: **{nivel}**  
- Tamaño de lote: **{tam_lote}**  
- NCA: **{aql}**  
- Letra del plan: **{letra}**  
- Tamaño de muestra `n`: **{n}**  
- Valor `M (k)` permitido (% defectuosos): **{k if k is not None else "No disponible para esta combinación"}**
"""
            )

st.markdown("---")

# ============================================================
# 5. PASO 2: REGISTRO / SIMULACIÓN DE PESOS
# ============================================================
st.subheader("2️⃣ Registro de pesos de la muestra")

col_nom, col_inf, col_sup = st.columns(3)
with col_nom:
    nominal = st.number_input("Peso nominal", value=100.0, step=0.01, format="%.2f")
with col_inf:
    lim_inf = st.number_input("Límite inferior", value=98.0, step=0.01, format="%.2f")
with col_sup:
    lim_sup = st.number_input("Límite superior", value=102.0, step=0.01, format="%.2f")

if not st.session_state.plan_calculado:
    st.info("Primero calcula el plan de muestreo para saber cuántos pesos registrar.")
else:
    n = st.session_state.n
    
    # Asegurar que pesos_input tenga la longitud correcta
    if len(st.session_state.pesos_input) != n:
        st.session_state.pesos_input = {f"peso_{i}": 0.0 for i in range(n)}
    
    st.markdown(f"**Tamaño de muestra n = {n}**")
    
    # Crear inputs para pesos - VERSIÓN CORREGIDA
    st.markdown("**Ingrese los pesos:**")
    
    # Dividir en columnas
    num_cols = 4 if n > 8 else (3 if n > 4 else 2)
    cols = st.columns(num_cols)
    
    pesos_actualizados = []
    
    for i in range(n):
        col_idx = i % num_cols
        with cols[col_idx]:
            key = f"peso_{i}"
            
            # Crear widget de entrada
            nuevo_valor = st.number_input(
                f"P{i+1}",
                key=key,
                value=float(st.session_state.pesos_input.get(key, 0.0)),
                step=0.01,
                format="%.2f",
                label_visibility="visible"
            )
            
            # Actualizar estado
            st.session_state.pesos_input[key] = nuevo_valor
            pesos_actualizados.append(nuevo_valor)
    
    # Actualizar lista de pesos
    st.session_state.pesos = pesos_actualizados
    
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        generar_clicked = st.button("🎲 Generar pesos aleatorios", key="generar_pesos")
    
    with col_btn2:
        calcular_clicked = st.button("📊 Calcular índices Z y decisión", key="calcular_decision")
    
    # Generar pesos aleatorios
    if generar_clicked:
        if lim_sup > lim_inf:
            sigma = (lim_sup - lim_inf) / 6.0
        else:
            sigma = max(0.1, abs(nominal) * 0.01)
        
        # Generar nuevos pesos
        nuevos_pesos = []
        for i in range(n):
            valor = random.gauss(nominal, sigma)
            nuevo_valor = round(valor, 2)
            nuevos_pesos.append(nuevo_valor)
            
            # Actualizar directamente en session_state usando el key único
            st.session_state[f"peso_{i}"] = nuevo_valor
        
        # Actualizar pesos_input también
        for i in range(n):
            st.session_state.pesos_input[f"peso_{i}"] = nuevos_pesos[i]
        
        # Actualizar pesos
        st.session_state.pesos = nuevos_pesos
        
        # Mostrar mensaje de éxito
        st.success(f"✅ Se generaron {n} pesos aleatorios correctamente.")
        st.rerun()
    
    # ========================================================
    # 6. PASO 3: CÁLCULO ESTADÍSTICO Y DECISIÓN
    # ========================================================
    if calcular_clicked:
        pesos = st.session_state.pesos
        
        # Verificar si hay valores ingresados
        if all(p == 0.0 for p in pesos):
            st.warning("⚠️ Todos los pesos están en cero. Ingrese valores o genere pesos aleatorios.")
        elif len(pesos) < 2:
            st.error("Se requieren al menos 2 observaciones para calcular la desviación estándar.")
        else:
            X_bar = np.mean(pesos)
            S = np.std(pesos, ddof=1)  # Desviación estándar muestral
            
            if S == 0:
                st.error("La desviación estándar S = 0 (no hay variación en los pesos).")
            else:
                Z_ES = (lim_sup - X_bar) / S
                Z_EI = (X_bar - lim_inf) / S
                
                pi = (1 - normal_cdf(Z_EI)) * 100
                ps = (1 - normal_cdf(Z_ES)) * 100
                p_total = pi + ps
                
                k = st.session_state.k
                if k is None:
                    decision = "No hay valor M (k) definido en la tabla para esta combinación."
                    color = "orange"
                else:
                    if p_total <= k:
                        decision = f"✅ **ACEPTAR** el lote (p = {p_total:.3f}% ≤ M = {k:.3f}%)"
                        color = "green"
                    else:
                        decision = f"❌ **RECHAZAR** el lote (p = {p_total:.3f}% > M = {k:.3f}%)"
                        color = "red"
                
                # Mostrar resultados en un contenedor estilizado
                st.markdown("---")
                st.markdown("### 📊 Resultados estadísticos")
                
                col_res1, col_res2 = st.columns(2)
                
                with col_res1:
                    st.markdown(f"""
                    **Datos muestrales:**
                    - n = **{n}**  
                    - Media X̄ = **{X_bar:.4f}**  
                    - Desviación estándar S = **{S:.4f}**
                    """)
                    
                    st.markdown(f"""
                    **Índices Z:**
                    - Z_ES = **{Z_ES:.4f}**  
                    - Z_EI = **{Z_EI:.4f}**
                    """)
                
                with col_res2:
                    st.markdown(f"""
                    **Porcentajes fuera de especificación:**
                    - pi (lado inferior) ≈ **{pi:.3f}%**  
                    - ps (lado superior) ≈ **{ps:.3f}%**  
                    - p = pi + ps ≈ **{p_total:.3f}%**
                    
                    **Valor M (k) de referencia:** **{k if k is not None else 'No disponible'}**
                    """)
                
                # Mostrar decisión
                st.markdown(f'<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid {color}; margin: 20px 0;">', unsafe_allow_html=True)
                st.markdown(f'<h4 style="color: {color};">{decision}</h4>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # ====== Gráfico ======
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # Configurar colores
                colors = plt.cm.Set3(np.linspace(0, 1, n))
                
                # Crear gráfico de dispersión
                scatter = ax.scatter(range(1, n + 1), pesos, s=80, c=colors, 
                                    edgecolors='black', alpha=0.8, label="Pesos muestrales")
                
                # Líneas de referencia
                ax.axhline(lim_inf, color="red", linestyle="--", linewidth=1.5, label="Límite inferior")
                ax.axhline(lim_sup, color="red", linestyle="--", linewidth=1.5, label="Límite superior")
                ax.axhline(nominal, color="green", linestyle="-.", linewidth=1.5, label="Peso nominal")
                ax.axhline(X_bar, color="blue", linestyle="-", linewidth=2, label="Media muestral")
                
                # Rellenar área de especificación
                ax.fill_between(range(0, n + 2), lim_inf, lim_sup, alpha=0.1, color='green', label='Área de especificación')
                
                # Configurar gráfico
                ax.set_title("Distribución de pesos de la muestra", fontsize=14, fontweight='bold')
                ax.set_xlabel("Ítem de muestra", fontsize=12)
                ax.set_ylabel("Peso", fontsize=12)
                ax.grid(True, alpha=0.3)
                ax.set_xticks(range(1, n + 1))
                ax.set_xlim(0.5, n + 0.5)
                
                # Añadir anotaciones
                for i, peso in enumerate(pesos, 1):
                    ax.annotate(f'{peso:.2f}', (i, peso), textcoords="offset points", 
                               xytext=(0,5), ha='center', fontsize=9)
                
                ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=10)
                fig.tight_layout()
                
                st.pyplot(fig)

st.markdown("---")

# Botón de reinicio
if st.button("🔁 Reiniciar aplicación", key="reiniciar"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.success("Aplicación reiniciada correctamente.")
    st.rerun()

# Pie de página
st.markdown(
    """
    <div style="text-align: center; margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
        <p style="color: #666; font-size: 0.9em;">
            <strong>NAWI KUYCHI</strong> - Sistema de muestreo MIL-STD-414<br>
            © 2024 - Herramienta para control de calidad en pesado de ovillos
        </p>
    </div>
    """,
    unsafe_allow_html=True
)