# Importa bibliotecas e funções úteis para o programa
import streamlit as st
import pandas as pd
from io import BytesIO
from Authenticate import check_password

# Muda o título da página na aba do navegador
st.set_page_config(
    page_title="Relatórios - Einstein PMRM",
    page_icon="📋",
    layout='wide',
)
st.header("Programa de Monitoramento de Resistência Microbiana", divider='green')

# Esconde a barra de acesso lateral durante o login do usuário
hide_bar = """
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
    background-size: contain;
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

    col1, col2, col3 = st.columns([1, 1, 2])

    # Carregar os dados do CSV
    url = "https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv"
    df = pd.read_csv(url)

    # Converter colunas para tipo de data
    df['dh_admissao_paciente'] = pd.to_datetime(df['dh_admissao_paciente'])
    df['dh_alta_paciente'] = pd.to_datetime(df['dh_alta_paciente'])

    # Mapeamento das colunas
    column_mapping = {
        'dh_admissao_paciente': 'Data de Admissão do Paciente',
        'dh_alta_paciente': 'Data de Alta do Paciente',
        'ds_tipo_encontro': 'Tipo de Encontro',
        'ds_unidade_coleta': 'Unidade de Coleta',
        'ds_predio_coleta': 'Prédio de Coleta',
        'ds_ala_coleta': 'Ala de Coleta',
        'ds_quarto_coleta': 'Quarto de Coleta',
        'ds_leito_coleta': 'Leito de Coleta',
        'dh_coleta_exame': 'Data e Hora de Coleta do Exame',
        'cd_sigla_microorganismo': 'Sigla do Microorganismo',
        'ds_micro_organismo': 'Microorganismo',
        'ds_antibiotico_microorganismo': 'Antibiótico para o Microorganismo',
        'cd_interpretacao_antibiograma': 'Interpretação do Antibiograma',
        'ic_crescimento_microorganismo': 'Crescimento do Microorganismo',
        'ds_resultado_exame': 'Resultado do Exame',
    }

    # Colunas específicas para filtragem
    filter_columns = [
        'ds_tipo_encontro',
        'ds_unidade_coleta',
        'ds_predio_coleta',
        'ds_ala_coleta',
        'ds_quarto_coleta',
        'ds_leito_coleta',
        'cd_sigla_microorganismo',
        'ds_micro_organismo',
        'ds_antibiotico_microorganismo',
        'cd_interpretacao_antibiograma',
        'ic_crescimento_microorganismo',
    ]

    # Layout da aplicação usando múltiplas colunas
    col1, col2, col3 = st.columns([1, 1, 2])

    # Botões para seleção de período
    periodo_opcao = col1.radio("Selecione o período:", ["30 dias", "90 dias", "6 meses", "1 ano", "Período completo"])

    # Calcular o período correspondente
    if periodo_opcao == "30 dias":
        data_maxima = df['dh_admissao_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=30)
    elif periodo_opcao == "90 dias":
        data_maxima = df['dh_admissao_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=90)
    elif periodo_opcao == "6 meses":
        data_maxima = df['dh_admissao_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(months=6)
    elif periodo_opcao == "1 ano":
        data_maxima = df['dh_admissao_paciente'].max().date()
        data_inicial = data_maxima - pd.DateOffset(years=1)
    else:  # Período completo
        data_inicial = df['dh_admissao_paciente'].min().date()
        data_maxima = df['dh_admissao_paciente'].max().date()

    # Adicionar filtro de período
    filtro_periodo = col1.date_input('Período Personalizado:', [data_inicial, data_maxima])

    # Aplicar filtros ao DataFrame
    df_filtrado = df[(df['dh_admissao_paciente'].dt.date >= filtro_periodo[0]) & (df['dh_admissao_paciente'].dt.date <= filtro_periodo[1])]

    # Renomear elementos do filtro principal de acordo com o mapeamento
    renamed_mapping = {v: k for k, v in column_mapping.items()}
    renamed_filters = [renamed_mapping.get(col, col) for col in df_filtrado.columns]
    df_filtrado.columns = renamed_filters

    # Adicionar checkbox para filtragem de colunas no subfiltro
    filter_columns_sub = col2.multiselect("Escolha as colunas para filtragem", filter_columns, format_func=lambda x: column_mapping[x])
    
    # Adicionar multiselect para selecionar dados dentro de cada coluna escolhida no subfiltro
    selected_data = {}
    for col in filter_columns_sub:
        unique_values = df_filtrado[col].unique()
        selected_data[col] = col2.multiselect(f"Selecione {column_mapping[col]}", unique_values)

    # Aplicar filtros adicionais
    for col, values in selected_data.items():
        if values:
            df_filtrado = df_filtrado[df_filtrado[col].isin(values)]

    # Obter todos os dados que correspondem aos filtros selecionados
    df_final = df_filtrado[column_mapping.keys()]

    # Renomear colunas do DataFrame final de acordo com o column_mapping
    df_final.columns = [column_mapping[col] for col in df_final.columns]

    # Exibir DataFrame resultante
    col3.dataframe(df_final)
    
else:
    st.stop()
