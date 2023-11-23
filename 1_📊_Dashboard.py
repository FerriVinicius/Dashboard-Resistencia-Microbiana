import streamlit as st
import pandas as pd
import altair as alt
from Authenticate import check_password

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide",
    )

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

check_password() 

df = pd.read_csv("https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv")

def load_data(url):
    data = pd.read_csv(url, parse_dates=['dh_admissao_paciente', 'dh_alta_paciente'])
    return data

# Função para criar gráfico interativo
def create_interactive_chart(data, x_column, y_column, chart_type, invert_axes):
    chart = None
    if chart_type == 'Barras':
        chart = alt.Chart(data).mark_bar().encode(
            x=alt.X(x_column, title=x_column, sort='-y' if x_column == 'ds_micro_organismo' else None),
            y=alt.Y(y_column, title=y_column)
        ).interactive()
    elif chart_type == 'Linhas':
        chart = alt.Chart(data).mark_line().encode(
            x=alt.X(x_column, title=x_column, sort='-y' if x_column == 'ds_micro_organismo' else None),
            y=alt.Y(y_column, title=y_column)
        ).interactive()

    if invert_axes:
        chart = chart.properties(width='container', height='container').encode(
            x=alt.X(y_column, title=y_column, sort='-x' if y_column == 'ds_micro_organismo' else None),
            y=alt.Y(x_column, title=x_column)
        )

    return chart

# Função para criar DataFrame com dados do gráfico e número total de casos
def create_summary_dataframe(data, x_column, y_column):
    summary_data = data[[x_column, y_column]].groupby(x_column).agg({y_column: 'mean'}).reset_index()
    total_cases = data.shape[0]
    return summary_data, total_cases

# Título da aplicação
st.title("Visualização Gráfica dos Dados:")

# URL do arquivo CSV
url = "https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv"
data = load_data(url)

# Criar nova variável dh_media
data['dh_media'] = (data['dh_alta_paciente'] - data['dh_admissao_paciente']).dt.days

# Formatar colunas de data no formato solicitado
data['dh_admissao_paciente'] = data['dh_admissao_paciente'].dt.strftime('%Y-%m-%d')
data['dh_alta_paciente'] = data['dh_alta_paciente'].dt.strftime('%Y-%m-%d')

# Seleção de colunas
x_column = st.selectbox("Selecione a coluna para o eixo X", ['ds_micro_organismo'] + list(data.columns[2:]))
y_column = st.selectbox("Selecione a coluna para o eixo Y", ['dh_media'] + list(data.columns[2:]))

# Seleção do tipo de gráfico
chart_type = st.radio("Selecione o tipo de gráfico", ['Barras', 'Linhas'])

# Botão para inverter os eixos
invert_axes = st.checkbox("Inverter Eixos")

# Criar gráfico interativo
st.subheader("Gráfico (Média de tempo de internação x Microorganismo")
chart = create_interactive_chart(data, x_column, y_column, chart_type, invert_axes)
st.altair_chart(chart, use_container_width=True)

# Montar DataFrame com dados do gráfico e número total de casos
st.subheader("Resumo dos Dados")
summary_data, total_cases = create_summary_dataframe(data, x_column, y_column)
st.write("Número Total de Casos:", total_cases)
st.write(summary_data)