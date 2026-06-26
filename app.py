import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("Painel do Vendedor - Sistema de Vendas")

# CONFIGURAÇÃO DE PARAMETRIZAÇÃO
PERCENTUAL_COMISSAO = 0.05  # 5% de comissão (Você pode alterar esse número quando quiser)

# Caminhos dos arquivos de dados na nuvem
CAMINHO_EXCEL = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES_EXCEL = "clientes_tigrao.xlsx"

# 1. Gerenciamento do Banco de Dados de Clientes (Excel)
if not os.path.exists(CAMINHO_CLIENTES_EXCEL):
    clientes_iniciais = pd.DataFrame([
        {"Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100", "IE": "Isento", "Telefone": "(11) 99999-9999"},
        {"Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500", "IE": "123456789", "Telefone": "(11) 98888-8888"}
    ])
    clientes_iniciais.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)

df_clientes_salvos = pd.read_excel(CAMINHO_CLIENTES_EXCEL)
lista_nomes_clientes = df_clientes_salvos["Nome"].dropna().tolist()

# 2. Inicialização do histórico de pedidos para evitar erros de leitura
if os.path.exists(CAMINHO_EXCEL):
    df_pedidos = pd.read_excel(CAMINHO_EXCEL)
    # Garante que a coluna Status existe caso seja uma planilha antiga
    if "Status" not in df_pedidos.columns:
        df_pedidos["Status"] = "Pendente"
        df_pedidos.to_excel(CAMINHO_EXCEL, index=False)
else:
    df_pedidos = pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status"])

# 3. Catálogo de Produtos
produtos_dados = {
    "Produto": ["Cerveja Lata 350ml (Fardo c/ 12)", "Refrigerante 2L (Fardo c/ 6)", "Água Mineral 500ml (Fardo c/ 12)", "Suco Caixa 1L (Caixa c/ 12)"],
    "Preço (R$)": [36.00, 48.00, 18.00, 60.00],
    "Estoque": [150, 200, 300, 100]
}
df_produtos = pd.DataFrame(produtos_dados)

# 4. Criação das Novas Abas no Aplicativo
aba_pedido, aba_cadastro, aba_historico = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Cliente", "📊 Histórico e Comissões"])

# --- ABA 1: PASSAR PEDIDO ---
with aba_pedido:
    with st.form("formulario_pedido"):
        st.subheader("1. Dados do Cliente")
        cliente_selecionado = st.selectbox("Selecione o Cliente para o Pedido", lista_nomes_clientes)
        
        if cliente_selecionado:
            dados_c = df_clientes_salvos[df_clientes_salvos["Nome"] == cliente_selecionado].iloc[0]
            st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']}")
        
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
        comissao_estimada = valor_final * PERCENTUAL_COMISSAO
        st.markdown(f"### 💰 Total do Pedido: **R$ {valor_final:.2f}**")
        st.caption(f"⭐ *Comissão estimada deste pedido ({(PERCENTUAL_COMISSAO*100):.0f}%): R$ {comissao_estimada:.2f}*")
        
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
                "Obs": observacao,
                "Status": "Pendente"  # Todo pedido entra como Pendente inicialmente
            }])
            
            df_final = pd.concat([df_pedidos, novo_pedido], ignore_index=True)
            df_final.to_excel(CAMINHO_EXCEL, index=False)
            st.success(f"✅ Pedido gravado com sucesso! Status: PENDENTE")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"Erro ao salvar o pedido: {e}")

# --- ABA 2: CADASTRAR NOVO CLIENTE ---
with aba_cadastro:
    st.subheader("📝 Cadastro de Novo Cliente - Dados Fiscais")
    with st.form("formulario_cliente"):
        nome_input = st.text_input("Nome Razão Social / Nome Fantasia")
        cnpj_input = st.text_input("CNPJ")
        ie_input = st.text_input("Inscrição Estadual (IE) / Se não tiver, digite 'Isento'")
        endereco_input = st.text_input("Endereço Completo")
        telefone_input = st.text_input("Telefone de Contato")
        
        botao_cadastrar = st.form_submit_button("💾 Salvar Cliente no Sistema")
        
    if botao_cadastrar:
        if nome_input.strip() == "" or cnpj_input.strip() == "":
            st.warning("⚠️ Nome e CNPJ são obrigatórios.")
        elif nome_input.strip() in lista_nomes_clientes:
            st.error("❌ Este nome de cliente já existe!")
        else:
            try:
                novo_cliente_df = pd.DataFrame([{
                    "Nome": nome_input.strip(),
                    "CNPJ": cnpj_input.strip(),
                    "Endereco": endereco_input.strip(),
                    "IE": ie_input.strip(),
                    "Telefone": telefone_input.strip()
                }])
                df_atualizado = pd.concat([df_clientes_salvos, novo_cliente_df], ignore_index=True)
                df_atualizado.to_excel(CAMINHO_CLIENTES_EXCEL, index=False)
                st.success(f"🎉 Cliente '{nome_input}' cadastrado com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cadastrar cliente: {e}")

# --- ABA 3: HISTÓRICO, STATUS E COMISSÕES ---
with aba_historico:
    st.subheader("📊 Relatório de Vendas e Acompanhamento")
    
    if not df_pedidos.empty:
        # Indicadores financeiros consolidados na tela do vendedor
        total_vendas_vendedor = df_pedidos["Total"].sum()
        total_comissao_vendedor = total_vendas_vendedor * PERCENTUAL_COMISSAO
        total_pedidos_vendedor = len(df_pedidos)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Qtd Pedidos", f"{total_pedidos_vendedor}")
        col2.metric("Total Vendido", f"R$ {total_vendas_vendedor:.2f}")
        col3.metric("Sua Comissão (5%)", f"R$ {total_comissao_vendedor:.2f}", delta_color="inverse")
        
        st.markdown("---")
        
        # Filtro de Busca de Clientes e Status para consulta rápida
        st.write("🔍 **Consultar Pedidos Lançados**")
        cliente_filtro = st.selectbox("Filtrar Histórico por Cliente (Opcional)", ["Todos"] + lista_nomes_clientes)
        
        df_filtrado = df_pedidos.copy()
        if cliente_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado["Cliente"] == cliente_filtro]
            
        # Exibe a tabela detalhada com o status da entrega atualizado em tempo real
        st.dataframe(
            df_filtrado[["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Status"]], 
            use_container_width=True
        )
    else:
        st.info("ℹ️ Nenhum pedido foi lançado no sistema ainda.")
