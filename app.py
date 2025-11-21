# PRUEBA SOLEMNE N°3
# INGE TALLER DE PROGRAMACIÓN II

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import numpy as np

# -----------------------------------------------------------------------------
# BLOQUE 1: CONFIGURACIÓN DE ENTORNO Y VISTA
# -----------------------------------------------------------------------------
# Configuración inicial de la página. 
# 'layout="wide"' permite utilizar todo el ancho del navegador.
st.set_page_config(
    page_title='Crypto Lab - Solemne 3', 
    layout='wide',
    initial_sidebar_state="expanded"
)

# Título y descripción principal de la aplicación
st.title("💠 Crypto Lab: Análisis de Mercado")
st.markdown("Entorno de visualización de activos digitales mediante CoinGecko API.")

# -----------------------------------------------------------------------------
# BLOQUE 2: PARAMETRIZACIÓN E INTERFAZ DE CONTROL (SIDEBAR)
# -----------------------------------------------------------------------------
st.sidebar.header("🎛️ Centro de Control")

# Selector para la moneda de conversión (Variable de Estado).
# Define en qué divisa se mostrarán los precios y volúmenes.
moneda_base = st.sidebar.selectbox(
    "Divisa de referencia:",
    ['USD', 'EUR', 'CLP'],
    index=0
)

# Selector para el criterio de ordenamiento de la API.
tipo_orden = st.sidebar.radio(
    "Criterio de clasificación:",
    ['Capitalización', 'Volumen']
)

# Slider numérico para limitar la carga de datos (Payload).
# Útil para controlar el rendimiento y no exceder límites de la API.
cantidad_monedas = st.sidebar.slider("Alcance del análisis (N° monedas)", 5, 50, 10)

# Input de texto para filtrado en tiempo real.
filtro_nombre = st.sidebar.text_input("🔭 Rastrear activo específico:")

st.sidebar.markdown("---")
st.sidebar.caption("📡 Datos sincronizados con CoinGecko")

# -----------------------------------------------------------------------------
# BLOQUE 3: CAPA DE DATOS Y CONEXIÓN API
# -----------------------------------------------------------------------------

# Decorador @st.cache_data:
# Optimiza la aplicación almacenando el resultado de la función en memoria caché.
# Evita llamar a la API externa cada vez que el usuario interactúa con un filtro local,
# previniendo el error 429 (Too Many Requests) y mejorando la velocidad de carga.
@st.cache_data
def cargar_datos(cantidad, moneda='usd', orden='market_cap_desc'):
    """
    Realiza una petición HTTP GET a la API de CoinGecko.
    Maneja excepciones y códigos de estado HTTP.
    """
    url = "https://api.coingecko.com/api/v3/coins/markets"

    # Parámetros de la consulta (Query Strings)
    params = {
        'vs_currency': moneda.lower(),
        'order': orden,
        'per_page': cantidad,
        'page': 1,
        'sparkline': False 
    }

    try:
        # Timeout de 10 segundos para evitar bloqueos indefinidos si la red falla
        resp = requests.get(url, params=params, timeout=10)

        if resp.status_code == 200:
            # Retorna un DataFrame si la petición fue exitosa
            return pd.DataFrame(resp.json())
        elif resp.status_code == 429:
            # Manejo específico para límite de tasa de la API
            st.warning("🚧 Tráfico denso en la API (Error 429). Reintentando enlace...")
            return pd.DataFrame()
        else:
            # Manejo de otros errores HTTP (4xx, 5xx)
            st.error(f"🚫 Fallo de protocolo {resp.status_code}")
            return pd.DataFrame()

    except Exception as e:
        # Captura de errores de conexión (DNS, SSL, desconexión)
        st.error(f"💀 Error fatal de conexión: {e}")
        return pd.DataFrame()

# Mapeo de diccionarios:
# Traduce las opciones legibles de la UI a parámetros técnicos que la API entiende.
moneda_map = {'USD': 'usd', 'EUR': 'eur', 'CLP': 'clp'}
orden_map = {'Capitalización': 'market_cap_desc', 'Volumen': 'volume_desc'}
simbolo_moneda = {'usd': '$', 'eur': '€', 'clp': '$'}[moneda_map[moneda_base]]

# Invocación de la función de carga
df = cargar_datos(cantidad_monedas, moneda_map[moneda_base], orden_map[tipo_orden])

