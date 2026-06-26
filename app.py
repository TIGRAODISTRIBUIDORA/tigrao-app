import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")

# PERCENTUAL DE COMISSÃO (5%)
PERCENTUAL_COMISSAO = 0.05  

# Caminhos dos arquivos de dados no servidor em nuvem
CAMINHO_EXCEL = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES_EXCEL = "clientes_tigrao.xlsx"
CAMINHO_USUARIOS_EXCEL = "usuarios_tigrao.xlsx"

# 1. BANCO DE DADOS DE USUÁRIOS/VENDEDORES
if not os.path.exists(CAMINHO_USUARIOS_EXCEL):
    usuarios_iniciais = pd.DataFrame([
        {"Nome": "Administrador Tigrao", "Email": "sodemilecem23@gmail.com", "Senha": "123", "Status": "Aprovado"}
    ])
    usuarios_iniciais.to_excel(CAMINHO_USUARIOS_EXCEL, index=False)

df_usuarios = pd.read_excel(CAMINHO_USUARIOS_EXCEL)

# 2. GERENCIAMENTO DE SESSÃO DO LOGIN
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario_nome" not in st.session_state:
    st.session_state["usuario_nome"] = ""

# --- TELA DE ACESSO (SÓ MOSTRA SE NÃO ESTIVER LOGADO) ---
if not st.session_state["logado"]:
    aba_login, aba_novo_cadastro = st.tabs(["🔐 Entrar no Sistema", "📝 Criar Nova Conta Vendedor"])
    
    with aba_login:
        st.subheader("Acesse sua Conta")
        email_login = st.text_input("E-mail cadastrado:")
        senha_login = st.text_input("Sua senha:", type="password")
        botao_logar = st.button("🚀 Entrar no Painel do Tigrão")
        
        if botao_logar:
            usuario_validar = df_usuarios[(df_usuarios["Email"].str.lower() == email_login.strip().lower()) & (df_usuarios["Senha"].astype(str) == senha_login.strip())]
            
            if not usuario_validar.empty:
                status_usuario = usuario_validar.iloc[0]["Status"]
                
                if status_usuario == "Aprovado":
                    st.session_state["logado"] = True
                    st.session_state["usuario_nome"] = usuario_validar.iloc[0]["Nome"]
                    st.success(f"Beta-vindo, {st.session_state['usuario_nome']}!")
                    st.rerun()
                else:
                    st.error("❌ Acesso Bloqueado! Sua licença ainda está 'Pendente' de aprovação na central do Tigrão.")
            else:
                st.error("❌ E-mail ou Senha incorretos.")
                
    with aba_novo_cadastro:
        st.subheader("Solicitar Cadastro de Vendedor")
        with st.form("form_cadastro_vendedor"):
            nome_cad = st.text_input("Seu Nome Completo:")
            email_cad = st.text_input("Seu E-mail:")
            senha_cad = st.text_input("Crie uma Senha:", type="password")
            botao_salvar_cad = st.form_submit_button("💾 Enviar Solicitação")
            
        if botao_salvar_cad:
            if nome_cad.strip() == "" or email_cad.strip() == "" or senha_cad.strip() == "":
                st.warning("⚠️ Todos os campos são obrigatórios.")
            elif email_cad.strip().lower() in df_usuarios["Email"].str.lower().tolist():
                st.error("❌ Este e-mail já está registrado!")
            else:
                try:
                    novo_user_df = pd.DataFrame([{
                        "Nome": nome_cad.strip(),
                        "Email": email_cad.strip().lower(),
                        "Senha": senha_cad.strip(),
                        "Status": "Pendente"
                    }])
                    df_novo_usuarios = pd.concat([df_usuarios, novo_user_df], ignore_index=True)
                    df_novo_usuarios.to_excel(CAMINHO_USUARIOS_EXCEL, index=False)
                    st.success("🎉 Cadastro enviado com sucesso! Aguarde Nelson aprovar.")
                except Exception as e:
                    st.error(f"Erro ao salvar cadastro: {e}")

