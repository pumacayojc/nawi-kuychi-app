import math
import random
import matplotlib.pyplot as plt
import streamlit as st

# ===============================
# CONFIG — MODO OSCURO
# ===============================
st.set_page_config(
    page_title="NAWI KUYCHI - Muestreo MIL-STD-414",
    layout="wide"
)

dark_css = """
<style>
[data-testid="stAppViewContainer"] {
    background-color: #020617;
}
[data-testid="stSidebar"] {
    background-color: #020617;
}
html, body, [class*="css"] {
    color: #E5E7EB !important;
    font-family: "Lato", sans-serif;
}
h1, h2, h3, h4, h5 {
    color: #E5E7EB !important;
}
div.stButton > button {
    background: linear-gradient(90deg, #2A9D8F, #E76F51);
    color: white;
    border: none;
    border-radius: 999px;
    font-size: 16px;
    padding: 8px 18px;
}
input, textarea, select {
    background-color: #0B1220 !important;
    color: #F9FAFB !important;
}
[data-testid="stAlert"] {
    background-color: #0B1220 !important;
    border-radius: 0.75rem;
}
</style>
"""
st.markdown(dark_css, unsafe_allow_html=True)

# ===============================
# LOGO SVG + HEADER
# ===============================
logo_svg = """
<div style="display:flex;align-items:center;gap:30px;margin-bottom:30px;">
<svg width="180" height="180" viewBox="0 0 620 260">
<circle cx="120" cy="130" r="78" stroke="#F9FAFB" stroke-width="6" fill="none"/>
<path d="M70 120 C90 100, 125 85, 165 110" stroke="#F9FAFB" stroke-width="4" fill="none"/>
<path d="M75 140 C100 120, 130 110, 175 135" stroke="#F9FAFB" stroke-width="4" fill="none"/>
<path d="M85 160 C115 140, 140 135, 185 150" stroke="#F9FAFB" stroke-width="4" fill="none"/>
<path d="M90 100 C125 90, 155 105, 175 125" stroke="#F9FAFB" stroke-width="4" fill="none"/>
<path d="M95 185 C130 160, 160 155, 190 175" stroke="#F9FAFB" stroke-width="4" fill="none"/>
<path d="M95 170 C180 160, 260 120, 345 115" stroke="#2A9D8F" stroke-width="6"/>
<path d="M100 175 C190 170, 275 150, 360 145" stroke="#E9C46A" stroke-width="6"/>
<path d="M105 180 C200 180, 285 175, 375 165" stroke="#E76F51" stroke-width="6"/>
</svg>
<div style="line-height:1.2">
<h1 style="font-weight:700;margin:0;color:#F9FAFB;">APLICATIVO NAWI KUYCHI</h1>
<p style="margin-top:6px;color:#E5E7EB;">Muestreo MIL-STD-414 — Medimos para crear valor.</p>
</div>
</div>
"""
st.markdown(logo_svg, unsafe_allow_html=True)

# ===============================
# FUNCIONES AUXILIARES
# ===============================

def normal_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))

def generar_pesos(n, nominal, LI, LS):
    sigma = (LS - LI) / 6 if LS > LI else abs(nominal * 0.03)
    return [round(random.gauss(nominal, sigma), 2) for _ in range(n)]

# ===============================
# TABLAS MIL-STD-414
# ===============================

rangos = [
    (3, 8,     {'I':'B', 'II':'B', 'III':'B', 'IV':'B', 'V':'C'}),
    (9, 15,    {'I':'B', 'II':'B', 'III':'B', 'IV':'B', 'V':'D'}),
    (16, 25,   {'I':'B', 'II':'B', 'III':'B', 'IV':'C', 'V':'E'}),
    (26, 40,   {'I':'B', 'II':'B', 'III':'B', 'IV':'D', 'V':'F'}),
    (41, 65,   {'I':'B', 'II':'B', 'III':'C', 'IV':'E', 'V':'G'}),
    (66, 110,  {'I':'B', 'II':'B', 'III':'D', 'IV':'F', 'V':'H'}),
    (111, 180, {'I':'B', 'II':'C', 'III':'E', 'IV':'G', 'V':'I'}),
    (181, 300, {'I':'B', 'II':'D', 'III':'F', 'IV':'H', 'V':'J'}),
    (301, 500, {'I':'C', 'II':'E', 'III':'G', 'IV':'I', 'V':'K'}),
    (501, 800, {'I':'D', 'II':'F', 'III':'H', 'IV':'J', 'V':'L'}),
    (801, 1300,{'I':'E', 'II':'G', 'III':'I', 'IV':'K', 'V':'L'}),
    (1301, 3200,{'I':'F', 'II':'H', 'III':'J', 'IV':'L', 'V':'M'}),
    (3201, 8000,{'I':'G', 'II':'I', 'III':'L', 'IV':'M', 'V':'N'}),
    (8001, 22000,{'I':'H', 'II':'J', 'III':'M', 'IV':'N', 'V':'O'}),
    (22001, 110000,{'I':'I', 'II':'K', 'III':'N', 'IV':'O', 'V':'P'}),
    (110001, 550000,{'I':'I', 'II':'K', 'III':'O', 'IV':'P', 'V':'Q'}),
    (550001, float('inf'),{'I':'I', 'II':'K', 'III':'P', 'IV':'Q', 'V':'Q'}),
]

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

