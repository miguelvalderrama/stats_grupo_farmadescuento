import streamlit as st
import pandas as pd
import numpy as np
import consultas
import datetime

if st.session_state.get("role") != "admin":
    st.error("No tienes permisos para acceder a esta pagina.")
    st.stop()

# Config
st.set_page_config(page_title='Estadistica Asesores', page_icon=':bar_chart:', layout='wide')

hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
st.markdown(hide_img_fs, unsafe_allow_html=True)

# Title
st.title('🖨️ Estadisticas de Maquinas Fiscales')

# Style
with open('style.css')as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html = True)

conexiones = consultas.get_data('Conexiones')
conexiones = conexiones[conexiones['grupo'] == 'SNFDO']
farmacias = [nombre for nombre in conexiones['nombre']]

c1, c2, c3, c4 = st.columns(4)

with c1:
    date_init = st.date_input(
        "Desde:")
with c2:
    date_end = st.date_input(
        "Hasta:")
with c3:
    option = st.selectbox('Farmacia a consultar:', options=farmacias)
farmacia = conexiones[conexiones['nombre'] == option].iloc[0]

if date_init > date_end:
    st.error('La fecha inicial debe ser menor que la final.')
    st.stop()

# Data Sources
stats_maquinas = consultas.get_data('estadisticas de maquinas fiscales', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])
# stats_maquinas= stats_maquinas.style.format({
#     'Util Ultimo Ingreso': '{:,.2f}%'.format,
#     'Util Costo Actual': '{:,.2f}%'.format,
#     'Costo Ingreso': '{:,.2f}'.format,
#     'Costo Actual': '{:,.2f}'.format,
# })


c1, c2 = st.columns(2)
with c1:
    st.dataframe(stats_maquinas, use_container_width=True)