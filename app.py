import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")

# PARAMETRIZAÇÃO GERAL DO TIGRÃO
PERCENTUAL_COMISSAO = 0.05  
SENHA_EXCLUSIVA_NELSON = "TigraoNelson2026"  # <--- ESSA É A SUA SENHA DE DONO PARA CONTROLAR TUDO

# Caminhos dos arquivos de banco de dados internos no servidor
CAMINHO_VENDAS = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES = "clientes_banco.xlsx"
CAMINHO_PRODUTOS = "produtos_banco.xlsx"

# 1. INICIALIZAÇÃO DOS ARQUIVOS SE NÃO EXISTIREM
if not os.path.exists(CAMINHO_PRODUTOS):
    pd.DataFrame([
        {"Produto": "Cerveja Lata 350ml (Fardo c/ 12)", "Preço": 36.00, "Estoque": 100},
        {"Produto": "Refrigerante 2L (Fardo c/ 6)", "Preço": 48.00, "Estoque": 100},
        {"Produto": "Água Mineral 500ml (Fardo c/ 12)", "Preço": 18.00, "Estoque": 100}
    ]).to_excel(CAMINHO_PRODUTOS, index=False)

if not os.path.exists(CAMINHO_CLIENTES):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500"}
    ]).to_excel(CAMINHO_CLIENTES, index=False)

if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Pagamento", "Obs", "Status"]).to_excel(CAMINHO_VENDAS, index=False)

# LEITURA CONSTANTE DOS BANCOS DE DADOS
df_produtos = pd.read_excel(CAMINHO_PRODUTOS)
df_clientes = pd.read_excel(CAMINHO_CLIENTES)
df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# ABAS DE TRABALHO DO APP
tab1, tab2, tab3, tab4 = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Cliente", "📦 Consultar Pedidos", "💰 Comissões"])

# --- ABA 1: PASSAR PEDIDO (PRODUTOS E PREÇOS DINÂMICOS) ---
with tab1:
    st.subheader("1. Dados do Cliente")
    lista_clientes = df_clientes["Nome"].dropna().astype(str).tolist()
    pesquisa_cl = st.text_input("🔍 Buscar Cliente por Nome ou Código:")
    
    if pesquisa_cl:
        df_f_cl = df_clientes[df_clientes["Nome"].str.contains(pesquisa_cl, case=False, na=False) | df_clientes["Codigo"].astype(str).str.contains(pesquisa_cl, na=False)]
        lista_cl_mostra = df_f_cl["Nome"].tolist()
    else:
        lista_cl_mostra = lista_clientes

    if pesquisa_cl and not lista_cl_mostra:
        st.error("❌ Cliente não localizado.")
        cliente_final = None
    else:
        cliente_final = st.selectbox("Selecione o cliente:", lista_cl_mostra if lista_cl_mostra else ["Nenhum cliente cadastrado"])
        if cliente_final and cliente_final != "Nenhum cliente cadastrado":
            dados_c = df_clientes[df_clientes["Nome"] == cliente_final].iloc[0]
            st.success(f"🟩 CLIENTE CONFIRMADO: {dados_c['Nome']} (COD-{dados_c['Codigo']})")

    st.markdown("---")
    st.subheader("2. Itens do Pedido")
    lista_produtos = df_produtos["Produto"].dropna().astype(str).tolist()
    pesquisa_pr = st.text_input("🔍 Buscar Produto por Nome:")
    
    lista_pr_mostra = [p for p in lista_produtos if pesquisa_pr.lower() in p.lower()] if pesquisa_pr else lista_produtos
    
    with st.form("form_pedido_venda"):
        prod_selecionado = st.selectbox("Confirme o Produto:", lista_pr_mostra if lista_pr_mostra else ["Nenhum produto"])
        
        try:
            linha_p = df_produtos[df_produtos["Produto"] == prod_selecionado].iloc[0]
            preco_un = float(linha_p["Preço"])
            estoque_un = int(linha_p["Estoque"])
            st.info(f"💰 Preço: R$ {preco_un:.2f} | 📦 Estoque: {estoque_un} fardos")
            qtd = st.number_input("Quantidade:", min_value=1, max_value=max(1, estoque_un), value=1, step=1)
            total_pedido = preco_un * qtd
        except Exception:
            preco_un, estoque_un, qtd, total_pedido = 0.0, 1, 1, 0.0

        forma_pagto = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix Tigrão", "Dinheiro"])
        obs = st.text_area("Observações")
        st.markdown(f"### 💰 Total: **R$ {total_pedido:.2f}**")
        btn_enviar = st.form_submit_button("🚀 Enviar Pedido")

    if btn_enviar and cliente_final and prod_selecionado != "Nenhum produto":
        novo_p = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), "Cliente": cliente_final, "Produto": prod_selecionado, "Quantidade": int(qtd), "Total": float(total_pedido), "Pagamento": forma_pagto, "Obs": obs, "Status": "Pendente"}])
        pd.concat([df_pedidos, novo_p], ignore_index=True).to_excel(CAMINHO_VENDAS, index=False)
        st.success("✅ Pedido enviado!")
        st.balloons()

