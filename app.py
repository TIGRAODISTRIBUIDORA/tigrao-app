import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")

# PARAMETRIZAÇÃO GERAL DO TIGRÃO
PERCENTUAL_COMISSAO = 0.05  
SENHA_EXCLUSIVA_NELSON = "TigraoNelson2026"  # <--- SUA SENHA DE DONO

# Caminhos dos arquivos de banco de dados internos no servidor
CAMINHO_VENDAS = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES = "clientes_banco.xlsx"
CAMINHO_PRODUTOS = "produtos_banco.xlsx"

# 1. INICIALIZAÇÃO DOS ARQUIVOS SE NÃO EXISTIREM (COM COLUNA DE DESCONTO MÁXIMO)
if not os.path.exists(CAMINHO_PRODUTOS):
    pd.DataFrame([
        {"Produto": "Cerveja Lata 350ml (Fardo c/ 12)", "Preço": 36.00, "Estoque": 100, "Desconto_Max": 10.0},
        {"Produto": "Refrigerante 2L (Fardo c/ 6)", "Preço": 48.00, "Estoque": 100, "Desconto_Max": 5.0},
        {"Produto": "Água Mineral 500ml (Fardo c/ 12)", "Preço": 18.00, "Estoque": 100, "Desconto_Max": 0.0}
    ]).to_excel(CAMINHO_PRODUTOS, index=False)

if not os.path.exists(CAMINHO_CLIENTES):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "Endereco": "Rua Principal, 100"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "Endereco": "Av. Central, 500"}
    ]).to_excel(CAMINHO_CLIENTES, index=False)

if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=["Data_Hora", "Cliente", "Produto", "Quantidade", "Desconto_Aplicado", "Total", "Pagamento", "Obs", "Status"]).to_excel(CAMINHO_VENDAS, index=False)

# LEITURA CONSTANTE DOS BANCOS DE DADOS
df_produtos = pd.read_excel(CAMINHO_PRODUTOS)
df_clientes = pd.read_excel(CAMINHO_CLIENTES)
df_pedidos = pd.read_excel(CAMINHO_VENDAS)

# Garante que a coluna Desconto_Max existe em bases antigas
if "Desconto_Max" not in df_produtos.columns:
    df_produtos["Desconto_Max"] = 0.0
    df_produtos.to_excel(CAMINHO_PRODUTOS, index=False)

# ABAS DE TRABALHO DO APP
tab1, tab2, tab3, tab4 = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Cliente", "📦 Consultar Pedidos", "💰 Comissões"])

# --- ABA 1: PASSAR PEDIDO (COM VALIDAÇÃO DE DESCONTO BLOQUEANTE) ---
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
            dados_c = df_clientes[df_clientes["Nome"] == cliente_final].iloc
            st.success(f"🟩 CLIENTE CONFIRMADO: {dados_c['Nome']} (COD-{dados_c['Codigo']})")

    st.markdown("---")
    st.subheader("2. Itens do Pedido")
    lista_produtos = df_produtos["Produto"].dropna().astype(str).tolist()
    pesquisa_pr = st.text_input("🔍 Buscar Produto por Nome:")
    
    lista_pr_mostra = [p for p in lista_produtos if pesquisa_pr.lower() in p.lower()] if pesquisa_pr else lista_produtos
    
    with st.form("form_pedido_venda"):
        prod_selecionado = st.selectbox("Confirme o Produto:", lista_pr_mostra if lista_pr_mostra else ["Nenhum produto"])
        
        try:
            linha_p = df_produtos[df_produtos["Produto"] == prod_selecionado].iloc
            preco_un = float(linha_p["Preço"])
            estoque_un = int(linha_p["Estoque"])
            desc_max_permitido = float(linha_p["Desconto_Max"])
            
            st.info(f"💰 Preço: R$ {preco_un:.2f} | 📦 Estoque: {estoque_un} fardos | 📉 Desconto Máximo Autorizado: {desc_max_permitido}%")
            
            qtd = st.number_input("Quantidade:", min_value=1, max_value=max(1, estoque_un), value=1, step=1)
            
            # Campo para o vendedor colocar o desconto
            desconto_vendedor = st.number_input("Desconto a Aplicar neste item (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            
            # Cálculo do valor bruto e do desconto líquido
            valor_bruto = preco_un * qtd
            valor_desconto = valor_bruto * (desconto_vendedor / 100.0)
            total_pedido = valor_bruto - valor_desconto
            
        except Exception:
            preco_un, estoque_un, qtd, total_pedido, desc_max_permitido, desconto_vendedor = 0.0, 1, 1, 0.0, 0.0, 0.0

        forma_pagto = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix Tigrão", "Dinheiro"])
        obs = st.text_area("Observações")
        
        st.markdown(f"### 💰 Total com Desconto: **R$ {total_pedido:.2f}**")
        btn_enviar = st.form_submit_button("🚀 Enviar Pedido")

    if btn_enviar and cliente_final and prod_selecionado != "Nenhum fardo":
        # BARREIRA DE SEGURANÇA: Se o vendedor estourar o limite, o app não grava o pedido de jeito nenhum
        if desconto_vendedor > desc_max_permitido:
            st.error(f"❌ PEDIDO BLOQUEADO! O desconto digitado ({desconto_vendedor}%) é maior do que o máximo autorizado pela diretoria do Tigrão para este produto ({desc_max_permitido}%).")
        else:
            novo_p = pd.DataFrame([{"Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"), "Cliente": cliente_final, "Produto": prod_selecionado, "Quantidade": int(qtd), "Desconto_Aplicado": f"{desconto_vendedor}%", "Total": float(total_pedido), "Pagamento": forma_pagto, "Obs": obs, "Status": "Pendente"}])
            pd.concat([df_pedidos, novo_p], ignore_index=True).to_excel(CAMINHO_VENDAS, index=False)
            st.success("✅ Pedido enviado perfeitamente dentro da margem de desconto!")
            st.balloons()
            st.rerun()

