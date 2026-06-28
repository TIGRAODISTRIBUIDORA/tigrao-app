import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="Tigrão - Sistema DEV", page_icon="🐯", layout="wide")

AMBIENTE = "DESENVOLVIMENTO"
COMISSAO_PADRAO = 0.07

PASTA_DADOS = "dados_dev" if AMBIENTE == "DESENVOLVIMENTO" else "dados_producao"

ARQ_USUARIOS = f"{PASTA_DADOS}/usuarios.xlsx"
ARQ_CLIENTES = f"{PASTA_DADOS}/clientes.xlsx"
ARQ_PRODUTOS = f"{PASTA_DADOS}/produtos.xlsx"
ARQ_PEDIDOS = f"{PASTA_DADOS}/pedidos.xlsx"

os.makedirs(PASTA_DADOS, exist_ok=True)

def carregar_excel(caminho):
    return pd.read_excel(caminho)

def salvar_excel(df, caminho):
    df.to_excel(caminho, index=False)

def criar_bancos():
    if not os.path.exists(ARQ_USUARIOS):
        pd.DataFrame([
            {"usuario": "admin", "senha": "123", "nome": "Nelson", "tipo": "admin", "ativo": "sim"},
            {"usuario": "joao", "senha": "123", "nome": "João Vendedor", "tipo": "vendedor", "ativo": "sim"}
        ]).to_excel(ARQ_USUARIOS, index=False)

    if not os.path.exists(ARQ_CLIENTES):
        pd.DataFrame(columns=[
            "codigo", "nome", "cnpj", "telefone", "cidade",
            "vendedor", "status", "data_cadastro"
        ]).to_excel(ARQ_CLIENTES, index=False)

    if not os.path.exists(ARQ_PRODUTOS):
        pd.DataFrame(columns=[
            "codigo", "produto", "preco", "desconto_maximo", "status"
        ]).to_excel(ARQ_PRODUTOS, index=False)

    if not os.path.exists(ARQ_PEDIDOS):
        pd.DataFrame(columns=[
            "numero", "data", "vendedor", "cliente", "produto",
            "quantidade", "preco", "subtotal", "desconto_percentual",
            "valor_desconto", "total", "prazo_pagamento_dias", "comissao"
        ]).to_excel(ARQ_PEDIDOS, index=False)

criar_bancos()

def ajustar_bancos():
    produtos = carregar_excel(ARQ_PRODUTOS)

    if "desconto_maximo" not in produtos.columns:
        produtos["desconto_maximo"] = 0.0
    if "status" not in produtos.columns:
        produtos["status"] = "ativo"

    produtos["codigo"] = produtos["codigo"].astype(str)
    produtos["produto"] = produtos["produto"].astype(str)
    produtos["status"] = produtos["status"].astype(str)
    produtos["preco"] = pd.to_numeric(produtos["preco"], errors="coerce").fillna(0.0)
    produtos["desconto_maximo"] = pd.to_numeric(produtos["desconto_maximo"], errors="coerce").fillna(0.0)

    salvar_excel(produtos, ARQ_PRODUTOS)

    clientes = carregar_excel(ARQ_CLIENTES)

    if "status" not in clientes.columns:
        clientes["status"] = "ativo"

    salvar_excel(clientes, ARQ_CLIENTES)

    usuarios = carregar_excel(ARQ_USUARIOS)

    if "ativo" not in usuarios.columns:
        usuarios["ativo"] = "sim"

    salvar_excel(usuarios, ARQ_USUARIOS)

    pedidos = carregar_excel(ARQ_PEDIDOS)

    for coluna in ["subtotal", "desconto_percentual", "valor_desconto", "comissao"]:
        if coluna not in pedidos.columns:
            pedidos[coluna] = 0.0

    if "prazo_pagamento_dias" not in pedidos.columns:
        pedidos["prazo_pagamento_dias"] = 0

    if "total" in pedidos.columns:
        pedidos["total"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0.0)
        pedidos["comissao"] = pedidos["total"] * COMISSAO_PADRAO

    salvar_excel(pedidos, ARQ_PEDIDOS)

