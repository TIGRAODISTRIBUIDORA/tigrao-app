import streamlit as st
import pandas as pd
from datetime import datetime
import io
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

# 1. INICIALIZAÇÃO DOS ARQUIVOS SE NÃO EXISTIREM
if not os.path.exists(CAMINHO_PRODUTOS):
    pd.DataFrame([
        {"Produto": "Cerveja Lata 350ml (Fardo c/ 12)", "Preço": 36.00, "Estoque": 100, "Desconto_Max": 10.0},
        {"Produto": "Refrigerante 2L (Fardo c/ 6)", "Preço": 48.00, "Estoque": 100, "Desconto_Max": 5.0},
        {"Produto": "Água Mineral 500ml (Fardo c/ 12)", "Preço": 18.00, "Estoque": 100, "Desconto_Max": 0.0}
    ]).to_excel(CAMINHO_PRODUTOS, index=False)

if not os.path.exists(CAMINHO_CLIENTES):
    pd.DataFrame([
        {"Codigo": 1, "Nome": "Supermercado Silva", "CNPJ": "00.000.000/0001-00", "IE": "Isento", "Endereco": "Rua Principal, 100", "Telefone": "(11) 99999-9999"},
        {"Codigo": 2, "Nome": "Mercado do João", "CNPJ": "11.111.111/0001-11", "IE": "123456789", "Endereco": "Av. Central, 500", "Telefone": "(11) 98888-8888"}
    ]).to_excel(CAMINHO_CLIENTES, index=False)

if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=[
        "Data_Hora", "Codigo_Cliente", "Cliente_Razao", "CNPJ", "IE", "Endereco", 
        "Produto", "Quantidade", "Desconto_Aplicado", "Total", "Pagamento", "Obs", "Status"
    ]).to_excel(CAMINHO_VENDAS, index=False)

# LEITURA CONSTANTE DOS BANCOS DE DADOS
df_produtos = pd.read_excel(CAMINHO_PRODUTOS)
df_clientes = pd.read_excel(CAMINHO_CLIENTES)
df_pedidos = pd.read_excel(CAMINHO_VENDAS)

if "Desconto_Max" not in df_produtos.columns:
    df_produtos["Desconto_Max"] = 0.0
    df_produtos.to_excel(CAMINHO_PRODUTOS, index=False)

# ABAS DE TRABALHO DO APP
tab1, tab2, tab3, tab4 = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Cliente", "📦 Consultar Pedidos", "💰 Comissões"])

