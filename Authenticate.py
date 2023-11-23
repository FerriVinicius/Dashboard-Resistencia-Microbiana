##importa bibliotecas úteis para a funcionalidade
import hmac
import streamlit as st

##função de autenticação por meio de um nome de usuário e uma senha
def check_password():
    ##retorna True se o usuário fornecer uma senha correta
    
    ##esconde a barra lateral de navegação enquanto o usuário não estiver autenticado
    hide_bar= """
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            visibility:hidden;
            width: 0px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            visibility:hidden;
        }
        </style>
    """
    
    ##aspectos visuais da sidebar
    st.sidebar.header("Bem vindo!")
    icon = "https://minhabiblioteca.com.br/wp-content/uploads/2021/04/logo-einstein.png"
    st.sidebar.image(icon, use_column_width=True)
    
    ##inicializa a sessão caso ela não exista
    if "show_error_message" not in st.session_state:
        st.session_state.show_error_message = False
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = None

    ##função para formulário de login
    def login_form():
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)
            st.markdown(hide_bar, unsafe_allow_html=True)
    
    #função para checar as credenciais inseridas no sistema, retorna True caso esteja correta
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state.password_correct = True
            del st.session_state["password"]  ##funcionalidade para não salvar as credenciais utilizadas
            del st.session_state["username"]
        else:
            st.session_state.password_correct = False
            st.session_state.show_error_message = True
            st.markdown(hide_bar, unsafe_allow_html=True)

    ##função para sair do sistema e retornar para a página de login
    def logout():
        st.session_state.password_correct = None
        st.session_state.show_error_message = False
       
    ##complemento da função check_password(), com inserção de botão para encerramento de sessão
    if st.session_state.password_correct is True:
        st.sidebar.button("❌ Encerrar Sessão", on_click=logout)
        return True

    ##completmento da função check_password(), retorna mensagem de erro ao inserir credenciais inválidas.
    login_form()
    if st.session_state.show_error_message:
        st.error("Usuário ou senha inválidas, tente novamente.")
        st.markdown(hide_bar, unsafe_allow_html=True)
    
    # Verifica se as credenciais são corretas antes de continuar
    if st.session_state.password_correct is True:
        return True
    else:
        return False
