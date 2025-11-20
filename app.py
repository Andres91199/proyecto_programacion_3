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
st.set_page_config(
    page_title='Crypto Lab - Solemne 3', 
    layout='wide',
    initial_sidebar_state="expanded"
)

# Cambio: Título con un estilo más geométrico/tech
st.title("💠 Crypto Lab: Análisis de Mercado")
st.markdown("Entorno de visualización de activos digitales mediante CoinGecko API.")

# -----------------------------------------------------------------------------
# BLOQUE 2: BARRA LATERAL (INPUTS DEL USUARIO)
# -----------------------------------------------------------------------------
# Cambio: 'Centro de Control' en lugar de 'Configuración'
st.sidebar.header("🎛️ Centro de Control")

moneda_base = st.sidebar.selectbox(
    "Divisa de referencia:",
    ['USD', 'EUR', 'CLP'],
    index=0
)

tipo_orden = st.sidebar.radio(
    "Criterio de clasificación:",
    ['Capitalización', 'Volumen']
)

cantidad_monedas = st.sidebar.slider("Alcance del análisis (N° monedas)", 5, 50, 10)

# Cambio: 'Telescopio' para la búsqueda
filtro_nombre = st.sidebar.text_input("🔭 Rastrear activo específico:")

st.sidebar.markdown("---")
st.sidebar.caption("📡 Datos sincronizados con CoinGecko")

# -----------------------------------------------------------------------------
# BLOQUE 3: LÓGICA DE CONEXIÓN A LA API
# -----------------------------------------------------------------------------
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
        
        if resp.status_code == 200:
            return pd.DataFrame(resp.json())
        elif resp.status_code == 429:
            # Cambio: Icono de 'Construcción/Espera'
            st.warning("🚧 Tráfico denso en la API (Error 429). Reintentando enlace...")
            return pd.DataFrame()
        else:
            st.error(f"🚫 Fallo de protocolo {resp.status_code}")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"💀 Error fatal de conexión: {e}")
        return pd.DataFrame()

moneda_map = {'USD': 'usd', 'EUR': 'eur', 'CLP': 'clp'}
orden_map = {'Capitalización': 'market_cap_desc', 'Volumen': 'volume_desc'}
simbolo_moneda = {'usd': '$', 'eur': '€', 'clp': '$'}[moneda_map[moneda_base]]

df = cargar_datos(cantidad_monedas, moneda_map[moneda_base], orden_map[tipo_orden])

if df.empty:
    st.warning("☁️ No se pudo establecer conexión con la nube de datos.")
    st.stop()

if filtro_nombre:
    df = df[df['name'].str.contains(filtro_nombre, case=False) | df['symbol'].str.contains(filtro_nombre, case=False)]
    if df.empty:
        st.warning(f"👻 El activo '{filtro_nombre}' no fue detectado en el radar actual.")
        st.stop()

# -----------------------------------------------------------------------------
# BLOQUE 4: VISUALIZACIÓN DE KPIs (INDICADORES CLAVE)
# -----------------------------------------------------------------------------
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
if not df.empty:
    top_coin = df.iloc[0]
    # Cambio: Iconos de Cohete, Tarjeta y Ola para dar sensación de movimiento
    col_kpi1.metric("🚀 Activo Dominante", top_coin['name'])
    col_kpi2.metric("💳 Cotización", f"{simbolo_moneda}{top_coin['current_price']:,.2f}")
    col_kpi3.metric("🌊 Flujo 24h", f"{top_coin['price_change_percentage_24h']:.2f}%", 
                    delta_color="normal" if top_coin['price_change_percentage_24h'] >= 0 else "inverse")

st.markdown("---")

# Cambio: Pestañas con temática de Archivo, Radar y Brújula
tab1, tab2, tab3 = st.tabs(["🗃️ Bóveda de Datos", "📡 Radar Visual", "🧭 Hallazgos"])

