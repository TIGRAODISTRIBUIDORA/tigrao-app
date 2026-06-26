import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("Painel do Vendedor - Sistema de Vendas")

# Caminhos dos arquivos de dados na nuvem
CAMINHO_EXCEL = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES = "clientes_tigrao.txt"

# 1. Gerenciamento da Lista de Clientes
clientes_padrao = ["Supermercado Silva", "Mercado do João", "Conveniência Posto Central", "Mercearia Alvorada"]

# Cria o arquivo de clientes se não existir
if not os.path.exists(CAMINHO_CLIENTES):
    with open(CAMINHO_CLIENTES, "w", encoding="utf-8") as f:
        for c in clientes_padrao:
            f.write(f"{c}\n")

# Lê os clientes cadastrados
with open(CAMINHO_CLIENTES, "r", encoding="utf-8") as f:
    clientes = [linha.strip() for linha in f.readlines() if linha.strip()]

# 2. Catálogo de Produtos
produtos_dados = {
    "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
    "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
    "Estoque": [150, 200, 500, 100]
}
df_produtos = pd.DataFrame(produtos_dados)

# 3. Criação das Abas no Aplicativo
aba_pedido, aba_cadastro = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Novo Cliente"])

# --- ABA 1: PASSAR PEDIDO ---
with aba_pedido:
    with st.form("formulario_pedido"):
        st.subheader("1. Dados do Cliente")
        cliente_selecionado = st.selectbox("Selecione o Cliente para o Pedido", clientes)
        
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
            novo_pedido = pd.DataFrame([{
                "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Cliente": cliente_selecionado,
                "Produto": produto_selecionado,
                "Quantidade": int(quantidade),
                "Total": float(valor_final),
                "Pagamento": forma_pagamento,
                "Obs": observacao
            }])
            
            if os.path.exists(CAMINHO_EXCEL):
                df_existente = pd.read_excel(CAMINHO_EXCEL)
                df_final = pd.concat([df_existente, novo_pedido], ignore_index=True)
            else:
                df_final = novo_pedido
                
            df_final.to_excel(CAMINHO_EXCEL, index=False)
            st.success(f"✅ Pedido gravado com sucesso!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Erro ao salvar o pedido: {e}")

# --- ABA 2: CADASTRAR NOVO CLIENTE ---
with aba_cadastro:
    st.subheader("📝 Cadastro de Novo Cliente")
    with st.form("formulario_cliente"):
        novo_cliente = st.text_input("Nome do Mercado / Cliente (Ex: Mercado da Vila)")
        botao_cadastrar = st.form_submit_button("💾 Salvar Cliente no Sistema")
        
    if botao_cadastrar:
        if novo_cliente.strip() == "":
            st.warning("⚠️ Por favor, digite o nome do cliente antes de salvar.")
        elif novo_cliente.strip() in clientes:
            st.error("❌ Este cliente já está cadastrado no sistema!")
        else:
            try:
                # Adiciona o novo cliente no arquivo de texto
                with open(CAMINHO_CLIENTES, "a", encoding="utf-8") as f:
                    f.write(f"{novo_cliente.strip()}\n")
                
                st.success(f"🎉 Cliente '{novo_cliente}' cadastrado com sucesso!")
                st.info("💡 Atualize a página do seu navegador para que ele apareça na lista de pedidos.")
            except Exception as e:
                st.error(f"Erro ao cadastrar cliente: {e}")