ajustar_bancos()

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
            st.error("Usuário ou senha inválidos, ou usuário inativo.")

def sair():
    st.session_state.clear()
    st.rerun()

def cadastro_clientes():
    st.header("👥 Cadastro de Clientes")

    usuarios = carregar_excel(ARQ_USUARIOS)
    vendedores = usuarios[
        (usuarios["tipo"] == "vendedor") &
        (usuarios["ativo"].astype(str).str.lower() == "sim")
    ]["usuario"].tolist()

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
    st.header("🔎 Consultar Clientes" if st.session_state["tipo"] == "admin" else "🔎 Meus Clientes")

    clientes = carregar_excel(ARQ_CLIENTES)

    if st.session_state["tipo"] != "admin":
        clientes = clientes[
            (clientes["vendedor"].astype(str) == st.session_state["usuario"]) &
            (clientes["status"].astype(str).str.lower() == "ativo")
        ]

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

        desconto_maximo = st.number_input(
            "Desconto máximo permitido (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.5
        )

        salvar = st.form_submit_button("Salvar Produto")

        if salvar:
            produtos = carregar_excel(ARQ_PRODUTOS)
            produtos["codigo"] = produtos["codigo"].astype(str)

            codigo_limpo = str(codigo).strip()
            produto_limpo = str(produto).strip()

            if codigo_limpo == "":
                st.error("Informe o código do produto.")
                return

            if produto_limpo == "":
                st.error("Informe o nome do produto.")
                return

            codigo_existe = produtos["codigo"].astype(str).str.strip().eq(codigo_limpo).any()

            if codigo_existe:
                st.error("Já existe um produto cadastrado com esse código.")
                return

            novo = {
                "codigo": codigo_limpo,
                "produto": produto_limpo,
                "preco": float(preco),
                "desconto_maximo": float(desconto_maximo),
                "status": "ativo"
            }

            produtos = pd.concat([produtos, pd.DataFrame([novo])], ignore_index=True)
            salvar_excel(produtos, ARQ_PRODUTOS)
            st.success("Produto cadastrado com sucesso!")

def consultar_produtos():
    st.header("🔎 Consultar Produtos")

    produtos = carregar_excel(ARQ_PRODUTOS)

    if st.session_state["tipo"] != "admin":
        produtos = produtos[produtos["status"].astype(str).str.lower() == "ativo"]

    if produtos.empty:
        st.warning("Nenhum produto cadastrado.")
        return

    busca = st.text_input("Pesquisar por nome ou código")

    if busca:
        busca = busca.lower()
        produtos = produtos[
            produtos["produto"].astype(str).str.lower().str.contains(busca) |
            produtos["codigo"].astype(str).str.lower().str.contains(busca)
        ]

    produtos_exibir = produtos[["codigo", "produto", "preco", "desconto_maximo", "status"]].copy()
    produtos_exibir["preco"] = pd.to_numeric(produtos_exibir["preco"], errors="coerce").fillna(0.0)
    produtos_exibir["desconto_maximo"] = pd.to_numeric(produtos_exibir["desconto_maximo"], errors="coerce").fillna(0.0)

    produtos_exibir["preco"] = produtos_exibir["preco"].apply(lambda x: f"R$ {x:.2f}")
    produtos_exibir["desconto_maximo"] = produtos_exibir["desconto_maximo"].apply(lambda x: f"{x:.1f}%")

    st.dataframe(produtos_exibir, use_container_width=True)