# -----------------------------------------------------------------------------
# PESTAÑA 1: TABLA DE DATOS DETALLADA
# -----------------------------------------------------------------------------
with tab1:
    st.subheader("Inventario de Activos")
    
    cols_to_show = ['image', 'name', 'symbol', 'current_price', 'market_cap', 'total_volume', 'price_change_percentage_24h']

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
    
    csv = df.to_csv(index=False).encode('utf-8')
    # Cambio: Disco para descarga
    st.download_button("💿 Exportar Dataset (CSV)", csv, 'crypto_lab_data.csv', 'text/csv')

# -----------------------------------------------------------------------------
# PESTAÑA 2: ANÁLISIS VISUAL (GRÁFICOS)
# -----------------------------------------------------------------------------
with tab2:
    st.header("Telemétrica de Mercado")

    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.subheader("Dominio de Capitalización")
        st.bar_chart(df.head(10).set_index('name')['market_cap'])

    with col_g2:
        st.subheader("Correlación Precio / Volatilidad")
        # Cambio: Pincel para colorear
        criterio_color = st.toggle("🖌️ Pigmentar por Dimensión (Cap)", value=True)
        color_chart = 'market_cap' if criterio_color else None
        
        st.scatter_chart(df, x='current_price', y='price_change_percentage_24h', color=color_chart, size='market_cap')

    st.subheader("Amplitud Térmica (Máx vs Mín 24h)")
    monedas_default = df['name'].iloc[:3].tolist()
    seleccion = st.multiselect("Comparativa de activos:", df['name'].tolist(), default=monedas_default)
    
    if seleccion:
        df_r = df[df['name'].isin(seleccion)].set_index('name')[['low_24h', 'high_24h']]
        st.bar_chart(df_r)
    
    st.markdown("---")

    st.subheader("Participación de Volumen (Top 5)")

    col_chart, col_txt = st.columns([2, 1])

    with col_chart:
        top5 = df.head(5).copy()
    
        def mostrar_valor(pct):
            return f'{pct:.1f}%' if pct > 5 else ''

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
            wedgeprops=dict(width=0.5, edgecolor='white')
        )

        plt.setp(autotexts, size=10, weight="bold", color="black")
        
        ax.text(0, 0, 'VOLUMEN\nTOTAL', ha='center', va='center', fontsize=10, fontweight='bold')

        total = top5['total_volume'].sum()
        etiquetas_leyenda = [f"{row['name']} ({(row['total_volume']/total)*100:.1f}%)" for index, row in top5.iterrows()]

        ax.legend(wedges, etiquetas_leyenda,
                  title="Tokens",
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1))
        
        st.pyplot(fig)

    with col_txt:
        st.markdown("""
        **Interpretación del Radar:**
        
        Este diagrama de anillo ilustra la liquidez relativa entre los activos dominantes.
        
        *Renderizado vía motor Matplotlib.*
        """)

# -----------------------------------------------------------------------------
# PESTAÑA 3: CONCLUSIONES AUTOMÁTICAS
# -----------------------------------------------------------------------------
with tab3:
    st.header("Síntesis de Inteligencia")
    mejor = df.loc[df['price_change_percentage_24h'].idxmax()]
    peor = df.loc[df['price_change_percentage_24h'].idxmin()]
    
    # Cambio: Rayo o Estrella para el "Insight"
    st.info(f"⚡ **Flash Insight:** El activo con mayor tracción alcista hoy es **{mejor['name']}** (+{mejor['price_change_percentage_24h']:.2f}%).")
    
    st.markdown(f"""
    ### 🧬 Diagnóstico de Mercado
    1. **Hegemonía:** {df.iloc[0]['name']} mantiene la supremacía con un valor de {simbolo_moneda}{df.iloc[0]['current_price']:,.2f}.
    2. **Zona Fría:** El desempeño más bajo del clúster lo presenta **{peor['name']}** ({peor['price_change_percentage_24h']:.2f}%).
    3. **Liquidez:** Verifica el diagrama radial en la pestaña anterior para confirmar dónde se agrupa el capital.
    """)
