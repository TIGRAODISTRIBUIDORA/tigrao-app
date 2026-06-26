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

# 1. BANCO DE DADOS DE USUÁRIOS/VENDEDORES (PROTEGIDO)
try:
    if not os.path.exists(CAMINHO_USUARIOS_EXCEL):
        usuarios_iniciais = pd.DataFrame([
            {"Nome": "Administrador Tigrao", "Email": "sodemilecem23@gmail.com", "Senha": "123", "Status": "Aprovado"}
        ])
        usuarios_iniciais.to_excel(CAMINHO_USUARIOS_EXCEL, index=False)
    df_usuarios = pd.read_excel(CAMINHO_USUARIOS_EXCEL)
except Exception:
    df_usuarios = pd.DataFrame([{"Nome": "Administrador Tigrao", "Email": "sodemilecem23@gmail.com", "Senha": "123", "Status": "Aprovado"}])

# GERENCIAMENTO DE SESSÃO DO LOGIN
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
            try:
                usuario_validar = df_usuarios[(df_usuarios["Email"].astype(str).str.lower() == email_login.strip().lower()) & (df_usuarios["Senha"].astype(str) == senha_login.strip())]
                if not usuario_validar.empty:
                    status_usuario = str(usuario_validar.iloc[0]["Status"])
                    if status_usuario == "Aprovado":
                        st.session_state["logado"] = True
                        st.session_state["usuario_nome"] = usuario_validar.iloc[0]["Nome"]
                        st.success(f"Bem-vindo, {st.session_state['usuario_nome']}!")
                        st.rerun()
                    else:
                        st.error("❌ Acesso Bloqueado! Sua licença está 'Pendente' de aprovação na central.")
                else:
                    st.error("❌ E-mail ou Senha incorretos.")
            except Exception:
                st.error("⚠️ Usuário inválido ou erro na leitura do cadastro.")
                
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
                    st.success("🎉 Cadastro enviado com sucesso! Aguarde a liberação na central.")
                except Exception:
                    st.error("❌ Ocorreu um problema ao salvar o cadastro. Tente novamente.")

# --- SISTEMA LIBERADO (APÓS LOGIN E APROVAÇÃO) ---
else:
    st.write(f"👤 Vendedor conectado: **{st.session_state['usuario_nome']}**")
    if st.button("🚪 Sair do Aplicativo"):
        st.session_state["logado"] = False
        st.session_state["usuario_nome"] = ""
        st.rerun()
        
    st.markdown("---")

    # CARREGA AS PLANILHAS DE VENDAS E CLIENTES COM TRATAMENTO DE ERROS BLINDADO
    try:
        if not os.path.exists(CAMINHO_CLIENTES_EXCEL):
            clientes_iniciais = pd.DataFrame([
                {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100", "IE": "Isento", "Telefone": "(11) 99999-9999"},
                {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500", "IE": "123456789", "Telefone": "(11) 98888-8888"}
            ])
            clientes_iniciais.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)
        df_clientes_salvos = pd.read_excel(CAMINHO_CLIENTES_EXCEL)
    except Exception:
        df_clientes_salvos = pd.DataFrame(columns=["Codigo", "Nome", "CNPJ", "IE", "Endereco", "Telefone"])

    lista_nomes_reais = df_clientes_salvos["Nome"].dropna().astype(str).tolist()

    try:
        if os.path.exists(CAMINHO_EXCEL):
            df_pedidos = pd.read_excel(CAMINHO_EXCEL)
        else:
            df_pedidos = pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status"])
    except Exception:
        df_pedidos = pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status"])

    # CATÁLOGO DE PRODUTOS
    produtos_dados = {
        "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
        "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
        "Estoque": [500, 300, 1000, 250]
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

    # --- ABA 1: PASSAR PEDIDO (BUSCA TOTALMENTE BLINDADA) ---
    with aba_pedido:
        st.subheader("1. Seleção do Cliente")
        
        # Entrada de texto limpa para o vendedor pesquisar livremente
        pesquisa_input = st.text_input("🔍 Digite o Nome ou o Código do cliente para buscar:")
        
        # Filtra a lista sem gerar erros de execução no script
        if pesquisa_input and not df_clientes_salvos.empty:
            texto_busca = pesquisa_input.strip().lower()
            df_filtrado_cl = df_clientes_salvos[
                df_clientes_salvos["Nome"].astype(str).str.lower().str.contains(texto_busca, na=False) |
                df_clientes_salvos["Codigo"].astype(str).str.contains(texto_busca, na=False)
            ]
        else:
            df_filtrado_cl = df_clientes_salvos.copy()
            
        lista_selectbox = df_filtrado_cl["Nome"].dropna().astype(str).tolist()
        
        # Se a pesquisa falhar, exibe erro visual limpo em vez de erro de script
        if pesquisa_input and not lista_selectbox:
            st.error(f"❌ CLIENTE NÃO ENCONTRADO! Nenhuma empresa corresponde a '{pesquisa_input}'")
            cliente_final_nome = None
        else:
            # Garante que a lista não venha vazia para o selectbox
            exibir_lista = lista_selectbox if lista_selectbox else ["Nenhum cliente disponível"]
            cliente_final_nome = st.selectbox("Selecione o cliente verificado na lista:", exibir_lista)
            
            if cliente_final_nome and cliente_final_nome != "Nenhum cliente disponível":
                try:
                    dados_c = df_clientes_salvos[df_clientes_salvos["Nome"].astype(str) == cliente_final_nome].iloc[0]
                    st.success(f"🟩 CLIENTE CONFIRMADO: {dados_c['Nome']} (COD-{int(dados_c['Codigo'])})")
                    st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']}")
                except Exception:
                    st.caption("📌 Carregando dados cadastrais do cliente...")

        st.markdown("---")
        st.subheader("2. Itens do Pedido")
        
        # Filtro de digitação seguro para os Produtos
        pesquisa_prod_input = st.text_input("🔍 Digite o nome do Produto para filtrar o catálogo:")
        
        if pesquisa_prod_input:
            df_filtrado_prod = df_produtos[df_produtos["Produto"].astype(str).str.lower().str.contains(pesquisa_prod_input.strip().lower(), na=False)]
            lista_produtos_filtrados = df_filtrado_prod["Produto"].tolist()
        else:
            lista_produtos_filtrados = lista_produtos_geral
            
        if pesquisa_prod_input and not lista_produtos_filtrados:
            st.warning(f"⚠️ Nenhum produto encontrado com o nome '{pesquisa_prod_input}'. Mostrando catálogo completo.")
            lista_produtos_filtrados = lista_produtos_geral

        # Formulário protegido do pedido
        with st.form("formulario_pedido"):
            produto_selecionado = st.selectbox("Selecione o Produto na lista filtrada:", lista_produtos_filtrados if lista_produtos_filtrados else ["Nenhum produto cadastrado"])
            
            try:
                preco_unitario = float(df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Preço (R$)"].values[0])
                estoque_atual = int(df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Estoque"].values[0])
                st.info(f"Preço Unitário: R$ {preco_unitario:.2f} | Estoque no Tigrão: {estoque_atual} fardos")

