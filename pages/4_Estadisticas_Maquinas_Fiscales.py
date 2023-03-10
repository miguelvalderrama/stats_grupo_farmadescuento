import streamlit as st
import consultas

if st.session_state.get("role") != "admin":
    st.error("No tienes permisos para acceder a esta pagina.")
    st.stop()

# Config
st.set_page_config(page_title='Estadistica Maquinas Fiscales', page_icon=':bar_chart:', layout='wide')

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
conexiones = conexiones[conexiones['grupo'] != 'OTROS']
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
stats_maquinas_sistema = consultas.get_data('estadisticas de maquinas fiscales sistema', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])
stats_maquinas_zetas = consultas.get_data('estadisticas de maquinas fiscales zetas', date_init, date_end, farmacia['servidor'], farmacia['nomusua'], farmacia['clave'], farmacia['basedata'])

if stats_maquinas_sistema is None or stats_maquinas_zetas is None:
    st.error('No hay informacion suficiente, seleccione un rango mayor de fechas')
    st.stop()

maquinas_fiscales = stats_maquinas_sistema.copy()
maquinas_fiscales = maquinas_fiscales.drop(columns=['Tickera'])
maquinas_fiscales = maquinas_fiscales[maquinas_fiscales['Fiscalserial'] != 'NENTREGA']

st.subheader('Maquinas Fiscales')
c1, c2 = st.columns(2)
with c1:
    st.write('**Monto Ventas en Sistema:**')
    st.dataframe(maquinas_fiscales, use_container_width=True)
    
with c2:
    st.write('**Monto Ventas en Zetas:**')
    st.dataframe(stats_maquinas_zetas, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    s1, s2 = st.columns(2)
    with s1:
        st.write('**Totales Ventas en Sistema:**')
        avg = maquinas_fiscales.drop(columns=['Fecha'])
        avg = avg.groupby('Fiscalserial').sum()
        st.dataframe(avg, use_container_width=True)
    with s2:
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.metric(label='Total Ventas en Sistema', value="Bs. {:,.2f}".format(avg['Maquina Fiscal'].sum()))
        st.metric(label='Promedio Maquinas Fiscales en Sistema', value="Bs. {:,.2f}".format(avg['Maquina Fiscal'].mean()))
with c2:
    s1, s2 = st.columns(2)
    with s1:
        st.write('**Totale Ventas en Zetas:**')
        avg = stats_maquinas_zetas.drop(columns=['Fecha'])
        avg = avg.groupby('Fiscalserial').sum()
        st.dataframe(avg, use_container_width=True)
    with s2:
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.write(' ')
        st.metric(label='Total Ventas en Zeta', value="Bs. {:,.2f}".format(avg['Maquina Fiscal'].sum()))
        st.metric(label='Promedio Maquinas Fiscales en Zeta', value="Bs. {:,.2f}".format(avg['Maquina Fiscal'].mean()))

st.subheader('Tickeras')
tickeras = stats_maquinas_sistema.copy()
tickeras = tickeras.drop(columns=['Maquina Fiscal'])
tickeras = tickeras[tickeras['Fiscalserial'] == 'NENTREGA'].reset_index(drop=True)
if tickeras.empty:
    st.error('No hay tickeras en esta tienda')
    st.stop()
c1, c2 = st.columns(2)
with c1:
    st.dataframe(tickeras, use_container_width=True)
with c2:
    st.metric(label='Total Monto Tickera', value="Bs. {:,.2f}".format(tickeras['Tickera'].sum()))
    st.metric(label='Promedio Diario Tickera', value="Bs. {:,.2f}".format(tickeras['Tickera'].mean()))

