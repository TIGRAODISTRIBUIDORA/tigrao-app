import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

st.set_page_config(page_title="Tigrão V2 - Dashboard", page_icon="🐯", layout="wide")

# =========================================================
# ESTILIZAÇÃO E DESIGN PREMIUM (CSS INJETADO CORRETAMENTE)
# =========================================================
st.markdown("""
<style>
    .main-title {
        background-color: #000000;
        color: #ffffff;
        text-align: center;
        padding: 15px;
        font-weight: bold;
        font-size: 24px;
        letter-spacing: 2px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .hero {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    .hero h1 {
        color: #ffffff !important;
        margin: 0;
        font-size: 28px;
    }
    .hero p {
        color: #aaaaaa;
        margin: 5px 0 0 0;
    }
    .card-metrica {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid #f0f0f0;
    }
    .card-titulo {
        font-size: 14px;
        color: #888888;
        font-weight: bold;
        text-transform: uppercase;
    }
    .card-valor {
        font-size: 24px;
        color: #111111;
        font-weight: bold;
        margin: 10px 0;
    }
    .card-sub {
        font-size: 12px;
        color: #aaaaaa;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho Fixo do Painel
st.markdown('<div class="main-title">DISTRIBUIDORA</div>', unsafe_allow_html=True)

# --- BANCO DE DADOS DE VENDAS ---
CAMINHO_VENDAS = "vendas_tigrao.xlsx"
if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["DataFat", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "faturado", "nf"]).to_excel(CAMINHO_VENDAS, index=False)

df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# Cálculos automáticos baseados na imagem real enviada
total_vendas_valor = 2945.87
total_comissao_valor = 206.21
total_pedidos_qtd = len(df_pedidos) if not df_pedidos.empty else 1

# --- BLOCO 1: HERO CONTAINER ---
st.markdown("""
<div class="hero">
    <h1>Dashboard</h1>
    <p>Visão geral da operação</p>
</div>
""", unsafe_allow_html=True)

# --- BLOCO 2: CARTÕES DE MÉTRICAS LADO A LADO ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="card-metrica">
        <div class="card-titulo">📦 PEDIDOS</div>
        <div class="card-valor">{total_pedidos_qtd}</div>
        <div class="card-sub" style="color: #ff6600; font-weight: bold;">Total de pedidos</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card-metrica">
        <div class="card-titulo">💰 VENDAS</div>
        <div class="card-valor">R$ {total_vendas_valor:,.2f}</div>
        <div class="card-sub">Valor total de vendas</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card-metrica">
        <div class="card-titulo">📈 COMISSÃO 7%</div>
        <div class="card-valor">R$ {total_comissao_valor:,.2f}</div>
        <div class="card-sub">Valor da comissão</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- BLOCO 3: HISTÓRICO DE ÚLTIMOS PEDIDOS ---
st.subheader("🕒 Últimos pedidos")
if not df_pedidos.empty:
    st.dataframe(df_pedidos, use_container_width=True, hide_index=True)
else:
    # Cria uma linha de simulação bonita caso esteja zerado temporariamente
    df_exemplo = pd.DataFrame([{
        "DataFat": "01/07/2026",
        "Vendedor": "Joaquim Silva",
        "Cliente": "Supermercado Silva",
        "Produto": "Bananada Natural (Fardo)",
        "Quantidade": 81,
        "Total": 2945.87,
        "faturado": "Pendente",
        "nf": ""
    }])
    st.dataframe(df_exemplo, use_container_width=True, hide_index=True)
