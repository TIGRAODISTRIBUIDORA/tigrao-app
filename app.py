import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Tigrão - Sistema DEV",
    page_icon="🐯",
    layout="wide"
)

AMBIENTE = "DESENVOLVIMENTO"
PASTA_DADOS = "dados_dev" if AMBIENTE == "DESENVOLVIMENTO" else "dados_producao"

ARQ_USUARIOS = f"{PASTA_DADOS}/usuarios.xlsx"
ARQ_CLIENTES = f"{PASTA_DADOS}/clientes.xlsx"
ARQ_PRODUTOS = f"{PASTA_DADOS}/produtos.xlsx"
ARQ_PEDIDOS = f"{PASTA_DADOS}/pedidos.xlsx"

os.makedirs(PASTA_DADOS, exist_ok=True)

def criar_bancos():
    if not os.path.exists(ARQ_USUARIOS):
        usuarios = pd.DataFrame([
            {"usuario": "admin", "senha": "123", "nome": "Nelson", "tipo": "admin", "ativo": "sim"},
            {"usuario": "joao", "senha": "123", "nome": "João Vendedor", "tipo": "vendedor", "ativo": "sim"}
        ])
        usuarios.to_excel(ARQ_USUARIOS, index=False)

    if not os.path.exists(ARQ_CLIENTES):
        clientes = pd.DataFrame(columns=[
            "codigo", "nome", "cnpj", "telefone", "cidade",
            "vendedor", "status", "data_cadastro"
        ])
        clientes.to_excel(ARQ_CLIENTES, index=False)

    if not os.path.exists(ARQ_PRODUTOS):
        produtos = pd.DataFrame(columns=[
            "codigo", "produto", "preco", "status"
        ])
        produtos.to_excel(ARQ_PRODUTOS, index=False)

    if not os.path.exists(ARQ_PEDIDOS):
        pedidos = pd.DataFrame(columns=[
            "numero", "data", "vendedor", "cliente",
            "produto", "quantidade", "preco", "total"
        ])
        pedidos.to_excel(ARQ_PEDIDOS, index=False)

criar_bancos()

def carregar_excel(caminho):
    return pd.read_excel(caminho)

def salvar_excel(df, caminho):
    df.to_excel(caminho, index=False)

