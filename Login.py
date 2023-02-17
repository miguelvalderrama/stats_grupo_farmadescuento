# Libraries
import streamlit as st
import consultas
from PIL import Image
from streamlit.components.v1 import html

def nav_page(page_name, timeout_secs=3):
    nav_script = """
        <script type="text/javascript">
            function attempt_nav_page(page_name, start_time, timeout_secs) {
                var links = window.parent.document.getElementsByTagName("a");
                for (var i = 0; i < links.length; i++) {
                    if (links[i].href.toLowerCase().endsWith("/" + page_name.toLowerCase())) {
                        links[i].click();
                        return;
                    }
                }
                var elasped = new Date() - start_time;
                if (elasped < timeout_secs * 1000) {
                    setTimeout(attempt_nav_page, 100, page_name, start_time, timeout_secs);
                } else {
                    alert("Unable to navigate to page '" + page_name + "' after " + timeout_secs + " second(s).");
                }
            }
            window.addEventListener("load", function() {
                attempt_nav_page("%s", new Date(), %d);
            });
        </script>
    """ % (page_name, timeout_secs)
    html(nav_script)

# Config
st.set_page_config(page_title='Login', page_icon=':bar_chart:', initial_sidebar_state="collapsed")

# Title
st.markdown("<h1 style='text-align: center;;'>Estadisticas Farmadescuento</h1>", unsafe_allow_html=True)

# Content
c1, c2, c3 = st.columns(3)
c1.write(' ')
c2.image(Image.open('images/farmadescuento-logo.png'))
c3.write(' ')

hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''
st.markdown(hide_img_fs, unsafe_allow_html=True)

# Create an empty container
placeholder = st.empty()

if not st.session_state:
    st.session_state['role'] = None

# Insert a form in the container
with placeholder.form("login"):
    st.markdown("#### Ingrese sus credenciales")
    password = st.text_input("Contraseña", type="password")
    submit = st.form_submit_button("Acceder")

if submit and consultas.autentificador(password) or st.session_state['role'] == 'admin':
    # If the form is submitted and the email and password are correct,
    # clear the form/container and display a success message
    placeholder.empty()
    st.success("Acceso exitoso")
    st.session_state['role'] = 'admin'
    nav_page("Estadisticas_de_Compras_y_Ventas")

elif submit:
    st.error("Login failed")
else:
    pass