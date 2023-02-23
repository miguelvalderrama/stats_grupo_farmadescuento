# Libraries
import streamlit as st
import pandas as pd
import numpy as np
import chart
import consultas
import datetime
import altair as alt
import chart

if st.session_state.get("role") != "admin":
    st.error("No tienes permisos para acceder a esta pagina.")
    st.stop()

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
st.title('🔄 Estadistica Compra/Ventas')

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

if date_init > date_end:
    st.error('La fecha inicial debe ser menor que la final.')
    st.stop()

# Data Sources
stats_ventas = consultas.get_data('estadisticas de ventas', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])
stats_compras = consultas.get_data('estadisticas de compras', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])
stats_areas = consultas.get_data('estadisticas por areas', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])
stats_lineas = consultas.get_data('estadisticas por lineas', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])

if stats_compras is None:
    stats_compras = pd.DataFrame(columns=['Fecha', 'Area', 'Unidades Ingresadas', 'pUnidades', 'Costo Totales', 'pCompras', 'Tasa Promedio', 'Costo Totales $'])

if stats_ventas is None:
    st.error('No hay informacion que mostrar. Pruebe con otro rango de fechas.')
    st.stop()

stats_devoluciones_tipo = consultas.get_data('estadisticas de devoluciones tipo', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])
stats_devoluciones_areas = consultas.get_data('estadisticas de devoluciones areas', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])
stats_devoluciones_lineas = consultas.get_data('estadisticas de devoluciones lineas', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])

stats_ventas['Ventas Bs'] = np.where((stats_ventas['Fecha']==stats_devoluciones_tipo['Fecha']) & (stats_ventas['Area']==stats_devoluciones_tipo['Areas']), stats_ventas['Ventas Bs'] - stats_devoluciones_tipo['Monto Devolucion Bs'], stats_ventas['Ventas Bs'])
stats_ventas['Ventas $'] = np.where((stats_ventas['Fecha']==stats_devoluciones_tipo['Fecha']) & (stats_ventas['Area']==stats_devoluciones_tipo['Areas']), stats_ventas['Ventas $'] - stats_devoluciones_tipo['Monto Devolucion $'], stats_ventas['Ventas $'])
stats_ventas['Unidades Vendidas'] = np.where((stats_ventas['Fecha']==stats_devoluciones_tipo['Fecha']) & (stats_ventas['Area']==stats_devoluciones_tipo['Areas']), stats_ventas['Unidades Vendidas'] - stats_devoluciones_tipo['Unidades Devueltas'], stats_ventas['Unidades Vendidas'])

stats_areas['Ventas Bs'] = np.where((stats_areas['Fecha']==stats_devoluciones_areas['Fecha']) & (stats_areas['Areas']==stats_devoluciones_areas['Areas']), stats_areas['Ventas Bs'] - stats_devoluciones_areas['Monto Devolucion Bs'], stats_areas['Ventas Bs'])
stats_areas['Ventas $'] = np.where((stats_areas['Fecha']==stats_devoluciones_areas['Fecha']) & (stats_areas['Areas']==stats_devoluciones_areas['Areas']), stats_areas['Ventas $'] - stats_devoluciones_areas['Monto Devolucion $'], stats_areas['Ventas $'])
stats_areas['Unidades'] = np.where((stats_areas['Fecha']==stats_devoluciones_areas['Fecha']) & (stats_areas['Areas']==stats_devoluciones_areas['Areas']), stats_areas['Unidades'] - stats_devoluciones_areas['Unidades Devueltas'], stats_areas['Unidades'])

stats_lineas['Ventas Bs'] =  np.where((stats_lineas['Fecha']==stats_devoluciones_lineas['Fecha']) & (stats_lineas['Linea']==stats_devoluciones_lineas['Linea']), stats_lineas['Ventas Bs'] - stats_devoluciones_lineas['Monto Devolucion Bs'], stats_lineas['Ventas Bs'])
stats_lineas['Ventas $'] =  np.where((stats_lineas['Fecha']==stats_devoluciones_lineas['Fecha']) & (stats_lineas['Linea']==stats_devoluciones_lineas['Linea']), stats_lineas['Ventas $'] - stats_devoluciones_lineas['Monto Devolucion $'], stats_lineas['Ventas $'])
stats_lineas['Unidades'] =  np.where((stats_lineas['Fecha']==stats_devoluciones_lineas['Fecha']) & (stats_lineas['Linea']==stats_devoluciones_lineas['Linea']), stats_lineas['Unidades'] - stats_devoluciones_lineas['Unidades Devueltas'], stats_lineas['Unidades'])