# --- ABA 2: CADASTRAR CLIENTE (VENDEDOR CADASTRA DA RUA) ---
with tab2:
    st.subheader("📝 Cadastrar Cliente")
    with st.form("form_vendedor_cliente"):
        n_cli = st.text_input("Razão Social:")
        c_cli = st.text_input("CNPJ:")
        e_cli = st.text_input("Endereço:")
        btn_c = st.form_submit_button("💾 Salvar Cliente")
    if btn_c and n_cli.strip():
        prox_cod = int(df_clientes["Codigo"].max() + 1) if not df_clientes.empty else 1
        pd.concat([df_clientes, pd.DataFrame([{"Codigo": prox_cod, "Nome": n_cli.strip(), "CNPJ": c_cli, "Endereco": e_cli}])], ignore_index=True).to_excel(CAMINHO_CLIENTES, index=False)
        st.success("🎉 Cliente salvo!")
        st.rerun()

# --- ABA 3: CONSULTAR PEDIDOS ---
with tab3:
    st.subheader("📦 Acompanhamento de Pedidos")
    st.dataframe(df_pedidos[["Data_Hora", "Cliente", "Produto", "Quantidade", "Total", "Status"]], use_container_width=True, hide_index=True)

# --- ABA 4: COMISSÕES ---
with tab4:
    st.subheader("💰 Suas Comissões")
    tot_v = df_pedidos["Total"].sum() if not df_pedidos.empty else 0.0
    st.metric("Volume Geral de Vendas", f"R$ {tot_v:.2f}")
    st.metric("Comissão Acumulada (5%)", f"R$ {(tot_v * PERCENTUAL_COMISSAO):.2f}")

# ==============================================================================
# 👑 CENTRAL EXCLUSIVA DO DONO (NELSON) - PROTEGIDA POR SENHA NO FINAL DA TELA
# ==============================================================================
st.markdown("---")
st.write("🔒 **Painel de Controle Exclusivo da Diretoria**")
acesso_senha = st.text_input("Insira sua Senha de Dono para abrir o Banco de Dados:", type="password")

if acesso_senha == SENHA_EXCLUSIVA_NELSON:
    st.success("👑 Autenticado! Painel de Controle do Tigrão Liberado.")
    
    op_dono = st.radio("Selecione o que deseja fazer no Banco de Dados:", ["Incluir Novo Produto", "Alterar Preço / Estoque", "Excluir Produto"], horizontal=True)
    
    # 1. INCLUIR PRODUTO NOVO
    if op_dono == "Incluir Novo Produto":
        st.subheader("➕ Adicionar Novo Item ao Catálogo")
        with st.form("form_add_prod"):
            p_nome = st.text_input("Nome do Produto:")
            p_preco = st.number_input("Preço de Venda (R$):", min_value=0.1, value=10.0, step=0.5)
            p_est = st.number_input("Estoque de Entrada (Fardos):", min_value=1, value=50, step=1)
            btn_add = st.form_submit_button("💾 Gravar no Sistema")
        if btn_add and p_nome.strip():
            if p_nome.strip() in lista_produtos:
                st.error("❌ Este produto já existe no catálogo!")
            else:
                novo_p_df = pd.DataFrame([{"Produto": p_nome.strip(), "Preço": float(p_preco), "Estoque": int(p_est)}])
                pd.concat([df_produtos, novo_p_df], ignore_index=True).to_excel(CAMINHO_PRODUTOS, index=False)
                st.success(f"🎉 '{p_nome}' incluído com sucesso!")
                st.rerun()

    # 2. ALTERAR PREÇO OU ESTOQUE
    elif op_dono == "Alterar Preço / Estoque":
        st.subheader("✏️ Atualizar Preços e Estoques de Itens Existentes")
        p_editar = st.selectbox("Escolha o produto que deseja alterar o preço:", lista_produtos)
        linha_edit = df_produtos[df_produtos["Produto"] == p_editar].index[0]
        
        preco_atual = float(df_produtos.loc[linha_edit, "Preço"])
        estoque_atual = int(df_produtos.loc[linha_edit, "Estoque"])
        
        col_ed1, col_ed2 = st.columns(2)
        novo_preco = col_ed1.number_input("Novo Preço (R$):", value=preco_atual, min_value=0.1, step=0.5)
        novo_estoque = col_ed2.number_input("Atualizar Estoque (Fardos):", value=estoque_atual, min_value=0, step=1)
        
        if st.button("🔄 Aplicar Novo Preço/Estoque"):
            df_produtos.loc[linha_edit, "Preço"] = novo_preco
            df_produtos.loc[linha_edit, "Estoque"] = novo_estoque
            df_produtos.to_excel(CAMINHO_PRODUTOS, index=False)
            st.success("✅ Tabela de preços atualizada com sucesso no celular de todos os vendedores!")
            st.rerun()

    # 3. EXCLUIR PRODUTO DO CATÁLOGO
    elif op_dono == "Excluir Produto":
        st.subheader("❌ Remover Produto Definitivamente")
        p_deletar = st.selectbox("Selecione o produto que deseja APAGAR do sistema:", lista_produtos)
        
        st.warning(f"Atenção: Ao clicar abaixo, o produto '{p_deletar}' sumirá da tela dos vendedores.")
        if st.button("🗑️ Confirmar Exclusão Definitiva"):
            df_produtos = df_produtos[df_produtos["Produto"] != p_deletar]
            df_produtos.to_excel(CAMINHO_PRODUTOS, index=False)
            st.success(f"🗑️ Produto removido do banco de dados!")
            st.rerun()
            
    st.markdown("---")
    st.write("📊 **Visualização Geral do seu Estoque e Preços:**")
    st.dataframe(df_produtos, use_container_width=True, hide_index=True)
