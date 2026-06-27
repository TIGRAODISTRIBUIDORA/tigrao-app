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
SENHA_NELSON = "TigraoNelson2026"

# BANCO DE DADOS FIXO DE ACESSOS (E-mail e Senha de cada um)
# Você pode alterar ou adicionar novas credenciais aqui quando quiser!
USUARIOS_CADASTRADOS = {
    "joaquim@tigrao.com": {"senha": "123", "nome": "Joaquim Silva"},
    "pedro@tigrao.com": {"senha": "123", "nome": "Pedro Santos"},
    "carlos@tigrao.com": {"senha": "123", "nome": "Carlos Oliveira"},
    "sodemilecem23@gmail.com": {"senha": "123", "nome": "Nelson Dono"} # Seu acesso admin
}

if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["Data_Hora", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Status"]).to_excel(CAMINHO_VENDAS, index=False)

df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# =========================================================
# GERENCIAMENTO DE MEMÓRIA PERMANENTE DO LOGIN
# =========================================================
if "vendedor_nome" not in st.session_state:
    st.session_state["vendedor_nome"] = ""
if "vendedor_email" not in st.session_state:
    st.session_state["vendedor_email"] = ""

# Se o usuário não está na memória do celular, mostra a tela de identificação única
if st.session_state["vendedor_nome"] == "":
    st.subheader("🔐 Ativação Única do Aplicativo")
    st.write("Insira seu e-mail e senha corporativa. O celular lembrará do seu acesso nas próximas visitas.")
    
    email_input = st.text_input("E-mail do Vendedor:")
    senha_input = st.text_input("Senha de Acesso:", type="password")
    
    if st.button("🚀 Ativar Aplicativo neste Celular"):
        email_limpo = email_input.strip().lower()
        if email_limpo in USUARIOS_CADASTRADOS and USUARIOS_CADASTRADOS[email_limpo]["senha"] == senha_input.strip():
            # Salva na memória do sistema
            st.session_state["vendedor_nome"] = USUARIOS_CADASTRADOS[email_limpo]["nome"]
            st.session_state["vendedor_email"] = email_limpo
            st.success(f"Dispositivo ativado com sucesso para {st.session_state['vendedor_nome']}!")
            st.rerun()
        else:
            st.error("❌ E-mail ou Senha incorretos. Verifique com a administração do Tigrão.")

# Se o celular já lembra quem é o vendedor, abre o painel direto sem pedir senhas
else:
    # Cabeçalho de identificação automática permanente
    st.success(f"👤 VENDEDOR CONECTADO: **{st.session_state['vendedor_nome'].upper()}**")
    
    # Botão opcional caso ele queira trocar de conta ou celular
    if st.button("🔄 Desconectar deste aparelho (Trocar de Vendedor)"):
        st.session_state["vendedor_nome"] = ""
        st.session_state["vendedor_email"] = ""
        st.rerun()
        
    st.markdown("---")

    # Divisão das abas de trabalho normais
    aba_vendedor, aba_diretoria = st.tabs(["📋 Passar Pedido", "👑 Recebimento Nelson (Central)"])

    # --- 1. TELA DO VENDEDOR (Lançamento Automático) ---
    with aba_vendedor:
        st.subheader("📋 Lançar Novo Pedido")
        
        cliente = st.selectbox("Selecione o Cliente:", ["Supermercado Silva", "Mercado do João", "Conveniência Central"])
        
        # Lista de produtos padrão do Bloco 1
        produtos_fixos = {"Bananada Natural (Fardo)": 36.00, "Cerveja Lata 350ml (Fardo)": 42.00, "Refrigerante 2L (Fardo)": 48.00}
        produto = st.selectbox("Selecione o Produto:", list(produtos_fixos.keys()))
        
        preco_un = produtos_fixos[produto]
        st.caption(f"Preço do fardo: R$ {preco_un:.2f}")
        
        quantidade = st.number_input("Quantidade de Fardos:", min_value=1, value=1, step=1)
        total_pedido = preco_un * quantidade
        st.markdown(f"#### 💰 Total do Pedido: **R$ {total_pedido:.2f}**")
        
        forma_pagto = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix", "Dinheiro"])
        
        if st.button("🚀 Enviar Pedido para a Central"):
            novo_p = pd.DataFrame([{
                "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Vendedor": st.session_state["vendedor_nome"], # Grava o nome da memória direto no Excel
                "Cliente": cliente,
                "Produto": produto,
                "Quantidade": int(quantidade),
                "Total": float(total_pedido),
                "Pagamento": forma_pagto,
                "Status": "Pendente"
            }])
            df_final = pd.concat([df_pedidos, novo_p], ignore_index=True)
            df_final.to_excel(CAMINHO_VENDAS, index=False)
            st.success(f"✅ Pedido de {st.session_state['vendedor_nome']} gravado no Excel com sucesso!")
            st.balloons()
            st.rerun()

    # --- 2. TELA DO NELSON (Recebimento com Auditoria por Vendedor) ---
    with aba_diretoria:
        st.subheader("🔒 Painel de Recebimento de Pedidos")
        senha_digitada = st.text_input("Digite a Senha de Dono:", type="password")
        
        if senha_digitada == SENHA_NELSON:
            st.success("Acesso Liberado!")
            
            if not df_pedidos.empty:
                df_ordenado = df_pedidos.sort_values(by="Data_Hora", ascending=False)
                
                st.write(f"📢 Você tem **{len(df_ordenado[df_ordenado['Status']=='Pendente'])}** pedido(s) pendente(s) para faturar no DISA.")
                
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_ordenado.to_excel(writer, index=False, sheet_name='Pedidos_Faturamento')
                
                st.download_button(
                    label="📥 Baixar Planilha Excel para Nota Fiscal (.xlsx)",
                    data=buffer.getvalue(),
                    file_name=f"faturamento_tigrao_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                st.write("---")
                st.write("📋 **Lista de Pedidos na Tela (Ordem de Chegada com Nome de quem vendeu):**")
                st.dataframe(df_ordenado[["Data_Hora", "Vendedor", "Cliente", "Produto", "Quantidade", "Total", "Status"]], use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Nenhum pedido foi recebido no sistema ainda.")
