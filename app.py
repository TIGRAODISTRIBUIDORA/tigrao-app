import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("Painel do Vendedor - Cada coisa no seu lugar")

# PARAMETRIZAÇÃO DE COMISSÃO (5%)
PERCENTUAL_COMISSAO = 0.05  

# Caminhos dos arquivos de dados no servidor em nuvem
CAMINHO_EXCEL = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES_EXCEL = "clientes_tigrao.xlsx"

# 1. BANCO DE DADOS DE CLIENTES
if not os.path.exists(CAMINHO_CLIENTES_EXCEL):
    clientes_iniciais = pd.DataFrame([
        {"Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100", "IE": "Isento", "Telefone": "(11) 99999-9999"},
        {"Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500", "IE": "123456789", "Telefone": "(11) 98888-8888"}
    ])
    clientes_iniciais.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)

df_clientes_salvos = pd.read_excel(CAMINHO_CLIENTES_EXCEL)
lista_nomes_clientes = df_clientes_salvos["Nome"].dropna().tolist()

# 2. BANCO DE DADOS DE PEDIDOS
if os.path.exists(CAMINHO_EXCEL):
    df_pedidos = pd.read_excel(CAMINHO_EXCEL)
    if "Status" not in df_pedidos.columns:
        df_pedidos["Status"] = "Pendente"
        df_pedidos.to_excel(CAMINHO_EXCEL, index=False)
else:
    df_pedidos = pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status"])

# 3. CATÁLOGO DE PRODUTOS
produtos_dados = {
    "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
    "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
    "Estoque": [150, 200, 300, 100]
}
df_produtos = pd.DataFrame(produtos_dados)

# 4. AS 5 ABAS ORGANIZADAS E SEPARADAS
aba_pedido, aba_cadastro, aba_ver_clientes, aba_consulta_pedidos, aba_comissoes = st.tabs([
    "📋 Passar Pedido", 
    "➕ Cadastrar Cliente",
    "🔍 Consultar Clientes",
    "📦 Consultar Pedidos", 
    "💰 Comissões"
])

# --- ABA 1: PASSAR PEDIDO ---
with aba_pedido:
    with st.form("formulario_pedido"):
        st.subheader("1. Dados do Cliente")
        cliente_selecionado = st.selectbox("Selecione o Cliente para o Pedido", lista_nomes_clientes)
        
        if cliente_selecionado:
            dados_c = df_clientes_salvos[df_clientes_salvos["Nome"] == cliente_selecionado].iloc[0]
            st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']}")
        
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
        comissao_estimada = valor_final * PERCENTUAL_COMISSAO
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
                "Obs": observacao,
                "Status": "Pendente"
            }])
            
            df_final = pd.concat([df_pedidos, novo_pedido], ignore_index=True)
            df_final.to_excel(CAMINHO_EXCEL, index=False)
            st.success(f"✅ Pedido enviado! Status inicial: PENDENTE")
            st.balloons()
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar o pedido: {e}")

# --- ABA 2: CADASTRAR CLIENTE ---
with aba_cadastro:
    st.subheader("📝 Cadastro de Novo Cliente")
    with st.form("formulario_cliente"):
        nome_input = st.text_input("Nome Razão Social / Nome Fantasia")
        cnpj_input = st.text_input("CNPJ")
        ie_input = st.text_input("Inscrição Estadual (IE)")
        endereco_input = st.text_input("Endereço Completo")
        telefone_input = st.text_input("Telefone de Contato")
        
        botao_cadastrar = st.form_submit_button("💾 Salvar Cliente no Sistema")
        
    if botao_cadastrar:
        if nome_input.strip() == "" or cnpj_input.strip() == "":
            st.warning("⚠️ Nome e CNPJ são obrigatórios.")
        elif nome_input.strip() in lista_nomes_clientes:
            st.error("❌ Este cliente já existe!")
        else:
            try:
                novo_cliente_df = pd.DataFrame([{
                    "Nome": nome_input.strip(),
                    "CNPJ": cnpj_input.strip(),
                    "Endereco": endereco_input.strip(),
                    "IE": ie_input.strip(),
                    "Telefone": telefone_input.strip()
                }])
                df_atualizado = pd.concat([df_clientes_salvos, novo_cliente_df], ignore_index=True)
                df_atualizado.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)
                st.success(f"🎉 Cliente '{nome_input}' cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar cliente: {e}")

# --- ABA 3: CONSULTAR CLIENTES (NOVA) ---
with aba_ver_clientes:
    st.subheader("🔍 Lista de Clientes Cadastrados")
    busca_cliente = st.text_input("🔍 Digite o nome do cliente para pesquisar")
    
    df_clientes_filtrados = df_clientes_salvos.copy()
    if busca_cliente:
        df_clientes_filtrados = df_clientes_filtrados[df_clientes_filtrados["Nome"].str.contains(busca_cliente, case=False, na=False)]
        
    st.dataframe(df_clientes_filtrados, use_container_width=True)

# --- ABA 4: CONSULTAR PEDIDOS (PENDENTES E FATURADOS SEPARADOS) ---
with aba_consulta_pedidos:
    st.subheader("📦 Acompanhamento de Pedidos")
    
    # Filtro rápido por Status (Pendente ou Faturado)
    status_escolhido = st.radio("Filtrar por Situação do Pedido:", ["Todos", "Apenas Pendentes", "Apenas Faturados", "Apenas Entregues"], horizontal=True)
    
    df_consulta = df_pedidos.copy()
    
    if status_escolhido == "Apenas Pendentes":
        df_consulta = df_consulta[df_consulta["Status"] == "Pendente"]
    elif status_escolhido == "Apenas Faturados":
        df_consulta = df_consulta[df_consulta["Status"] == "Faturado"]
    elif status_escolhido == "Apenas Entregues":
        df_consulta = df_consulta[df_consulta["Status"] == "Entregue"]

    if not df_consulta.empty:
        st.dataframe(df_consulta[["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Status", "Pagamento"]], use_container_width=True)
    else:
        st.info(f"ℹ️ Nenhum pedido encontrado na categoria: {status_escolhido}.")

# --- ABA 5: APENAS COMISSÕES (PURAMENTE FINANCEIRO) ---
with aba_comissoes:
    st.subheader("💰 Extrato Financeiro de Comissões")
    
    if not df_pedidos.empty:
        total_vendas = df_pedidos["Total"].sum()
        total_comissao = total_vendas * PERCENTUAL_COMISSAO
        
        # Painel puramente financeiro, sem misturar tabelas de entrega
        c1, c2 = st.columns(2)
        c1.metric("Volume Total Vendido", f"R$ {total_vendas:.2f}")
        c2.metric("Sua Comissão Acumulada (5%)", f"R$ {total_comissao:.2f}")
        
        st.markdown("---")
        st.write("📊 **Resumo de ganhos por pedido enviado:**")
        
        # Cria uma tabelinha simples focada só em quanto ele ganhou por venda
        df_comissao_aba = df_pedidos.copy()
        df_comissao_aba["Comissão (R$)"] = df_comissao_aba["Total"] * PERCENTUAL_COMISSAO
        st.dataframe(df_comissao_aba[["Data_Hora", "Cliente", "Total", "Comissão (R$)"]], use_container_width=True)
    else:
        st.info("ℹ️ Nenhuma comissão acumulada. Lance pedidos para ver seus ganhos aqui.")
