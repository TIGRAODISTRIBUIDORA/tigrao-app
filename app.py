import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("Painel do Vendedor - Sistema de Vendas")

# Caminhos dos arquivos de dados na nuvem
CAMINHO_EXCEL = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES_EXCEL = "clientes_tigrao.xlsx"

# 1. Gerenciamento do Banco de Dados de Clientes (Excel)
if not os.path.exists(CAMINHO_CLIENTES_EXCEL):
    # Cria uma planilha inicial de clientes se não existir
    clientes_iniciais = pd.DataFrame([
        {"Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100", "IE": "Isento", "Telefone": "(11) 99999-9999"},
        {"Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500", "IE": "123456789", "Telefone": "(11) 98888-8888"}
    ])
    clientes_iniciais.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)

# Lê os clientes cadastrados na planilha
df_clientes_salvos = pd.read_excel(CAMINHO_CLIENTES_EXCEL)
lista_nomes_clientes = df_clientes_salvos["Nome"].dropna().tolist()

# 2. Catálogo de Produtos
produtos_dados = {
    "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
    "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
    "Estoque": [150, 200, 300, 100]
}
df_produtos = pd.DataFrame(produtos_dados)

# 3. Criação das Abas no Aplicativo
aba_pedido, aba_cadastro, aba_visualizar = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Cliente Completo", "🔍 Ver Clientes Cadastrados"])

# --- ABA 1: PASSAR PEDIDO ---
with aba_pedido:
    with st.form("formulario_pedido"):
        st.subheader("1. Dados do Cliente")
        cliente_selecionado = st.selectbox("Selecione o Cliente para o Pedido", lista_nomes_clientes)
        
        # Mostra os dados do cliente selecionado automaticamente para o vendedor conferir
        if cliente_selecionado:
            dados_c = df_clientes_salvos[df_clientes_salvos["Nome"] == cliente_selecionado].iloc[0]
            st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']} | **Tel:** {dados_c['Telefone']}")
        
        st.subheader("2. Itens do Pedido")
        produto_selecionado = st.selectbox("Selecione o Produto", df_produtos["Produto"].tolist())
        
        preco_unitario = float(df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Preço (R$)"].values)
        estoque_atual = int(df_produtos.loc[df_produtos["Produto"] == produto_selecionado, "Estoque"].values)
        
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
                "Cliente": cliente_selecionado,
                "Produto": produto_selecionado,
                "Quantidade": int(quantidade),
                "Total": float(valor_final),
                "Pagamento": forma_pagamento,
                "Obs": observacao
            }])
            
            if os.path.exists(CAMINHO_EXCEL):
                df_existente = pd.read_excel(CAMINHO_EXCEL)
                df_final = pd.concat([df_existente, novo_pedido], ignore_index=True)
            else:
                df_final = novo_pedido
                
            df_final.to_excel(CAMINHO_EXCEL, index=False)
            st.success(f"✅ Pedido gravado com sucesso!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Erro ao salvar o pedido: {e}")

# --- ABA 2: CADASTRAR NOVO CLIENTE COM TODOS OS DADOS ---
with aba_cadastro:
    st.subheader("📝 Cadastro de Novo Cliente - Dados Fiscais")
    with st.form("formulario_cliente"):
        nome_input = st.text_input("Nome Razão Social / Nome Fantasia")
        cnpj_input = st.text_input("CNPJ (Apenas números ou formatado)")
        ie_input = st.text_input("Inscrição Estadual (IE) / Se não tiver, digite 'Isento'")
        endereco_input = st.text_input("Endereço Completo (Rua, Número, Bairro, Cidade)")
        telefone_input = st.text_input("Telefone de Contato com DDD")
        
        botao_cadastrar = st.form_submit_button("💾 Salvar Cliente no Sistema")
        
    if botao_cadastrar:
        if nome_input.strip() == "" or cnpj_input.strip() == "":
            st.warning("⚠️ Nome e CNPJ são obrigatórios para o cadastro.")
        elif nome_input.strip() in lista_nomes_clientes:
            st.error("❌ Este nome de cliente já existe no sistema!")
        else:
            try:
                # Cria a linha do novo cliente
                novo_cliente_df = pd.DataFrame([{
                    "Nome": nome_input.strip(),
                    "CNPJ": cnpj_input.strip(),
                    "Endereco": endereco_input.strip(),
                    "IE": ie_input.strip(),
                    "Telefone": telefone_input.strip()
                }])
                
                # Junta com a planilha existente e salva
                df_atualizado = pd.concat([df_clientes_salvos, novo_cliente_df], ignore_index=True)
                df_atualizado.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)
                
                st.success(f"🎉 Cliente '{nome_input}' cadastrado com sucesso!")
                st.info("💡 Clique no botão 'Atualizar' da página para atualizar a lista.")
                st.rerun()
                
            except Exception as e:
                st.error(f"Erro ao cadastrar cliente: {e}")

# --- ABA 3: VISUALIZAR CLIENTES ---
with aba_visualizar:
    st.subheader("🔍 Clientes Cadastrados na Distribuidora")
    st.dataframe(df_clientes_salvos, use_container_width=True)
