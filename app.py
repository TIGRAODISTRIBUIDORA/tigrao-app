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
            {
                "usuario": "admin",
                "senha": "123",
                "nome": "Nelson",
                "tipo": "admin",
                "telefone": "",
                "email": "",
                "comissao_percentual": 0.0,
                "meta_mensal": 0.0,
                "ativo": "sim"
            },
            {
                "usuario": "joao",
                "senha": "123",
                "nome": "João Vendedor",
                "tipo": "vendedor",
                "telefone": "",
                "email": "",
                "comissao_percentual": 7.0,
                "meta_mensal": 0.0,
                "ativo": "sim"
            }
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

    colunas_usuarios = {
        "telefone": "",
        "email": "",
        "comissao_percentual": 7.0,
        "meta_mensal": 0.0,
        "ativo": "sim"
    }

    for coluna, valor in colunas_usuarios.items():
        if coluna not in usuarios.columns:
            usuarios[coluna] = valor

    usuarios["usuario"] = usuarios["usuario"].astype(str)
    usuarios["senha"] = usuarios["senha"].astype(str)
    usuarios["nome"] = usuarios["nome"].astype(str)
    usuarios["tipo"] = usuarios["tipo"].astype(str)
    usuarios["telefone"] = usuarios["telefone"].astype(str)
    usuarios["email"] = usuarios["email"].astype(str)
    usuarios["ativo"] = usuarios["ativo"].astype(str)
    usuarios["comissao_percentual"] = pd.to_numeric(usuarios["comissao_percentual"], errors="coerce").fillna(7.0)
    usuarios["meta_mensal"] = pd.to_numeric(usuarios["meta_mensal"], errors="coerce").fillna(0.0)

    usuarios.loc[usuarios["tipo"].str.lower() == "admin", "comissao_percentual"] = 0.0

    salvar_excel(usuarios, ARQ_USUARIOS)

    pedidos = carregar_excel(ARQ_PEDIDOS)

    for coluna in ["subtotal", "desconto_percentual", "valor_desconto", "comissao"]:
        if coluna not in pedidos.columns:
            pedidos[coluna] = 0.0

    if "prazo_pagamento_dias" not in pedidos.columns:
        pedidos["prazo_pagamento_dias"] = 0

    if "total" in pedidos.columns:
        pedidos["total"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0.0)
        pedidos["comissao"] = pd.to_numeric(pedidos["comissao"], errors="coerce").fillna(pedidos["total"] * COMISSAO_PADRAO)

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

def obter_comissao_vendedor(usuario):
    usuarios = carregar_excel(ARQ_USUARIOS)
    linha = usuarios[usuarios["usuario"].astype(str) == str(usuario)]

    if linha.empty:
        return COMISSAO_PADRAO

    percentual = pd.to_numeric(linha.iloc[0].get("comissao_percentual", 7.0), errors="coerce")

    if pd.isna(percentual):
        percentual = 7.0

    return float(percentual) / 100