st.subheader('Vista general')
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric(label='**Ventas Totales Bs.**', value=str("Bs. {:,.2f}".format(stats_ventas['Ventas Bs'].sum())))
    st.metric(label='**Compras Totales Bs.**', value=str("Bs. {:,.2f}".format(stats_compras['Costo Totales'].sum())))
with c2:
    st.metric(label='**Ventas Totales $.**', value=str("$ {:,.2f}".format(stats_ventas['Ventas $'].sum())))
    st.metric(label='**Relacion Compra/Venta**', value=str("{:,.2f}%".format((stats_compras['Costo Totales'].sum()/stats_ventas['Ventas Bs'].sum())*100)))
with c3:
    st.metric(label='**Promedio Diario de Ventas Bs.**', value=str("Bs. {:,.2f}".format(stats_ventas['Ventas Bs'].mean()*2)))
    st.metric(label='**Ticket Promedio Bs.**', value=str("Bs. {:,.2f}".format(stats_ventas['Ticket Promedio'].astype(float).sum()/(len(stats_ventas)/2))))    
with c4:
    st.metric(label='**Promedio Diario de Ventas $**', value=str("$ {:,.2f}".format(stats_ventas['Ventas $'].mean()*2)))
    st.metric(label='**Promedio Unidades Por Ticket**', value=str("{:,.2f}".format(stats_ventas['UPT'].astype(float).sum()/(len(stats_ventas)/2))))

c1, c2, c3 = st.columns(3)
with c1:
    st.metric(label='**Unidades Vendidas**', value=str("{:,.0f}".format(stats_ventas['Unidades Vendidas'].sum())))
with c2:
    st.metric(label='**Unidades Compradas**', value=str("{:,.0f}".format(stats_compras['Unidades Ingresadas'].sum())))
with c3:
    st.metric(label='**Relacion Unidades Compra/Venta**', value=str("{:,.2f}%".format(stats_compras['Unidades Ingresadas'].sum()/stats_ventas['Unidades Vendidas'].sum()*100)))

c1, c2 = st.columns(2)
with c1:
    st.metric(label='**Clientes Totales**', value=str("{:,.0f}".format(stats_areas['Clientes'].sum())))
with c2:
    st.metric(label='**Promedio Clientes Diarios**', value=str("{:,.0f}".format(stats_areas['Clientes'].mean()*len(stats_areas['Areas'].unique()))))

stats_ventas['Unidades Vendidas'] = stats_ventas['Unidades Vendidas'].astype(int)
stats_compras['Unidades Ingresadas'] = stats_compras['Unidades Ingresadas'].astype(int)

st.subheader('Compra/Venta Detallado Por Dia')
c1, c2 = st.columns(2)
with c1:
    st.write('**Compras Detalladas:**')
    st.dataframe(stats_compras)
    if (date_end - date_init) > datetime.timedelta(days=0):
        df_ventas = stats_ventas[['Fecha', 'Unidades Vendidas']].copy()
        df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha'])
        df_ventas = df_ventas.groupby(['Fecha']).sum()
        df_ventas.rename(columns={'Unidades Vendidas': 'Unidades'}, inplace=True)
        df_ventas['Tipo'] = 'Unidades Vendidas'

        df_compras = stats_compras[['Fecha', 'Unidades Ingresadas']].copy()
        df_compras['Fecha'] = pd.to_datetime(df_compras['Fecha'])
        df_compras = df_compras.groupby(['Fecha']).sum()
        df_compras.rename(columns={'Unidades Ingresadas': 'Unidades'}, inplace=True)
        df_compras['Tipo'] = 'Unidades Ingresadas'

        df = pd.concat([df_compras, df_ventas])
        df = df.reset_index()

        s1, s2 = st.columns(2)
        with s1:
            st.metric(label='**Unidades Compradas Farmacia**', value=str("{:,.0f}".format(stats_compras.loc[stats_compras['Area']=='Farmacia', 'Unidades Ingresadas'].sum())))
            st.metric(label='**Costo Totales Farmacia**', value=str("Bs. {:,.2f}".format(stats_compras.loc[stats_compras['Area']=='Farmacia', 'Costo Totales'].sum())))
            st.metric(label='**Relacion Unidades Compradas Farmacia/MiniMarket**', value=str("{:,.2f}%".format(stats_compras.loc[stats_compras['Area']=='Farmacia', 'Unidades Ingresadas'].sum()/stats_compras.loc[stats_compras['Area']=='Mini Market', 'Unidades Ingresadas'].sum()*100)))

        with s2:
            st.metric(label='**Unidades Compradas MiniMarket**', value=str("{:,.0f}".format(stats_compras.loc[stats_compras['Area']=='Mini Market', 'Unidades Ingresadas'].sum())))
            st.metric(label='**Costo Totales MiniMarket**', value=str("Bs. {:,.2f}".format(stats_compras.loc[stats_compras['Area']=='Mini Market', 'Costo Totales'].sum())))
            if stats_compras.loc[stats_compras['Area']=='Mini Market', 'Costo Totales'].sum() == 0:
                st.metric(label='**Relacion Costos Farmacia/MiniMarket**', value=str("{:,.2f}%".format(0)))
            else:
                st.metric(label='**Relacion Costos Farmacia/MiniMarket**', value=str("{:,.2f}%".format(stats_compras.loc[stats_compras['Area']=='Farmacia', 'Costo Totales'].sum()/stats_compras.loc[stats_compras['Area']=='Mini Market', 'Costo Totales'].sum()*100)))

        chart_try = chart.get_chart(df, 'Unidades Vendidas y Compradas:', 'Unidades', 'Unidades', 'Tipo')
        st.altair_chart(chart_try, use_container_width=True)

