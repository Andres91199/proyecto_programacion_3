# Dashboard de Criptomonedas
# Dashboard de criptomonedas

Proyecto Solemne 3 - Taller de Programación II (INGE B001)

## Resumen

Aplicación en Streamlit que consulta la API pública de CoinGecko mediante `requests`, organiza los resultados con pandas y los muestra en una tabla simple, cuatro gráficos básicos y dos métricas. Todo el contenido se presenta en español para mantener una documentación consistente.

## Requisitos

1. Python 3.13 o superior.
2. Dependencias listadas en `requirements.txt`.

```
pip install -r requirements.txt
```

## Ejecución

```
python -m streamlit run app.py
```

La aplicación se abre en `http://localhost:8501`. Desde la barra lateral puedes cambiar la moneda base (USD/EUR/CLP), el tipo de orden (capitalización o volumen) y la cantidad de monedas consultadas.

## Visualización

- Tabla principal con separador de miles en los valores monetarios.
- Gráficos nativos de Streamlit: barras de capitalización, dispersión precio vs variación, barra de rangos alto/bajo y torta con el volumen de las 5 primeras monedas.
- Métrica con la moneda líder y su variación diaria.

## Cambios recientes

- Tabla y métricas ahora muestran separadores de miles para evitar confusiones.
- README resumido y unificado en español.

## Autores

- Alberto (@punkyyy01)
- Tomás (@cookiecodespy)
- Andrés Abarca
