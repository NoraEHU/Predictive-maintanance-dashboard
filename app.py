import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Predictive Maintenance HMI", layout="wide")

# 1) Carga
df = pd.read_csv("data/predictive_maintenance.csv")

# 2) Limpieza ligera (renombra columnas largas a algo corto si quieres)
rename_map = {
    "Air temperature [K]": "AirTempK",
    "Process temperature [K]": "ProcTempK",
    "Rotational speed [rpm]": "RPM",
    "Torque [Nm]": "Torque",
    "Tool wear [min]": "ToolWear",
    "Failure Type": "FailureType"
}
df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})

# 3) Filtros
colf1, colf2, colf3 = st.columns(3)
type_sel = colf1.multiselect("Type", sorted(df["Type"].dropna().unique()), default=None)
failure_sel = colf2.multiselect("FailureType", sorted(df["FailureType"].dropna().unique()), default=None)
target_sel = colf3.multiselect("Target (0=OK,1=Fail)", sorted(df["Target"].dropna().unique()), default=None)

fdf = df.copy()
if type_sel: fdf = fdf[fdf["Type"].isin(type_sel)]
if failure_sel: fdf = fdf[fdf["FailureType"].isin(failure_sel)]
if target_sel: fdf = fdf[fdf["Target"].isin(target_sel)]

# 4) KPIs
c1, c2, c3, c4 = st.columns(4)
fail_rate = (fdf["Target"].mean()*100) if "Target" in fdf else 0
c1.metric("Registros", f"{len(fdf):,}")
c2.metric("Fallo (%)", f"{fail_rate:.2f}%")
if "RPM" in fdf:      c3.metric("RPM medio", f"{fdf['RPM'].mean():.0f}")
if "Torque" in fdf:   c4.metric("Torque medio", f"{fdf['Torque'].mean():.2f} Nm")

st.divider()

# 5) Gráficos
gcol1, gcol2 = st.columns(2)
if {"RPM","Torque"}.issubset(fdf.columns):
    fig_sc = px.scatter(fdf, x="RPM", y="Torque", color="Target",
                        title="Relación RPM vs Torque (color=Target)")
    gcol1.plotly_chart(fig_sc, use_container_width=True)

if {"ToolWear","Target"}.issubset(fdf.columns):
    fig_box = px.box(fdf, x="Target", y="ToolWear", points="all",
                     title="Desgaste herramienta por estado (Target)")
    gcol2.plotly_chart(fig_box, use_container_width=True)

st.divider()

if "FailureType" in fdf.columns:
    fail_counts = fdf["FailureType"].value_counts().reset_index()
    fail_counts.columns = ["FailureType", "count"]
    fig_bar = px.bar(fail_counts, x="FailureType", y="count",
                     title="Tipos de fallo (conteo)")
    st.plotly_chart(fig_bar, use_container_width=True)

# 6) Tabla final
st.subheader("Muestras (vista previa)")
st.dataframe(fdf.head(50))
