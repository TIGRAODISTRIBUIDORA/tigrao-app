import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("Painel do Vendedor - Lançamento de Pedidos")

# Onde o arquivo vai ser salvo no seu computador
CAMINHO_EXCEL = os.path.expanduser("~/Downloads/vendas_tigrao.xlsx")

clientes = ["Supermercado Silva", "Mercado do João", "Conveniência Posto Central", "Mercearia Alvorada"]
produtos_dados = {
    "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
    "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
    "Estoque": [150, 200, 500, 120]
}
df_produtos = pd.DataFrame(produtos_dados)

with st.form("formulario_pedido"):
    st.subheader("1. Dados do Cliente")
    cliente_selecionado = st.selectbox("Selecione o Cliente", clientes)
    
    st.subheader("2. Itens do Pedido")
    produto_selecionado = st.selectbox("Selecione o Produto", df_produtos["Produto"].tolist())
    
    preco_unitario = float(df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Preço (R$)"].values[0])
    estoque_atual = int(df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Estoque"].values[0])
    
    st.info(f"Preço Unitário: R$ {preco_unitario:.2f} | Estoque no Tigrão: {estoque_atual} fardos")
    
    quantidade = st.number_input("Quantidade de Fardos/Caixas", min_value=1, max_value=estoque_atual, step=1)
    
    st.subheader("3. Pagamento e Entrega")
    forma_pagamento = st.selectbox("Forma de Pagamento", ["Boleto 30 dias", "Pix Tigrão", "Dinheiro", "Cartão na Entrega"])
    observacao = st.text_area("Observações do Pedido")
    
    valor_final = preco_unitario * quantidade
    st.markdown(f"### 💰 Total do Pedido: **R$ {valor_final:.2f}**")
    
    botao_enviar = st.form_submit_button("🚀 Enviar Pedido para o Tigrão")

if botao_enviar:
    try:
        # Cria a linha com as informações do novo pedido
        novo_pedido = pd.DataFrame([{
            "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Cliente": cliente_selecionado,
            "Produto": produto_selecionado,
            "Quantidade": int(quantidade),
            "Total": float(valor_final),
            "Pagamento": forma_pagamento,
            "Obs": observacao
        }])
        
        # Carrega o arquivo existente ou cria um novo se não houver
        if os.path.exists(CAMINHO_EXCEL):
            df_existente = pd.read_excel(CAMINHO_EXCEL)
            df_final = pd.concat([df_existente, novo_pedido], ignore_index=True)
        else:
            df_final = novo_pedido
            
        # Grava os dados no Excel
        df_final.to_excel(CAMINHO_EXCEL, index=False)
        
        st.success(f"✅ Pedido gravado no arquivo 'vendas_tigrao.xlsx' com sucesso!")
        st.balloons()
        
        st.write("Resumo do pedido:")
        st.dataframe(novo_pedido)
        
    except Exception as e:
        st.error(f"Erro ao salvar o arquivo: {e}. Tente instalar a ferramenta com o comando: pip install openpyxl")
