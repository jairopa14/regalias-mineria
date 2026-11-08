# Estimador de regalías mineras en Colombia

Proyecto integrador de la Maestría en Ciencia de Datos (UPB), hecho con la metodología CRISP-DM.

El modelo estima cuánto se paga de regalías (en pesos) según el mineral, el volumen explotado, el departamento, el año, el trimestre y si es un gran proyecto o no. La idea es usarlo para detectar pagos que no cuadran con el volumen declarado.

Autor: Jairo

## Datos

Agencia Nacional de Minería, "ANM Volumen de Explotación de Minerales Asociados a Pagos de Regalías", en Datos Abiertos Colombia: https://www.datos.gov.co/d/r85m-vv6c

Descargado el 7 de noviembre de 2026 (79.151 registros, 2012 a 2026). Los registros de 2026 se dejaron aparte como datos nuevos.

## Resultados en el conjunto de prueba

| Modelo | RMSE (log) | R2 (log) |
|---|---|---|
| HistGradientBoosting (elegido) | 0,467 | 0,980 |
| Bagging | 0,486 | 0,979 |
| Votación | 0,501 | 0,977 |
| Árbol de decisión ajustado | 0,558 | 0,972 |
| Ridge / Regresión lineal | 0,573 | 0,971 |

## Archivos

- `app.py`: aplicación de Streamlit
- `model/modelo_regalias.joblib`: pipeline completo (preprocesamiento y modelo)
- `model/metadata.json`: categorías válidas y métricas que usa la app
- `Proyecto_Integrador_Regalias_ANM.ipynb`: notebook con todo el proceso
- `data/`: dataset original, registros de 2026 y un CSV de ejemplo para probar la carga por lotes
- `artifacts/`: reporte de ydata-profiling y figuras

## Cómo correrlo

```
pip install -r requirements.txt
streamlit run app.py
```

App publicada: (pegar aquí la URL de Streamlit)