def cadastro_clientes():
    st.header("👥 Cadastro de Clientes")

    usuarios = carregar_excel(ARQ_USUARIOS)
    vendedores = usuarios[
        (usuarios["tipo"].astype(str) == "vendedor") &
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
                "nome": nome.strip(),
                "cnpj": cnpj.strip(),
                "telefone": telefone.strip(),
                "cidade": cidade.strip(),
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
    st.header("📦 Produtos")

    if st.session_state["tipo"] != "admin":
        st.error("Acesso bloqueado.")
        return

    aba = st.radio(
        "Escolha uma opção",
        ["Cadastrar manualmente", "Importar produtos por Excel", "Exportar produtos para Excel"],
        horizontal=True
    )

    if aba == "Cadastrar manualmente":
        st.subheader("➕ Cadastrar produto manualmente")

        with st.form("form_produto"):
            codigo = st.text_input("Código do produto")
            produto = st.text_input("Nome do produto")
            preco = st.number_input("Preço", min_value=0.0, step=0.01)

            desconto_maximo = st.number_input(
                "Desconto máximo permitido (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.5
            )

            salvar = st.form_submit_button("Salvar Produto")

            if salvar:
                produtos = carregar_excel(ARQ_PRODUTOS)
                produtos["codigo"] = produtos["codigo"].astype(str).str.strip()

                codigo_limpo = str(codigo).strip()
                produto_limpo = str(produto).strip()

                if codigo_limpo == "":
                    st.error("Informe o código do produto.")
                    return

                if produto_limpo == "":
                    st.error("Informe o nome do produto.")
                    return

                if produtos["codigo"].eq(codigo_limpo).any():
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

    elif aba == "Importar produtos por Excel":
        st.subheader("📥 Importar cadastro de produtos por Excel")

        st.info("A planilha deve ter pelo menos estas colunas: codigo, produto, preco. As colunas desconto_maximo e status são opcionais.")

        modelo = pd.DataFrame([
            {
                "codigo": "001",
                "produto": "CHÁ CAMOMILA TIGRÃO",
                "preco": 3.50,
                "desconto_maximo": 10,
                "status": "ativo"
            },
            {
                "codigo": "002",
                "produto": "CHÁ BOLDO TIGRÃO",
                "preco": 3.50,
                "desconto_maximo": 10,
                "status": "ativo"
            }
        ])

        buffer_modelo = BytesIO()
        modelo.to_excel(buffer_modelo, index=False, engine="openpyxl")
        buffer_modelo.seek(0)

        st.download_button(
            label="📄 Baixar modelo de importação de produtos",
            data=buffer_modelo,
            file_name="modelo_importar_produtos_tigrao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        arquivo = st.file_uploader(
            "Selecione a planilha Excel com os produtos",
            type=["xlsx"],
            key="upload_produtos_excel"
        )

        if arquivo is not None:
            try:
                novos_produtos = pd.read_excel(arquivo)
            except Exception as erro:
                st.error(f"Erro ao ler a planilha: {erro}")
                return

            st.write("Pré-visualização da planilha:")
            st.dataframe(novos_produtos, use_container_width=True)

            if st.button("✅ Confirmar importação e cadastrar produtos no sistema"):
                colunas_obrigatorias = ["codigo", "produto", "preco"]

                for coluna in colunas_obrigatorias:
                    if coluna not in novos_produtos.columns:
                        st.error(f"A planilha precisa ter a coluna obrigatória: {coluna}")
                        return

                produtos_atual = carregar_excel(ARQ_PRODUTOS)

                for coluna in ["codigo", "produto", "preco", "desconto_maximo", "status"]:
                    if coluna not in produtos_atual.columns:
                        if coluna == "desconto_maximo":
                            produtos_atual[coluna] = 0.0
                        elif coluna == "status":
                            produtos_atual[coluna] = "ativo"
                        else:
                            produtos_atual[coluna] = ""

                produtos_atual["codigo"] = produtos_atual["codigo"].astype(str).str.strip()

                if "desconto_maximo" not in novos_produtos.columns:
                    novos_produtos["desconto_maximo"] = 0.0

                if "status" not in novos_produtos.columns:
                    novos_produtos["status"] = "ativo"

                novos_produtos = novos_produtos[["codigo", "produto", "preco", "desconto_maximo", "status"]].copy()

                novos_produtos["codigo"] = novos_produtos["codigo"].astype(str).str.strip()
                novos_produtos["produto"] = novos_produtos["produto"].astype(str).str.strip()
                novos_produtos["preco"] = pd.to_numeric(novos_produtos["preco"], errors="coerce").fillna(0.0)
                novos_produtos["desconto_maximo"] = pd.to_numeric(novos_produtos["desconto_maximo"], errors="coerce").fillna(0.0)
                novos_produtos["status"] = novos_produtos["status"].astype(str).str.lower().str.strip()

                novos_produtos.loc[~novos_produtos["status"].isin(["ativo", "inativo"]), "status"] = "ativo"

                novos_produtos = novos_produtos[
                    (novos_produtos["codigo"] != "") &
                    (novos_produtos["codigo"].str.lower() != "nan") &
                    (novos_produtos["produto"] != "") &
                    (novos_produtos["produto"].str.lower() != "nan")
                ]

                qtd_linhas_validas = len(novos_produtos)

                novos_produtos = novos_produtos.drop_duplicates(subset=["codigo"], keep="first")

                codigos_existentes = set(produtos_atual["codigo"].astype(str).str.strip())
                produtos_para_importar = novos_produtos[
                    ~novos_produtos["codigo"].astype(str).str.strip().isin(codigos_existentes)
                ]

                ignorados = qtd_linhas_validas - len(produtos_para_importar)

                produtos_final = pd.concat(
                    [produtos_atual, produtos_para_importar],
                    ignore_index=True
                )

                produtos_final = produtos_final[["codigo", "produto", "preco", "desconto_maximo", "status"]]

                salvar_excel(produtos_final, ARQ_PRODUTOS)

                st.success(f"Importação concluída! Produtos cadastrados no sistema: {len(produtos_para_importar)}")

                if ignorados > 0:
                    st.warning(f"Produtos ignorados por código duplicado, vazio ou inválido: {ignorados}")

                st.rerun()

    elif aba == "Exportar produtos para Excel":
        st.subheader("📤 Exportar produtos para Excel")

        produtos = carregar_excel(ARQ_PRODUTOS)

        buffer = BytesIO()
        produtos.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="📤 Baixar produtos cadastrados",
            data=buffer,
            file_name="produtos_tigrao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


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

def gerenciar_vendedores():
    st.header("👨‍💼 Gerenciar Vendedores")

    if st.session_state["tipo"] != "admin":
        st.error("Acesso bloqueado.")
        return

    usuarios = carregar_excel(ARQ_USUARIOS)

    aba = st.radio(
        "Escolha uma opção",
        ["Cadastrar vendedor", "Editar vendedor", "Resumo dos vendedores"],
        horizontal=True
    )

    if aba == "Cadastrar vendedor":
        st.subheader("➕ Cadastrar novo vendedor")

        with st.form("form_cadastrar_vendedor"):
            nome = st.text_input("Nome do vendedor")
            usuario = st.text_input("Usuário de login")
            senha = st.text_input("Senha", type="password")
            telefone = st.text_input("Telefone")
            email = st.text_input("E-mail")
            comissao_percentual = st.number_input("Comissão (%)", min_value=0.0, max_value=100.0, value=7.0, step=0.5)
            meta_mensal = st.number_input("Meta mensal (R$)", min_value=0.0, step=100.0)
            ativo = st.selectbox("Status", ["sim", "nao"])

            salvar = st.form_submit_button("Salvar vendedor")

            if salvar:
                usuario_limpo = str(usuario).strip()
                nome_limpo = str(nome).strip()

                if nome_limpo == "":
                    st.error("Informe o nome do vendedor.")
                    return

                if usuario_limpo == "":
                    st.error("Informe o usuário de login.")
                    return

                if str(senha).strip() == "":
                    st.error("Informe a senha.")
                    return

                if usuarios["usuario"].astype(str).str.strip().eq(usuario_limpo).any():
                    st.error("Já existe um usuário com esse login.")
                    return

                novo = {
                    "usuario": usuario_limpo,
                    "senha": str(senha).strip(),
                    "nome": nome_limpo,
                    "tipo": "vendedor",
                    "telefone": str(telefone).strip(),
                    "email": str(email).strip(),
                    "comissao_percentual": float(comissao_percentual),
                    "meta_mensal": float(meta_mensal),
                    "ativo": ativo
                }

                usuarios = pd.concat([usuarios, pd.DataFrame([novo])], ignore_index=True)
                salvar_excel(usuarios, ARQ_USUARIOS)
                st.success("Vendedor cadastrado com sucesso!")
                st.rerun()

    elif aba == "Editar vendedor":
        st.subheader("✏️ Editar vendedor")

        vendedores = usuarios[usuarios["tipo"].astype(str) == "vendedor"]

        if vendedores.empty:
            st.warning("Nenhum vendedor cadastrado.")
            return

        busca = st.text_input("Pesquisar vendedor por nome ou usuário")

        vendedores_filtrados = vendedores.copy()

        if busca:
            busca = busca.lower()
            vendedores_filtrados = vendedores[
                vendedores["nome"].astype(str).str.lower().str.contains(busca) |
                vendedores["usuario"].astype(str).str.lower().str.contains(busca)
            ]

        if vendedores_filtrados.empty:
            st.warning("Nenhum vendedor encontrado.")
            return

        escolha = st.selectbox(
            "Selecione o vendedor",
            vendedores_filtrados.index.tolist(),
            format_func=lambda i: f"{usuarios.loc[i, 'usuario']} - {usuarios.loc[i, 'nome']} - {usuarios.loc[i, 'ativo']}"
        )

        linha = usuarios.loc[escolha]

        with st.form("form_editar_vendedor"):
            novo_usuario = st.text_input("Usuário de login", value=str(linha["usuario"]))
            novo_nome = st.text_input("Nome", value=str(linha["nome"]))
            nova_senha = st.text_input("Senha", value=str(linha["senha"]))
            novo_telefone = st.text_input("Telefone", value=str(linha.get("telefone", "")))
            novo_email = st.text_input("E-mail", value=str(linha.get("email", "")))
            nova_comissao = st.number_input(
                "Comissão (%)",
                min_value=0.0,
                max_value=100.0,
                value=float(linha.get("comissao_percentual", 7.0)),
                step=0.5
            )
            nova_meta = st.number_input(
                "Meta mensal (R$)",
                min_value=0.0,
                value=float(linha.get("meta_mensal", 0.0)),
                step=100.0
            )

            ativo_atual = str(linha.get("ativo", "sim")).lower()
            ativo_index = 0 if ativo_atual == "sim" else 1
            novo_ativo = st.selectbox("Status", ["sim", "nao"], index=ativo_index)

            salvar = st.form_submit_button("Salvar alterações")

            if salvar:
                usuario_limpo = str(novo_usuario).strip()
                nome_limpo = str(novo_nome).strip()

                if usuario_limpo == "":
                    st.error("O usuário não pode ficar vazio.")
                    return

                if nome_limpo == "":
                    st.error("O nome não pode ficar vazio.")
                    return

                outros = usuarios.drop(index=escolha)
                usuario_existe = outros["usuario"].astype(str).str.strip().eq(usuario_limpo).any()

                if usuario_existe:
                    st.error("Já existe outro vendedor com esse usuário.")
                    return

                usuario_antigo = str(usuarios.loc[escolha, "usuario"])

                usuarios.at[escolha, "usuario"] = usuario_limpo
                usuarios.at[escolha, "senha"] = str(nova_senha).strip()
                usuarios.at[escolha, "nome"] = nome_limpo
                usuarios.at[escolha, "tipo"] = "vendedor"
                usuarios.at[escolha, "telefone"] = str(novo_telefone).strip()
                usuarios.at[escolha, "email"] = str(novo_email).strip()
                usuarios.at[escolha, "comissao_percentual"] = float(nova_comissao)
                usuarios.at[escolha, "meta_mensal"] = float(nova_meta)
                usuarios.at[escolha, "ativo"] = novo_ativo

                salvar_excel(usuarios, ARQ_USUARIOS)

                if usuario_antigo != usuario_limpo:
                    clientes = carregar_excel(ARQ_CLIENTES)
                    pedidos = carregar_excel(ARQ_PEDIDOS)

                    clientes.loc[clientes["vendedor"].astype(str) == usuario_antigo, "vendedor"] = usuario_limpo
                    pedidos.loc[pedidos["vendedor"].astype(str) == usuario_antigo, "vendedor"] = usuario_limpo

                    salvar_excel(clientes, ARQ_CLIENTES)
                    salvar_excel(pedidos, ARQ_PEDIDOS)

                st.success("Vendedor atualizado com sucesso!")
                st.rerun()

    elif aba == "Resumo dos vendedores":
        st.subheader("📊 Resumo dos vendedores")

        vendedores = usuarios[usuarios["tipo"].astype(str) == "vendedor"].copy()
        clientes = carregar_excel(ARQ_CLIENTES)
        pedidos = carregar_excel(ARQ_PEDIDOS)

        if vendedores.empty:
            st.warning("Nenhum vendedor cadastrado.")
            return

        resumo = []

        for _, vendedor in vendedores.iterrows():
            usuario_vendedor = str(vendedor["usuario"])

            clientes_vendedor = clientes[clientes["vendedor"].astype(str) == usuario_vendedor]
            pedidos_vendedor = pedidos[pedidos["vendedor"].astype(str) == usuario_vendedor]

            total_vendido = pd.to_numeric(pedidos_vendedor.get("total", 0), errors="coerce").fillna(0).sum() if not pedidos_vendedor.empty else 0
            total_comissao = pd.to_numeric(pedidos_vendedor.get("comissao", 0), errors="coerce").fillna(0).sum() if not pedidos_vendedor.empty else 0
            meta = float(vendedor.get("meta_mensal", 0.0))
            atingimento = (total_vendido / meta * 100) if meta > 0 else 0

            resumo.append({
                "usuario": usuario_vendedor,
                "nome": vendedor["nome"],
                "status": vendedor["ativo"],
                "comissao_%": vendedor.get("comissao_percentual", 7.0),
                "meta_mensal": meta,
                "clientes": len(clientes_vendedor),
                "pedidos": len(pedidos_vendedor),
                "total_vendido": total_vendido,
                "comissao_acumulada": total_comissao,
                "atingimento_meta_%": atingimento
            })

        resumo_df = pd.DataFrame(resumo)
        st.dataframe(resumo_df, use_container_width=True)

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
        vendedores = usuarios[usuarios["tipo"].astype(str) == "vendedor"]

        if vendedores.empty:
            st.warning("Nenhum vendedor cadastrado.")
            return

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

    prazo_pagamento_dias = st.text_input(
    "Prazo de pagamento (dias) - Ex: 28 ou 28/56/84/112",
    value="0"
)


    valor_desconto = subtotal * (desconto_percentual / 100)
    total = subtotal - valor_desconto
    percentual_comissao_vendedor = obter_comissao_vendedor(st.session_state["usuario"])
    comissao = total * percentual_comissao_vendedor

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
    col2.metric("Comissão", f"R$ {total_comissao:,.2f}")

    resumo = pedidos.groupby("vendedor", as_index=False).agg({
        "total": "sum",
        "comissao": "sum"
    })

    st.dataframe(resumo, use_container_width=True)

    st.subheader("Pedidos com comissão")
    st.dataframe(pedidos, use_container_width=True)


def limpar_pedidos_invalidos():
    st.subheader("🧹 Limpar Pedidos Inválidos")

    pedidos = carregar_excel(ARQ_PEDIDOS)

    if pedidos.empty:
        st.info("Não há pedidos para limpar.")
        return

    total_antes = len(pedidos)

    colunas_chave = ["numero", "vendedor", "cliente", "produto", "quantidade", "preco", "total"]

    for coluna in colunas_chave:
        if coluna not in pedidos.columns:
            pedidos[coluna] = ""

    pedidos_limpos = pedidos.copy()

    pedidos_limpos = pedidos_limpos[
        pedidos_limpos["cliente"].notna() &
        pedidos_limpos["produto"].notna() &
        pedidos_limpos["vendedor"].notna()
    ]

    pedidos_limpos = pedidos_limpos[
        (pedidos_limpos["cliente"].astype(str).str.lower() != "none") &
        (pedidos_limpos["produto"].astype(str).str.lower() != "none") &
        (pedidos_limpos["vendedor"].astype(str).str.lower() != "none") &
        (pedidos_limpos["cliente"].astype(str).str.strip() != "") &
        (pedidos_limpos["produto"].astype(str).str.strip() != "") &
        (pedidos_limpos["vendedor"].astype(str).str.strip() != "")
    ]

    removidos = total_antes - len(pedidos_limpos)

    st.warning(f"Registros inválidos encontrados: {removidos}")

    if removidos > 0:
        if st.button("🧹 Confirmar limpeza do histórico"):
            salvar_excel(pedidos_limpos, ARQ_PEDIDOS)
            st.success(f"Histórico limpo com sucesso! Registros removidos: {removidos}")
            st.rerun()
    else:
        st.success("Nenhum registro inválido encontrado.")


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
    col4.metric("Vendedores", len(usuarios[usuarios["tipo"].astype(str) == "vendedor"]))
    col5.metric("Comissões", f"R$ {total_comissao:,.2f}")

    st.success(f"Total vendido: R$ {total_vendido:,.2f}")

    ferramentas_excel_pedidos()

    limpar_pedidos_invalidos()

    st.subheader("Transferir Cliente de Vendedor")

    if not clientes.empty:
        cliente_nome = st.selectbox("Cliente", clientes["nome"].tolist())
        vendedores = usuarios[
            (usuarios["tipo"].astype(str) == "vendedor") &
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
                "Gerenciar Vendedores",
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
    elif menu == "Gerenciar Vendedores":
        gerenciar_vendedores()
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
