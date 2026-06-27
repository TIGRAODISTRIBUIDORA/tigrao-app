import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("Painel de Vendas Prático")

# Configurações básicas
PERCENTUAL_COMISSAO = 0.05
SENHA_DONO = "TigraoNelson2026"

CAMINHO_VENDAS = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES = "clientes_banco.xlsx"

# Inicializa arquivos básicos se não existirem
if not os.path.exists(CAMINHO_CLIENTES):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "IE": "Isento", "Endereco": "Rua Principal, 100"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "IE": "123456789", "Endereco": "Av. Central, 500"}
    ]).to_excel(CAMINHO_CLIENTES, index=False)

if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Status"]).to_excel(CAMINHO_VENDAS, index=False)

df_clientes = pd.read_excel(CAMINHO_CLIENTES)
df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# Lista simples de produtos fixa para nunca dar erro de leitura
produtos_tabela = {
    "Bananada Natural (Fardo)": 36.00,
    "Cerveja Lata 350ml (Fardo)": 42.00,
    "Refrigerante 2L (Fardo)": 48.00,
    "Água Mineral 500ml (Fardo)": 18.00
}

tab1, tab2, tab3 = st.tabs(["📋 Passar Pedido", "📦 Consultar Pedidos", "👑 Central do Dono"])

# --- ABA 1: PASSAR PEDIDO ---
with tab1:
    st.subheader("1. Escolha o Cliente")
    lista_nomes = df_clientes["Nome"].dropna().tolist()
    cliente_escolhido = st.selectbox("Selecione o Cliente:", lista_nomes)
    
    st.markdown("---")
    st.subheader("2. Itens do Pedido")
    produto_escolhido = st.selectbox("Selecione o Produto:", list(produtos_tabela.keys()))
    
    preco_un = produtos_tabela[produto_escolhido]
    st.info(f"💰 Preço unitário: R$ {preco_un:.2f}")
    
    qtd = st.number_input("Quantidade de Fardos:", min_value=1, value=1, step=1)
    total_pedido = preco_un * qtd
    st.markdown(f"### 💰 Total do Pedido: **R$ {total_pedido:.2f}**")
    
    forma_pagto = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix", "Dinheiro"])
    
    if st.button("🚀 Enviar Pedido para o Tigrão"):
        novo_p = pd.DataFrame([{
            "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "Cliente": cliente_escolhido,
            "Produto": produto_escolhido,
            "Quantidade": int(qtd),
            "Total": float(total_pedido),
            "Pagamento": forma_pagto,
            "Status": "Pendente"
        }])
        df_final = pd.concat([df_pedidos, novo_p], ignore_index=True)
        df_final.to_excel(CAMINHO_VENDAS, index=False)
        st.success("✅ Pedido enviado com sucesso!")
        st.balloons()
        st.rerun()

# --- ABA 2: CONSULTAR PEDIDOS ---
with tab2:
    st.subheader("📦 Histórico de Pedidos Lançados")
    if not df_pedidos.empty:
        st.dataframe(df_pedidos, use_container_width=True, hide_index=True)
    else:
        st.info("Nenhum pedido lançado ainda.")

# --- ABA 3: CENTRAL DO DONO ---
with tab3:
    st.subheader("🔒 Acesso Restrito da Diretoria")
    senha = st.text_input("Insira a Senha Master:", type="password")
    
    if senha == SENHA_DONO:
        st.success("👑 Painel Liberado!")
        
        # Botão simples para baixar o arquivo Excel para o seu sistema DISA
        if not df_pedidos.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_pedidos.to_excel(writer, index=False, sheet_name='Pedidos')
            
            st.download_button(
                label="📥 Baixar Planilha Excel para Nota Fiscal (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"pedidos_tigrao_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("Nenhum pedido disponível para baixar.")

