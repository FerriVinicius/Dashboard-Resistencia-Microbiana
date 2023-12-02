##importa bibliotecas e funções úteis para o programa
import streamlit as st
import pandas as pd
from io import BytesIO
from Authenticate import check_password

##muda o título da página na aba do navegador
st.set_page_config(
    page_title="Relatórios - Einstein PMRM",
    page_icon="📋",
    )
st.header("Programa de Monitoramento de Resistência Microbiana")

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
if check_password():
    col1 = st.columns(1)
    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        modify = st.checkbox("Adicionar Filtros")
        
        if not modify:
            return df
        
        df = df.copy()
        
        modification_container = st.container()
    
        with modification_container:
            to_filter_columns = col1.multiselect("Filtrar tabela por:", list(column_mapping.values()))
            to_filter_columns = [key for key, value in column_mapping.items() if value in to_filter_columns]
            
            for column_key in to_filter_columns:
                # Use a chave mapeada para acessar a coluna
                column = column_mapping[column_key]
                
                left, right = st.columns((1, 20))
                left.write("↳")
    
                if pd.api.types.is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Valores para {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif pd.api.types.is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Valores para {column}",
                        _min,
                        _max,
                        (_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif pd.api.types.is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Valores para {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Filtros adicionais {column}",
                    )
                    if user_text_input:
                        df = df[df[column].str.contains(user_text_input)]
    
            # Adiciona o botão de exportação
            export_button = col1.button("Preparar dados para exportação")
    
            # Se o botão for pressionado, exporta o DataFrame
            if export_button:
                export_data = BytesIO()
                df.to_csv(export_data, index=False)
                export_data.seek(0)
                col1.download_button(
                    label="Download",
                    data=export_data,
                    file_name="dados_filtrados.csv",
                    key="download_button",
                )
            
            return df
    
    # Mapeamento de colunas para nomes mais usuais
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

    # Carrega os dados do arquivo CSV no sistema
    df = pd.read_csv("https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv")

    # Filtra apenas as colunas mencionadas no column_mapping
    filtered_df = df[list(column_mapping.keys())]

    # Renomeia as colunas conforme o mapeamento
    filtered_df = filtered_df.rename(columns=column_mapping)

    # Mostra o DataFrame filtrado e adiciona a funcionalidade de exportação
    filtered_df = filter_dataframe(filtered_df)
    col1.dataframe(filtered_df)
else:
    st.stop()
