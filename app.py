import math
import random

import matplotlib.pyplot as plt
import streamlit as st

# ============================================================
# CONFIGURACIÓN BÁSICA
# ============================================================
st.set_page_config(
    page_title="NAWI KUYCHI - Muestreo MIL-STD-414",
    page_icon="🧶",
    layout="wide",
)

# Logo simple NAWI KUYCHI en SVG (opcional)
logo_svg = """
<svg width="260" height="120" viewBox="0 0 620 260" xmlns="http://www.w3.org/2000/svg">
  <circle cx="120" cy="130" r="78" stroke="#E9C46A" stroke-width="6" fill="none"/>
  <path d="M70 120 C90 100, 125 85, 165 110" stroke="#2A9D8F" stroke-width="4" fill="none"/>
  <path d="M75 140 C100 120, 130 110, 175 135" stroke="#2A9D8F" stroke-width="4" fill="none"/>
  <path d="M85 160 C115 140, 140 135, 185 150" stroke="#E76F51" stroke-width="4" fill="none"/>
  <path d="M90 100 C125 90, 155 105, 175 125" stroke="#E76F51" stroke-width="4" fill="none"/>
  <path d="M95 185 C130 160, 160 155, 190 175" stroke="#E9C46A" stroke-width="4" fill="none"/>
  <path d="M95 170 C180 160, 260 120, 345 115" stroke="#2A9D8F" stroke-width="6" fill="none"/>
  <path d="M100 175 C190 170, 275 150, 360 145" stroke="#E9C46A" stroke-width="6" fill="none"/>
  <path d="M105 180 C200 180, 285 175, 375 165" stroke="#E76F51" stroke-width="6" fill="none"/>
  <text x="395" y="120" font-family="Montserrat, sans-serif" font-weight="600" font-size="30" fill="#F4F4F4">
    NAWI KUYCHI
  </text>
  <text x="395" y="155" font-family="Lato, sans-serif" font-size="18" fill="#E9C46A">
    Medimos para crear valor.
  </text>
</svg>
"""

st.markdown(
    f"""
<div style="display:flex;align-items:center;gap:1rem;">
  {logo_svg}
</div>
""",
    unsafe_allow_html=True,
)

st.title("APLICATIVO NAWI KUYCHI – Muestreo MIL-STD-414 para pesado de ovillos")

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


def inicializar_estado():
    if "plan_calculado" not in st.session_state:
        st.session_state.plan_calculado = False
    if "n" not in st.session_state:
        st.session_state.n = 0
    if "k" not in st.session_state:
        st.session_state.k = None


inicializar_estado()

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

if st.button("Calcular plan"):
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

            st.success("Plan de muestreo calculado correctamente.")
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
    st.write(f"**Tamaño de muestra n = {n}**")

    # Generar o leer pesos
    pesos = []
    cols = st.columns(4)
    for i in range(n):
        col = cols[i % 4]
        key = f"peso_{i}"
        if key not in st.session_state:
            st.session_state[key] = 0.0
        with col:
            st.session_state[key] = st.number_input(
                f"P{i+1}",
                key=key,
                value=st.session_state[key],
                step=0.01,
                format="%.2f",
            )
        pesos.append(st.session_state[key])

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if st.button("Generar pesos aleatorios"):
            if lim_sup > lim_inf:
                sigma = (lim_sup - lim_inf) / 6.0
            else:
                sigma = max(0.1, abs(nominal) * 0.01)
            for i in range(n):
                key = f"peso_{i}"
                valor = random.gauss(nominal, sigma)
                st.session_state[key] = round(valor, 2)
            st.experimental_rerun()

    with col_btn2:
        calcular = st.button("Calcular índices Z y decisión")

    # ========================================================
    # 6. PASO 3: CÁLCULO ESTADÍSTICO Y DECISIÓN
    # ========================================================
    if calcular:
        pesos = [st.session_state[f"peso_{i}"] for i in range(n)]
        if n < 2:
            st.error("Se requieren al menos 2 observaciones para calcular la desviación estándar.")
        else:
            X_bar = sum(pesos) / n
            S = math.sqrt(sum((x - X_bar) ** 2 for x in pesos) / (n - 1))

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
                        decision = f"ACEPTAR el lote (p = {p_total:.3f}% ≤ M = {k:.3f}%)"
                        color = "green"
                    else:
                        decision = f"RECHAZAR el lote (p = {p_total:.3f}% > M = {k:.3f}%)"
                        color = "red"

                st.markdown(
                    f"""
### 📊 Resultados estadísticos

- n = **{n}**  
- Media X̄ = **{X_bar:.4f}**  
- Desviación estándar S = **{S:.4f}**  

- Z_ES = **{Z_ES:.4f}**  
- Z_EI = **{Z_EI:.4f}**  

- pi (lado inferior) ≈ **{pi:.3f}%**  
- ps (lado superior) ≈ **{ps:.3f}%**  
- p = pi + ps ≈ **{p_total:.3f}%**

<span style="color:{color};font-weight:bold;font-size:18px;">{decision}</span>
""",
                    unsafe_allow_html=True,
                )

                # ====== Gráfico ======
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.scatter(range(1, n + 1), pesos, s=60, label="Pesos")
                ax.axhline(lim_inf, color="red", linestyle="--", label="Límite inferior")
                ax.axhline(lim_sup, color="red", linestyle="--", label="Límite superior")
                ax.axhline(nominal, color="green", linestyle="-.", label="Nominal")
                ax.axhline(X_bar, color="black", linestyle="-", linewidth=2, label="Media muestral")

                ax.set_title("Distribución de pesos de la muestra")
                ax.set_xlabel("Ítem de muestra")
                ax.set_ylabel("Peso")
                ax.grid(True)
                ax.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
                fig.tight_layout()

                st.pyplot(fig)

st.markdown("---")

# Botón de reinicio de toda la app
if st.button("🔁 Reiniciar aplicación"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()