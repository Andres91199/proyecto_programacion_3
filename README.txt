# Dashboard de Criptomonedas

Proyecto Solemne 3 - Taller de Programación II
INGE B001 - Universidad San Sebastián

## Descripción

Aplicación web interactiva que consume la API REST de CoinGecko para mostrar 
información actualizada sobre criptomonedas, incluyendo precios, capitalización 
de mercado y variaciones en las últimas 24 horas.

## Características

- Consulta de datos en tiempo real mediante API REST
- Visualización de datos en tablas interactivas
- 4 gráficos distintos para análisis visual
- Filtros configurables (moneda base, tipo de orden, cantidad)
- Interfaz organizada en pestañas

## Requisitos

- Python 3.13 o superior
- Librerías listadas en requirements.txt

## Instalación

1. Asegúrate de tener Python instalado
2. Instala las dependencias:

pip install -r requirements.txt

## Ejecución

Para ejecutar la aplicación:

python -m streamlit run app.py

La aplicación se abrirá automáticamente en tu navegador en http://localhost:8501

## Uso

1. Ajusta los parámetros en la barra lateral:
   - Selecciona la moneda base (USD, EUR, CLP)
   - Elige el criterio de ordenamiento
   - Define la cantidad de criptomonedas a analizar

2. Explora las pestañas:
   - Datos Crudos: Tabla con información detallada
   - Gráficos Interactivos: Visualizaciones del mercado
   - Conclusiones: Interpretación de resultados

## API Utilizada

CoinGecko API (https://www.coingecko.com/api)
- Endpoint: /api/v3/coins/markets
- Método: GET
- Sin necesidad de autenticación

## Autores

- Alberto (GitHub: @punkyyy01)
- Tomás (@cookiecodespy)
- Andrés Abarca

## Fecha

Noviembre 2025
