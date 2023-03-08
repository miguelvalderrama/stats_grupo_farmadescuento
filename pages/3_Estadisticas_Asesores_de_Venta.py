import streamlit as st
import pandas as pd
import numpy as np
import consultas
import datetime
import altair as alt
import chart

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
        datetime.date.today())
with c2:
    date_end = st.date_input(
        "Hasta:",
        datetime.date.today())
with c3:
    option = st.selectbox('Farmacia a consultar:', options=farmacias)
farmacia = conexiones[conexiones['nombre'] == option].iloc[0]

usuarios = consultas.get_data('Usuarios', host=farmacia['servidor'], user=farmacia['nomusua'], password=farmacia['clave'], database=farmacia['basedata'])
usuarios = [nombre for nombre in usuarios['nombre']]

c1, c2 = st.columns(2)
with c1:
    asesor = st.multiselect('Asesores:', usuarios)

if date_init > date_end:
    st.error('La fecha inicial debe ser menor que la final.')
    st.stop()

# Data Sources
stats_asesores = consultas.get_data('estadisticas de asesor', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])
stats_devoluciones_asesores = consultas.get_data('estadisticas de devoluciones asesores', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])

if len(asesor) > 0:
    stats_asesores = stats_asesores.query("Usuario == @asesor")
    stats_devoluciones_asesores = stats_devoluciones_asesores.query("Usuario == @asesor")

stats_asesores['Ventas Bs'] = np.where((stats_asesores['Fecha']==stats_devoluciones_asesores['Fecha']) & (stats_asesores['Usuario']==stats_devoluciones_asesores['Usuario']), stats_asesores['Ventas Bs'] - stats_devoluciones_asesores['Monto Devolucion Bs'], stats_asesores['Ventas Bs'])
stats_asesores['Ventas $'] = np.where((stats_asesores['Fecha']==stats_devoluciones_asesores['Fecha']) & (stats_asesores['Usuario']==stats_devoluciones_asesores['Usuario']), stats_asesores['Ventas $'] - stats_devoluciones_asesores['Monto Devolucion $'], stats_asesores['Ventas $'])
stats_asesores['Unidades'] = np.where((stats_asesores['Fecha']==stats_devoluciones_asesores['Fecha']) & (stats_asesores['Usuario']==stats_devoluciones_asesores['Usuario']), stats_asesores['Unidades'] - stats_devoluciones_asesores['Unidades Devueltas'], stats_asesores['Unidades'])

stats_asesores['Unidades'] = stats_asesores['Unidades'].astype(int)
stats_asesores['Clientes'] = stats_asesores['Clientes'].astype(int)
stats_asesores['Ventas Bs'] = stats_asesores['Ventas Bs'].astype(float)
stats_asesores['Ventas $'] = stats_asesores['Ventas $'].astype(float)
stats_asesores['Ticket Promedio'] = stats_asesores['Ticket Promedio'].astype(float)
stats_asesores['UPT'] = stats_asesores['UPT'].astype(float)

stats_devoluciones_asesores['Unidades Devueltas'] = stats_devoluciones_asesores['Unidades Devueltas'].astype(int)
stats_devoluciones_asesores['Monto Devolucion Bs'] = stats_devoluciones_asesores['Monto Devolucion Bs'].astype(float)
stats_devoluciones_asesores['Monto Devolucion $'] = stats_devoluciones_asesores['Monto Devolucion $'].astype(float)

c1, c2  = st.columns(2)
with c1:
    st.write('**Detallado Diario:**')
    st.dataframe(stats_asesores, use_container_width=True)

    st.write('**Devoluciones Totales Por Asesor:**')
    stats_devoluciones_asesores.drop(columns=['Fecha'], inplace=True)
    stats_devoluciones_asesores = stats_devoluciones_asesores.groupby(['Usuario']).sum()
    st.dataframe(stats_devoluciones_asesores, use_container_width=True)
with c2:
    st.write('**Totales Por Usuario:**')
    stats_asesores['Fecha'] = pd.to_datetime(stats_asesores['Fecha'])
    stats_asesores = stats_asesores.set_index('Fecha')

    mean_stats_asesores = stats_asesores.groupby(['Usuario']).mean()
    mean_stats_asesores['Clientes'] = mean_stats_asesores['Clientes'].astype(int)
    mean_stats_asesores['Unidades'] = mean_stats_asesores['Unidades'].astype(int)

    stats_asesores = stats_asesores.reset_index()
    df_asesores = stats_asesores.copy()
    df_asesores.drop(columns=['Fecha', 'UPT', 'Ticket Promedio'], inplace=True)
    df_asesores = df_asesores.groupby(['Usuario']).sum()

    st.dataframe(df_asesores, use_container_width=True)
    st.write('**Promedios Por Usuario:**')
    st.dataframe(mean_stats_asesores.round(2), use_container_width=True)

if (date_end - date_init) > datetime.timedelta(days=0) and len(stats_asesores['Usuario'].unique()) <= 10 and len(stats_asesores) > 0:
    chart_ventas_usuario = chart.get_chart(stats_asesores, 'Ventas Por Area Usuario', 'Ventas Bs', 'Monto Bs', 'Usuario', True, 'mean(Ventas Bs)')
    st.altair_chart(chart_ventas_usuario, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        chart_ventas_usuario = chart.get_chart(stats_asesores, 'Clientes Por Usuario', 'Clientes', 'Clientes', 'Usuario', True, 'mean(Clientes)')
        st.altair_chart(chart_ventas_usuario, use_container_width=True)
    with c2:
        chart_ventas_usuario = chart.get_chart(stats_asesores, 'Unidades Por Usuario', 'Unidades', 'Unidades', 'Usuario', True, 'mean(Unidades)')
        st.altair_chart(chart_ventas_usuario, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        chart_ventas_usuario = chart.get_chart(stats_asesores, 'Ticket Promedio Por Usuario', 'Ticket Promedio', 'Promedio', 'Usuario', True, 'mean(Ticket Promedio)')
        st.altair_chart(chart_ventas_usuario, use_container_width=True)
    with c2:
        chart_ventas_usuario = chart.get_chart(stats_asesores, 'UPT Por Usuario', 'UPT', 'UPT', 'Usuario', True, 'mean(UPT)')
        st.altair_chart(chart_ventas_usuario, use_container_width=True)