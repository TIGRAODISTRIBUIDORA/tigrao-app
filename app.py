import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")

# PERCENTUAL DE COMISSÃO PADRÃO (5%)
PERCENTUAL_COMISSAO = 0.05  
EMAIL_DONO = "sodemilecem23@gmail.com"

# Caminhos dos arquivos de dados no servidor em nuvem
CAMINHO_EXCEL = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES_EXCEL = "clientes_tigrao.xlsx"
CAMINHO_USUARIOS_EXCEL = "usuarios_tigrao.xlsx"
CAMINHO_PRODUTOS_EXCEL = "produtos_tigrao.xlsx"

# 1. INICIALIZAÇÃO DOS BANCOS DE DADOS
if not os.path.exists(CAMINHO_USUARIOS_EXCEL):
    pd.DataFrame([{"Nome": "Nelson Dono", "Email": EMAIL_DONO, "Senha": "123", "Status": "Aprovado"}]).to_excel(CAMINHO_USUARIOS_EXCEL, index=False)

if not os.path.exists(CAMINHO_PRODUTOS_EXCEL):
    pd.DataFrame([
        {"Produto": "Cerveja Lata 350ml (Fardo c/ 12)", "Preço (R$)": 36.00, "Estoque": 100},
        {"Produto": "Refrigerante 2L (Fardo c/ 6)", "Preço (R$)": 48.00, "Estoque": 100},
        {"Produto": "Água Mineral 500ml (Fardo c/ 12)", "Preço (R$)": 18.00, "Estoque": 100},
        {"Produto": "Suco Caixa 1L (Caixa c/ 12)", "Preço (R$)": 60.00, "Estoque": 100}
    ]).to_excel(CAMINHO_PRODUTOS_EXCEL, index=False)

if not os.path.exists(CAMINHO_CLIENTES_EXCEL):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100", "IE": "Isento", "Telefone": "(11) 99999-9999"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500", "IE": "123456789", "Telefone": "(11) 98888-8888"}
    ]).to_excel(CAMINHO_CLIENTES_EXCEL, index=False)

if not os.path.exists(CAMINHO_EXCEL):
    pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status", "Vendedor"]).to_excel(CAMINHO_EXCEL, index=False)

# RELEITURA DOS DADOS ATUALIZADOS
df_usuarios = pd.read_excel(CAMINHO_USUARIOS_EXCEL)
df_produtos = pd.read_excel(CAMINHO_PRODUTOS_EXCEL)
df_clientes_salvos = pd.read_excel(CAMINHO_CLIENTES_EXCEL)
df_pedidos = pd.read_excel(CAMINHO_EXCEL)

# GERENCIAMENTO DE SESSÃO DO LOGIN
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario_nome" not in st.session_state:
    st.session_state["usuario_nome"] = ""
if "usuario_email" not in st.session_state:
    st.session_state["usuario_email"] = ""

# --- TELA DE ACESSO ---
if not st.session_state["logado"]:
    aba_login, aba_novo_cadastro = st.tabs(["🔐 Entrar no Sistema", "📝 Criar Nova Conta Vendedor"])
    
    with aba_login:
        st.subheader("Acesse sua Conta")
        email_login = st.text_input("E-mail cadastrado:")
        senha_login = st.text_input("Sua senha:", type="password")
        botao_logar = st.button("🚀 Entrar no Painel do Tigrão")
        
        if botao_logar:
            usuario_validar = df_usuarios[(df_usuarios["Email"].astype(str).str.lower() == email_login.strip().lower()) & (df_usuarios["Senha"].astype(str) == senha_login.strip())]
            if not usuario_validar.empty:
                status_usuario = str(usuario_validar.iloc[0]["Status"])
                if status_usuario == "Aprovado":
                    st.session_state["logado"] = True
                    st.session_state["usuario_nome"] = usuario_validar.iloc[0]["Nome"]
                    st.session_state["usuario_email"] = usuario_validar.iloc[0]["Email"].strip().lower()
                    st.success(f"Bem-vindo, {st.session_state['usuario_nome']}!")
                    st.rerun()
                else:
                    st.error("❌ Acesso Bloqueado! Sua licença está 'Pendente' de aprovação na central do Tigrão.")
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
                novo_user_df = pd.DataFrame([{"Nome": nome_cad.strip(), "Email": email_cad.strip().lower(), "Senha": senha_cad.strip(), "Status": "Pendente"}])
                pd.concat([df_usuarios, novo_user_df], ignore_index=True).to_excel(CAMINHO_USUARIOS_EXCEL, index=False)
                st.success("🎉 Cadastro enviado com sucesso! Aguarde a liberação do administrador.")

