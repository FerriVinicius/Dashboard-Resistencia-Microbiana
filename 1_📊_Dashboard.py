##importa bibliotecas e funções úteis para o programa
import streamlit as st
from Authenticate import check_password
from Graph1 import graph1
from Graph2 import graph2
from Graph3 import graph3

##muda o título da página na aba do navegador
st.set_page_config(
    page_title="Dashboard - Einstein PMRM",
    page_icon="📊",
    layout="wide",
    )
st.header("Programa de Monitoramento de Resistência Microbiana", divider='green')

##esconde a barra de acesso lateral durante o login do usuário
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

if check_password() == True:
    
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image: url("https://www.willametteinnovators.com/wp-content/uploads/2019/07/Capture2-600x425@2x.png");
    background-size: 150%;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: local;
    }}
    [data-testid="stSidebar"] > div:first-child {{
    background-image: url("https://minhabiblioteca.com.br/wp-content/uploads/2021/04/logo-einstein.png");
    background-position: center; 
    background-repeat: no-repeat;
    background-attachment: fixed;
    }}
    
    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}
    
    [data-testid="stToolbar"] {{
    right: 2rem;
    }}
    """
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    st.session_state.sbstate = 'expanded'
    tab1, tab2, tab3 = st.tabs(["Internações", "Microorganismos", "Alas"])
    with tab1:
        graph1()
    with tab2:
        graph2()
    with tab3:
        graph3()
else:
    st.stop()
