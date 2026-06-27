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
CAMINHO_CLIENTES = "clientes_banco.xlsx"

# ConfiguraÇÕES DE SEGURANÇA E ACESSOS DIRETOS NO MOTOR DO APP
SENHA_NELSON_MESTRE = "TigraoNelson2026"
EMAIL_DONO = "sodemilecem23@gmail.com"

# DICIONÁRIO DE ACESSOS FIXO E BLINDADO (Evita erro de senha incorreta)
USUARIOS_SISTEMA = {
    "sodemilecem23@gmail.com": {"senha": "123", "nome": "Nelson Dono"},
    "joaquim@tigrao.com": {"senha": "123", "nome": "Joaquim Silva"},
    "pedro@tigrao.com": {"senha": "123", "nome": "Pedro Santos"}
}

# 1. INICIALIZAÇÃO DO BANCO DE DADOS DE CLIENTES
if not os.path.exists(CAMINHO_CLIENTES):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11"}
    ]).to_excel(CAMINHO_CLIENTES, index=False)

df_clientes = pd.read_excel(CAMINHO_CLIENTES)

# 2. INICIALIZAÇÃO DO BANCO DE DADOS DE VENDAS
if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["DataFat", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "faturado", "nf"]).to_excel(CAMINHO_VENDAS, index=False)

df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# Compatibilidade de cabeçalhos antigos de faturamento
if "Data_Hora" in df_pedidos.columns: df_pedidos = df_pedidos.rename(columns={"Data_Hora": "DataFat"})
if "Status" in df_pedidos.columns: df_pedidos = df_pedidos.rename(columns={"Status": "faturado"})
if "Numero_NFe" in df_pedidos.columns: df_pedidos = df_pedidos.rename(columns={"Numero_NFe": "nf"})

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

# --- TELA DE ATIVAÇÃO ÚNICA (LOGIN BLINDADO) ---
if st.session_state["vendedor_nome"] == "":
    st.subheader("🔐 Ativação Única do Aplicativo")
    st.write("Insira seu e-mail e senha corporativa para liberar o aparelho.")
    
    email_input = st.text_input("E-mail do Vendedor:")
    senha_input = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("🚀 Ativar Aplicativo neste Celular"):
        email_limpo = email_input.strip().lower()
        senha_limpa = senha_input.strip()
        
        # Validação direta e infalível no dicionário fixo do código
        if email_limpo in USUARIOS_SISTEMA and USUARIOS_SISTEMA[email_limpo]["senha"] == senha_limpa:
            st.session_state["vendedor_nome"] = USUARIOS_SISTEMA[email_limpo]["nome"]
            st.session_state["vendedor_email"] = email_limpo
            st.success("Dispositivo ativado com sucesso!")
            st.rerun()
        else:
            st.error("❌ E-mail ou Senha incorretos. Digite o e-mail completo e a senha 123.")

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
    tab_pedido, tab_cadastro, tab_consulta_prod, tab_recebimento = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Cliente", "🔍 Consultar Produtos", "👑 Recebimento Nelson (Central)"])
    else:
    tab_pedido, tab_cadastro, tab_consulta_prod = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Cliente", "🔍 Consultar Produtos"])

    cliente_escolhido = st.selectbox("Selecione o Cliente Cadastrado:", lista_nomes_clientes)
        
    if cliente_escolhido:
    dados_busca = df_clientes[df_clientes["Nome"] == cliente_escolhido]
    if not dados_busca.empty:
    st.info(f"🟩 CLIENTE CONFERIDO | Código: COD-{int(dados_busca.iloc[0]['Codigo'])} | CNPJ: {dados_busca.iloc[0]['CNPJ']}")
            
        st.markdown("---")
        st.subheader("2. Itens do Pedido")
        produto = st.selectbox("Selecione o Produto:", list(produtos_fixos.keys()))
        
        preco_un = produtos_fixos[produto]
        st.caption(f"Preço do fardo: R$ {preco_un:.2f}")
        quantidade = st.number_input("Quantidade de Fardos:", min_value=1, value=1, step=1)
        total_pedido = preco_un * quantidade
        st.markdown(f"#### 💰 Total do Pedido: **R$ {total_pedido:.2f}**")
        
        forma_pagto = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix", "Dinheiro"])
        
        if st.button("🚀 Enviar Pedido para a Central", key="btn_enviar_pedido_venda"):
            novo_p = pd.DataFrame([{
                "DataFat": datetime.now().strftime("%d/%m/%Y"),
                "Vendedor": st.session_state["vendedor_nome"],
                "Cliente": cliente_escolhido,
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

    # --- ABA 3: 🔍 CONSULTAR PRODUTOS ---
    with tab_consulta_prod:
        st.subheader("🔍 Catálogo e Tabela de Preços")
        st.write("Consulte a tabela oficial de valores de fardos para venda externa.")
        
        df_catalogo_visual = pd.DataFrame([
            {"🏷️ Nome do Produto": prod, "💰 Preço de Tabela (R$)": f"R$ {preco:.2f}"}
            for prod, preco in produtos_fixos.items()
        ])
        
        busca_prod_filtro = st.text_input("Filtrar produto por nome:")
        if busca_prod_filtro:
            df_catalogo_visual = df_catalogo_visual[df_catalogo_visual["🏷️ Nome do Produto"].str.contains(busca_prod_filtro, case=False, na=False)]
            
        st.dataframe(df_catalogo_visual, use_container_width=True, hide_index=True)

    # --- ABA 4: RECEBIMENTO NELSON ---
    with tab_recebimento:
        st.subheader("🔒 Painel de Recebimento de Pedidos")
        
        liberar_painel = False
        if is_admin:
            liberar_painel = True
            st.info("👑 Reconhecido como Diretor. Painel Liberado.")
        else:
            senha_digitada = st.text_input("Digite a Senha Master da Empresa:", type="password", key="senha_nelson_receb_aba")
            if senha_digitada == SENHA_NELSON_MESTRE:
                liberar_painel = True
            elif senha_digitada != "":
                st.error("❌ Senha master incorreta.")
        
        if liberar_painel:
            df_pedidos_atualizado = pd.read_excel(CAMINHO_VENDAS) if os.path.exists(CAMINHO_VENDAS) else df_pedidos
            df_pedidos_atualizado["faturado"] = df_pedidos_atualizado["faturado"].fillna("Pendente")
            df_pedidos_atualizado["nf"] = df_pedidos_atualizado["nf"].fillna("")
            df_ordenado = df_pedidos_atualizado.sort_values(by="DataFat", ascending=False)
            
            # 1. DOWNLOAD DA PLANILHA PARA O DISA
            st.subheader("📥 1. Baixar Planilha para o DISA")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_ordenado.to_excel(writer, index=False, sheet_name='Pedidos_Faturamento')
            dados_planilha = buffer.getvalue()
            
            st.download_button(label="📥 Baixar Planilha Excel para Nota Fiscal (.xlsx)", data=dados_planilha, file_name=f"faturamento_tigrao_{datetime.now().strftime('%d_%m_%Y')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            
            st.markdown("---")
            # 2. VISUALIZAÇÃO E EDIÇÃO MANUAL DA PLANILHA VIVA NA TELA
            st.subheader("📊 2. Histórico e Faturamento Gerencial")
