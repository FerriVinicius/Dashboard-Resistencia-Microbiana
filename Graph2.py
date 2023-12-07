import streamlit as st
import pandas as pd
import numpy as np
import altair as alt


def calcular_delta_casos_ala(df_periodo_selecionado, df_periodo_anterior, antibiotico, interpretacao):
    casos_periodo_selecionado = df_periodo_selecionado[(df_periodo_selecionado['cd_interpretacao_antibiograma'] == interpretacao) & (df_periodo_selecionado['ds_antibiotico_microorganismo'] == antibiotico)]
    casos_periodo_anterior = df_periodo_anterior[(df_periodo_anterior['cd_interpretacao_antibiograma'] == interpretacao) & (df_periodo_anterior['ds_antibiotico_microorganismo'] == antibiotico)]

    alas_periodo_selecionado = casos_periodo_selecionado['ds_ala_coleta'].unique()
    alas_periodo_anterior = casos_periodo_anterior['ds_ala_coleta'].unique()

    alas_com_mais_de_um_caso_selecionado = [ala for ala in alas_periodo_selecionado if casos_periodo_selecionado[casos_periodo_selecionado['ds_ala_coleta'] == ala].shape[0] > 1]
    alas_com_mais_de_um_caso_anterior = [ala for ala in alas_periodo_anterior if casos_periodo_anterior[casos_periodo_anterior['ds_ala_coleta'] == ala].shape[0] > 1]

    delta_casos_ala = len(set(alas_com_mais_de_um_caso_selecionado) - set(alas_com_mais_de_um_caso_anterior))

    return delta_casos_ala, set(alas_com_mais_de_um_caso_selecionado)


