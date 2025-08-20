import datetime
import random
import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from read_process_last_run import read_process_last_run
from datetime import datetime, timedelta
from typing import List
from tab_sales_by_payment import tab_sales_by_payment
from tab_sales_total import tab_sales_total


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
st.sidebar.header("🗓️ Período de Análise")

start_date = st.sidebar.date_input("Data Inicial", datetime.now().date())
end_date = st.sidebar.date_input("Data Final", datetime.now().date())

if start_date > end_date:
    st.sidebar.error("⚠️ Erro: A data inicial não pode ser posterior à data final.")
else:
    # --- Criação das Abas ---
    tab_geral, tab_pagamento = st.tabs(["Resumo Geral", "Vendas por Pagamento"])

    with tab_geral:
        tab_sales_total(start_date, end_date)

    with tab_pagamento:
        tab_sales_by_payment(start_date, end_date)
            
    # --- Status de Processamento na Barra Lateral (comum para as duas abas) ---
    st.sidebar.markdown("---")
    st.sidebar.header("🔄 Status de Processamento")
    last_run_df = read_process_last_run(["SALES_THE_BEST", "IFOOD_ORDERS_PROCESS", "99FOOD_ORDERS_PROCESS"])
    if not last_run_df.empty:
        for index, row in last_run_df.iterrows():
            st.sidebar.info(f"**{row['name']}**\nÚltima atualização: {row['last_run_date'].strftime('%d/%m/%Y %H:%M:%S')}")
    else:
        st.sidebar.warning("Nenhum dado de status encontrado.")
