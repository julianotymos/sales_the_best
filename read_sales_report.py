import streamlit as st
import psycopg2
import pandas as pd
from psycopg2.extras import RealDictCursor
import datetime

from get_conection import get_connection

def read_sales_report(start_date, end_date):
    """
    Modificado para incluir dados de vendas do 99food.
    """
    query = """
    SELECT 
        s.data_venda, 
        s.total + COALESCE(i.total_ifood, 0) + COALESCE(N.total_99food, 0) AS total, 
        s.total AS total_loja, 
        s.qtd_vendas AS qtd_vendas_loja, 
        ROUND(s.ticket_medio, 2) AS ticket_medio_loja,
        COALESCE(i.total_ifood, 0) AS total_ifood, 
        COALESCE(i.QTD_IFOOD, 0) AS qtd_vendas_ifood, 
        ROUND(COALESCE(i.ticket_medio_ifood, 0), 2) AS ticket_medio_ifood ,
        COALESCE(N.total_99food, 0) AS total_99food, 
        COALESCE(N.qtd_99food, 0) AS qtd_vendas_99food, 
        ROUND(COALESCE(N.ticket_medio_99food, 0), 2) AS ticket_medio_99food 
    FROM (
        SELECT 
            DATE(s.created_at) AS data_venda,
            SUM(s.amount - S.CHANGE_AMOUNT) AS total,
            COUNT(1) AS qtd_vendas,
            SUM(s.amount - S.CHANGE_AMOUNT) / COUNT(1) AS ticket_medio
        FROM sales s
        WHERE 
        s.type = 0
        AND S.abstract_sale = false
        GROUP BY DATE(s.created_at)
    ) AS s
    LEFT JOIN (
        SELECT 
            DATE(od.order_date) AS data_venda,
            SUM(od.ITEM_VALUE) AS total_ifood,
            COUNT(1) AS qtd_ifood,
            SUM(od.ITEM_VALUE) / COUNT(1) AS ticket_medio_ifood
        FROM order_delivery od
        where 1=1
        and od.sales_channel in ('iFood' , 'Sob Demanda')
        AND od.CANCELLATION_SOURCE IS not null

        GROUP BY DATE(od.order_date)
    ) AS i ON i.data_venda = s.data_venda
    LEFT JOIN (
        SELECT 
            DATE(od.order_date) AS data_venda,
            SUM(od.ITEM_VALUE) AS total_99food,
            COUNT(1) AS qtd_99food,
            SUM(od.ITEM_VALUE) / COUNT(1) AS ticket_medio_99food
        FROM order_delivery od
        where 1=1
        and od.sales_channel in ('99food')
        AND od.CANCELLATION_SOURCE IS not null
        GROUP BY DATE(od.order_date)
    ) AS N ON N.data_venda = s.data_venda

    WHERE s.data_venda >= %s
    AND s.data_venda <= %s
    ORDER BY s.data_venda desc;
    """
    column_rename_map = {
        'data_venda': 'Data da Venda',
        'total': 'Total Geral',
        'total_loja': 'Total Loja',
        'qtd_vendas_loja': 'Qtd. Vendas Loja',
        'ticket_medio_loja': 'Ticket Médio Loja',
        'total_ifood': 'Total iFood',
        'qtd_vendas_ifood': 'Qtd. Vendas iFood',
        'ticket_medio_ifood': 'Ticket Médio iFood',
        # --- COLUNAS ADICIONADAS ---
        'total_99food': 'Total 99food',
        'qtd_vendas_99food': 'Qtd. Vendas 99food',
        'ticket_medio_99food': 'Ticket Médio 99food'
    }
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (start_date, end_date))
            data = cursor.fetchall()
            df = pd.DataFrame(data)
            if not df.empty:
                # Renomeia as colunas do DataFrame principal para ter nomes temporários para o pandas
                df.columns = list(column_rename_map.keys())
                
                # Conversão de tipos para garantir que sejam numéricos
                numeric_cols_original = list(column_rename_map.keys())[1:]
                for col in numeric_cols_original:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # --- CALCULA O DATAFRAME DE TOTAIS ---
                # Cria um dicionário com os totais de cada coluna
                total_row_data = df[numeric_cols_original].sum().to_dict()
                
                # Calcula o total de vendas geral
                total_vendas_geral = (
                    total_row_data['qtd_vendas_loja'] + 
                    total_row_data['qtd_vendas_ifood'] + 
                    total_row_data['qtd_vendas_99food'] # Adicionado 99food
                )
                
                # Calcula o ticket médio geral
                ticket_medio_geral = total_row_data['total'] / total_vendas_geral if total_vendas_geral > 0 else 0
                
                # Adiciona as métricas calculadas ao dicionário de totais
                total_row_data['ticket_medio_loja'] = total_row_data['total_loja'] / total_row_data['qtd_vendas_loja'] if total_row_data['qtd_vendas_loja'] > 0 else 0
                total_row_data['ticket_medio_ifood'] = total_row_data['total_ifood'] / total_row_data['qtd_vendas_ifood'] if total_row_data['qtd_vendas_ifood'] > 0 else 0
                total_row_data['ticket_medio_99food'] = total_row_data['total_99food'] / total_row_data['qtd_vendas_99food'] if total_row_data['qtd_vendas_99food'] > 0 else 0 # Adicionado 99food
                
                # Adiciona o ticket médio geral ao dicionário de totais
                total_row_data['ticket_medio_total'] = ticket_medio_geral
                
                # Cria o DataFrame de totais com uma única linha
                total_row_df = pd.DataFrame([total_row_data])

                cols_financeiras = [
                    'ticket_medio_loja', 
                    'ticket_medio_ifood', 
                    'ticket_medio_99food', # Adicionado 99food
                    'ticket_medio_total'
                ]
                # Arredonda as colunas financeiras
                total_row_df[cols_financeiras] = total_row_df[cols_financeiras].round(2)

                # Define as colunas que devem ser arredondadas para 0 casas decimais (inteiro)
                cols_inteiras = ['qtd_vendas_loja', 'qtd_vendas_ifood', 'qtd_vendas_99food'] # Adicionado 99food
                total_row_df[cols_inteiras] = total_row_df[cols_inteiras].round(0).astype(int)

                # --- RENOMEIA AS COLUNAS DOS DOIS DATAFRAMES ---
                df.rename(columns=column_rename_map, inplace=True)
                total_row_df.rename(columns=column_rename_map, inplace=True)
                
                return df, total_row_df
                
            # Retorna DataFrames vazios caso não haja dados
            return pd.DataFrame(columns=list(column_rename_map.values())), pd.DataFrame(columns=list(column_rename_map.values()))

#start_date = datetime.date(2025, 8, 12) # Primeiro dia de agosto de 2025
#end_date = datetime.date(2025, 8, 12)   # Nono dia de agosto de 2025
#data , sum_data = read_sales_report(end_date=end_date , start_date=start_date )
#print(data )
#print(sum_data)