with c2:
    st.write('**Ventas Detalladas:**')
    st.dataframe(stats_ventas)
    if (date_end - date_init) > datetime.timedelta(days=0):
        df_ventas = stats_ventas[['Fecha', 'Ventas Bs']].copy()
        df_ventas['Ventas Bs'] = df_ventas['Ventas Bs'].astype(float)
        df_ventas['Fecha'] = pd.to_datetime(df_ventas['Fecha'])
        df_ventas = df_ventas.groupby(['Fecha']).sum()
        df_ventas.rename(columns={'Ventas Bs': 'Bs'}, inplace=True)
        df_ventas['Tipo'] = 'Ventas'

        df_compras = stats_compras[['Fecha', 'Costo Totales']].copy()
        df_compras['Costo Totales'] = df_compras['Costo Totales'].astype(float)
        df_compras['Fecha'] = pd.to_datetime(df_compras['Fecha'])
        df_compras = df_compras.groupby(['Fecha']).sum()
        df_compras.rename(columns={'Costo Totales': 'Bs'}, inplace=True)
        df_compras['Tipo'] = 'Compras'

        df = pd.concat([df_compras, df_ventas])
        df = df.reset_index()

        s1, s2 = st.columns(2)
        with s1:
            st.metric(label='**Unidades Vendidas Farmacia**', value=str("{:,.0f}".format(stats_ventas.loc[stats_ventas['Area']=='Farmacia', 'Unidades Vendidas'].sum())))
            st.metric(label='**Ventas Totales Farmacia**', value=str("Bs. {:,.2f}".format(stats_ventas.loc[stats_ventas['Area']=='Farmacia', 'Ventas Bs'].sum())))
            st.metric(label='**Relacion Unidades Vendidas Farmacia/MiniMarket**', value=str("{:,.2f}%".format(stats_ventas.loc[stats_ventas['Area']=='Farmacia', 'Unidades Vendidas'].sum()/stats_ventas.loc[stats_ventas['Area']=='Mini Market', 'Unidades Vendidas'].sum()*100)))
        with s2:
            st.metric(label='**Unidades Vendidas MiniMarket**', value=str("{:,.0f}".format(stats_ventas.loc[stats_ventas['Area']=='Mini Market', 'Unidades Vendidas'].sum())))
            st.metric(label='**Ventas Totales MiniMarket**', value=str("Bs. {:,.2f}".format(stats_ventas.loc[stats_ventas['Area']=='Mini Market', 'Ventas Bs'].sum())))
            st.metric(label='**Relacion Ventas Farmacia/MiniMarket**', value=str("{:,.2f}%".format(stats_ventas.loc[stats_ventas['Area']=='Farmacia', 'Ventas Bs'].sum()/stats_ventas.loc[stats_ventas['Area']=='Mini Market', 'Ventas Bs'].sum()*100)))

        chart_try = chart.get_chart(df, 'Compras y Ventas en Bs:', 'Bs', 'Monto Bs', 'Tipo')
        st.altair_chart(chart_try, use_container_width=True)