# Validación de integridad de datos:
# Si el DataFrame está vacío, detenemos la ejecución para evitar errores en los gráficos.
if df.empty:
    st.warning("☁️ No se pudo establecer conexión con la nube de datos.")
    st.stop()

# Lógica de filtrado local (Post-Procesamiento):
# Filtra el DataFrame por nombre o símbolo si el usuario escribió algo.
if filtro_nombre:
    df = df[df['name'].str.contains(filtro_nombre, case=False) | df['symbol'].str.contains(filtro_nombre, case=False)]
    if df.empty:
        st.warning(f"👻 El activo '{filtro_nombre}' no fue detectado en el radar actual.")
        st.stop()

# -----------------------------------------------------------------------------
# BLOQUE 4: DASHBOARD Y VISUALIZACIÓN
# -----------------------------------------------------------------------------
# Definición de columnas para métricas clave (KPIs)
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

if not df.empty:
    # Selección del activo con mayor ranking actual (fila 0)
    top_coin = df.iloc[0]

    # Visualización de métricas con indicador de variación (delta)
    col_kpi1.metric("🚀 Activo Dominante", top_coin['name'])
    col_kpi2.metric("💳 Cotización", f"{simbolo_moneda}{top_coin['current_price']:,.2f}")
    col_kpi3.metric("🌊 Flujo 24h", f"{top_coin['price_change_percentage_24h']:.2f}%", 
                    delta_color="normal" if top_coin['price_change_percentage_24h'] >= 0 else "inverse")

st.markdown("---")

# Creación de pestañas para organizar la información visualmente
tab1, tab2, tab3 = st.tabs(["🗃️ Bóveda de Datos", "📡 Radar Visual", "🧭 Hallazgos"])

# -----------------------------------------------------------------------------
# PESTAÑA 1: REPRESENTACIÓN TABULAR
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Inventario de Activos")

    cols_to_show = ['image', 'name', 'symbol', 'current_price', 'market_cap', 'total_volume', 'price_change_percentage_24h']

    # st.dataframe con column_config para formateo avanzado (imágenes y números)
    st.dataframe(
        df[cols_to_show],
        column_config={
            "image": st.column_config.ImageColumn("Token"),
            "name": "Identificador",
            "symbol": "Ticker",
            "current_price": st.column_config.NumberColumn(f"Valor ({moneda_base})", format=f"{simbolo_moneda}%.2f"),
            "market_cap": st.column_config.NumberColumn("Cap. Global", format=f"{simbolo_moneda}%.0f"),
            "total_volume": st.column_config.NumberColumn("Volumen Op.", format=f"{simbolo_moneda}%.0f"),
            "price_change_percentage_24h": st.column_config.NumberColumn("Delta 24h", format="%.2f%%", help="Volatilidad diaria")
        },
        use_container_width=True,
        hide_index=True
    )

    # Funcionalidad de exportación a CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💿 Exportar Dataset (CSV)", csv, 'crypto_lab_data.csv', 'text/csv')

