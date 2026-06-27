import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

st.set_page_config(page_title="Tigrão - Sistema Comercial", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("### 📦 Painel Integrado de Vendas e Cadastro")

# Configurações do Banco de Dados Local do Bloco 1 e 2
CAMINHO_VENDAS = "vendas_tigrao.xlsx"
CAMINHO_USUARIOS = "usuarios_banco.xlsx"
CAMINHO_CLIENTES = "clientes_banco.xlsx"  # <--- Nova Planilha do Bloco de Clientes

# CONFIGURAÇÕES DE SEGURANÇA FIXAS
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

# 2. INICIALIZAÇÃO DO BANCO DE DADOS DE CLIENTES (NOVO)
if not os.path.exists(CAMINHO_CLIENTES):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11"}
    ]).to_excel(CAMINHO_CLIENTES, index=False)

df_clientes = pd.read_excel(CAMINHO_CLIENTES)

# 3. INICIALIZAÇÃO DO BANCO DE DADOS DE VENDAS
if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["Data_Hora", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Status"]).to_excel(CAMINHO_VENDAS, index=False)

df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# GERENCIAMENTO DE SESSÃO DO LOGIN
if "vendedor_nome" not in st.session_state:
    st.session_state["vendedor_nome"] = ""
if "vendedor_email" not in st.session_state:
    st.session_state["vendedor_email"] = ""

# --- TELA DE ATIVAÇÃO ÚNICA ---
if st.session_state["vendedor_nome"] == "":
    st.subheader("🔐 Ativação Única do Aplicativo")
    st.write("Insira seu e-mail e senha corporativa para liberar o aparelho.")
    
    email_input = st.text_input("E-mail do Vendedor:")
    senha_input = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("🚀 Ativar Aplicativo neste Celular"):
        email_limpo = email_input.strip().lower()
        
        if email_limpo == EMAIL_DONO and senha_input.strip() == "123":
            st.session_state["vendedor_nome"] = "Nelson Dono"
            st.session_state["vendedor_email"] = EMAIL_DONO
            st.success("Dispositivo ativado com sucesso para Nelson Dono!")
            st.rerun()
        else:
            usuario_validar = df_usuarios[(df_usuarios["Email"].astype(str).str.lower() == email_limpo) & (df_usuarios["Senha"].astype(str) == senha_input.strip())]
            if not usuario_validar.empty:
                st.session_state["vendedor_nome"] = usuario_validar.iloc["Nome"]
                st.session_state["vendedor_email"] = email_limpo
                st.success(f"Dispositivo ativado com sucesso para {st.session_state['vendedor_nome']}!")
                st.rerun()
            else:
                st.error("❌ E-mail ou Senha incorretos.")

# --- SISTEMA LIBERADO ---
else:
    st.success(f"👤 CONECTADO: **{st.session_state['vendedor_nome'].upper()}**")
    
    if st.button("🔄 Desconectar deste aparelho"):
        st.session_state["vendedor_nome"] = ""
        st.session_state["vendedor_email"] = ""
        st.rerun()
        
    st.markdown("---")

    is_admin = st.session_state["vendedor_email"] == EMAIL_DONO
    
    # Organização das abas incluindo o Novo Bloco de Clientes de forma limpa
    abas_titulos = ["📋 Passar Pedido", "➕ Cadastrar Cliente", "👑 Recebimento Nelson (Central)"]
    if is_admin:
        abas_titulos.append("👥 Gestão da Equipe")
        
    tab_pedido, tab_cadastro, tab_recebimento, *tab_extra = st.tabs(abas_titulos)
    tab_equipe = tab_extra[0] if tab_extra else None

    # --- ABA 1: PASSAR PEDIDO ---
    with tab_pedido:
        st.subheader("1. Escolha o Cliente")
        
        # Puxa dinamicamente os clientes cadastrados no banco de dados real
        lista_nomes_clientes = df_clientes["Nome"].dropna().astype(str).tolist()
        cliente_escolhido = st.selectbox("Selecione o Cliente Cadastrado:", lista_nomes_clientes)
        
        # Validação na tela para o vendedor conferir o CNPJ antes de vender
        if cliente_escolhido:
            linha_c = df_clientes[df_clientes["Nome"] == cliente_escolhido].iloc[0]
            st.info(f"🟩 CLIENTE CONFERIDO | Código: COD-{int(linha_c['Codigo'])} | CNPJ: {linha_c['CNPJ']}")
            
        st.markdown("---")
        st.subheader("2. Itens do Pedido")
        
        produtos_fixos = {"Bananada Natural (Fardo)": 36.00, "Cerveja Lata 350ml (Fardo)": 42.00, "Refrigerante 2L (Fardo)": 48.00}
        produto = st.selectbox("Selecione o Produto:", list(produtos_fixos.keys()))
        
        preco_un = produtos_fixos[produto]
        st.caption(f"Preço do fardo: R$ {preco_un:.2f}")
        
        quantidade = st.number_input("Quantidade de Fardos:", min_value=1, value=1, step=1)
        total_pedido = preco_un * quantidade
        st.markdown(f"#### 💰 Total do Pedido: **R$ {total_pedido:.2f}**")
        
        forma_pagto = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix", "Dinheiro"])
        
        if st.button("🚀 Enviar Pedido para a Central", key="btn_enviar_pedido_venda"):
            novo_p = pd.DataFrame([{
                "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Vendedor": st.session_state["vendedor_nome"],
                "Cliente": cliente_escolhido,
                "Produto": produto,
                "Quantidade": int(quantidade),
                "Total": float(total_pedido),
                "Pagamento": forma_pagto,
                "Status": "Pendente"
            }])
            df_final = pd.concat([df_pedidos, novo_p], ignore_index=True)
            df_final.to_excel(CAMINHO_VENDAS, index=False)
            st.success("✅ Pedido gravado no Excel com sucesso!")
            st.balloons()
            st.rerun()

    # --- ABA 2: ➕ CADASTRAR CLIENTE (NOVA INTRODUÇÃO SEGUIDA À RISCA) ---
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
                    # Calcula o próximo código sequencial de forma automática
                    proximo_cod = int(df_clientes["Codigo"].max() + 1) if not df_clientes.empty else 1
                    
                    novo_cl_df = pd.DataFrame([{"Codigo": proximo_cod, "Nome": razao_social.strip(), "CNPJ": cnpj_digitado.strip()}])
                    df_clientes_atualizado = pd.concat([df_clientes, novo_cl_df], ignore_index=True)
                    df_clientes_atualizado.to_excel(CAMINHO_CLIENTES, index=False)
                    
                    st.success(f"🎉 Cliente '{razao_social}' cadastrado com sucesso! Código gerado: COD-{proximo_cod}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar cliente: {e}")

    # --- ABA 3: RECEBIMENTO NELSON ---
    with tab_recebimento:
        st.subheader("🔒 Painel de Recebimento de Pedidos")
        
        liberar_painel = False
        if is_admin:
            liberar_painel = True
            st.info("👑 Reconhecido como Diretor. Senha interna dispensada.")
        else:
            senha_digitada = st.text_input("Digite a Senha Master da Empresa:", type="password", key="campo_senha_master_nelson")
            if senha_digitada == SENHA_NELSON_MESTRE:
                liberar_painel = True
            elif senha_digitada != "":
                st.error("❌ Senha master incorreta.")
        
        if liberar_painel:
            if os.path.exists(CAMINHO_VENDAS):
                df_pedidos_atualizado = pd.read_excel(CAMINHO_VENDAS)
            else:
                df_pedidos_atualizado = df_pedidos
            
            if not df_pedidos_atualizado.empty:
                df_ordenado = df_pedidos_atualizado.sort_values(by="Data_Hora", ascending=False)
                st.write(f"📢 Você tem **{len(df_ordenado[df_ordenado['Status']=='Pendente'])}** pedido(s) pendente(s) para faturar no DISA.")
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_ordenado.to_excel(writer, index=False, sheet_name='Pedidos_Faturamento')
                
                st.download_button(
                    label="📥 Baixar Planilha Excel para Nota Fiscal (.xlsx)",
                    data=buffer.getvalue(),
                    file_name=f"faturamento_tigrao_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="btn_download_excel_nelson"
                )
                
                st.write("---")
                st.dataframe(df_ordenado[["Data_Hora", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Status"]], use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Nenhum pedido foi recebido no sistema ainda.")

    # --- ABA 4: GESTÃO DA EQUIPE ---
    if is_admin and tab_equipe:
        with tab_equipe:
