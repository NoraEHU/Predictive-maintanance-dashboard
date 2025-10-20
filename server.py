from flask import Flask, render_template_string
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)

# ---------- CONFIGURACIÓN ----------
CSV_PATH = "data/predictive_maintenance.csv"

# ---------- CARGA DE DATOS ----------
df = pd.read_csv(CSV_PATH)

# Renombramos columnas largas para facilidad
rename_map = {
    "Air temperature [K]": "AirTempK",
    "Process temperature [K]": "ProcTempK",
    "Rotational speed [rpm]": "RPM",
    "Torque [Nm]": "Torque",
    "Tool wear [min]": "ToolWear",
    "Failure Type": "FailureType",
}
df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})


# ---------- GENERACIÓN DE FIGURAS ----------
def make_dashboard():
    # Muestras limitadas para rendimiento
    df_sample = df.sample(min(len(df), 3000), random_state=42)

    # Scatter RPM vs Torque
    fig1 = px.scatter(
        df_sample,
        x="RPM",
        y="Torque",
        color="Target",
        opacity=0.6,
        title="Relación entre RPM y Torque (color = Target)",
    )
    fig1_html = fig1.to_html(full_html=False)

    # Boxplot ToolWear por estado Target
    fig2 = px.box(
        df,
        x="Target",
        y="ToolWear",
        points="all",
        title="Desgaste de herramienta (ToolWear) por estado de máquina",
    )
    fig2_html = fig2.to_html(full_html=False)

    # Barras de tipos de fallo
    if "FailureType" in df.columns:
        fail_counts = df["FailureType"].value_counts().reset_index()
        fail_counts.columns = ["FailureType", "count"]
        fig3 = px.bar(
            fail_counts,
            x="FailureType",
            y="count",
            title="Frecuencia de tipos de fallo",
            color="FailureType",
        )
        fig3_html = fig3.to_html(full_html=False)
    else:
        fig3_html = "<p>No hay columna 'FailureType' en los datos.</p>"

    # Devolvemos todo como un diccionario de HTML embebido
    return {
        "fig1": fig1_html,
        "fig2": fig2_html,
        "fig3": fig3_html,
    }


# ---------- RUTA PRINCIPAL ----------
@app.route("/")
def dashboard():
    figs = make_dashboard()
    html = f"""
    <html>
    <head>
        <title>Predictive Maintenance Dashboard</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #004d80; }}
            .chart {{ margin-bottom: 50px; }}
        </style>
    </head>
    <body>
        <h1>Machine Predictive Maintenance - Dashboard</h1>
        <p>Visualización de datos del dataset de Kaggle (Predictive Maintenance Classification)</p>

        <div class="chart">{figs["fig1"]}</div>
        <div class="chart">{figs["fig2"]}</div>
        <div class="chart">{figs["fig3"]}</div>

        <footer style="margin-top:40px;color:gray;font-size:12px;">
            Desplegado con Flask + Plotly en Render.com
        </footer>
    </body>
    </html>
    """
    return render_template_string(html)


# ---------- EJECUCIÓN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render asigna el puerto
    app.run(host="0.0.0.0", port=port)
