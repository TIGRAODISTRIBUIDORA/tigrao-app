import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

st.set_page_config(page_title="Tigrão Distribuidora", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")

PERCENTUAL_COMISSAO = 0.05  
SENHA_EXCLUSIVA_NELSON = "TigraoNelson2026"  

CAMINHO_VENDAS = "vendas_tigrao.xlsx"
CAMINHO_CLIENTES = "clientes_banco.xlsx"
CAMINHO_PRODUTOS = "produtos_banco.xlsx"

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

df_produtos = pd.read_excel(CAMINHO_PRODUTOS)
df_clientes = pd.read_excel(CAMINHO_CLIENTES)
df_pedidos = pd.read_excel(CAMINHO_VENDAS)

if "Desconto_Max" not in df_produtos.columns:
    df_produtos["Desconto_Max"] = 0.0
    df_produtos.to_excel(CAMINHO_PRODUTOS, index=False)

tab1, tab2, tab3, tab4 = st.tabs(["📋 Passar Pedido", "➕ Cadastrar Cliente", "📦 Consultar Pedidos", "💰 Comissões"])

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
        
        if cliente_final and cliente_final != "Nenhum cliente cadastrado":
            dados_filtrados = df_clientes[df_clientes["Nome"] == cliente_final]
            if not dados_filtrados.empty:
                dados_c = dados_filtrados.iloc[0]
                st.success(f"🟩 CLIENTE CONFIRMADO: {dados_c['Nome']} (COD-{int(dados_c['Codigo'])})")
                st.caption(f"📌 **CNPJ:** {dados_c['CNPJ']} | **Endereço:** {dados_c['Endereco']}")

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
                    "Cliente": cliente_final,
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
        st.success("🎉 Cliente saved!")
        st.rerun()

with tab3:
    st.subheader("📦 Acompanhamento de Pedidos")
    if not df_pedidos.empty:
        st.dataframe(df_pedidos[["Data_Hora", "Cliente", "Produto", "Quantidade", "Desconto_Aplicado", "Total", "Status"]], use_container_width=True, hide_index=True)

with tab4:
    st.subheader("💰 Suas Comissões")
    tot_v = df_pedidos["Total"].sum() if not df_pedidos.empty else 0.0
    st.metric("Volume Geral de Vendas", f"R$ {tot_v:.2f}")
    st.metric("Comissão Acumulada (5%)", f"R$ {(tot_v * PERCENTUAL_COMISSAO):.2f}")

st.markdown("---")
st.write("🔒 **Painel de Controle Exclusivo da Diretoria**")
acesso_senha = st.text_input("Insira sua Senha de Dono para abrir o Banco de Dados:", type="password")

if acesso_senha == SENHA_EXCLUSIVA_NELSON:
    st.success("👑 Autenticado! Painel de Controle do Tigrão Liberado.")
    
    st.subheader("🚚 Exportar Vendas para Faturamento")
    if not df_pedidos.empty:
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_pedidos.to_excel(writer, index=False, sheet_name='Pedidos_Faturamento')
        dados_excel_puros = buffer_excel.getvalue()
        
        st.download_button(
            label="📥 Baixar Planilha para Nota Fiscal (Excel .xlsx)",
            data=dados_excel_puros,
            file_name=f"faturamento_tigrao_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("Nenhum pedido foi lançado no sistema ainda para faturar.")
        
    st.markdown("---")
    op_dono = st.radio("Selecione a ação gerencial:", ["Alterar Preços e Estoques (Modo Planilha)", "Incluir Novo Produto", "Excluir Produto"], horizontal=True)
    
    if op_dono == "Alterar Preços e Estoques (Modo Planilha)":
        st.subheader("✏️ Alterar Preços Direto na Tabela (Estilo Excel)")
        tabela_editavel = st.data_editor(
            df_produtos[["Produto", "Preço", "Estoque", "Desconto_Max"]],
            use_container_width=True,
            hide_index=True,
            disabled=["Produto"]
        )
        if st.button("💾 Salvar Alterações da Tabela"):
            try:
                tabela_editavel.to_excel(CAMINHO_PRODUTOS, index=False)
                st.success("✅ Toda a tabela foi atualizada!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar a tabela: {e}")

    elif op_dono == "Incluir Novo Produto":
        st.subheader("➕ Adicionar Novo Item ao Catálogo")
        with st.form("form_add_prod"):
            p_nome = st.text_input("Nome do Produto:")
            p_preco = st.number_input("Preço de Venda (R$):", min_value=0.1, value=10.0, step=0.5)
