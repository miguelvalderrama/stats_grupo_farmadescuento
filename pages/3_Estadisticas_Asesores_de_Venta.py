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
st.set_page_config(page_title='Estadistica Asesores', page_icon=':bar_chart:', layout='wide')

hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
st.markdown(hide_img_fs, unsafe_allow_html=True)

# Title
st.title('👩‍⚕💛 Estadisticas de Asesores de Venta')

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