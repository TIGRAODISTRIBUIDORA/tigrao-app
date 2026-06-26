import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("Painel do Vendedor - Sistema Prático de Vendas")

# PERCENTUAL DE COMISSÃO PADRÃO (5%)
PERCENTUAL_COMISSAO = 0.05  

# Caminhos dos arquivos de dados no servidor em nuvem
CAMINHO_EXCEL = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES_EXCEL = "clientes_tigrao.xlsx"

# 1. INICIALIZAÇÃO DOS BANCOS DE DADOS
if not os.path.exists(CAMINHO_CLIENTES_EXCEL):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100", "IE": "Isento", "Telefone": "(11) 99999-9999"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500", "IE": "123456789", "Telefone": "(11) 98888-8888"}
    ]).to_excel(CAMINHO_CLIENTES_EXCEL, index=False)

if not os.path.exists(CAMINHO_EXCEL):
    pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status"]).to_excel(CAMINHO_EXCEL, index=False)

# RELEITURA DOS DADOS
df_clientes_salvos = pd.read_excel(CAMINHO_CLIENTES_EXCEL)
df_pedidos = pd.read_excel(CAMINHO_EXCEL)

# CATÁLOGO FIXO DE PRODUTOS
produtos_dados = {
    "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
    "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
    "Estoque": [100, 100, 100, 100]
}
df_produtos = pd.DataFrame(produtos_dados)

lista_nomes_reais = df_clientes_salvos["Nome"].dropna().astype(str).tolist()
lista_produtos_geral = df_produtos["Produto"].tolist()

# AS 5 ABAS LIMPAS E DIRETAS DO SISTEMA
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Passar Pedido", "➕ Cadastrar Cliente", "🔍 Consultar Clientes", 
    "📦 Consultar Pedidos", "💰 Comissões"
])

# --- ABA 1: PASSAR PEDIDO ---
with tab1:
    st.subheader("1. Seleção do Cliente")
    pesquisa_input = st.text_input("🔍 Digite o Nome ou o Código do cliente para buscar:")
    if pesquisa_input and not df_clientes_salvos.empty:
        texto_busca = pesquisa_input.strip().lower()
        df_filtrado_cl = df_clientes_salvos[df_clientes_salvos["Nome"].astype(str).str.lower().str.contains(texto_busca, na=False) | df_clientes_salvos["Codigo"].astype(str).str.contains(texto_busca, na=False)]
    else:
        df_filtrado_cl = df_clientes_salvos.copy()
    lista_selectbox = df_filtrado_cl["Nome"].dropna().astype(str).tolist()
    
    if pesquisa_input and not lista_selectbox:
        st.error(f"❌ CLIENTE NÃO ENCONTRADO!")
        cliente_final_nome = None
    else:
        exibir_lista = lista_selectbox if lista_selectbox else ["Nenhum cliente disponível"]
        cliente_final_nome = st.selectbox("Selecione o cliente verificado na lista:", exibir_lista, key="sel_cliente_pedido")
        if cliente_final_nome and cliente_final_nome != "Nenhum cliente disponível":
            dados_c = df_clientes_salvos[df_clientes_salvos["Nome"].astype(str) == cliente_final_nome].iloc[0]
            st.success(f"🟩 CLIENTE CONFIRMADO: {dados_c['Nome']} (COD-{int(dados_c['Codigo'])})")
            st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']}")

    st.markdown("---")
    st.subheader("2. Itens do Pedido")
    pesquisa_prod_input = st.text_input("🔍 Digite o nome do Produto para buscar no catálogo:")
    if pesquisa_prod_input:
        df_filtrado_prod = df_produtos[df_produtos["Produto"].astype(str).str.lower().str.contains(pesquisa_prod_input.strip().lower(), na=False)]
        lista_produtos_filtrados = df_filtrado_prod["Produto"].tolist()
    else:
        lista_produtos_filtrados = lista_produtos_geral
        
    if pesquisa_prod_input and not lista_produtos_filtrados:
        st.warning(f"⚠️ Nenhum produto encontrado com o nome '{pesquisa_prod_input}'. Mostrando catálogo completo.")
        lista_produtos_filtrados = lista_produtos_geral

    with st.form("formulario_pedido"):
        produto_selecionado = st.selectbox("Confirme o Produto na lista:", lista_produtos_filtrados if lista_produtos_filtrados else ["Nenhum produto"])
        try:
            prod_linha = df_produtos[df_produtos["Produto"] == produto_selecionado].iloc[0]
            preco_unitario = float(prod_linha["Preço (R$)"])
            estoque_atual = int(prod_linha["Estoque"])
            st.info(f"Preço Unitário: R$ {preco_unitario:.2f} | Estoque no Tigrão: {estoque_atual} fardos")
            quantidade = st.number_input("Quantidade", min_value=1, max_value=max(1, estoque_atual), step=1)
            valor_final = preco_unitario * quantidade
        except Exception:
            preco_unitario, estoque_atual, quantidade, valor_final = 0.0, 1, 1, 0.0
        
        forma_pagamento = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix Tigrão", "Dinheiro", "Cartão na Entrega"])
        observacao = st.text_area("Observações")
        st.markdown(f"### 💰 Total do Pedido: **R$ {valor_final:.2f}**")
        botao_enviar = st.form_submit_button("🚀 Enviar Pedido para o Tigrão")

    if botao_enviar and cliente_final_nome and produto_selecionado != "Nenhum produto":
        novo_pedido = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), "Cliente": cliente_final_nome, "Produto": produto_selecionado, "Quantidade": int(quantidade), "Total": float(valor_final), "Pagamento": forma_pagamento, "Obs": observacao, "Status": "Pendente"}])
        pd.concat([df_pedidos, novo_pedido], ignore_index=True).to_excel(CAMINHO_EXCEL, index=False)
        st.success(f"✅ Pedido enviado!")
        st.balloons()
        st.rerun()