st.subheader('Ventas y Unidades Por Linea')
c1, c2, c3 = st.columns(3)
with c1:
    st.write('**Detallado:**')
    stats_lineas['Unidades'] = stats_lineas['Unidades'].astype(int)
    stats_lineas['Ventas Bs'] = stats_lineas['Ventas Bs'].astype(float)
    stats_lineas['Ventas $'] = stats_lineas['Ventas Bs'].astype(float)
    df_lineas = stats_lineas.copy()
    df_lineas.drop(columns=['Fecha'], inplace=True)
    df_lineas = df_lineas.groupby(['Linea']).sum()
    st.dataframe(df_lineas, height=490, use_container_width=True)
with c2:
    st.write('**Ventas:**')
    df_lineas = df_lineas.reset_index()
    chart_lineas_ventas = alt.Chart(df_lineas).mark_bar(color='orange').encode(
    x='Ventas Bs',
    y='Linea'
    ).properties(height=520)
    st.altair_chart(chart_lineas_ventas, use_container_width=True)
with c3:
    st.write('**Unidades:**')
    df_lineas = df_lineas.reset_index()
    chart_lineas_ventas = alt.Chart(df_lineas).mark_bar(color='orange').encode(
    x='Unidades',
    y='Linea'
    ).properties(height=520)
    st.altair_chart(chart_lineas_ventas, use_container_width=True)

st.subheader('Ventas y Unidades por Area')
stats_areas['Unidades'] = stats_areas['Unidades'].astype(int)
stats_areas['Clientes'] = stats_areas['Clientes'].astype(int)
stats_areas['Ventas Bs'] = stats_areas['Ventas Bs'].astype(float)
stats_areas['Ventas $'] = stats_areas['Ventas $'].astype(float)
stats_areas['Ticket Promedio'] = stats_areas['Ticket Promedio'].astype(float)
stats_areas['UPT'] = stats_areas['UPT'].astype(float)
if option != 'FARMA HOSPITAL':
    stats_areas['Areas'] = 'Area Interna'
    stats_areas = stats_areas.groupby(['Fecha', 'Areas']).sum()
    stats_areas = stats_areas.reset_index()

c1, c2  = st.columns(2)
with c1:
    st.write('**Detallado Diario:**')
    st.dataframe(stats_areas, use_container_width=True)
with c2:
    st.write('**Totales Por Area:**')
    stats_areas['Fecha'] = pd.to_datetime(stats_areas['Fecha'])
    stats_areas = stats_areas.set_index('Fecha')

    mean_stats_area = stats_areas.groupby(['Areas']).mean()
    mean_stats_area['Clientes'] = mean_stats_area['Clientes'].astype(int)
    mean_stats_area['Unidades'] = mean_stats_area['Unidades'].astype(int)

    stats_areas = stats_areas.reset_index()
    df_areas = stats_areas.copy()
    df_areas.drop(columns=['Fecha', 'UPT', 'Ticket Promedio'], inplace=True)
    df_areas = df_areas.groupby(['Areas']).sum()

    st.dataframe(df_areas)
    st.write('**Promedios Por Areas:**')
    st.dataframe(mean_stats_area.round(2))

if (date_end - date_init) > datetime.timedelta(days=0):
    chart_ventas_areas = chart.get_chart(stats_areas, 'Ventas Por Area Bs', 'Ventas Bs', 'Monto Bs', 'Areas')
    st.altair_chart(chart_ventas_areas, use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        chart_ventas_areas = chart.get_chart(stats_areas, 'Clientes Por Area', 'Clientes', 'Clientes', 'Areas')
        st.altair_chart(chart_ventas_areas, use_container_width=True)
    with c2:
        chart_ventas_areas = chart.get_chart(stats_areas, 'Unidades Por Area', 'Unidades', 'Unidades', 'Areas')
        st.altair_chart(chart_ventas_areas, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        chart_ventas_areas = chart.get_chart(stats_areas, 'Ticket Promedio Por Area', 'Ticket Promedio', 'Promedio', 'Areas')
        st.altair_chart(chart_ventas_areas, use_container_width=True)
    with c2:
        chart_ventas_areas = chart.get_chart(stats_areas, 'UPT Por Area', 'UPT', 'UPT', 'Areas')
        st.altair_chart(chart_ventas_areas, use_container_width=True)


