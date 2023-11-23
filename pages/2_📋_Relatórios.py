##importa bibliotecas e funções úteis para o programa
import streamlit as st
import pandas as pd
import base64
from io import BytesIO
from Authenticate import check_password
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)

##muda o título da página na aba do navegador
st.set_page_config(
    page_title="Relatórios - Einstein PMRM",
    page_icon="📋",
    )

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
    def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        modify = st.checkbox("Adicionar Filtros")
        
        if not modify:
            return df
        
        df = df.copy()
        
        for col in df.columns:
            if pd.api.types.is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass
    
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)
        
        modification_container = st.container()
        
        with modification_container:
            to_filter_columns = st.multiselect("Filtrar tabela por:", df.columns)
            for column in to_filter_columns:
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
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].str.contains(user_text_input)]
        
        if st.button("Exportar para Excel"):
            # Exporta o DataFrame filtrado para um arquivo Excel
            excel_data = BytesIO()
            df.to_excel(excel_data, index=False, engine='openpyxl')
            b64 = base64.b64encode(excel_data.getvalue()).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="filtered_data.xlsx">Download Excel</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        return df
    
    # Carrega os dados do arquivo CSV no sistema
    df = pd.read_csv("https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv")
    
    # Mostra o DataFrame filtrado e adiciona a funcionalidade de exportação
    filtered_df = filter_dataframe(df)
    st.dataframe(filtered_df)
else:
    st.stop()