def letra_plan(nivel, lote):
    for lo, hi, tabla in rangos:
        if lo <= lote <= hi:
            return tabla[nivel]
    return None

# ===============================
# SESSION STATE
# ===============================
if "paso" not in st.session_state:
    st.session_state.paso = 1
if "pesos" not in st.session_state:
    st.session_state.pesos = []

# ===============================
# PASO 1 — SELECCIÓN DEL PLAN
# ===============================
def paso1():
    st.subheader("1️⃣ Selección del plan de muestreo")
    col1, col2, col3 = st.columns(3)

    nivel = col1.selectbox("Nivel de inspección", ["I","II","III"])
    lote = col2.number_input("Tamaño de lote", min_value=3, value=25)
    aql = col3.selectbox("NCA (AQL)", ["1","1.5","2.5","4"])

    letra = letra_plan(nivel, lote)
    if letra is None:
        st.error("No existe letra para ese rango.")
        return

    n = tabla_k[letra]["m"]
    k = tabla_k[letra][aql]

    st.success(f"Letra = {letra} → n = {n}, M(k)= {k if k else 'No definido'}")

    if st.button("➡️ Continuar"):
        st.session_state.plan = (nivel, lote, aql, letra, n, k)
        st.session_state.paso = 2

# ===============================
# PASO 2 — INGRESO DE PESOS
# ===============================
def paso2():
    st.subheader("2️⃣ Captura de pesos de la muestra")

    nivel, lote, aql, letra, n, k = st.session_state.plan

    col1, col2, col3 = st.columns(3)
    nominal = col1.number_input("Peso nominal", value=100.0, step=0.1)
    LI = col2.number_input("Límite inferior", value=97.0)
    LS = col3.number_input("Límite superior", value=103.0)

    if st.button("🔁 Generar muestra aleatoria"):
        st.session_state.pesos = generar_pesos(n, nominal, LI, LS)

    st.write("📦 Ingrese o edite los pesos:")

    nuevos = []
    cols = st.columns(3)
    for i in range(n):
        v = cols[i%3].number_input(
            f"P{i+1}",
            value=st.session_state.pesos[i] if i<len(st.session_state.pesos) else nominal
        )
        nuevos.append(v)

    st.session_state.pesos = nuevos

    if st.button("➡️ Calcular"):
        st.session_state.limites = (nominal, LI, LS)
        st.session_state.paso = 3

# ===============================
# PASO 3 — RESULTADOS
# ===============================
def paso3():
    st.subheader("3️⃣ Resultados")

    pesos = st.session_state.pesos
    nominal, LI, LS = st.session_state.limites
    _, _, _, _, n, k = st.session_state.plan

    X = sum(pesos)/n
    S = math.sqrt(sum((p - X)**2 for p in pesos) / (n-1))

    ZEI = (X - LI) / S
    ZES = (LS - X) / S

    pi = (1 - normal_cdf(ZEI)) * 100
    ps = (1 - normal_cdf(ZES)) * 100
    p = pi + ps

    st.write(f"📌 Media = {X:.4f}")
    st.write(f"📌 Desviación σ = {S:.4f}")
    st.write(f"📌 Z (inf) = {ZEI:.3f}")
    st.write(f"📌 Z (sup) = {ZES:.3f}")
    st.write(f"📌 Defectuosos estimados = {p:.3f}%")

    if k is not None:
        if p <= k:
            st.success("✅ ACEPTAR LOTE")
        else:
            st.error("❌ RECHAZAR LOTE")

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.plot(pesos, marker="o", color="#60A5FA")
    ax.axhline(LI, color="red", linestyle="--")
    ax.axhline(LS, color="red", linestyle="--")
    ax.axhline(nominal, color="green")
    ax.set_title("Distribución de Pesos")
    st.pyplot(fig)

    if st.button("🔁 Reiniciar"):
    # limpiar estado y recargar la app
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ===============================
# RENDER WIZARD
# ===============================
if st.session_state.paso == 1:
    paso1()
elif st.session_state.paso == 2:
    paso2()
else:
    paso3()