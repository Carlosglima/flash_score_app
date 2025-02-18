import streamlit as st
import os

# Função de autenticação
def authenticate(username, password):
    return username == os.getenv("APP_USERNAME") and password == os.getenv("APP_PASSWORD")

# Função para exibir a página de login
def show_login_page():
    st.markdown(
        """
        <style>
        .main-container {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 100%;
            max-width: 400px;
        }
        .login-container {
            padding: 2rem;
            border-radius: 10px;
            background-color: #f8f9fa;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        .login-container h2 {
            color: #007bff;
        }
        </style>
        """,
        unsafe_allow_html=True
    )



    st.markdown("<h1>🎮 Bem Vindo ao Zerador Gamer</h1>", unsafe_allow_html=True)
    st.markdown("<h2>🔑 Faça seu Login</h2>", unsafe_allow_html=True)
    
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    login_button_clicked = st.button("Entrar")

    st.markdown("</div></div>", unsafe_allow_html=True)  # Fechando as divs corretamente

    return username, password, login_button_clicked

# Função para logout
def show_logout_button():
    if st.sidebar.button("Logout"):
        st.session_state['authenticated'] = False
        st.rerun()

# Função para verificar login
def require_login():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if not st.session_state['authenticated']:
        username, password, login_button_clicked = show_login_page()
        if login_button_clicked and authenticate(username, password):
            st.session_state['authenticated'] = True
            st.rerun()
        elif login_button_clicked:
            st.error("❌ Usuário ou senha inválidos.")
        return False
    return True
