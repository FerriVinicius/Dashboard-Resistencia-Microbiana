##importa bibliotecas Ãºteis para a funcionalidade
import hmac
import streamlit as st

##funÃ§Ã£o de autenticaÃ§Ã£o por meio de um nome de usuÃ¡rio e uma senha
def check_password():
    ##retorna True se o usuÃ¡rio fornecer uma senha correta
    
    ##esconde a barra lateral de navegaÃ§Ã£o enquanto o usuÃ¡rio nÃ£o estiver autenticado
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
    
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image: url("https://raw.githubusercontent.com/FerriVinicius/Dashboard-Resistencia-Microbiana/main/194065878_l_normal_none.jpg");
    background-size: 150%;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: local;
    }}
    
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}
    
    [data-testid="stToolbar"] {{
    right: 2rem;
    }}
    """
    
    stform = """
    <style>
    [data-testid="stForm"] {
        background-color: lightsteelblue;
    }
    </style>
    """

        
    st.markdown(page_bg_img, unsafe_allow_html=True)
    
    ##aspectos visuais da sidebar
    st.sidebar.header("Bem vindo!")
    icon = "https://minhabiblioteca.com.br/wp-content/uploads/2021/04/logo-einstein.png"
    st.sidebar.image(icon, use_column_width=True)
    
    ##inicializa a sessÃ£o caso ela nÃ£o exista
    if "show_error_message" not in st.session_state:
        st.session_state.show_error_message = False
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = None

    ##funÃ§Ã£o para formulÃ¡rio de login
    def login_form():
        with st.form("Credentials"):
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            st.form_submit_button("Entrar", on_click=password_entered)
            st.markdown(hide_bar, unsafe_allow_html=True)
            st.markdown(stform, unsafe_allow_html=True)
    
    #funÃ§Ã£o para checar as credenciais inseridas no sistema, retorna True caso esteja correta
    def password_entered():
        if st.session_state["username"] in st.secrets["passwords"] and hmac.compare_digest(
                st.session_state["password"],
                st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state.password_correct = True
            del st.session_state["password"]  ##funcionalidade para nÃ£o salvar as credenciais utilizadas
            del st.session_state["username"]
        else:
            st.session_state.password_correct = False
            st.session_state.show_error_message = True
            st.markdown(hide_bar, unsafe_allow_html=True)

    ##funÃ§Ã£o para sair do sistema e retornar para a pÃ¡gina de login
    def logout():
        st.session_state.password_correct = None
        st.session_state.show_error_message = False
       
    ##complemento da funÃ§Ã£o check_password(), com inserÃ§Ã£o de botÃ£o para encerramento de sessÃ£o
    if st.session_state.password_correct is True:
        st.sidebar.button("❌ Encerrar Sessão", on_click=logout)
        return True

    ##completmento da funÃ§Ã£o check_password(), retorna mensagem de erro ao inserir credenciais invÃ¡lidas.
    login_form()
    if st.session_state.show_error_message:
        st.error("Usuário ou senha inválidas, tente novamente.")
        st.markdown(hide_bar, unsafe_allow_html=True)
    
    # Verifica se as credenciais sÃ£o corretas antes de continuar
    if st.session_state.password_correct is True:
        return True
    else:
        return False
