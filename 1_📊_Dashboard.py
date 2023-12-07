##importa bibliotecas e funções úteis para o programa
import streamlit as st
from Authenticate import check_password
from Graph1 import graph1
from Graph2 import graph2
from Graph3 import graph3
from Graph4 import graph4

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
    background-image: url("https://raw.githubusercontent.com/FerriVinicius/Dashboard-Resistencia-Microbiana/main/151537457_l_normal_none.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: repeat;
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
    tab1, tab2, tab3, tab4 = st.tabs(["Sensibilidade por Antibióticos", "Sensibilidade por Microorganismos", "Infecções por Ala Hospitalar", "Internações por Microorganismo"])
    with tab1:
        graph2()
    with tab2:
        graph4()
    with tab3:
        graph3()
    with tab4:
        graph1()
else:
    st.stop()
