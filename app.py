import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("Painel do Vendedor - Confirmação Visual Ativada")

# PARAMETRIZAÇÃO DE COMISSÃO (5%)
PERCENTUAL_COMISSAO = 0.05  

# Caminhos dos arquivos de dados no servidor em nuvem
CAMINHO_EXCEL = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES_EXCEL = "clientes_tigrao.xlsx"

# 1. BANCO DE DADOS DE CLIENTES
if not os.path.exists(CAMINHO_CLIENTES_EXCEL):
    clientes_iniciais = pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100", "IE": "Isento", "Telefone": "(11) 99999-9999"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500", "IE": "123456789", "Telefone": "(11) 98888-8888"}
    ])
    clientes_iniciais.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)

df_clientes_salvos = pd.read_excel(CAMINHO_CLIENTES_EXCEL)

# Garante que a coluna Codigo existe na planilha
if "Codigo" not in df_clientes_salvos.columns:
    df_clientes_salvos.insert(0, "Codigo", range(1, len(df_clientes_salvos) + 1))
    df_clientes_salvos.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)

# Cria a lista de exibição combinando Código + Nome para facilitar a busca do vendedor
df_clientes_salvos["Exibicao"] = df_clientes_salvos.apply(lambda r: f"[COD-{int(r['Codigo']):03d}] {r['Nome']}", axis=1)
lista_clientes_busca = df_clientes_salvos["Exibicao"].tolist()

# 2. BANCO DE DADOS DE PEDIDOS
if os.path.exists(CAMINHO_EXCEL):
    df_pedidos = pd.read_excel(CAMINHO_EXCEL)
else:
    df_pedidos = pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status"])

# 3. CATÁLOGO DE PRODUTOS
produtos_dados = {
    "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
    "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
    "Estoque": [150, 200, 500, 100]
}
df_produtos = pd.DataFrame(produtos_dados)

# 4. AS ABAS DO APLICATIVO
aba_pedido, aba_cadastro, aba_ver_clientes, aba_consulta_pedidos, aba_comissoes = st.tabs([
    "📋 Passar Pedido", 
    "➕ Cadastrar Cliente",
    "🔍 Consultar Clientes",
    "📦 Consultar Pedidos", 
    "💰 Comissões"
])

# --- ABA 1: PASSAR PEDIDO (COM VERIFICAÇÃO EM VERDE) ---
with aba_pedido:
    st.subheader("1. Dados do Cliente")
    
    texto_pesquisa = st.text_input("🔍 Digite o Nome ou o Código do cliente para buscar:")
    
    opcoes_filtradas = [c for c in lista_clientes_busca if texto_pesquisa.lower() in c.lower()]
    
    if not opcoes_filtradas:
        st.warning("⚠️ Nenhum cliente encontrado com esse nome ou código.")
        opcoes_filtradas = lista_clientes_busca  
        
    cliente_selecionado_comb = st.selectbox("Selecione o Cliente na lista abaixo:", opcoes_filtradas)
    
    # Extrai o nome limpo do cliente para busca interna
    nome_limpo_cliente = cliente_selecionado_comb.split("] ", 1)[1] if "]" in cliente_selecionado_comb else cliente_selecionado_comb

    # Puxa os dados desse cliente específico
    dados_c = df_clientes_salvos[df_clientes_salvos["Nome"] == nome_limpo_cliente].iloc[0]
    
    # BOX VERDE DE VERIFICAÇÃO ATIVA 🟩
    st.success(f"✅ CLIENTE VERIFICADO: {dados_c['Nome']} (COD-{int(dados_c['Codigo'])})")
    
    # Mostra os detalhes fiscais organizados logo abaixo da tarja verde
    st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']} | **Tel:** {dados_c['Telefone']}")

    # Formulário para os itens do pedido
    with st.form("formulario_pedido"):
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
                "Cliente": nome_limpo_cliente,
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
        elif nome_input.strip() in df_clientes_salvos["Nome"].tolist():
            st.error("❌ Este cliente já existe!")
        else:
            try:
                proximo_codigo = int(df_clientes_salvos["Codigo"].max() + 1) if not df_clientes_salvos.empty else 1
                
                novo_cliente_df = pd.DataFrame([{
                    "Codigo": proximo_codigo,
                    "Nome": nome_input.strip(),
                    "CNPJ": cnpj_input.strip(),
                    "Endereco": endereco_input.strip(),
                    "IE": ie_input.strip(),
                    "Telefone": telefone_input.strip()
                }])
                df_atualizado = pd.concat([df_clientes_salvos.drop(columns=["Exibicao"], errors="ignore"), novo_cliente_df], ignore_index=True)
                df_atualizado.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)
                st.success(f"🎉 Cliente cadastrado com sucesso! Código gerado: COD-{proximo_codigo}")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar cliente: {e}")