def login():
    st.title("🐯 Tigrão Distribuidora")
    st.subheader("Login do Sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        usuarios = carregar_excel(ARQ_USUARIOS)

        acesso = usuarios[
            (usuarios["usuario"].astype(str) == usuario) &
            (usuarios["senha"].astype(str) == senha) &
            (usuarios["ativo"].astype(str).str.lower() == "sim")
        ]

        if not acesso.empty:
            st.session_state["logado"] = True
            st.session_state["usuario"] = acesso.iloc[0]["usuario"]
            st.session_state["nome"] = acesso.iloc[0]["nome"]
            st.session_state["tipo"] = acesso.iloc[0]["tipo"]
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

def sair():
    st.session_state.clear()
    st.rerun()

def cadastro_clientes():
    st.header("👥 Cadastro de Clientes")

    usuarios = carregar_excel(ARQ_USUARIOS)
    vendedores = usuarios[usuarios["tipo"] == "vendedor"]["usuario"].tolist()

    with st.form("form_cliente"):
        nome = st.text_input("Nome do cliente")
        cnpj = st.text_input("CNPJ")
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")

        if st.session_state["tipo"] == "admin":
            vendedor = st.selectbox("Vendedor responsável", vendedores)
        else:
            vendedor = st.session_state["usuario"]
            st.info(f"Cliente será vinculado ao vendedor: {st.session_state['nome']}")

        salvar = st.form_submit_button("Salvar Cliente")

        if salvar:
            if nome.strip() == "":
                st.error("Informe o nome do cliente.")
                return

            clientes = carregar_excel(ARQ_CLIENTES)

            novo = {
                "codigo": len(clientes) + 1,
                "nome": nome,
                "cnpj": cnpj,
                "telefone": telefone,
                "cidade": cidade,
                "vendedor": vendedor,
                "status": "ativo",
                "data_cadastro": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            clientes = pd.concat([clientes, pd.DataFrame([novo])], ignore_index=True)
            salvar_excel(clientes, ARQ_CLIENTES)

            st.success("Cliente cadastrado com sucesso!")

def consultar_clientes():
    if st.session_state["tipo"] == "admin":
        st.header("🔎 Consultar Clientes")
    else:
        st.header("🔎 Meus Clientes")

    clientes = carregar_excel(ARQ_CLIENTES)

    if st.session_state["tipo"] != "admin":
        clientes = clientes[clientes["vendedor"].astype(str) == st.session_state["usuario"]]

    busca = st.text_input("Pesquisar por nome, CNPJ ou cidade")

    if busca:
        busca = busca.lower()
        clientes = clientes[
            clientes["nome"].astype(str).str.lower().str.contains(busca) |
            clientes["cnpj"].astype(str).str.lower().str.contains(busca) |
            clientes["cidade"].astype(str).str.lower().str.contains(busca)
        ]

    st.dataframe(clientes, use_container_width=True)

def cadastro_produtos():
    st.header("📦 Cadastro de Produtos")

    if st.session_state["tipo"] != "admin":
        st.error("Acesso bloqueado.")
        return

    with st.form("form_produto"):
        codigo = st.text_input("Código do produto")
        produto = st.text_input("Nome do produto")
        preco = st.number_input("Preço", min_value=0.0, step=0.01)

        salvar = st.form_submit_button("Salvar Produto")

        if salvar:
            if produto.strip() == "":
                st.error("Informe o nome do produto.")
                return

            produtos = carregar_excel(ARQ_PRODUTOS)

            novo = {
                "codigo": codigo,
                "produto": produto,
                "preco": preco,
                "status": "ativo"
            }

            produtos = pd.concat([produtos, pd.DataFrame([novo])], ignore_index=True)
            salvar_excel(produtos, ARQ_PRODUTOS)

            st.success("Produto cadastrado com sucesso!")

def novo_pedido():
    st.header("🛒 Novo Pedido")

    clientes = carregar_excel(ARQ_CLIENTES)
    produtos = carregar_excel(ARQ_PRODUTOS)

    if st.session_state["tipo"] != "admin":
        clientes = clientes[clientes["vendedor"].astype(str) == st.session_state["usuario"]]

    if clientes.empty:
        st.warning("Nenhum cliente disponível para este vendedor.")
        return

    if produtos.empty:
        st.warning("Nenhum produto cadastrado.")
        return

    busca_cliente = st.text_input("Pesquisar cliente")

    if busca_cliente:
        clientes_filtrados = clientes[
            clientes["nome"].astype(str).str.lower().str.contains(busca_cliente.lower())
        ]
    else:
        clientes_filtrados = clientes

    if clientes_filtrados.empty:
        st.warning("Nenhum cliente encontrado.")
        return

    cliente = st.selectbox("Cliente", clientes_filtrados["nome"].tolist())

    busca_produto = st.text_input("Pesquisar produto por nome ou código")

    if busca_produto:
        produtos_filtrados = produtos[
            produtos["produto"].astype(str).str.lower().str.contains(busca_produto.lower()) |
            produtos["codigo"].astype(str).str.lower().str.contains(busca_produto.lower())
        ]
    else:
        produtos_filtrados = produtos

    if produtos_filtrados.empty:
        st.warning("Nenhum produto encontrado.")
        return

    produto_nome = st.selectbox("Produto", produtos_filtrados["produto"].tolist())
    produto_linha = produtos[produtos["produto"] == produto_nome].iloc[0]

    preco = float(produto_linha["preco"])
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    total = preco * quantidade

    st.info(f"Preço: R$ {preco:.2f}")
    st.success(f"Total: R$ {total:.2f}")

    if st.button("Salvar Pedido"):
        pedidos = carregar_excel(ARQ_PEDIDOS)

        novo = {
            "numero": len(pedidos) + 1,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "vendedor": st.session_state["usuario"],
            "cliente": cliente,
            "produto": produto_nome,
            "quantidade": quantidade,
            "preco": preco,
            "total": total
        }

        pedidos = pd.concat([pedidos, pd.DataFrame([novo])], ignore_index=True)
        salvar_excel(pedidos, ARQ_PEDIDOS)

        st.success(f"Pedido nº {len(pedidos)} salvo com sucesso!")

def historico_pedidos():
    if st.session_state["tipo"] == "admin":
        st.header("📋 Histórico de Pedidos")
    else:
        st.header("📋 Meus Pedidos")

    pedidos = carregar_excel(ARQ_PEDIDOS)

    if st.session_state["tipo"] != "admin":
        pedidos = pedidos[pedidos["vendedor"].astype(str) == st.session_state["usuario"]]

    st.dataframe(pedidos, use_container_width=True)

def painel_admin():
    st.header("⚙️ Painel Administrativo")

    if st.session_state["tipo"] != "admin":
        st.error("Acesso bloqueado.")
        return

    clientes = carregar_excel(ARQ_CLIENTES)
    produtos = carregar_excel(ARQ_PRODUTOS)
    pedidos = carregar_excel(ARQ_PEDIDOS)
    usuarios = carregar_excel(ARQ_USUARIOS)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Clientes", len(clientes))
    col2.metric("Produtos", len(produtos))
    col3.metric("Pedidos", len(pedidos))
    col4.metric("Vendedores", len(usuarios[usuarios["tipo"] == "vendedor"]))

    st.subheader("Transferir Cliente de Vendedor")

    if not clientes.empty:
        cliente_nome = st.selectbox("Cliente", clientes["nome"].tolist())
        vendedores = usuarios[usuarios["tipo"] == "vendedor"]["usuario"].tolist()
        novo_vendedor = st.selectbox("Novo vendedor", vendedores)

        if st.button("Transferir Cliente"):
            clientes.loc[clientes["nome"] == cliente_nome, "vendedor"] = novo_vendedor
            salvar_excel(clientes, ARQ_CLIENTES)
            st.success("Cliente transferido com sucesso!")

# =========================
# APP PRINCIPAL
# =========================

if "logado" not in st.session_state:
    login()
else:
    st.sidebar.title("🐯 Tigrão")
    st.sidebar.write(f"Usuário: {st.session_state['nome']}")
    st.sidebar.write(f"Tipo: {st.session_state['tipo']}")
    st.sidebar.warning(f"Ambiente: {AMBIENTE}")

    if st.session_state["tipo"] == "admin":
        menu = st.sidebar.radio(
            "Menu",
            [
                "Painel Administrativo",
                "Novo Pedido",
                "Cadastrar Cliente",
                "Consultar Clientes",
                "Cadastrar Produto",
                "Histórico de Pedidos",
                "Sair"
            ]
        )
    else:
        menu = st.sidebar.radio(
            "Menu",
            [
                "Novo Pedido",
                "Cadastrar Cliente",
                "Meus Clientes",
                "Meus Pedidos",
                "Sair"
            ]
        )

    if menu == "Novo Pedido":
        novo_pedido()

    elif menu == "Cadastrar Cliente":
        cadastro_clientes()

    elif menu in ["Consultar Clientes", "Meus Clientes"]:
        consultar_clientes()

    elif menu == "Cadastrar Produto":
        cadastro_produtos()

    elif menu in ["Histórico de Pedidos", "Meus Pedidos"]:
        historico_pedidos()

    elif menu == "Painel Administrativo":
        painel_admin()

    elif menu == "Sair":
        sair()
