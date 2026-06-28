import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

st.set_page_config(page_title="Tigrão - Sistema Comercial", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("### 📦 Painel Integrado de Vendas e Cadastro")

# Caminhos dos arquivos de banco de dados locais estáveis
CAMINHO_VENDAS = "vendas_tigrao.xlsx"
CAMINHO_USUARIOS = "usuarios_banco.xlsx"
CAMINHO_CLIENTES = "clientes_banco.xlsx"
CAMINHO_FORNECEDORES = "fornecedores_banco.xlsx"

# Configurações de segurança fixas da empresa
SENHA_NELSON_MESTRE = "TigraoNelson2026"
EMAIL_DONO = "sodemilecem23@gmail.com"

# 1. INICIALIZAÇÃO DO BANCO DE DADOS DE VENDEDORES
if not os.path.exists(CAMINHO_USUARIOS):
    pd.DataFrame([
        {"Email": EMAIL_DONO, "Senha": "123", "Nome": "Nelson Dono"},
        {"Email": "joaquim@tigrao.com", "Senha": "123", "Nome": "Joaquim Silva"},
        {"Email": "pedro@tigrao.com", "Senha": "123", "Nome": "Pedro Santos"}
    ]).to_excel(CAMINHO_USUARIOS, index=False)

df_usuarios = pd.read_excel(CAMINHO_USUARIOS)

# 2. INICIALIZAÇÃO DO BANCO DE DADOS DE CLIENTES
if not os.path.exists(CAMINHO_CLIENTES):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11"}
    ]).to_excel(CAMINHO_CLIENTES, index=False)

df_clientes = pd.read_excel(CAMINHO_CLIENTES)

# 3. INICIALIZAÇÃO DO BANCO DE DADOS DE FORNECEDORES
if not os.path.exists(CAMINHO_FORNECEDORES):
    pd.DataFrame([
        {"Codigo": 1, "Fornecedor": "Fábrica Bananada Real", "CNPJ": "22.222.222/0001-22"},
        {"Codigo": 2, "Fornecedor": "Ambev Distribuição", "CNPJ": "33.333.333/0001-33"}
    ]).to_excel(CAMINHO_FORNECEDORES, index=False)

df_fornecedores = pd.read_excel(CAMINHO_FORNECEDORES)

# 4. INICIALIZAÇÃO DO BANCO DE DADOS DE VENDAS
if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["DataFat", "Vendedor", "Cliente", "Fornecedor", "Produto", "Quantidade", "Total", "Pagamento", "faturado", "nf"]).to_excel(CAMINHO_VENDAS, index=False)

df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# Compatibilidade de cabeçalhos antigos de faturamento
if "Data_Hora" in df_pedidos.columns: df_pedidos = df_pedidos.rename(columns={"Data_Hora": "DataFat"})
if "Status" in df_pedidos.columns: df_pedidos = df_pedidos.rename(columns={"Status": "faturado"})
if "Numero_NFe" in df_pedidos.columns: df_pedidos = df_pedidos.rename(columns={"Numero_NFe": "nf"})

if "Fornecedor" not in df_pedidos.columns:
    df_pedidos["Fornecedor"] = "Não Informado"
if "faturado" not in df_pedidos.columns: df_pedidos["faturado"] = "Pendente"
if "nf" not in df_pedidos.columns: df_pedidos["nf"] = ""

# TABELA FIXA DE PRODUTOS PADRÃO DO SISTEMA
produtos_fixos = {
    "Bananada Natural (Fardo)": 36.00, 
    "Cerveja Lata 350ml (Fardo)": 42.00, 
    "Refrigerante 2L (Fardo)": 48.00
}

# Gerenciamento de sessão de login permanente
if "vendedor_nome" not in st.session_state:
    st.session_state["vendedor_nome"] = ""
if "vendedor_email" not in st.session_state:
    st.session_state["vendedor_email"] = ""

# --- TELA DE ATIVAÇÃO ÚNICA (LOGIN) ---
if st.session_state["vendedor_nome"] == "":
    st.subheader("🔐 Ativação Única do Aplicativo")
    st.write("Insira seu e-mail e senha corporativa para liberar o aparelho.")
    
    email_input = st.text_input("E-mail do Vendedor:")
    senha_input = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("🚀 Ativar Aplicativo neste Celular"):
        email_limpo = email_input.strip().lower()
        senha_limpa = senha_input.strip()
        
        if email_limpo in ["sodemilecem23@gmail.com", "joaquim@tigrao.com", "pedro@tigrao.com"] and senha_limpa == "123":
            nomes_mapa = {"sodemilecem23@gmail.com": "Nelson Dono", "joaquim@tigrao.com": "Joaquim Silva", "pedro@tigrao.com": "Pedro Santos"}
            st.session_state["vendedor_nome"] = nomes_mapa[email_limpo]
            st.session_state["vendedor_email"] = email_limpo
            st.success("Dispositivo ativado com sucesso!")
            st.rerun()
        else:
            st.error("❌ E-mail ou Senha incorretos. Use a senha 123.")