# --- ABA 3: CONSULTAR CLIENTES ---
with aba_ver_clientes:
    st.subheader("🔍 Lista de Clientes Cadastrados")
    busca_cliente = st.text_input("🔍 Digite o Nome ou Código para pesquisar na listagem geral")
    
    df_clientes_visualizar = df_clientes_salvos.drop(columns=["Exibicao"], errors="ignore").copy()
    if busca_cliente:
        df_clientes_visualizar["Codigo_Str"] = df_clientes_visualizar["Codigo"].astype(str)
        df_clientes_visualizar = df_clientes_visualizar[
            df_clientes_visualizar["Nome"].str.contains(busca_cliente, case=False, na=False) |
            df_clientes_visualizar["Codigo_Str"].str.contains(busca_cliente, case=False, na=False)
        ]
        df_clientes_visualizar = df_clientes_visualizar.drop(columns=["Codigo_Str"])
        
    st.dataframe(df_clientes_visualizar[["Codigo", "Nome", "CNPJ", "IE", "Endereco", "Telefone"]], use_container_width=True, hide_index=True)

# --- ABA 4: CONSULTAR PEDIDOS ---
with aba_consulta_pedidos:
    st.subheader("📦 Acompanhamento de Pedidos")
    status_escolhido = st.radio("Filtrar por Situação do Pedido:", ["Todos", "Apenas Pendentes", "Apenas Faturados", "Apenas Entregues"], horizontal=True)
    
    df_consulta = df_pedidos.copy()
    if status_escolhido == "Apenas Pendentes":
        df_consulta = df_consulta[df_consulta["Status"] == "Pendente"]
    elif status_escolhido == "Apenas Faturados":
        df_consulta = df_consulta[df_consulta["Status"] == "Faturado"]
    elif status_escolhido == "Apenas Entregues":
        df_consulta = df_consulta[df_consulta["Status"] == "Entregue"]

    if not df_consulta.empty:
        st.dataframe(df_consulta[["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Status", "Pagamento"]], use_container_width=True, hide_index=True)
    else:
        st.info(f"ℹ️ Nenhum pedido encontrado na categoria: {status_escolhido}.")

# --- ABA 5: COMISSÕES ---
with aba_comissoes:
    st.subheader("💰 Extrato Financeiro de Comissões")
    if not df_pedidos.empty:
        total_vendas = df_pedidos["Total"].sum()
        total_comissao = total_vendas * PERCENTUAL_COMISSAO
        
        c1, c2 = st.columns(2)
        c1.metric("Volume Total Vendido", f"R$ {total_vendas:.2f}")
        c2.metric("Sua Comissão Acumulada (5%)", f"R$ {total_comissao:.2f}")
        
        st.markdown("---")
        st.write("📊 **Resumo de ganhos por pedido enviado:**")
        
        df_comissao_aba = df_pedidos.copy()
        df_comissao_aba["Comissão (R$)"] = df_comissao_aba["Total"] * PERCENTUAL_COMISSAO
