import streamlit as st
import pandas as pd
import consultas
import datetime
import altair as alt

if st.session_state.get("role") != "admin":
    st.error("No tienes permisos para acceder a esta pagina.")
    st.stop()

# Global Variables
theme_plotly = None # None or streamlit
week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Config
st.set_page_config(page_title='Estadistica Compras/Ventas', page_icon=':bar_chart:', layout='wide')

hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
st.markdown(hide_img_fs, unsafe_allow_html=True)

# Title
st.title('🎯 Estadisticas de Productos')

# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

conexiones = consultas.get_data('Conexiones')
conexiones = conexiones[conexiones['grupo'] == 'SNFDO']
farmacias = [nombre for nombre in conexiones['nombre']]

c1, c2, c3, c4 = st.columns(4)

with c1:
    date_init = st.date_input(
        "Desde:",
        datetime.datetime.today())
with c2:
    date_end = st.date_input(
        "Hasta:",
        datetime.datetime.today())
with c3:
    option = st.selectbox('Farmacia a consultar:', options=farmacias)
farmacia = conexiones[conexiones['nombre'] == option].iloc[0]

if date_init > date_end:
    st.error('La fecha inicial debe ser menor que la final.')
    st.stop()

# Data Sources
stats_mayor_utilidad = consultas.get_data('estadisticas productos con mayor utilidad', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])

stats_mayor_utilidad['Stock'] = stats_mayor_utilidad['Stock'].astype(int)
stats_mayor_utilidad['Cantidad Vendida'] = stats_mayor_utilidad['Cantidad Vendida'].astype(int)
stats_mayor_utilidad['Costo Ingreso'] = stats_mayor_utilidad['Costo Ingreso'].astype(float)
stats_mayor_utilidad['Costo Actual'] = stats_mayor_utilidad['Costo Actual'].astype(float)
stats_mayor_utilidad['Util Ultimo Ingreso'] = stats_mayor_utilidad['Util Ultimo Ingreso'].astype(float)
stats_mayor_utilidad['Util Costo Actual'] = stats_mayor_utilidad['Util Costo Actual'].astype(float)

stats_mayor_utilidad = stats_mayor_utilidad.style.format({
    'Util Ultimo Ingreso': '{:,.2f}%'.format,
    'Util Costo Actual': '{:,.2f}%'.format,
    'Costo Ingreso': '{:,.2f}%'.format,
    'Costo Actual': '{:,.2f}%'.format,
})

st.subheader('Productos Con Mayor Utilidad')
st.dataframe(stats_mayor_utilidad, use_container_width=True)