# -----------------------------------------------------------------------------
# PESTAÑA 2: ANALÍTICA GRÁFICA
# -----------------------------------------------------------------------------
with tab2:
    st.header("Telemétrica de Mercado")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Dominio de Capitalización")
        # Gráfico de barras nativo de Streamlit.
        # Se indexa por nombre para que el eje X muestre las etiquetas correctas.
        st.bar_chart(df.head(10).set_index('name')['market_cap'])

    with col_g2:
        st.subheader("Correlación Precio / Volatilidad")
        criterio_color = st.toggle("🖌️ Pigmentar por Dimensión (Cap)", value=True)
        
        # PRE-PROCESAMIENTO PARA GRÁFICOS:
        # Se renombra las columnas del DataFrame temporalmente para que los tooltips
        # y ejes de los gráficos muestren etiquetas profesionales en español
        # en lugar de los nombres técnicos de las variables (e.g., 'Precio Actual' vs 'current_price').
        df_scatter = df.rename(columns={
            'current_price': 'Precio Actual',
            'price_change_percentage_24h': 'Variación 24h (%)',
            'market_cap': 'Capitalización'
        })
        
        # Lógica condicional para el coloreado del gráfico
        color_chart = 'Capitalización' if criterio_color else None

        # Gráfico de dispersión (Scatter Chart) con los nuevos nombres de columnas
        st.scatter_chart(
            df_scatter, 
            x='Precio Actual', 
            y='Variación 24h (%)', 
            color=color_chart, 
            size='Capitalización'
        )

    # Visualización de Rangos (High/Low).
    st.subheader("Amplitud Térmica (Máx vs Mín 24h)")
    monedas_default = df['name'].iloc[:3].tolist()
    seleccion = st.multiselect("Comparativa de activos:", df['name'].tolist(), default=monedas_default)

    if seleccion:
        # Filtramos datos y renombramos columnas para la visualización correcta en la leyenda
        df_r = df[df['name'].isin(seleccion)].set_index('name')[['low_24h', 'high_24h']]
        df_r = df_r.rename(columns={'low_24h': 'Mínimo 24h', 'high_24h': 'Máximo 24h'})
        
        st.bar_chart(df_r)

    st.markdown("---")

    # Integración Avanzada con Matplotlib (Donut Chart).
    # Se utiliza Matplotlib para crear gráficos circulares personalizados que
    # Streamlit no soporta nativamente con este nivel de detalle.
    st.subheader("Participación de Volumen (Top 5)")

    col_chart, col_txt = st.columns([2, 1])

    with col_chart:
        top5 = df.head(5).copy()

        # Función lambda auxiliar para ocultar porcentajes pequeños y limpiar el gráfico
        def mostrar_valor(pct):
            return f'{pct:.1f}%' if pct > 5 else ''

        fig, ax = plt.subplots(figsize=(6, 6))

        # Configuración de fondo transparente para integración con modo claro/oscuro
        fig.patch.set_alpha(0.0) 
        ax.patch.set_alpha(0.0)

        colors = plt.cm.Set3(np.linspace(0, 1, len(top5)))

        # Renderizado del gráfico de anillo (Pie Chart con wedgeprops)
        wedges, texts, autotexts = ax.pie(
            top5['total_volume'], 
            labels=None,            
            autopct=mostrar_valor, 
            startangle=90,
            colors=colors,
            pctdistance=0.80,       
            wedgeprops=dict(width=0.5, edgecolor='white')
        )

        # Estilización de etiquetas internas y centrales
        plt.setp(autotexts, size=10, weight="bold", color="black")
        ax.text(0, 0, 'VOLUMEN\nTOTAL', ha='center', va='center', fontsize=10, fontweight='bold')

        # Cálculo de leyenda externa personalizada
        total = top5['total_volume'].sum()
        etiquetas_leyenda = [f"{row['name']} ({(row['total_volume']/total)*100:.1f}%)" for index, row in top5.iterrows()]

        ax.legend(wedges, etiquetas_leyenda,
                  title="Tokens",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))

        # Despliegue del objeto figura de Matplotlib en Streamlit
        st.pyplot(fig)

    with col_txt:
        st.markdown("""
        **Interpretación del Radar:**

        Este diagrama de anillo ilustra la liquidez relativa entre los activos dominantes.
        
        *Renderizado vía motor Matplotlib.*
        """)

# -----------------------------------------------------------------------------
# PESTAÑA 3: INSIGHTS AUTOMATIZADOS
# -----------------------------------------------------------------------------
with tab3:
    st.header("Síntesis de Inteligencia")
    
    # Análisis descriptivo automático: Detección de extremos
    mejor = df.loc[df['price_change_percentage_24h'].idxmax()]
    peor = df.loc[df['price_change_percentage_24h'].idxmin()]

    st.info(f"⚡ **Flash Insight:** El activo con mayor tracción alcista hoy es **{mejor['name']}** (+{mejor['price_change_percentage_24h']:.2f}%).")

    st.markdown(f"""
    ### 🧬 Diagnóstico de Mercado
    1. **Hegemonía:** {df.iloc[0]['name']} mantiene la supremacía con un valor de {simbolo_moneda}{df.iloc[0]['current_price']:,.2f}.
    2. **Zona Fría:** El desempeño más bajo del clúster lo presenta **{peor['name']}** ({peor['price_change_percentage_24h']:.2f}%).
    3. **Liquidez:** Verifica el diagrama radial en la pestaña anterior para confirmar dónde se agrupa el capital.
    """)
