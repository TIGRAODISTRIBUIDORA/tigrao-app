import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

st.set_page_config(page_title="Tigrão - Bloco Pedidos", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("### 📦 Bloco 1: Gestão e Faturamento de Pedidos")

# Configurações do Banco de Dados Local do Bloco 1
CAMINHO_VENDAS = "vendas_tigrao.xlsx"
SENHA_NELSON = "TigraoNelson2026"

# DICIONÁRIO DE VENDEDORES AUTORIZADOS (Seus acessos exclusivos)
# Você pode mudar ou adicionar novos nomes e códigos aqui quando quiser!
VENDEDORES_CADASTRADOS = {
    "101": "Joaquim Silva",
    "102": "Pedro Santos",
    "103": "Carlos Oliveira",
    "000": "Nelson Dono"  # Seu código de teste
}

if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["Data_Hora", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Status"]).to_excel(CAMINHO_VENDAS, index=False)

df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# Garante que a coluna Vendedor existe se a planilha for antiga
if "Vendedor" not in df_pedidos.columns:
    df_pedidos.insert(1, "Vendedor", "Não Identificado")
    df_pedidos.to_excel(CAMINHO_VENDAS, index=False)

# Lista de Produtos Fixa deste Bloco
produtos_fixos = {
    "Bananada Natural (Fardo)": 36.00,
    "Cerveja Lata 350ml (Fardo)": 42.00,
    "Refrigerante 2L (Fardo)": 48.00
}

# Separação Visual das abas
aba_vendedor, aba_diretoria = st.tabs(["📱 Tela do Vendedor (Rua)", "👑 Recebimento Nelson (Central)"])

# --- 1. TELA DO VENDEDOR (Lançamento de Pedidos com Acesso) ---
with aba_vendedor:
    st.subheader("🔐 Identificação do Vendedor")
    
    # Campo de acesso exclusivo por código
    codigo_vendedor = st.text_input("Digite o seu Código Exclusivo de Vendedor:", type="password")
    
    vendedor_ativo = ""
    if codigo_vendedor:
        if codigo_vendedor in VENDEDORES_CADASTRADOS:
            vendedor_ativo = VENDEDORES_CADASTRADOS[codigo_vendedor]
            st.success(f"✅ VENDEDOR CONECTADO: {vendedor_ativo.upper()}")
        else:
            st.error("❌ CÓDIGO INVÁLIDO! Acesso não autorizado no sistema do Tigrão.")
            
    st.markdown("---")
    st.subheader("📋 Lançar Novo Pedido")
    
    cliente = st.selectbox("Selecione o Cliente:", ["Supermercado Silva", "Mercado do João", "Conveniência Central"])
    produto = st.selectbox("Selecione o Produto:", list(produtos_fixos.keys()))
    
    preco_un = produtos_fixos[produto]
    st.caption(f"Preço do fardo: R$ {preco_un:.2f}")
    
    quantidade = st.number_input("Quantidade de Fardos:", min_value=1, value=1, step=1)
    total_pedido = preco_un * quantidade
    st.markdown(f"#### 💰 Total do Pedido: **R$ {total_pedido:.2f}**")
    
    forma_pagto = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix", "Dinheiro"])
    
    if st.button("🚀 Enviar Pedido para a Central"):
        if not vendedor_ativo:
            st.error("❌ ERRO: O pedido não pode ser enviado sem um Código de Vendedor válido e ativo!")
        else:
            novo_p = pd.DataFrame([{
                "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Vendedor": vendedor_ativo,
                "Cliente": cliente,
                "Produto": produto,
                "Quantidade": int(quantidade),
                "Total": float(total_pedido),
                "Pagamento": forma_pagto,
                "Status": "Pendente"
            }])
            df_final = pd.concat([df_pedidos, novo_p], ignore_index=True)
            df_final.to_excel(CAMINHO_VENDAS, index=False)
            st.success(f"✅ Pedido de {vendedor_ativo} gravado no Excel com sucesso!")
            st.balloons()
            st.rerun()

# --- 2. TELA DO NELSON (Recebimento e Extração do Excel com nome do Vendedor) ---
with aba_diretoria:
    st.subheader("🔒 Painel de Recebimento de Pedidos")
    senha_digitada = st.text_input("Digite a Senha de Dono:", type="password")
    
    if senha_digitada == SENHA_NELSON:
        st.success("Acesso Liberado!")
        
        if not df_pedidos.empty:
            df_ordenado = df_pedidos.sort_values(by="Data_Hora", ascending=False)
            
            st.write(f"📢 Você tem **{len(df_ordenado[df_ordenado['Status']=='Pendente'])}** pedido(s) pendente(s) para faturar no DISA.")
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_ordenado.to_excel(writer, index=False, sheet_name='Pedidos_Faturamento')
            
            st.download_button(
                label="📥 Baixar Planilha Excel para Nota Fiscal (.xlsx)",
                data=buffer.getvalue(),
                file_name=f"faturamento_tigrao_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.write("---")
            st.write("📋 **Lista de Pedidos na Tela (Ordem de Chegada com Vendedor):**")
            st.dataframe(df_ordenado[["Data_Hora", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Status"]], use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ Nenhum pedido foi recebido no sistema ainda.")