def editar_produtos():
    st.header("✏️ Editar Produto")

    if st.session_state["tipo"] != "admin":
        st.error("Acesso bloqueado.")
        return

    produtos = carregar_excel(ARQ_PRODUTOS)

    if produtos.empty:
        st.warning("Nenhum produto cadastrado.")
        return

    produtos["codigo"] = produtos["codigo"].astype(str)
    produtos["produto"] = produtos["produto"].astype(str)
    produtos["status"] = produtos["status"].astype(str)
    produtos["preco"] = pd.to_numeric(produtos["preco"], errors="coerce").fillna(0.0)
    produtos["desconto_maximo"] = pd.to_numeric(produtos["desconto_maximo"], errors="coerce").fillna(0.0)

    busca = st.text_input("Pesquisar produto para editar por nome ou código")

    produtos_filtrados = produtos.copy()

    if busca:
        busca = busca.lower()
        produtos_filtrados = produtos[
            produtos["produto"].astype(str).str.lower().str.contains(busca) |
            produtos["codigo"].astype(str).str.lower().str.contains(busca)
        ]

    if produtos_filtrados.empty:
        st.warning("Nenhum produto encontrado.")
        return

    escolha = st.selectbox(
        "Selecione o produto",
        produtos_filtrados.index.tolist(),
        format_func=lambda i: f"{produtos.loc[i, 'codigo']} - {produtos.loc[i, 'produto']} - desconto: {produtos.loc[i, 'desconto_maximo']}%"
    )

    linha = produtos.loc[escolha]

    with st.form("form_editar_produto"):
        novo_codigo = st.text_input("Código do produto", value=str(linha["codigo"]))
        novo_produto = st.text_input("Nome do produto", value=str(linha["produto"]))

        novo_preco = st.number_input(
            "Preço",
            min_value=0.0,
            max_value=999999.0,
            step=0.01,
            value=float(linha["preco"])
        )

        novo_desconto = st.number_input(
            "Desconto máximo permitido (%)",
            min_value=0.0,
            max_value=100.0,
            step=0.5,
            value=float(linha["desconto_maximo"])
        )

        status_atual = str(linha["status"]).lower()
        status_index = 0 if status_atual == "ativo" else 1
        novo_status = st.selectbox("Status", ["ativo", "inativo"], index=status_index)

        salvar = st.form_submit_button("Salvar Alterações")

        if salvar:
            codigo_limpo = str(novo_codigo).strip()
            produto_limpo = str(novo_produto).strip()

            if codigo_limpo == "":
                st.error("O código do produto não pode ficar vazio.")
                return

            if produto_limpo == "":
                st.error("O nome do produto não pode ficar vazio.")
                return

            outros_produtos = produtos.drop(index=escolha)
            codigo_existe = outros_produtos["codigo"].astype(str).str.strip().eq(codigo_limpo).any()

            if codigo_existe:
                st.error("Já existe outro produto com esse código.")
                return

            produtos.at[escolha, "codigo"] = str(codigo_limpo)
            produtos.at[escolha, "produto"] = str(produto_limpo)
            produtos.at[escolha, "preco"] = float(novo_preco)
            produtos.at[escolha, "desconto_maximo"] = float(novo_desconto)
            produtos.at[escolha, "status"] = str(novo_status)

            salvar_excel(produtos, ARQ_PRODUTOS)
            st.success(f"Produto atualizado! Desconto salvo: {novo_desconto:.1f}%")
            st.rerun()

def gerenciar_status():
    st.header("🔒 Gerenciar Status")

    if st.session_state["tipo"] != "admin":
        st.error("Acesso bloqueado.")
        return

    opcao = st.selectbox("O que deseja gerenciar?", ["Produto", "Cliente", "Vendedor"])

    if opcao == "Produto":
        produtos = carregar_excel(ARQ_PRODUTOS)

        item = st.selectbox(
            "Selecione o produto",
            produtos.index.tolist(),
            format_func=lambda i: f"{produtos.loc[i, 'codigo']} - {produtos.loc[i, 'produto']} - {produtos.loc[i, 'status']}"
        )

        novo_status = st.selectbox("Novo status", ["ativo", "inativo"])

        if st.button("Salvar status do produto"):
            produtos.at[item, "status"] = novo_status
            salvar_excel(produtos, ARQ_PRODUTOS)
            st.success("Status do produto atualizado com sucesso!")
            st.rerun()

    elif opcao == "Cliente":
        clientes = carregar_excel(ARQ_CLIENTES)

        item = st.selectbox(
            "Selecione o cliente",
            clientes.index.tolist(),
            format_func=lambda i: f"{clientes.loc[i, 'codigo']} - {clientes.loc[i, 'nome']} - {clientes.loc[i, 'status']}"
        )

        novo_status = st.selectbox("Novo status", ["ativo", "inativo"])

        if st.button("Salvar status do cliente"):
            clientes.at[item, "status"] = novo_status
            salvar_excel(clientes, ARQ_CLIENTES)
            st.success("Status do cliente atualizado com sucesso!")
            st.rerun()

    elif opcao == "Vendedor":
        usuarios = carregar_excel(ARQ_USUARIOS)
        vendedores = usuarios[usuarios["tipo"] == "vendedor"]

        item = st.selectbox(
            "Selecione o vendedor",
            vendedores.index.tolist(),
            format_func=lambda i: f"{usuarios.loc[i, 'usuario']} - {usuarios.loc[i, 'nome']} - {usuarios.loc[i, 'ativo']}"
        )

        novo_status = st.selectbox("Novo status", ["sim", "nao"])

        if st.button("Salvar status do vendedor"):
            usuarios.at[item, "ativo"] = novo_status
            salvar_excel(usuarios, ARQ_USUARIOS)
            st.success("Status do vendedor atualizado com sucesso!")
            st.rerun()