# --- ABA 2: CADASTRAR CLIENTE ---
with tab2:
    st.subheader("📝 Cadastro de Novo Cliente")
    with st.form("formulario_cliente"):
        nome_input = st.text_input("Nome Razão Social")
        cnpj_input = st.text_input("CNPJ")
        ie_input = st.text_input("IE")
        endereco_input = st.text_input("Endereço")
        telefone_input = st.text_input("Telefone")
        botao_cadastrar = st.form_submit_button("💾 Salvar Cliente")
    if botao_cadastrar and nome_input.strip() and cnpj_input.strip():
        proximo_codigo = int(df_clientes_salvos["Codigo"].max() + 1) if not df_clientes_salvos.empty else 1
        novo_cl = pd.DataFrame([{"Codigo": proximo_codigo, "Nome": nome_input.strip(), "CNPJ": cnpj_input.strip(), "Endereco": endereco_input.strip(), "IE": ie_input.strip(), "Telefone": telefone_input.strip()}])
        pd.concat([df_clientes_salvos, novo_cl], ignore_index=True).to_excel(CAMINHO_CLIENTES_EXCEL, index=False)
        st.success("🎉 Cliente cadastrado!")
        st.rerun()

# --- ABA 3: CONSULTAR CLIENTES ---
with tab3:
    st.subheader("🔍 Lista de Clientes")
    busca_cliente = st.text_input("Pesquisar cliente geral:")
    df_vis_cl = df_clientes_salvos.copy()
    if busca_cliente:
        df_vis_cl = df_vis_cl[df_vis_cl["Nome"].astype(str).str.lower().str.contains(busca_cliente.strip().lower(), na=False)]
    st.dataframe(df_vis_cl, use_container_width=True, hide_index=True)

# --- ABA 4: CONSULTAR PEDIDOS ---
with tab4:
    st.subheader("📦 Pedidos lançados")
    status_escolhido = st.radio("Filtrar Situação:", ["Todos", "Apenas Pendentes", "Apenas Faturados"], horizontal=True)
    df_c = df_pedidos.copy()
    if status_escolhido == "Apenas Pendentes" and not df_c.empty: df_c = df_c[df_c["Status"] == "Pendente"]
    elif status_escolhido == "Apenas Faturados" and not df_c.empty: df_c = df_c[df_c["Status"] == "Faturado"]
    st.dataframe(df_c, use_container_width=True, hide_index=True)

# --- ABA 5: COMISSÕES ---
with tab5:
    st.subheader("💰 Comissões do Vendedor")
    total_vendas = df_pedidos["Total"].sum() if not df_pedidos.empty else 0.0
    st.metric("Total Geral Vendido", f"R$ {total_vendas:.2f}")
    st.metric("Comissão Acumulada (5%)", f"R$ {(total_vendas * PERCENTUAL_COMISSAO):.2f}")
    if not df_pedidos.empty:
        df_comissao_aba = df_pedidos.copy()
        df_comissao_aba["Comissão (R$)"] = df_comissao_aba["Total"] * PERCENTUAL_COMISSAO
        st.dataframe(df_comissao_aba[["Data_Hora", "Cliente", "Total", "Comissão (R$)"]], use_container_width=True, hide_index=True)
