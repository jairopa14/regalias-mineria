import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Estimador de regalías mineras", layout="wide")


@st.cache_resource
def cargar_modelo():
    modelo = joblib.load("model/modelo_regalias.joblib")
    with open("model/metadata.json", encoding="utf-8") as f:
        info = json.load(f)
    return modelo, info


modelo, info = cargar_modelo()
columnas = info["features_num"] + info["features_cat"]
rmse = info["rmse_log_test"]


def pesos(valor):
    return "$ " + f"{valor:,.0f}".replace(",", ".")


st.title("Estimador de regalías mineras - Colombia")
st.write(
    f"Modelo: {info['modelo']}. RMSE en prueba (escala log): {rmse:.3f}, R2: {info['r2_log_test']:.3f}. "
    f"Datos de la ANM en [datos.gov.co]({info['fuente']})."
)

tab1, tab2 = st.tabs(["Un registro", "Varios registros (CSV)"])

with tab1:
    minerales = info["minerales"]
    deptos = info["departamentos"]

    col1, col2, col3 = st.columns(3)
    mineral = col1.selectbox("Mineral", minerales, index=minerales.index("Carbon térmico (Ton)"))
    depto = col2.selectbox("Departamento", deptos, index=deptos.index("Cesar"))
    gran = col3.radio("Gran proyecto", ["No", "Si"], horizontal=True)

    col4, col5, col6 = st.columns(3)
    vol_inicial = float(info["mediana_volumen"].get(mineral, 1000.0))
    volumen = col4.number_input("Volumen (en la unidad del mineral)", min_value=0.01, value=vol_inicial)
    anio = col5.number_input("Año", min_value=info["anio_min"], max_value=info["anio_max"] + 2,
                             value=info["anio_max"] + 1, step=1)
    trimestre = col6.selectbox("Trimestre", [1, 2, 3, 4])

    pagado = st.number_input("Regalía pagada en pesos (opcional, para comparar)", min_value=0.0, value=0.0,
                             step=1000000.0)

    if st.button("Estimar"):
        x = pd.DataFrame([{
            "volumen": volumen, "anio": anio, "trimestre_num": trimestre,
            "mineral": mineral, "nombre_departamento": depto, "gran_proyecto": gran,
        }])[columnas]
        estimado = float(modelo.predict(x)[0])
        factor = np.exp(rmse)

        c1, c2 = st.columns(2)
        c1.metric("Regalía estimada", pesos(estimado))
        c2.metric("Rango típico", f"{pesos(estimado / factor)} a {pesos(estimado * factor)}")

        if pagado > 0:
            diferencia = (pagado - estimado) / estimado
            if abs(np.log(pagado / estimado)) > 2 * rmse:
                st.warning(f"Lo pagado se aleja {diferencia:+.0%} de lo estimado. Conviene revisar la liquidación.")
            else:
                st.success(f"Lo pagado está dentro de lo esperado ({diferencia:+.0%}).")

with tab2:
    st.write("El archivo debe tener las columnas: " + ", ".join(columnas) +
             ". Si trae la columna regalias (lo pagado), se calcula la desviación.")
    archivo = st.file_uploader("Subir CSV", type="csv")

    if archivo is not None:
        datos = pd.read_csv(archivo)
        faltantes = [c for c in columnas if c not in datos.columns]
        if faltantes:
            st.error(f"Faltan columnas: {faltantes}")
        else:
            datos["regalia_estimada"] = modelo.predict(datos[columnas]).round(0)
            if "regalias" in datos.columns:
                datos["desviacion_%"] = (100 * (datos["regalias"] - datos["regalia_estimada"])
                                         / datos["regalia_estimada"]).round(1)
                datos["revisar"] = np.abs(np.log(datos["regalias"] / datos["regalia_estimada"])) > 2 * rmse
                st.write(f"Registros para revisar: {int(datos['revisar'].sum())} de {len(datos)}")
            st.dataframe(datos)
            st.download_button("Descargar resultados", datos.to_csv(index=False).encode("utf-8"),
                               "predicciones.csv")
