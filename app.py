# PRUEBA SOLEMNE N°3
# INGE B001 TALLER DE PROGRAMACIÓN II

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------------------------
# BLOQUE 1: CONFIGURACIÓN INICIAL DE LA PÁGINA
# -----------------------------------------------------------------------------
# Se define el título de la pestaña del navegador, el layout 'wide' para aprovechar
# el ancho de la pantalla y el estado inicial de la barra lateral.
st.set_page_config(
    page_title='Crypto Dashboard - Solemne 3', 
    layout='wide',
    initial_sidebar_state="expanded"
)

st.title("🪙 Dashboard de Criptomonedas")
st.markdown("Aplicación para analizar el mercado actual utilizando la API de CoinGecko.")

# -----------------------------------------------------------------------------
# BLOQUE 2: BARRA LATERAL (INPUTS DEL USUARIO)
# -----------------------------------------------------------------------------
# Esta sección captura las preferencias del usuario para filtrar los datos.
st.sidebar.header("⚙️ Configuración")

# Selector para determinar la moneda de conversión (USD, EUR, CLP).
moneda_base = st.sidebar.selectbox(
    "Moneda base:",
    ['USD', 'EUR', 'CLP'],
    index=0
)

# Selector para el criterio de ordenamiento de la API.
tipo_orden = st.sidebar.radio(
    "Ordenar por:",
    ['Capitalización', 'Volumen']
)

# Slider para limitar la cantidad de datos a descargar (evita saturar la API).
cantidad_monedas = st.sidebar.slider("Cantidad de monedas a analizar", 5, 50, 10)

# Campo de texto para filtrar localmente por nombre.
# Nota: Busca dentro de las monedas ya cargadas por el slider anterior.
filtro_nombre = st.sidebar.text_input("🔍 Buscar moneda (en la lista cargada):")

st.sidebar.markdown("---")
st.sidebar.caption("Datos provistos por CoinGecko API")

# -----------------------------------------------------------------------------
# BLOQUE 3: LÓGICA DE CONEXIÓN A LA API
# -----------------------------------------------------------------------------
# Se utiliza el decorador @st.cache_data para almacenar en caché los resultados
# y evitar llamadas excesivas a la API cada vez que se interactúa con la interfaz.
@st.cache_data
def cargar_datos(cantidad, moneda='usd', orden='market_cap_desc'):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': moneda.lower(),
        'order': orden,
        'per_page': cantidad,
        'page': 1,
        'sparkline': False 
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        
        # Manejo de respuestas HTTP
        if resp.status_code == 200:
            return pd.DataFrame(resp.json())
        elif resp.status_code == 429:
            st.warning("⚠️ API saturada (Error 429). Por favor espera unos segundos antes de recargar.")
            return pd.DataFrame()
        else:
            st.error(f"Error {resp.status_code} al consultar la API")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# Mapeos auxiliares para traducir la selección del usuario a parámetros de la API.
moneda_map = {'USD': 'usd', 'EUR': 'eur', 'CLP': 'clp'}
orden_map = {'Capitalización': 'market_cap_desc', 'Volumen': 'volume_desc'}
simbolo_moneda = {'usd': '$', 'eur': '€', 'clp': '$'}[moneda_map[moneda_base]]

# Ejecución de la función de carga de datos.
df = cargar_datos(cantidad_monedas, moneda_map[moneda_base], orden_map[tipo_orden])

# Validación crítica: Si el DataFrame está vacío, se detiene la ejecución.
if df.empty:
    st.warning("No se pudieron cargar los datos. Intenta más tarde.")
    st.stop()

# Aplicar filtro de búsqueda local si el usuario escribió algo.
if filtro_nombre:
    df = df[df['name'].str.contains(filtro_nombre, case=False) | df['symbol'].str.contains(filtro_nombre, case=False)]
    if df.empty:
        st.warning(f"No se encontraron monedas con el nombre '{filtro_nombre}' dentro del Top {cantidad_monedas} cargado.")
        st.stop()

# -----------------------------------------------------------------------------
# BLOQUE 4: VISUALIZACIÓN DE KPIs (INDICADORES CLAVE)
# -----------------------------------------------------------------------------
# Muestra métricas rápidas sobre la criptomoneda líder del set de datos actual.
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
if not df.empty:
    top_coin = df.iloc[0]
    col_kpi1.metric("🔥 Top 1 Mercado", top_coin['name'])
    col_kpi2.metric("💰 Precio Actual", f"{simbolo_moneda}{top_coin['current_price']:,.2f}")
    col_kpi3.metric("📈 Variación 24h", f"{top_coin['price_change_percentage_24h']:.2f}%", 
                    delta_color="normal" if top_coin['price_change_percentage_24h'] >= 0 else "inverse")

st.markdown("---")

# Creación de pestañas para organizar la información.
tab1, tab2, tab3 = st.tabs(["📊 Datos Crudos", "📈 Gráficos Interactivos", "📝 Conclusiones"])

