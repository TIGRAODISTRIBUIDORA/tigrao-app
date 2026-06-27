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
CAMINHO_USUARIOS = "usuarios_banco.xlsx"
SENHA_NELSON = "TigraoNelson2026"
EMAIL_DONO = "sodemilecem23@gmail.com"

# 1. INICIALIZAÇÃO DO BANCO DE DADOS DE VENDEDORES
if not os.path.exists(CAMINHO_USUARIOS):
    pd.DataFrame([
        {"Email": EMAIL_DONO, "Senha": "123", "Nome": "Nelson Dono"},
        {"Email": "joaquim@tigrao.com", "Senha": "123", "Nome": "Joaquim Silva"},
        {"Email": "pedro@tigrao.com", "Senha": "123", "Nome": "Pedro Santos"},
        {"Email": "carlos@tigrao.com", "Senha": "123", "Nome": "Carlos Oliveira"}
    ]).to_excel(CAMINHO_USUARIOS, index=False)

df_usuarios = pd.read_excel(CAMINHO_USUARIOS)

# 2. INICIALIZAÇÃO DO BANCO DE DADOS DE VENDAS
if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["Data_Hora", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Status"]).to_excel(CAMINHO_VENDAS, index=False)

df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# GERENCIAMENTO DE SESSÃO DO LOGIN
if "vendedor_nome" not in st.session_state:
    st.session_state["vendedor_nome"] = ""
if "vendedor_email" not in st.session_state:
    st.session_state["vendedor_email"] = ""

# --- TELA DE ATIVAÇÃO ÚNICA (SÓ MOSTRA SE O CELULAR ESTIVER DESCONECTADO) ---
if st.session_state["vendedor_nome"] == "":
    st.subheader("🔐 Ativação Única do Aplicativo")
    st.write("Insira seu e-mail e senha corporativa para liberar o aparelho.")
    
    email_input = st.text_input("E-mail do Vendedor:")
    senha_input = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("🚀 Ativar Aplicativo neste Celular"):
        email_limpo = email_input.strip().lower()
        usuario_validar = df_usuarios[(df_usuarios["Email"].astype(str).str.lower() == email_limpo) & (df_usuarios["Senha"].astype(str) == senha_input.strip())]
        
        if not usuario_validar.empty:
            st.session_state["vendedor_nome"] = usuario_validar.iloc[0]["Nome"]
            st.session_state["vendedor_email"] = email_limpo
            st.success(f"Dispositivo ativado com sucesso para {st.session_state['vendedor_nome']}!")
            st.rerun()
        else:
            st.error("❌ E-mail ou Senha incorretos. Verifique com a administração do Tigrão.")

# --- SISTEMA LIBERADO (CELULAR JÁ LEMBRA QUEM É O VENDEDOR) ---
else:
    st.success(f"👤 VENDEDOR CONECTADO: **{st.session_state['vendedor_nome'].upper()}**")
    
    if st.button("🔄 Desconectar deste aparelho"):
        st.session_state["vendedor_nome"] = ""
        st.session_state["vendedor_email"] = ""
        st.rerun()
        
    st.markdown("---")

    # CRIAÇÃO DAS VARIÁVEIS DE ABAS SEPARADAS E INDEPENDENTES
    is_admin = st.session_state["vendedor_email"] == EMAIL_DONO
    
    if is_admin:
        tab1, tab2, tab3 = st.tabs(["📋 Passar Pedido", "👑 Recebimento Nelson (Central)", "👥 Gestão da Equipe"])
    else:
        tab1, tab2 = st.tabs(["📋 Passar Pedido", "👑 Recebimento Nelson (Central)"])

    # --- ABA 1: PASSAR PEDIDO (CORRIGIDA) ---
    with tab1:
        st.subheader("📋 Lançar Novo Pedido")
        cliente = st.selectbox("Selecione o Cliente:", ["Supermercado Silva", "Mercado do João", "Conveniência Central"])
        
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
                "Cliente": cliente,
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

    # --- ABA 2: RECEBIMENTO NELSON (CORRIGIDA) ---
    with tab2:
        st.subheader("🔒 Painel de Recebimento de Pedidos")
        senha_digitada = st.text_input("Digite a Senha de Dono:", type="password", key="senha_receb_nelson")
        
        if senha_digitada == SENHA_NELSON:
            st.success("Acesso Liberado!")
            
            # Recarrega a planilha atualizada da nuvem
            df_pedidos_atualizado = pd.read_excel(CAMINHO_VENDAS)
            
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

    # --- ABA 3: 👥 GESTÃO DA EQUIPE (CORRIGIDA) ---
    if is_admin:
        with tab3:
            st.subheader("👑 Controle de Vendedores do Tigrão")
            
            st.write("➕ **Adicionar Novo Vendedor no Sistema:**")
            with st.form("form_add_vendedor"):
                v_nome = st.text_input("Nome Completo do Vendedor:")
                v_email = st.text_input("E-mail de Login:")
                v_senha = st.text_input("Senha Inicial:")
                btn_v = st.form_submit_button("💾 Salvar Novo Vendedor")
                
            if btn_v and v_nome.strip() and v_email.strip():
                email_l_novo = v_email.strip().lower()
                if email_l_novo in df_usuarios["Email"].astype(str).str.lower().tolist():
                    st.error("❌ Este e-mail de vendedor já está cadastrado!")
                else:
                    novo_u_df = pd.DataFrame([{"Email": email_l_novo, "Senha": v_senha.strip(), "Nome": v_nome.strip()}])
                    df_usuarios_atualizado = pd.concat([df_usuarios, novo_u_df], ignore_index=True)
                    df_usuarios_atualizado.to_excel(CAMINHO_USUARIOS, index=False)
                    st.success(f"🎉 Vendedor '{v_nome}' cadastrado com sucesso!")
                    st.rerun()
            
            st.markdown("---")
            st.write("🗑️ **Excluir Vendedor do Sistema:**")
            lista_emails_excluir = [e for e in df_usuarios["Email"].tolist() if e != EMAIL_DONO]
            
            if lista_emails_excluir:
                email_deletar = st.selectbox("Selecione o e-mail do funcionário que deseja remover:", lista_emails_excluir)
                if st.button("❌ Confirmar Exclusão Definitiva"):
                    df_usuarios_novos = df_usuarios[df_usuarios["Email"] != email_deletar]
                    df_usuarios_novos.to_excel(CAMINHO_USUARIOS, index=False)
                    st.success("🗑️ Funcionário removido do banco de dados com sucesso!")
                    st.rerun()
            else:
                st.info("Nenhum vendedor cadastrado para remoção.")
                
            st.markdown("---")
            st.write("📋 **Lista de Vendedores Cadastrados no Banco:**")
            st.dataframe(df_usuarios[["Nome", "Email", "Senha"]], use_container_width=True, hide_index=True)
