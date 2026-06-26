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

# Garante compatibilidade de colunas na tabela de pedidos se for antiga
if "Cliente_Razao" not in df_pedidos.columns and "Cliente" in df_pedidos.columns:
    df_pedidos = df_pedidos.rename(columns={"Cliente": "Cliente_Razao"})

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
        
        # Criação das variáveis fiscais vazias por segurança
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
    
  # ==============================================================================
# 👑 CENTRAL EXCLUSIVA DO DONO (NELSON) - AJUSTE DE RECEBIMENTO EXCEL DISA
# ==============================================================================
st.markdown("---")
st.write("🔒 **Painel de Controle Exclusivo da Diretoria**")
acesso_senha = st.text_input("Insira sua Senha de Dono para abrir o Banco de Dados:", type="password")

if acesso_senha == SENHA_EXCLUSIVA_NELSON:
    st.success("👑 Autenticado! Painel de Controle do Tigrão Liberado.")
    
    st.subheader("🚚 1. Recebimento de Pedidos para o ADS TEC DISA")
    
    if not df_pedidos.empty:
        # Ajuste: Organiza os pedidos por ordem de chegada (Mais recentes primeiro)
        df_disa = df_pedidos.copy()
        if "Data_Hora" in df_disa.columns:
            df_disa = df_disa.sort_values(by="Data_Hora", ascending=False)
            
        st.write(f"📢 Você tem **{len(df_disa[df_disa['Status']=='Pendente'])}** pedido(s) pendente(s) aguardando faturamento!")
        
        # Converte a tabela atualizada em formato Excel (.xlsx) puro para o DISA
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            df_disa.to_excel(writer, index=False, sheet_name='Importar_DISA')
        dados_excel_puros = buffer_excel.getvalue()
        
        # Botão direto para baixar o arquivo pronto
        st.download_button(
            label="📥 Baixar Pedidos em Excel para Nota Fiscal (.xlsx)",
            data=dados_excel_puros,
            file_name=f"pedidos_disa_{datetime.now().strftime('%d_%m_%Y_%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="btn_download_disa_def"
        )
        st.caption("💡 *Clique acima para baixar o arquivo. Depois, é só entrar no seu sistema DISA e importar essa planilha para rodar as notas fiscais automaticamente.*")
        
        # Exibe um resumo visual rápido dos pedidos recebidos em ordem
        st.write("📋 **Visualização dos Pedidos Recebidos (Ordem de Chegada):**")
        st.dataframe(df_disa[["Data_Hora", "Cliente_Razao", "Produto", "Quantidade", "Total", "Status"]], use_container_width=True, hide_index=True)
    else:
        st.info("ℹ️ Nenhum pedido foi recebido no sistema até o momento.")
        
    st.markdown("---")
    # (O restante do código de Incluir e Excluir Produto continua igual abaixo...)
