import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Cargar datos
@st.cache_data
def load_data():
    files = {
        "2016": "/mnt/data/partidos_politicos_2016_normalizado.xlsx",
        "2019 Abril": "/mnt/data/partidos_politicos_201904_normalizado.xlsx",
        "2019 Noviembre": "/mnt/data/partidos_politicos_201911_normalizado.xlsx",
        "2023": "/mnt/data/partidos_politicos_2023_normalizado.xlsx"
    }
    return {year: pd.read_excel(path) for year, path in files.items()}

data = load_data()

st.title("Informe Interactivo de Elecciones Generales España")

# Selección de año y provincia
year = st.selectbox("Selecciona el año de la elección", list(data.keys()))
df = data[year]

provincia = st.selectbox("Selecciona una provincia", ["Todas"] + sorted(df['Nombre de Provincia'].unique()))

if provincia != "Todas":
    df = df[df['Nombre de Provincia'] == provincia]

# KPIs
censo_total = df['Total censo electoral'].sum()
votantes_total = df['Total votantes CER'].sum() + df['Total votantes CERA'].sum()
participacion = (votantes_total / censo_total) * 100

st.metric("Censo Electoral", f"{censo_total:,}")
st.metric("Total Votantes", f"{votantes_total:,}")
st.metric("Participación (%)", f"{participacion:.2f}%")

# Provincia con mayor afluencia
afluencia = data[year].copy()
afluencia["Total Votantes"] = afluencia['Total votantes CER'] + afluencia['Total votantes CERA']
prov_max = afluencia.groupby('Nombre de Provincia')["Total Votantes"].sum().idxmax()

st.write(f"**Provincia con mayor afluencia de voto:** {prov_max}")

# Votos por escaño
if 'Total Diputados' in df.columns:
    df['Total Diputados'] = df[[col for col in df.columns if col.endswith('_Diputados')]].sum(axis=1)

votos_por_escano = votantes_total / df['Total Diputados'].sum()
st.write(f"**Votos necesarios por escaño (media):** {votos_por_escano:.0f}")

# Distribución de votos
votos_cols = [col for col in df.columns if col.endswith('_Votos')]
votos_partidos = df[votos_cols].sum().sort_values(ascending=False)
votos_partidos.index = votos_partidos.index.str.replace('_Votos', '')

votos_acumulados = votos_partidos.cumsum() / votos_partidos.sum()
principales = votos_acumulados[votos_acumulados <= 0.8].index

otros = votos_partidos[~votos_partidos.index.isin(principales)].sum()

distribucion = votos_partidos[principales].append(pd.Series(otros, index=['Otros']))

fig, ax = plt.subplots()
distribucion.plot.pie(ax=ax, autopct='%1.1f%%', figsize=(6, 6))
ax.set_ylabel('')
st.pyplot(fig)

st.write("### Datos de Partidos Pequeños")
st.dataframe(votos_partidos[~votos_partidos.index.isin(principales)])
