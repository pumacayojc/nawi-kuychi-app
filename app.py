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
    (3, 8,     {'I': 'B', 'II': 'B', 'III': 'B', 'IV': 'B', 'V': 'C'}),
    (9, 15,    {'I': 'B', 'II': 'B', 'III': 'B', 'IV': 'B', 'V': 'D'}),
    (16, 25,   {'I': 'B', 'II': 'B', 'III': 'B', 'IV': 'C', 'V': 'E'})
]

tabla_k = {
    "B": {"m":3,"1":None,"1.5":5.5,"2.5":10.92,"4":18.86},
    "C": {"m":4,"1":1.53,"1.5":5.83,"2.5":9.8,"4":16.45},
    "D": {"m":5,"1":1.33,"1.5":5.83,"2.5":9.8,"4":14.39},
    "E": {"m":7,"1":3.55,"1.5":5.35,"2.5":8.4,"4":12.2},
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
        st.session_state.clear()
        st.experimental_rerun()

# ===============================
# RENDER WIZARD
# ===============================
if st.session_state.paso == 1:
    paso1()
elif st.session_state.paso == 2:
    paso2()
else:
    paso3()