def ferramentas_excel_pedidos():
    st.subheader("📥 Importar / Exportar Pedidos em Excel")

    pedidos = carregar_excel(ARQ_PEDIDOS)

    buffer = BytesIO()
    pedidos.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    st.download_button(
        label="📤 Exportar pedidos para Excel",
        data=buffer,
        file_name="pedidos_tigrao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    arquivo = st.file_uploader("📥 Importar planilha de pedidos", type=["xlsx"])

    if arquivo is not None:
        novos_pedidos = pd.read_excel(arquivo)

        st.write("Pré-visualização da planilha importada:")
        st.dataframe(novos_pedidos, use_container_width=True)

        if st.button("Confirmar importação"):
            pedidos_atual = carregar_excel(ARQ_PEDIDOS)

            for coluna in pedidos_atual.columns:
                if coluna not in novos_pedidos.columns:
                    novos_pedidos[coluna] = ""

            novos_pedidos = novos_pedidos[pedidos_atual.columns]

            pedidos_final = pd.concat([pedidos_atual, novos_pedidos], ignore_index=True)
            salvar_excel(pedidos_final, ARQ_PEDIDOS)

            st.success("Pedidos importados com sucesso!")
            st.rerun()

def novo_pedido():
    st.header("🛒 Novo Pedido")

    clientes = carregar_excel(ARQ_CLIENTES)
    produtos = carregar_excel(ARQ_PRODUTOS)

    clientes = clientes[clientes["status"].astype(str).str.lower() == "ativo"]
    produtos = produtos[produtos["status"].astype(str).str.lower() == "ativo"]

    if st.session_state["tipo"] != "admin":
        clientes = clientes[clientes["vendedor"].astype(str) == st.session_state["usuario"]]

    if clientes.empty:
        st.warning("Nenhum cliente ativo disponível para este vendedor.")
        return

    if produtos.empty:
        st.warning("Nenhum produto ativo cadastrado.")
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
    desconto_maximo = float(produto_linha.get("desconto_maximo", 0))

    quantidade = st.number_input("Quantidade", min_value=1, step=1)

    subtotal = preco * quantidade

    desconto_percentual = st.number_input(
        f"Desconto (%) - máximo permitido: {desconto_maximo:.1f}%",
        min_value=0.0,
        max_value=desconto_maximo,
        step=0.5
    )

    prazo_pagamento_dias = st.number_input(
        "Prazo de pagamento (dias)",
        min_value=0,
        max_value=365,
        value=0,
        step=1
    )

    valor_desconto = subtotal * (desconto_percentual / 100)
    total = subtotal - valor_desconto
    comissao = total * COMISSAO_PADRAO

    st.info(f"Preço unitário: R$ {preco:.2f}")
    st.info(f"Subtotal: R$ {subtotal:.2f}")
    st.warning(f"Valor do desconto: R$ {valor_desconto:.2f}")
    st.success(f"Total do pedido: R$ {total:.2f}")
    st.info(f"Prazo de pagamento: {prazo_pagamento_dias} dias")
    st.warning(f"Comissão do vendedor: R$ {comissao:.2f}")

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
            "subtotal": subtotal,
            "desconto_percentual": desconto_percentual,
            "valor_desconto": valor_desconto,
            "total": total,
            "prazo_pagamento_dias": int(prazo_pagamento_dias),
            "comissao": comissao
        }

        pedidos = pd.concat([pedidos, pd.DataFrame([novo])], ignore_index=True)
        salvar_excel(pedidos, ARQ_PEDIDOS)

        st.success(f"Pedido nº {len(pedidos)} salvo com sucesso!")