# --- SISTEMA LIBERADO (APÓS LOGIN E APROVAÇÃO) ---
else:
    st.write(f"👤 Vendedor conectado: **{st.session_state['usuario_nome']}**")
    if st.button("🚪 Sair do Aplicativo"):
        st.session_state["logado"] = False
        st.session_state["usuario_nome"] = ""
        st.rerun()
        
    st.markdown("---")

    # CARREGA AS PLANILHAS DE VENDAS E CLIENTES
    if not os.path.exists(CAMINHO_CLIENTES_EXCEL):
        clientes_iniciais = pd.DataFrame([
            {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100", "IE": "Isento", "Telefone": "(11) 99999-9999"},
            {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500", "IE": "123456789", "Telefone": "(11) 98888-8888"}
        ])
        clientes_iniciais.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)

    df_clientes_salvos = pd.read_excel(CAMINHO_CLIENTES_EXCEL)
    lista_nomes_reais = df_clientes_salvos["Nome"].dropna().tolist()

    if os.path.exists(CAMINHO_EXCEL):
        df_pedidos = pd.read_excel(CAMINHO_EXCEL)
    else:
        df_pedidos = pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status"])

    # CATÁLOGO DE PRODUTOS DO TIGRÃO
    produtos_dados = {
        "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
        "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
        "Estoque": [150, 200, 500, 80]
    }
    df_produtos = pd.DataFrame(produtos_dados)
    lista_produtos_geral = df_produtos["Produto"].tolist()

    # AS 5 ABAS DO SISTEMA
    aba_pedido, aba_cadastro, aba_ver_clientes, aba_consulta_pedidos, aba_comissoes = st.tabs([
        "📋 Passar Pedido", 
        "➕ Cadastrar Cliente",
        "🔍 Consultar Clientes",
        "📦 Consultar Pedidos", 
        "💰 Comissões"
    ])

    # --- ABA 1: PASSAR PEDIDO (COM SELEÇÃO E BUSCA DINÂMICA) ---
    with aba_pedido:
        st.subheader("1. Seleção do Cliente")
        
        # Campo de pesquisa do cliente com a Lupinha 🔍
        pesquisa_input = st.text_input("🔍 Digite o Nome ou o Código do cliente para buscar:")
        
        if pesquisa_input:
            df_filtrado_cl = df_clientes_salvos[
                df_clientes_salvos["Nome"].str.contains(pesquisa_input, case=False, na=False) |
                df_clientes_salvos["Codigo"].astype(str).str.contains(pesquisa_input, case=False, na=False)
            ]
        else:
            df_filtrado_cl = df_clientes_salvos.copy()
            
        lista_selectbox = df_filtrado_cl["Nome"].dropna().tolist()
        
        if pesquisa_input and df_filtrado_cl.empty:
            st.error(f"🟥 CLIENTE NÃO ENCONTRADO! Nenhuma empresa corresponde a '{pesquisa_input}'")
            cliente_final_nome = None
        else:
            cliente_final_nome = st.selectbox("Selecione o cliente verificado na lista:", lista_selectbox)
            if cliente_final_nome:
                dados_c = df_clientes_salvos[df_clientes_salvos["Nome"] == cliente_final_nome].iloc[0]
                st.success(f"🟩 CLIENTE CONFIRMADO: {dados_c['Nome']} (COD-{int(dados_c['Codigo'])})")
                st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']}")

        st.markdown("---")
        st.subheader("2. Itens do Pedido")
        
        # NOVO FILTRO: Pesquisa por digitação para os Produtos 🔍
        pesquisa_prod_input = st.text_input("🔍 Digite o nome do Produto para filtrar o catálogo:")
        
        if pesquisa_prod_input:
            df_filtrado_prod = df_produtos[df_produtos["Produto"].str.contains(pesquisa_prod_input, case=False, na=False)]
            lista_produtos_filtrados = df_filtrado_prod["Produto"].tolist()
        else:
            lista_produtos_filtrados = lista_produtos_geral
            
        if pesquisa_prod_input and df_filtrado_prod.empty:
            st.warning(f"⚠️ Nenhum produto encontrado com o nome '{pesquisa_prod_input}'. Mostrando catálogo completo.")
            lista_produtos_filtrados = lista_produtos_geral

        # Formulário para fechar as quantidades e valores com segurança
        with st.form("formulario_pedido"):
            produto_selecionado = st.selectbox("Selecione o Produto na lista filtrada:", lista_produtos_filtrados)
            
            preco_unitario = float(df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Preço (R$)"].values[0])
            estoque_atual = int(df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Estoque"].values[0])
            
            st.info(f"Preço Unitário: R$ {preco_unitario:.2f} | Estoque no Tigrão: {estoque_atual} fardos")
            
            quantidade = st.number_input("Quantidade de Fardos/Caixas", min_value=1, max_value=estoque_atual, step=1)
            
            st.subheader("3. Pagamento e Entrega")
            # Apenas seleção fechada (vendedor não edita o nome do boleto, apenas escolhe)
            forma_pagamento = st.selectbox("Forma de Pagamento autorizada:", ["Boleto 30 dias", "Pix Tigrão", "Dinheiro", "Cartão na Entrega"])
            observacao = st.text_area("Observações do Pedido (Ex: Entregar no período da manhã)")
            
            valor_final = preco_unitario * quantidade
            st.markdown(f"### 💰 Total do Pedido: **R$ {valor_final:.2f}**")
            
            botao_enviar = st.form_submit_button("🚀 Enviar Pedido para o Tigrão")

        if botao_enviar:
            if not cliente_final_nome:
                st.error("❌ Erro: Selecione um cliente verificado antes de processar o pedido.")
            else:
                try:
                    novo_pedido = pd.DataFrame([{
                        "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Cliente": cliente_final_nome,
                        "Produto": produto_selecionado,
                        "Quantidade": int(quantidade),
                        "Total": float(valor_final),
                        "Pagamento": forma_pagamento,
                        "Obs": observacao,
