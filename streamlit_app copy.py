import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from read_process_last_run import read_process_last_run
from datetime import datetime, timedelta
from typing import List
from read_sales_report import read_sales_report
# Show app title and description.
# --- Início da Aplicação Streamlit ---

st.set_page_config(
    page_title="Dashboard de Vendas",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Dashboard de Vendas")
st.markdown("Visão geral das vendas diárias e totais da loja e do iFood.")

# --- Barra Lateral para Filtros e Status ---
st.sidebar.header("🗓️ Filtros de Data")

start_date = st.sidebar.date_input("Data Inicial", datetime.now().date().replace(day=1))

end_date = st.sidebar.date_input("Data Final", datetime.now().date())

if start_date > end_date:
    st.sidebar.error("⚠️ Erro: A data inicial não pode ser posterior à data final.")
else:
    # --- Chamada das Funções ---
    daily_sales_df, total_sales_df = read_sales_report(start_date, end_date)
    last_run_df = read_process_last_run(["SALES_THE_BEST", "IFOOD_ORDERS_PROCESS"])

    # --- Seção de Métricas Principais (Totais) ---
    st.header("Metricas Totais")

    if not total_sales_df.empty:
        total_row = total_sales_df.iloc[0]
        
        col1, col2, col3, col4 , col5 , col6 , col7 , col8 , col9 = st.columns(9)
        with col1:
            st.metric("Total Geral", f"R$ {total_row['Total Geral']:,.2f}")

        with col2:
            st.metric("Qtd. Total de Vendas", int(total_row['Qtd. Vendas Loja'] + total_row['Qtd. Vendas iFood']))
        
        with col3:
            st.metric("Ticket Medio Total", f"R$ {total_row['ticket_medio_total']:,.2f}")

        with col4:
            st.metric("Total Loja", f"R$ {total_row['Total Loja']:,.2f}")
        with col5:
            st.metric("Qtd. Vendas Loja", int(total_row['Qtd. Vendas Loja']))
        with col6:
            st.metric("Ticket Médio Loja", f"R$ {total_row['Ticket Médio Loja']:,.2f}" )
        with col7:
            st.metric("Total iFood", f"R$ {total_row['Total iFood']:,.2f}")
        with col8:
            st.metric("Qtd. Vendas iFood", int(total_row['Qtd. Vendas iFood']))
        with col9:
            st.metric("Ticket Médio iFood", f"R$ {total_row['Ticket Médio iFood']:,.2f}" )
        
        st.markdown("---")
        
        # --- Seção de Gráficos ---
        st.header("Análise Diária de Vendas")
        
        st.subheader("Gráfico de Vendas por Canal")
        
        st.line_chart(daily_sales_df, x='Data da Venda', y=['Total Loja', 'Total iFood', 'Total Geral'])
        
        # --- Tabela de Dados Brutos ---
        st.subheader("Tabela de Dados Detalhada")
        st.dataframe(daily_sales_df.set_index('Data da Venda'))
    
    else:
        st.warning("⚠️ Não há dados de vendas para o período selecionado. Por favor, ajuste o filtro de datas.")
        
    # --- Status de Processamento na Barra Lateral ---
    st.sidebar.markdown("---")
    st.sidebar.header("🔄 Status de Processamento")
    if not last_run_df.empty:
        for index, row in last_run_df.iterrows():
            st.sidebar.info(f"**{row['name']}**\nÚltima execução: {row['last_run_date'].strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        st.sidebar.warning("Nenhum dado de status encontrado.")