# --- SISTEMA LIBERADO (PAINEL OPERACIONAL) ---
else:
    st.success(f"👤 CONECTADO: **{st.session_state['vendedor_nome'].upper()}**")
    if st.button("🔄 Desconectar deste aparelho (Sair)"):
        st.session_state["vendedor_nome"] = ""
        st.session_state["vendedor_email"] = ""
        st.rerun()
        
    st.markdown("---")
    is_admin = st.session_state["vendedor_email"] == EMAIL_DONO
    
    if is_admin:
        tab_pedido, tab_cadastro, tab_fornecedores, tab_consulta_prod, tab_recebimento = st.tabs([
            "📋 Passar Pedido", "➕ Cadastrar Cliente", "🏭 Cadastrar Fornecedor", "🔍 Consultar Produtos", "👑 Recebimento Nelson (Central)"
        ])
    else:
        tab_pedido, tab_cadastro, tab_consulta_prod = st.tabs([
            "📋 Passar Pedido", "➕ Cadastrar Cliente", "🔍 Consultar Produtos"
        ])

    # --- ABA 1: PASSAR PEDIDO ---
    with tab_pedido:
        st.subheader("1. Escolha o Cliente")
        lista_nomes_clientes = df_clientes["Nome"].dropna().astype(str).tolist()
        cliente_escolhido = st.selectbox("Selecione o Cliente Cadastrado:", lista_nomes_clientes)
        
        if cliente_escolhido:
            dados_busca = df_clientes[df_clientes["Nome"] == cliente_escolhido]
            if not dados_busca.empty:
                st.info(f"🟩 CLIENTE CONFERIDO | Código: COD-{int(dados_busca.iloc[0]['Codigo'])} | CNPJ: {dados_busca.iloc[0]['CNPJ']}")
        
        st.markdown("---")
        st.subheader("2. Vincular Fornecedor")
        lista_nomes_fornecedores = df_fornecedores["Fornecedor"].dropna().astype(str).tolist()
        fornecedor_escolhido = st.selectbox("Selecione o Fornecedor da Mercadoria:", lista_nomes_fornecedores)
            
        st.markdown("---")
        st.subheader("3. Itens do Pedido")
        produto = st.selectbox("Selecione O Produto:", list(produtos_fixos.keys()))
        
        preco_un = produtos_fixos[produto]
        st.caption(f"Preço do fardo: R$ {preco_un:.2f}")
        quantidade = st.number_input("Quantidade de Fardos:", min_value=1, value=1, step=1)
        total_pedido = preco_un * quantidade
        st.markdown(f"#### 💰 Total do Pedido: **R$ {total_pedido:.2f}**")
        
        prazo_dias = st.number_input("Prazo de Pagamento (em dias):", min_value=0, max_value=365, value=30, step=1)
        forma_pagto = f"Boleto {prazo_dias} dias" if prazo_dias > 0 else "À Vista / Pix"
        st.caption(f"Formato gravado: {forma_pagto}")
        
        if st.button("🚀 Enviar Pedido para a Central", key="btn_enviar_pedido_venda"):
            novo_p = pd.DataFrame([{
                "DataFat": datetime.now().strftime("%d/%m/%Y"),
                "Vendedor": st.session_state["vendedor_nome"],
                "Cliente": cliente_escolhido,
                "Fornecedor": fornecedor_escolhido,
                "Produto": produto,
                "Quantidade": int(quantidade),
                "Total": float(total_pedido),
                "Pagamento": forma_pagto,
                "faturado": "Pendente",
                "nf": ""
            }])
            df_final = pd.concat([df_pedidos, novo_p], ignore_index=True)
            df_final.to_excel(CAMINHO_VENDAS, index=False)
            st.success("✅ Pedido gravado no Excel com sucesso!")
            st.balloons()
            st.rerun()

    # --- ABA 2: CADASTRAR CLIENTE ---
    with tab_cadastro:
        st.subheader("➕ Cadastro de Novo Cliente Comercial")
        with st.form("form_novo_cliente_rua"):
            razao_social = st.text_input("Razão Social / Nome Fantasia da Empresa:")
            cnpj_digitado = st.text_input("CNPJ do Cliente:")
            btn_salvar_cl = st.form_submit_button("💾 Gravar Cliente no Banco do Tigrão")
            
        if btn_salvar_cl and razao_social.strip():
            if razao_social.strip() in lista_nomes_clientes:
                st.error("❌ Este cliente já está cadastrado no sistema!")
            else:
                try:
                    proximo_cod = int(df_clientes["Codigo"].max() + 1) if not df_clientes.empty else 1
                    novo_cl_df = pd.DataFrame([{"Codigo": proximo_cod, "Nome": razao_social.strip(), "CNPJ": cnpj_digitado.strip()}])
                    pd.concat([df_clientes, novo_cl_df], ignore_index=True).to_excel(CAMINHO_CLIENTES, index=False)
                    st.success(f"🎉 Cliente '{razao_social}' cadastrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar: {e}")

    # --- ABA 3: CADASTRAR FORNECEDOR (EXCLUSIVO DO DONO - LINEAR E BLINDADO) ---
    if is_admin:
        with tab_fornecedores:
            st.subheader("🏭 Cadastro de Fornecedores do Tigrão")
            with st.form("form_novo_fornecedor"):
                nome_fornecedor = st.text_input("Nome / Razão Social do Fornecedor:")
                cnpj_fornecedor = st.text_input("CNPJ do Fornecedor:")
                btn_salvar_forn = st.form_submit_button("💾 Gravar Fornecedor no Banco")
                
            if btn_salvar_forn and nome_fornecedor.strip():
                prox_cod_f = int(df_fornecedores["Codigo"].max() + 1) if not df_fornecedores.empty else 1
                novo_f_df = pd.DataFrame([{"Codigo": prox_cod_f, "Fornecedor": nome_fornecedor.strip(), "CNPJ": cnpj_fornecedor.strip()}])
                df_forn_atualizado = pd.concat([df_fornecedores, novo_f_df], ignore_index=True)
                df_forn_atualizado.to_excel(CAMINHO_FORNECEDORES, index=False)
                st.success(f"🎉 Fornecedor '{nome_fornecedor}' cadastrado com sucesso!")
                st.rerun()

    # --- ABA 4: 🔍 CONSULTAR PRODUTOS ---
    with tab_consulta_prod:
        st.subheader("🔍 Catálogo e Tabela de Preços")