def graph2():
    st.header("Sensibilidade por Antibióticos")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    # Carregar os dados do CSV
    url = "https://raw.githubusercontent.com/AndersonEduardo/pbl-2023/main/sample_data_clean.csv"
    df = pd.read_csv(url)
    
    # Converter a coluna de datas
    df['dh_liberacao_exame'] = pd.to_datetime(df['dh_liberacao_exame'])
    
    # Botões para seleção de período
    periodo_opcao = col1.radio("1- Selecione o período:", ["30 dias", "90 dias", "6 meses", "1 ano", "Período completo"])
    
    # Calcular o período correspondente
    if periodo_opcao == "30 dias":
        data_maxima = df['dh_liberacao_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=30)
    elif periodo_opcao == "90 dias":
        data_maxima = df['dh_liberacao_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(days=90)
    elif periodo_opcao == "6 meses":
        data_maxima = df['dh_liberacao_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(months=6)
    elif periodo_opcao == "1 ano":
        data_maxima = df['dh_liberacao_exame'].max().date()
        data_inicial = data_maxima - pd.DateOffset(years=1)
    else:  # Período completo
        data_inicial = df['dh_liberacao_exame'].min().date()
        data_maxima = df['dh_liberacao_exame'].max().date()
    
    # Adicionar filtro de período
    filtro_periodo = col1.date_input('1- Selecione o período:', [data_inicial, data_maxima])
    
    # Converter para numpy.datetime64
    filtro_periodo = [np.datetime64(date) for date in filtro_periodo]
    
    # Aplicar filtro de período
    df_filtrado = df[(df['dh_liberacao_exame'] >= filtro_periodo[0]) & (df['dh_liberacao_exame'] <= filtro_periodo[1])]
    
    # Pipeline de dados: Excluir valores nulos do gráfico, mas mostrá-los no DataFrame
    df_chart = df_filtrado.dropna(subset=['ds_antibiotico_microorganismo', 'cd_interpretacao_antibiograma', 'ds_ala_coleta'])
    df_chart = df_chart.replace(np.nan, 'Sem informações', regex=True)
    
    # Adicionar filtros
    microorganismos_selecionados = col2.multiselect(
        '1- Selecione os microorganismos:',
        df_filtrado['cd_sigla_microorganismo'].unique(),
        default=df_filtrado['cd_sigla_microorganismo'].unique(),  # Selecionar todos por padrão
        key='microorganismos_multiselect'
    )
    
    # Verificar se há dados para os microorganismos selecionados
    if not df_chart[df_chart['cd_sigla_microorganismo'].isin(microorganismos_selecionados)].empty:
        # Criar gráfico para a sensibilidade aos antibióticos usando Altair
        chart = alt.Chart(df_chart).mark_bar().encode(
            x=alt.X('ds_antibiotico_microorganismo:N', title='Antibiótico'),
            y=alt.Y('count():Q', title='Contagem'),
            color=alt.Color('cd_interpretacao_antibiograma:N', title='Interpretação')
        ).properties(
            width=400,
            height=250
        )
    
        col3.altair_chart(chart, use_container_width=True)
    
    st.header("", divider='green')
    col4, col5, col6 = st.columns([1, 1, 2])
    
    # Filtrar dados para o período selecionado
    df_periodo_selecionado = df_chart[(df_chart['dh_liberacao_exame'] >= filtro_periodo[0]) & (df_chart['dh_liberacao_exame'] <= filtro_periodo[1])]

    # Filtrar dados para o período anterior aos 30 dias
    data_final_anterior = filtro_periodo[0] - pd.DateOffset(days=1)
    data_inicial_anterior = data_final_anterior - pd.DateOffset(days=30)
    df_periodo_anterior = df_chart[(df_chart['dh_liberacao_exame'] >= data_inicial_anterior) & (df_chart['dh_liberacao_exame'] <= data_final_anterior)]

    # Calcular resistência por antibiótico para o período selecionado e anterior aos 30 dias
    resistencia_periodo_selecionado = df_periodo_selecionado[df_periodo_selecionado['cd_interpretacao_antibiograma'] == 'Resistente']
    resistencia_periodo_anterior = df_periodo_anterior[df_periodo_anterior['cd_interpretacao_antibiograma'] == 'Resistente']

    # Calcular interpretações "Sensível Aumentando Exposição" e "Sensível Dose-Dependente" para o período selecionado e anterior aos 30 dias
    sensivel_periodo_selecionado = df_periodo_selecionado[df_periodo_selecionado['cd_interpretacao_antibiograma'].isin(['Sensível Aumentando Exposição', 'Sensível Dose-Dependente'])]
    sensivel_periodo_anterior = df_periodo_anterior[df_periodo_anterior['cd_interpretacao_antibiograma'].isin(['Sensível Aumentando Exposição', 'Sensível Dose-Dependente'])]

    # Selecionar os três antibióticos com mais resistência
    antibioticos_maior_resistencia = resistencia_periodo_selecionado['ds_antibiotico_microorganismo'].value_counts().head(3).index.tolist()

    # Selecionar os três antibióticos com mais interpretações "Sensível Aumentando Exposição" e "Sensível Dose-Dependente"
    antibioticos_maior_sensivel = sensivel_periodo_selecionado.groupby('ds_antibiotico_microorganismo').size().sort_values(ascending=False).head(3).index.tolist()

    col4, col5, col6 = st.columns([1, 1, 2])

    # Coluna 4
    col4.subheader("Resistente", divider="green")
    for i, antibiotico in enumerate(antibioticos_maior_resistencia):
        delta_casos_ala, alas_selecionadas = calcular_delta_casos_ala(df_periodo_selecionado, df_periodo_anterior, antibiotico, 'Resistente')

        col4.metric(f"{antibiotico}",
                    f"{resistencia_periodo_selecionado[resistencia_periodo_selecionado['ds_antibiotico_microorganismo'] == antibiotico].shape[0]} casos",
                    delta=f"Casos na mesma ala: {delta_casos_ala}"
                    )
        st.markdown(f"Ala(s): {', '.join(alas_selecionadas)} - Antibiótico: {antibiotico}")

    # Coluna 5
    col5.subheader("Sensível AD/DD", divider="green")
    
    for i, antibiotico in enumerate(antibioticos_maior_sensivel):
        resultado_sensivel_AE = calcular_delta_casos_ala(df_periodo_selecionado, df_periodo_anterior, antibiotico, 'Sensível Aumentando Exposição')
        resultado_sensivel_DD = calcular_delta_casos_ala(df_periodo_selecionado, df_periodo_anterior, antibiotico, 'Sensível Dose-Dependente')

        delta_casos_ala = resultado_sensivel_AE[0] + resultado_sensivel_DD[0]
        alas_selecionadas = resultado_sensivel_AE[1].union(resultado_sensivel_DD[1])

        col5.metric(f"{antibiotico}",
                    f"{sensivel_periodo_selecionado[sensivel_periodo_selecionado['ds_antibiotico_microorganismo'] == antibiotico].shape[0]} casos",
                    delta=f"Casos na mesma ala: {delta_casos_ala}"
                    )
        st.markdown(f"Ala(s): {', '.join(alas_selecionadas)} - Antibiótico: {antibiotico}")

    # Exibir resumo no DataFrame abaixo do gráfico
    resumo_antibioticos = df_chart.groupby(['ds_antibiotico_microorganismo', 'cd_interpretacao_antibiograma']).size().unstack(fill_value=0)
    resumo_antibioticos = resumo_antibioticos.reset_index()
    
    # Renomear a coluna 'ds_antibiotico_microorganismo' para 'Antibiótico'
    resumo_antibioticos = resumo_antibioticos.rename(columns={'ds_antibiotico_microorganismo': 'Antibiótico'})
    
    col6.dataframe(resumo_antibioticos, use_container_width=True, hide_index=True)
    
    # Adicionar informações sobre os microorganismos selecionados
    st.write(f"Microorganismos selecionados: {', '.join(microorganismos_selecionados) if microorganismos_selecionados else 'Todos'}")
    st.write(f"Período selecionado: {filtro_periodo[0]} a {filtro_periodo[1]}")
    st.write("(AD): Aumento de Dose e (DD): Dose Dependente")