# --- ABA 2: CADASTRAR CLIENTE ---
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
    if not df_pedidos.empty:
        st.dataframe(df_pedidos[["Data_Hora", "Cliente", "Produto", "Quantidade", "Desconto_Aplicado", "Total", "Status"]], use_container_width=True, hide_index=True)

# --- ABA 4: COMISSÕES ---
with tab4:
    st.subheader("💰 Suas Comissões")
    tot_v = df_pedidos["Total"].sum() if not df_pedidos.empty else 0.0
    st.metric("Volume Geral de Vendas", f"R$ {tot_v:.2f}")
    st.metric("Comissão Acumulada (5%)", f"R$ {(tot_v * PERCENTUAL_COMISSAO):.2f}")

# ==============================================================================
# 👑 CENTRAL EXCLUSIVA DO DONO (NELSON) - COM PARÂMETROS DE DESCONTO
# ==============================================================================
st.markdown("---")
st.write("🔒 **Painel de Controle Exclusivo da Diretoria**")
acesso_senha = st.text_input("Insira sua Senha de Dono para abrir o Banco de Dados:", type="password")

if acesso_senha == SENHA_EXCLUSIVA_NELSON:
    st.success("👑 Autenticado! Painel de Controle do Tigrão Liberado.")
    
    op_dono = st.radio("Selecione o que deseja fazer no Banco de Dados:", ["Incluir Novo Produto", "Alterar Preço / Estoque / Desconto Max", "Excluir Produto"], horizontal=True)
    
    # 1. INCLUIR PRODUTO NOVO COM DESCONTO MÁXIMO
    if op_dono == "Incluir Novo Produto":
        st.subheader("➕ Adicionar Novo Item ao Catálogo")
        with st.form("form_add_prod"):
            p_nome = st.text_input("Nome do Produto:")
            p_preco = st.number_input("Preço de Venda (R$):", min_value=0.1, value=10.0, step=0.5)
            p_est = st.number_input("Estoque de Entrada (Fardos):", min_value=1, value=50, step=1)
            p_desc = st.number_input("Desconto Máximo Autorizado para o Vendedor (%):", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
            btn_add = st.form_submit_button("💾 Gravar no Sistema")
        if btn_add and p_nome.strip():
            if p_nome.strip() in lista_produtos:
                st.error("❌ Este produto já existe!")
            else:
                novo_p_df = pd.DataFrame([{"Produto": p_nome.strip(), "Preço": float(p_preco), "Estoque": int(p_est), "Desconto_Max": float(p_desc)}])
                pd.concat([df_produtos, novo_p_df], ignore_index=True).to_excel(CAMINHO_PRODUTOS, index=False)
                st.success(f"🎉 Item incluído com {p_desc}% de margem limite de desconto!")
                st.rerun()

    # 2. ALTERAR PREÇO, ESTOQUE OU DESCONTO
    elif op_dono == "Alterar Preço / Estoque / Desconto Max":
        st.subheader("✏️ Atualizar Parâmetros de Venda")
        p_editar = st.selectbox("Escolha o produto:", lista_produtos)
        linha_edit = df_produtos[df_produtos["Produto"] == p_editar].index
        
        preco_atual = float(df_produtos.loc[linha_edit, "Preço"])
        estoque_atual = int(df_produtos.loc[linha_edit, "Estoque"])
        desconto_atual = float(df_produtos.loc[linha_edit, "Desconto_Max"])
        
        col_ed1, col_ed2, col_ed3 = st.columns(3)
        novo_preco = col_ed1.number_input("Novo Preço (R$):", value=preco_atual, min_value=0.1, step=0.5)