def historico_pedidos():
    st.header("📋 Histórico de Pedidos" if st.session_state["tipo"] == "admin" else "📋 Meus Pedidos")

    pedidos = carregar_excel(ARQ_PEDIDOS)

    if st.session_state["tipo"] != "admin":
        pedidos = pedidos[pedidos["vendedor"].astype(str) == st.session_state["usuario"]]

    st.dataframe(pedidos, use_container_width=True)

def comissoes():
    st.header("💰 Comissão dos Vendedores" if st.session_state["tipo"] == "admin" else "💰 Minha Comissão")

    pedidos = carregar_excel(ARQ_PEDIDOS)

    if pedidos.empty:
        st.warning("Nenhum pedido lançado.")
        return

    if st.session_state["tipo"] != "admin":
        pedidos = pedidos[pedidos["vendedor"].astype(str) == st.session_state["usuario"]]

    if pedidos.empty:
        st.warning("Nenhum pedido encontrado.")
        return

    total_vendas = pedidos["total"].fillna(0).astype(float).sum()
    total_comissao = pedidos["comissao"].fillna(0).astype(float).sum()

    col1, col2 = st.columns(2)
    col1.metric("Total vendido", f"R$ {total_vendas:,.2f}")
    col2.metric("Comissão 7%", f"R$ {total_comissao:,.2f}")

    resumo = pedidos.groupby("vendedor", as_index=False).agg({
        "total": "sum",
        "comissao": "sum"
    })

    st.dataframe(resumo, use_container_width=True)

    st.subheader("Pedidos com comissão")
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

    total_vendido = pedidos["total"].fillna(0).astype(float).sum() if not pedidos.empty else 0
    total_comissao = pedidos["comissao"].fillna(0).astype(float).sum() if not pedidos.empty else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Clientes", len(clientes))
    col2.metric("Produtos", len(produtos))
    col3.metric("Pedidos", len(pedidos))
    col4.metric("Vendedores", len(usuarios[usuarios["tipo"] == "vendedor"]))
    col5.metric("Comissões", f"R$ {total_comissao:,.2f}")

    st.success(f"Total vendido: R$ {total_vendido:,.2f}")

    ferramentas_excel_pedidos()

    st.subheader("Transferir Cliente de Vendedor")

    if not clientes.empty:
        cliente_nome = st.selectbox("Cliente", clientes["nome"].tolist())
        vendedores = usuarios[
            (usuarios["tipo"] == "vendedor") &
            (usuarios["ativo"].astype(str).str.lower() == "sim")
        ]["usuario"].tolist()

        novo_vendedor = st.selectbox("Novo vendedor", vendedores)

        if st.button("Transferir Cliente"):
            clientes.loc[clientes["nome"] == cliente_nome, "vendedor"] = novo_vendedor
            salvar_excel(clientes, ARQ_CLIENTES)
            st.success("Cliente transferido com sucesso!")

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
                "Consultar Produto",
                "Editar Produto",
                "Gerenciar Status",
                "Histórico de Pedidos",
                "Comissões",
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
                "Consultar Produto",
                "Meus Pedidos",
                "Minha Comissão",
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
    elif menu == "Consultar Produto":
        consultar_produtos()
    elif menu == "Editar Produto":
        editar_produtos()
    elif menu == "Gerenciar Status":
        gerenciar_status()
    elif menu in ["Histórico de Pedidos", "Meus Pedidos"]:
        historico_pedidos()
    elif menu in ["Comissões", "Minha Comissão"]:
        comissoes()
    elif menu == "Painel Administrativo":
        painel_admin()
    elif menu == "Sair":
        sair()
