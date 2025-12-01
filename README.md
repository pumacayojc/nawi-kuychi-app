\# 🧶 NAWI KUYCHI – Muestreo MIL-STD-414 para pesaje de ovillos



Aplicativo web desarrollado en \*\*Python + Streamlit\*\* para aplicar planes de muestreo por variables (norma \*\*MIL-STD-414\*\*) en el control de peso de ovillos en una planta textil.



> Medimos para crear valor.



---



\## 🎯 Objetivo



Facilitar al área de Calidad / Producción la \*\*toma de muestras, evaluación estadística y decisión de aceptación o rechazo de lotes\*\*, reduciendo desperdicio y reprocesos.



---



\## ✨ Funcionalidades principales



\- Selección de \*\*nivel de inspección\*\* y \*\*tamaño de lote\*\*.

\- Determinación automática de:

&nbsp; - \*\*Letra del plan\*\*.

&nbsp; - \*\*Tamaño de muestra \_n\_\*\*.

&nbsp; - \*\*Valor de referencia \_M (k)\_\*\* según NCA (AQL).

\- Ingreso de pesos:

&nbsp; - Manual, uno por uno.

&nbsp; - O generación \*\*aleatoria\*\* para simulaciones.

\- Cálculo automático de:

&nbsp; - Media muestral \\(\\bar{X}\\)

&nbsp; - Desviación estándar \\(S\\)

&nbsp; - Índices \\(Z\_{EI}\\) y \\(Z\_{ES}\\)

&nbsp; - Porcentaje estimado de unidades defectuosas.

\- Decisión automática:

&nbsp; - ✅ \*\*Aceptar lote\*\*  

&nbsp; - ❌ \*\*Rechazar lote\*\*

\- Gráfico de los pesos medidos vs. límites:

&nbsp; - Límite inferior

&nbsp; - Peso nominal

&nbsp; - Límite superior

\- Interfaz tipo \*\*wizard\*\*, modo oscuro y estilo corporativo \*\*NAWI KUYCHI\*\*.



---



\## 🛠️ Tecnologías



\- Python

\- \[Streamlit](https://streamlit.io/)

\- Matplotlib



---



\## 📦 Instalación y ejecución local



1\. Clonar este repositorio:



```bash

git clone https://github.com/pumacayojc/nawi-kuychi-app.git

cd nawi-kuychi-app