# -----------------------------------------------------------------------------
# PESTAÑA 1: TABLA DE DATOS DETALLADA
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Listado de Criptomonedas")
    
    # Se seleccionan las columnas relevantes, incluyendo la imagen.
    cols_to_show = ['image', 'name', 'symbol', 'current_price', 'market_cap', 'total_volume', 'price_change_percentage_24h']

    # Se configura la tabla con formato específico para imágenes, monedas y porcentajes.
    st.dataframe(
        df[cols_to_show],
        column_config={
            "image": st.column_config.ImageColumn("Logo"), # Visualiza la URL como imagen
            "name": "Nombre",
            "symbol": "Símbolo",
            "current_price": st.column_config.NumberColumn(f"Precio ({moneda_base})", format=f"{simbolo_moneda}%.2f"),
            "market_cap": st.column_config.NumberColumn("Cap. Mercado", format=f"{simbolo_moneda}%.0f"),
            "total_volume": st.column_config.NumberColumn("Volumen Total", format=f"{simbolo_moneda}%.0f"),
            "price_change_percentage_24h": st.column_config.NumberColumn("Cambio 24h", format="%.2f%%", help="Variación en las últimas 24h")
        },
        use_container_width=True,
        hide_index=True
    )
    
    # Botón para descargar el dataset actual en formato CSV.
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar datos como CSV", csv, 'crypto_data.csv', 'text/csv')

# -----------------------------------------------------------------------------
# PESTAÑA 2: ANÁLISIS VISUAL (GRÁFICOS)
# -----------------------------------------------------------------------------
with tab2:
    st.header("Análisis Visual")

    col_g1, col_g2 = st.columns(2)
    
    # Gráfico 1: Barras simples para Capitalización de Mercado.
    with col_g1:
        st.subheader("Top Cap. de Mercado")
        st.bar_chart(df.head(10).set_index('name')['market_cap'])

    # Gráfico 2: Dispersión para analizar Precio vs Volatilidad.
    with col_g2:
        st.subheader("Relación Precio / Volatilidad")
        criterio_color = st.toggle("🎨 Colorear por Capitalización", value=True)
        color_chart = 'market_cap' if criterio_color else None
        
        st.scatter_chart(df, x='current_price', y='price_change_percentage_24h', color=color_chart, size='market_cap')

    # Gráfico 3: Comparación personalizada de Máximos y Mínimos.
    st.subheader("Comparación de Precios (Máximo vs Mínimo 24h)")
    monedas_default = df['name'].iloc[:3].tolist()
    seleccion = st.multiselect("Comparar monedas:", df['name'].tolist(), default=monedas_default)
    
    if seleccion:
        # Filtra el dataframe según la selección del usuario.
        df_r = df[df['name'].isin(seleccion)].set_index('name')[['low_24h', 'high_24h']]
        st.bar_chart(df_r)
    
    st.markdown("---")

    # Gráfico 4: Gráfico de Dona Avanzado con Matplotlib.
    st.subheader("Distribución de Volumen (Top 5)")

    col_chart, col_txt = st.columns([2, 1])

    with col_chart:
        top5 = df.head(5).copy()
    
        # Función interna para ocultar etiquetas de porcentajes muy pequeños.
        def mostrar_valor(pct):
            return f'{pct:.1f}%' if pct > 5 else ''

        # Creación de la figura y los ejes con fondo transparente para integración UI.
        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_alpha(0.0) 
        ax.patch.set_alpha(0.0)

        colors = plt.cm.Set3(np.linspace(0, 1, len(top5)))

        wedges, texts, autotexts = ax.pie(
            top5['total_volume'], 
            labels=None,           
            autopct=mostrar_valor, 
            startangle=90,
            colors=colors,
            pctdistance=0.80,      
            wedgeprops=dict(width=0.5, edgecolor='white') # Crea el efecto de "Dona"
        )

        # Configuración de estilo para los textos internos del gráfico.
        plt.setp(autotexts, size=10, weight="bold", color="black")
        
        # Texto central informativo.
        ax.text(0, 0, 'VOLUMEN\nTOTAL', ha='center', va='center', fontsize=10, fontweight='bold')

        # Leyenda externa para identificar cada segmento.
        total = top5['total_volume'].sum()
        etiquetas_leyenda = [f"{row['name']} ({(row['total_volume']/total)*100:.1f}%)" for index, row in top5.iterrows()]

        ax.legend(wedges, etiquetas_leyenda,
                  title="Criptomonedas",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        st.pyplot(fig)

    with col_txt:
        st.markdown("""
        **Detalle del Gráfico:**
        
        Se muestra la proporción de volumen transado por las 5 principales monedas cargadas.
        
        *Nota: Se utiliza Matplotlib para generar una visualización personalizada tipo 'Donut Chart'.*
        """)

# -----------------------------------------------------------------------------
# PESTAÑA 3: CONCLUSIONES AUTOMÁTICAS
# -----------------------------------------------------------------------------
with tab3:
    st.header("Interpretación")
    # Se calculan dinámicamente la mejor y peor moneda del día.
    mejor = df.loc[df['price_change_percentage_24h'].idxmax()]
    peor = df.loc[df['price_change_percentage_24h'].idxmin()]
    
    st.info(f"💡 **Dato clave:** La criptomoneda con mayor crecimiento hoy es **{mejor['name']}** (+{mejor['price_change_percentage_24h']:.2f}%).")
    
    st.markdown(f"""
    ### Resumen del Mercado
    1. **Liderazgo:** {df.iloc[0]['name']} domina con un precio de {simbolo_moneda}{df.iloc[0]['current_price']:,.2f}.
    2. **Tendencia:** La moneda con peor desempeño en este grupo es **{peor['name']}** ({peor['price_change_percentage_24h']:.2f}%).
    3. **Liquidez:** El gráfico de distribución en la pestaña anterior destaca dónde se concentra el volumen de operaciones.
    """)