# --- SISTEMA LIBERADO (APÓS LOGIN COM SUCESSO) ---
else:
    st.write(f"👤 Conectado como: **{st.session_state['usuario_nome']}** ({st.session_state['usuario_email']})")
    if st.button("🚪 Sair do Aplicativo"):
        st.session_state["logado"] = False
        st.session_state["usuario_nome"] = ""
        st.session_state["usuario_email"] = ""
        st.rerun()
        
    st.markdown("---")

    lista_nomes_reais = df_clientes_salvos["Nome"].dropna().astype(str).tolist()
    lista_produtos_geral = df_produtos["Produto"].tolist()

    # CRIAÇÃO DAS ABAS INDEPENDENTES
    is_admin = st.session_state["usuario_email"] == EMAIL_DONO
    abas_titulos = ["📋 Passar Pedido", "➕ Cadastrar Cliente", "🔍 Consultar Clientes", "📦 Consultar Pedidos", "💰 Comissões"]
    if is_admin:
        abas_titulos.append("👑 Central do Dono")
        
    abas = st.tabs(abas_titulos)

    # --- ABA 1: PASSAR PEDIDO ---
    with abas[0]:
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
            cliente_final_nome = st.selectbox("Selecione o cliente verificado na lista:", exibir_lista)
            if cliente_final_nome and cliente_final_nome != "Nenhum cliente disponível":
                dados_c = df_clientes_salvos[df_clientes_salvos["Nome"].astype(str) == cliente_final_nome].iloc[0]
                st.success(f"🟩 CLIENTE CONFIRMADO: {dados_c['Nome']} (COD-{int(dados_c['Codigo'])})")
                st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']}")

        st.markdown("---")
        st.subheader("2. Itens do Pedido")
        pesquisa_prod_input = st.text_input("🔍 Digite o nome do Produto para filtrar o catálogo:")
        if pesquisa_prod_input:
            df_filtrado_prod = df_produtos[df_produtos["Produto"].astype(str).str.lower().str.contains(pesquisa_prod_input.strip().lower(), na=False)]
            lista_produtos_filtrados = df_filtrado_prod["Produto"].tolist()
        else:
            lista_produtos_filtrados = lista_produtos_geral

        with st.form("formulario_pedido"):
            produto_selecionado = st.selectbox("Selecione o Produto:", lista_produtos_filtrados if lista_produtos_filtrados else ["Nenhum produto"])
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
            novo_pedido = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), "Cliente": cliente_final_nome, "Produto": produto_selecionado, "Quantidade": int(quantidade), "Total": float(valor_final), "Pagamento": forma_pagamento, "Obs": observacao, "Status": "Pendente", "Vendedor": st.session_state["usuario_nome"]}])
            pd.concat([df_pedidos, novo_pedido], ignore_index=True).to_excel(CAMINHO_EXCEL, index=False)
            st.success(f"✅ Pedido enviado!")
            st.balloons()
            st.rerun()

    # --- ABA 2: CADASTRAR CLIENTE ---
    with abas[1]:
        st.subheader("📝 Cadastro de Novo Cliente")
        with st.form("formulario_cliente"):
            nome_input = st.text_input("Nome Razão Social")
            cnpj_input = st.text_input("CNPJ")
            ie_input = st.text_input("IE")
            endereco_input = st.text_input("Endereço")