# --- ABA 1: PASSAR PEDIDO ---
with tab1:
    st.subheader("1. Dados do Cliente")
    lista_clientes = df_clientes["Nome"].dropna().astype(str).tolist()
    pesquisa_cl = st.text_input("🔍 Buscar Cliente por Nome ou Código:")
    
    if pesquisa_cl:
        df_f_cl = df_clientes[df_clientes["Nome"].astype(str).str.contains(pesquisa_cl, case=False, na=False) | df_clientes["Codigo"].astype(str).str.contains(pesquisa_cl, na=False)]
        lista_cl_mostra = df_f_cl["Nome"].tolist()
    else:
        lista_cl_mostra = lista_clientes

    if pesquisa_cl and not lista_cl_mostra:
        st.error("❌ Cliente não localizado.")
        cliente_final = None
    else:
        exibir_lista_cl = lista_cl_mostra if lista_cl_mostra else ["Nenhum cliente cadastrado"]
        cliente_final = st.selectbox("Selecione o cliente:", exibir_lista_cl)
        
        cod_c, cnpj_c, ie_c, end_c = "", "", "", ""
        
        if cliente_final and cliente_final != "Nenhum cliente cadastrado":
            dados_filtrados = df_clientes[df_clientes["Nome"] == cliente_final]
            if not dados_filtrados.empty:
                dados_c = dados_filtrados.iloc[0]
                cod_c = dados_c['Codigo']
                cnpj_c = dados_c['CNPJ']
                ie_c = dados_c.get('IE', 'Isento')
                end_c = dados_c['Endereco']
                st.success(f"🟩 CLIENTE CONFIRMADO: {dados_c['Nome']} (COD-{int(cod_c)})")
                st.caption(f"📌 **CNPJ:** {cnpj_c} | **IE:** {ie_c} | **Endereço:** {end_c}")

    st.markdown("---")
    st.subheader("2. Itens do Pedido")
    lista_produtos = df_produtos["Produto"].dropna().astype(str).tolist()
    pesquisa_pr = st.text_input("🔍 Buscar Produto por Nome:")
    
    lista_pr_mostra = [p for p in lista_produtos if pesquisa_pr.lower() in p.lower()] if pesquisa_pr else lista_produtos
    
    exibir_lista_pr = lista_pr_mostra if lista_pr_mostra else ["Nenhum produto"]
    prod_selecionado = st.selectbox("Confirme o Produto:", exibir_lista_pr)
    
    try:
        dados_prod_filtrados = df_produtos[df_produtos["Produto"] == prod_selecionado]
        if not dados_prod_filtrados.empty:
            linha_p = dados_prod_filtrados.iloc[0]
            preco_un = float(linha_p["Preço"])
            estoque_un = int(linha_p["Estoque"])
            desc_max_permitido = float(linha_p["Desconto_Max"])
            
            st.info(f"💰 Preço: R$ {preco_un:.2f} | 📦 Estoque: {estoque_un} fardos | 📉 Limite de Desconto: {desc_max_permitido}%")
            
            qtd = st.number_input("Quantidade:", min_value=1, max_value=max(1, estoque_un), value=1, step=1)
            desconto_vendedor = st.number_input("Desconto a Aplicar neste item (%):", min_value=0.0, max_value=100.0, value=0.0, step=0.5)
            
            valor_bruto = preco_un * qtd
            valor_desconto = valor_bruto * (desconto_vendedor / 100.0)
            total_pedido = valor_bruto - valor_desconto
        else:
            preco_un, estoque_un, qtd, total_pedido, desc_max_permitido, desconto_vendedor = 0.0, 1, 1, 0.0, 0.0, 0.0
    except Exception:
        preco_un, estoque_un, qtd, total_pedido, desc_max_permitido, desconto_vendedor = 0.0, 1, 1, 0.0, 0.0, 0.0

    estourou_limite = desconto_vendedor > desc_max_permitido

    if estourou_limite:
        st.error(f"🚨 VOCÊ ULTRAPASSOU O DESCONTO MÁXIMO PERMITIDO! O limite para este produto é de {desc_max_permitido}%.")
    else:
        st.write(f"💰 Total calculado com desconto: **R$ {total_pedido:.2f}**")

    with st.form("form_pedido_venda"):
        forma_pagto = st.selectbox("Forma de Pagamento:", ["Boleto 30 dias", "Pix Tigrão", "Dinheiro"])
        obs = st.text_area("Observações")
        btn_enviar = st.form_submit_button("🚀 Enviar Pedido")

    if btn_enviar:
        if estourou_limite:
            st.error("❌ ERRO: O desconto ultrapassa o limite autorizado.")
        elif not cliente_final or cliente_final == "Nenhum cliente cadastrado" or prod_selecionado == "Nenhum produto":
            st.error("❌ ERRO: Selecione um cliente e um produto válidos.")
        else:
            try:
                novo_p = pd.DataFrame([{
                    "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Codigo_Cliente": cod_c,
                    "Cliente_Razao": cliente_final,
                    "CNPJ": cnpj_c,
                    "IE": ie_c,
                    "Endereco": end_c,
                    "Produto": prod_selecionado,
                    "Quantidade": int(qtd),
                    "Desconto_Aplicado": f"{desconto_vendedor}%",
                    "Total": float(total_pedido),
                    "Pagamento": forma_pagto,
                    "Obs": obs,
                    "Status": "Pendente"
                }])
                df_final = pd.concat([df_pedidos, novo_p], ignore_index=True)
                df_final.to_excel(CAMINHO_VENDAS, index=False)
                st.success("✅ Pedido enviado!")
                st.balloons()
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# --- ABA 2: CADASTRAR CLIENTE (CORRIGIDA) ---
with tab2:
    st.subheader("📝 Cadastrar Cliente")
    with st.form("form_vendedor_cliente"):
        n_cli = st.text_input("Razão Social / Nome Fantasia:")
        c_cli = st.text_input("CNPJ:")
        i_cli = st.text_input("Inscrição Estadual (IE) / Se não tiver coloque 'Isento':", value="Isento")
        e_cli = st.text_input("Endereço Completo:")
        t_cli = st.text_input("Telefone:")
        btn_c = st.form_submit_button("💾 Salvar Cliente")
        
    if btn_c and n_cli.strip():
        prox_cod = int(df_clientes["Codigo"].max() + 1) if not df_clientes.empty else 1
        novo_cl_df = pd.DataFrame([{"Codigo": prox_cod, "Nome": n_cli.strip(), "CNPJ": c_cli, "IE": i_cli, "Endereco": e_cli, "Telefone": t_cli}])
        pd.concat([df_clientes, novo_cl_df], ignore_index=True).to_excel(CAMINHO_CLIENTES, index=False)
        st.success("🎉 Cliente salvo com dados fiscais!")
        st.rerun()

# --- ABA 3: CONSULTAR PEDIDOS ---
with tab3:
    st.subheader("📦 Acompanhamento de Pedidos")
    if not df_pedidos.empty:
        st.dataframe(df_pedidos[["Data_Hora", "Cliente_Razao", "Produto", "Quantidade", "Desconto_Aplicado", "Total", "Status"]], use_container_width=True, hide_index=True)

# --- ABA 4: COMISSÕES ---
with tab4:
    st.subheader("💰 Suas Comissões")
    tot_v = df_pedidos["Total"].sum() if not df_pedidos.empty else 0.0
    st.metric("Volume Geral de Vendas", f"R$ {tot_v:.2f}")
    st.metric("Comissão Acumulada (5%)", f"R$ {(tot_v * PERCENTUAL_COMISSAO):.2f}")

# ==============================================================================
# 👑 CENTRAL EXCLUSIVA DO DONO (NELSON)
# ==============================================================================
st.markdown("---")
st.write("🔒 **Painel de Controle Exclusivo da Diretoria**")
acesso_senha = st.text_input("Insira sua Senha de Dono para abrir o Banco de Dados:", type="password")

if acesso_senha == SENHA_EXCLUSIVA_NELSON:
    st.success("👑 Autenticado! Painel de Controle do Tigrão Liberado.")
    
    st.subheader("🚚 Exportar Vendas para o ADS TEC DISA (Ordem de Chegada)")
    if not df_pedidos.empty:
        df_disa = df_pedidos.copy()
        if "Data_Hora" in df_disa.columns:
            df_disa = df_disa.sort_values(by="Data_Hora", ascending=False)
            
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_disa.to_excel(writer, index=False, sheet_name='DISA_Faturamento')
        dados_excel_puros = buffer_excel.getvalue()
        
        st.download_button(
