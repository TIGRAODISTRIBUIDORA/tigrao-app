import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Tigrão ERP", page_icon="🐯", layout="wide")

PASTA = "dados_tigrao"
ARQ_PRODUTOS = f"{PASTA}/produtos.xlsx"
ARQ_CLIENTES = f"{PASTA}/clientes.xlsx"
ARQ_PEDIDOS = f"{PASTA}/pedidos.xlsx"

os.makedirs(PASTA, exist_ok=True)

USUARIO = "admin"
SENHA = "tigrao123"
COMISSAO = 0.07


def criar_bancos():
    if not os.path.exists(ARQ_PRODUTOS):
        pd.DataFrame(columns=["codigo", "produto", "un", "preco"]).to_excel(ARQ_PRODUTOS, index=False)

    if not os.path.exists(ARQ_CLIENTES):
        pd.DataFrame([{
            "codigo": 1,
            "cliente": "CLIENTE PADRÃO",
            "cnpj": "",
            "telefone": "",
            "cidade": ""
        }]).to_excel(ARQ_CLIENTES, index=False)

    if not os.path.exists(ARQ_PEDIDOS):
        pd.DataFrame(columns=[
            "pedido", "data", "vendedor", "cliente", "codigo",
            "produto", "un", "quantidade", "preco", "desconto",
            "subtotal", "total", "status"
        ]).to_excel(ARQ_PEDIDOS, index=False)


criar_bancos()


def ler_excel(caminho):
    try:
        return pd.read_excel(caminho)
    except:
        return pd.DataFrame()


def salvar_excel(df, caminho):
    df.to_excel(caminho, index=False)


def limpar_colunas(df):
    df.columns = [
        str(c).strip().lower()
        .replace("ç", "c")
        .replace("ã", "a")
        .replace("á", "a")
        .replace("à", "a")
        .replace("â", "a")
        .replace("é", "e")
        .replace("ê", "e")
        .replace("í", "i")
        .replace("ó", "o")
        .replace("ô", "o")
        .replace("ú", "u")
        for c in df.columns
    ]
    return df


def formatar_real(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"


st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #050505, #101820);
    color: white;
}

[data-testid="stSidebar"] {
    background: #060606;
    border-right: 1px solid #252525;
}

h1, h2, h3, label, p {
    color: white !important;
}

.card {
    background: #111827;
    border: 1px solid #263241;
    border-radius: 18px;
    padding: 18px;
    margin-bottom: 16px;
}

.titulo {
    font-size: 34px;
    font-weight: 900;
    color: white;
    margin-bottom: 20px;
}

.valor {
    color: #ff7a00;
    font-size: 30px;
    font-weight: 900;
}

.sugestao {
    background: #0b1118;
    border: 1px solid #27313d;
    border-radius: 14px;
    padding: 14px;
    margin-bottom: 8px;
    font-size: 18px;
}

.codigo {
    color: #ff7a00;
    font-weight: 900;
}

div.stButton > button {
    background: linear-gradient(90deg, #ff7a00, #ff4d00);
    color: white;
    border: none;
    border-radius: 12px;
    height: 48px;
    font-weight: 800;
}

div.stButton > button:hover {
    background: linear-gradient(90deg, #ff8c1a, #ff5a00);
    color: white;
}
</style>
""", unsafe_allow_html=True)


if "logado" not in st.session_state:
    st.session_state.logado = False

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if "produto_selecionado" not in st.session_state:
    st.session_state.produto_selecionado = None


# LOGIN
if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>🐯 TIGRÃO DISTRIBUIDORA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Sistema de Pedidos</h3>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.2, 1])

    with c2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("ENTRAR"):
            if usuario == USUARIO and senha == SENHA:
                st.session_state.logado = True
                st.session_state.vendedor = "Administrador"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# MENU
st.sidebar.markdown("## 🐯 TIGRÃO")
st.sidebar.markdown("### Distribuidora")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Novo Pedido",
        "Pedidos Lançados",
        "Clientes",
        "Produtos",
        "Importar Produtos",
        "Comissões",
        "Sair"
    ]
)

if menu == "Sair":
    st.session_state.logado = False
    st.rerun()


# DASHBOARD
if menu == "Dashboard":
    pedidos = ler_excel(ARQ_PEDIDOS)

    st.markdown("<div class='titulo'>📊 Dashboard</div>", unsafe_allow_html=True)

    total_vendas = pedidos["total"].sum() if len(pedidos) and "total" in pedidos.columns else 0
    qtd_pedidos = pedidos["pedido"].nunique() if len(pedidos) and "pedido" in pedidos.columns else 0
    comissao = total_vendas * COMISSAO

    a, b, c = st.columns(3)

    with a:
        st.markdown(f"<div class='card'>Pedidos<br><div class='valor'>{qtd_pedidos}</div></div>", unsafe_allow_html=True)

    with b:
        st.markdown(f"<div class='card'>Vendas<br><div class='valor'>{formatar_real(total_vendas)}</div></div>", unsafe_allow_html=True)

    with c:
        st.markdown(f"<div class='card'>Comissão 7%<br><div class='valor'>{formatar_real(comissao)}</div></div>", unsafe_allow_html=True)


# NOVO PEDIDO
elif menu == "Novo Pedido":
    produtos = ler_excel(ARQ_PRODUTOS)
    clientes = ler_excel(ARQ_CLIENTES)

    st.markdown("<div class='titulo'>🛒 Novo Pedido</div>", unsafe_allow_html=True)

    if len(produtos) == 0:
        st.warning("Nenhum produto cadastrado. Vá em 'Importar Produtos' para importar sua planilha.")
        st.stop()

    col_cliente, col_vendedor = st.columns(2)

    with col_cliente:
        lista_clientes = clientes["cliente"].astype(str).tolist() if "cliente" in clientes.columns else ["CLIENTE PADRÃO"]
        cliente = st.selectbox("Cliente", lista_clientes)

    with col_vendedor:
        vendedor = st.text_input("Vendedor", value=st.session_state.vendedor)

    busca = st.text_input("🔍 Buscar produto por código ou nome")

    if busca:
        filtro = produtos[
            produtos["produto"].astype(str).str.contains(busca, case=False, na=False) |
            produtos["codigo"].astype(str).str.contains(busca, case=False, na=False)
        ]
    else:
        filtro = produtos.head(8)

    st.markdown("### Sugestões de produtos")

    for _, row in filtro.head(8).iterrows():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(
                f"<div class='sugestao'><span class='codigo'>{row['codigo']}</span> - {row['produto']} | {formatar_real(row['preco'])}</div>",
                unsafe_allow_html=True
            )

        with col2:
            if st.button("Selecionar", key=f"sel_{row['codigo']}"):
                st.session_state.produto_selecionado = row.to_dict()
                st.rerun()

    if st.session_state.produto_selecionado:
        p = st.session_state.produto_selecionado

        st.markdown("### Produto selecionado")
        st.markdown(f"<div class='card'><b>{p['codigo']} - {p['produto']}</b></div>", unsafe_allow_html=True)

        q1, q2, q3 = st.columns(3)

        with q1:
            quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)

        with q2:
            desconto = st.number_input("% Desconto", min_value=0.0, value=0.0, step=1.0)

        with q3:
            preco = float(p["preco"])
            st.text_input("Preço", value=formatar_real(preco), disabled=True)

        subtotal = preco * quantidade
        valor_desc = subtotal * (desconto / 100)
        total = subtotal - valor_desc

        st.markdown(f"### Total do item: {formatar_real(total)}")

        if st.button("➕ ADICIONAR AO PEDIDO"):
            st.session_state.carrinho.append({
                "codigo": p["codigo"],
                "produto": p["produto"],
                "un": p.get("un", "UN"),
                "quantidade": quantidade,
                "preco": preco,
                "desconto": desconto,
                "subtotal": subtotal,
                "total": total
            })
            st.session_state.produto_selecionado = None
            st.success("Produto adicionado.")
            st.rerun()

    st.markdown("---")
    st.markdown(f"### Carrinho ({len(st.session_state.carrinho)} itens)")

    if len(st.session_state.carrinho):
        df_carrinho = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_carrinho, use_container_width=True)

        subtotal_geral = df_carrinho["subtotal"].sum()
        total_geral = df_carrinho["total"].sum()
        desconto_geral = subtotal_geral - total_geral

        r1, r2, r3 = st.columns(3)

        with r1:
            st.markdown(f"<div class='card'>Subtotal<br><div class='valor'>{formatar_real(subtotal_geral)}</div></div>", unsafe_allow_html=True)

        with r2:
            st.markdown(f"<div class='card'>Desconto<br><div class='valor'>{formatar_real(desconto_geral)}</div></div>", unsafe_allow_html=True)

        with r3:
            st.markdown(f"<div class='card'>Total<br><div class='valor'>{formatar_real(total_geral)}</div></div>", unsafe_allow_html=True)

    else:
        st.info("Nenhum produto adicionado ao pedido.")

    f1, f2 = st.columns(2)

    with f1:
        if st.button("✅ FINALIZAR PEDIDO"):
            if len(st.session_state.carrinho) == 0:
                st.warning("Adicione pelo menos um produto.")
            else:
                pedidos = ler_excel(ARQ_PEDIDOS)
                numero = 1 if len(pedidos) == 0 else int(pedidos["pedido"].max()) + 1
                data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                novos = []

                for item in st.session_state.carrinho:
                    novos.append({
                        "pedido": numero,
                        "data": data,
                        "vendedor": vendedor,
                        "cliente": cliente,
                        "codigo": item["codigo"],
                        "produto": item["produto"],
                        "un": item["un"],
                        "quantidade": item["quantidade"],
                        "preco": item["preco"],
                        "desconto": item["desconto"],
                        "subtotal": item["subtotal"],
                        "total": item["total"],
                        "status": "PENDENTE"
                    })

                pedidos = pd.concat([pedidos, pd.DataFrame(novos)], ignore_index=True)
                salvar_excel(pedidos, ARQ_PEDIDOS)

                st.session_state.carrinho = []
                st.success(f"Pedido nº {numero} salvo com sucesso!")
                st.rerun()

    with f2:
        if st.button("🗑️ LIMPAR PEDIDO"):
            st.session_state.carrinho = []
            st.session_state.produto_selecionado = None
            st.rerun()


# PEDIDOS LANÇADOS
elif menu == "Pedidos Lançados":
    st.markdown("<div class='titulo'>📋 Pedidos Lançados</div>", unsafe_allow_html=True)

    pedidos = ler_excel(ARQ_PEDIDOS)

    if len(pedidos) == 0:
        st.info("Nenhum pedido lançado.")
    else:
        st.dataframe(pedidos, use_container_width=True)

        st.markdown("---")
        st.markdown("### 🗑️ Excluir Pedido")

        lista_pedidos = sorted(pedidos["pedido"].dropna().unique())

        pedido_excluir = st.selectbox("Selecione o número do pedido que deseja excluir", lista_pedidos)

        dados_pedido = pedidos[pedidos["pedido"] == pedido_excluir]

        if len(dados_pedido):
            cliente_pedido = dados_pedido["cliente"].iloc[0]
            total_pedido = dados_pedido["total"].sum()
            st.warning(
                f"Você está prestes a excluir o pedido nº {pedido_excluir} "
                f"do cliente {cliente_pedido}, total {formatar_real(total_pedido)}."
            )

        confirmar = st.checkbox(f"Confirmo que desejo excluir o pedido nº {pedido_excluir}")

        if st.button("🗑️ EXCLUIR PEDIDO"):
            if not confirmar:
                st.warning("Marque a confirmação antes de excluir.")
            else:
                pedidos = pedidos[pedidos["pedido"] != pedido_excluir]
                salvar_excel(pedidos, ARQ_PEDIDOS)
                st.success(f"Pedido nº {pedido_excluir} excluído com sucesso.")
                st.rerun()

        st.markdown("---")

        pedidos.to_excel("pedidos_exportados.xlsx", index=False)

        with open("pedidos_exportados.xlsx", "rb") as f:
            st.download_button(
                "⬇️ Baixar pedidos em Excel",
                f,
                file_name="pedidos_tigrao.xlsx"
            )


# CLIENTES
elif menu == "Clientes":
    st.markdown("<div class='titulo'>👥 Clientes</div>", unsafe_allow_html=True)

    clientes = ler_excel(ARQ_CLIENTES)

    with st.expander("Cadastrar cliente"):
        codigo = st.number_input("Código do cliente", min_value=1, step=1)
        nome = st.text_input("Nome")
        cnpj = st.text_input("CNPJ")
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")

        if st.button("Salvar Cliente"):
            novo = pd.DataFrame([{
                "codigo": codigo,
                "cliente": nome,
                "cnpj": cnpj,
                "telefone": telefone,
                "cidade": cidade
            }])
            clientes = pd.concat([clientes, novo], ignore_index=True)
            salvar_excel(clientes, ARQ_CLIENTES)
            st.success("Cliente salvo.")
            st.rerun()

    busca_cliente = st.text_input("Buscar cliente")

    if busca_cliente:
        clientes_filtrados = clientes[
            clientes.astype(str).apply(
                lambda linha: linha.str.contains(busca_cliente, case=False, na=False).any(),
                axis=1
            )
        ]
        st.dataframe(clientes_filtrados, use_container_width=True)
    else:
        st.dataframe(clientes, use_container_width=True)


# PRODUTOS
elif menu == "Produtos":
    st.markdown("<div class='titulo'>📦 Produtos</div>", unsafe_allow_html=True)

    produtos = ler_excel(ARQ_PRODUTOS)

    with st.expander("Cadastrar produto manual"):
        codigo = st.text_input("Código")
        produto = st.text_input("Produto")
        un = st.text_input("Unidade", value="UN")
        preco = st.number_input("Preço", min_value=0.0, step=0.10)

        if st.button("Salvar Produto"):
            novo = pd.DataFrame([{
                "codigo": codigo,
                "produto": produto,
                "un": un,
                "preco": preco
            }])
            produtos = pd.concat([produtos, novo], ignore_index=True)
            salvar_excel(produtos, ARQ_PRODUTOS)
            st.success("Produto salvo.")
            st.rerun()

    st.markdown("---")
    st.markdown("### 📤 Exportar modelo / produtos")

    modelo_produtos = pd.DataFrame([
        {
            "codigo": "187",
            "produto": "37 ERVAS 500MG 100 CAPSULAS",
            "un": "UN",
            "preco": 20.77
        },
        {
            "codigo": "188",
            "produto": "37 ERVAS 500MG 60 CAPSULAS",
            "un": "UN",
            "preco": 13.90
        }
    ])

    modelo_produtos.to_excel("modelo_produtos_tigrao.xlsx", index=False)

    with open("modelo_produtos_tigrao.xlsx", "rb") as f:
        st.download_button(
            "⬇️ Baixar modelo de importação",
            f,
            file_name="modelo_produtos_tigrao.xlsx"
        )

    if len(produtos) > 0:
        produtos.to_excel("produtos_tigrao_exportados.xlsx", index=False)

        with open("produtos_tigrao_exportados.xlsx", "rb") as f:
            st.download_button(
                "⬇️ Exportar produtos cadastrados",
                f,
                file_name="produtos_tigrao.xlsx"
            )

    st.markdown("---")
    st.markdown("### 🔍 Consultar produtos")

    busca_prod = st.text_input("Buscar produto")

    if busca_prod:
        produtos_filtrados = produtos[
            produtos["produto"].astype(str).str.contains(busca_prod, case=False, na=False) |
            produtos["codigo"].astype(str).str.contains(busca_prod, case=False, na=False)
        ]
        st.dataframe(produtos_filtrados, use_container_width=True)
    else:
        st.dataframe(produtos, use_container_width=True)


# IMPORTAR PRODUTOS
elif menu == "Importar Produtos":
    st.markdown("<div class='titulo'>📥 Importar Produtos por Excel</div>", unsafe_allow_html=True)

    st.info("A planilha precisa ter código, produto, unidade e preço.")

    arquivo = st.file_uploader("Escolha a planilha de produtos", type=["xlsx", "xls", "csv"])

    if arquivo:
        if arquivo.name.endswith(".csv"):
            novo_df = pd.read_csv(arquivo)
        else:
            novo_df = pd.read_excel(arquivo)

        novo_df = limpar_colunas(novo_df)

        mapa = {}

        for col in novo_df.columns:
            if col in ["codigo", "cod", "cod_produto", "id"]:
                mapa[col] = "codigo"
            elif col in ["produto", "descricao", "nome", "nome_produto"]:
                mapa[col] = "produto"
            elif col in ["un", "und", "unidade"]:
                mapa[col] = "un"
            elif col in ["preco", "preco_venda", "valor", "valor_venda"]:
                mapa[col] = "preco"

        novo_df = novo_df.rename(columns=mapa)

        obrigatorias = ["codigo", "produto", "preco"]
        faltando = [c for c in obrigatorias if c not in novo_df.columns]

        if faltando:
            st.error(f"Faltam colunas obrigatórias na planilha: {faltando}")
            st.stop()

        if "un" not in novo_df.columns:
            novo_df["un"] = "UN"

        novo_df = novo_df[["codigo", "produto", "un", "preco"]]
        novo_df["codigo"] = novo_df["codigo"].astype(str).str.strip()
        novo_df["produto"] = novo_df["produto"].astype(str).str.strip()
        novo_df["un"] = novo_df["un"].astype(str).str.strip()
        novo_df["preco"] = pd.to_numeric(novo_df["preco"], errors="coerce").fillna(0)

        novo_df = novo_df[novo_df["produto"] != ""]
        novo_df = novo_df.drop_duplicates(subset=["codigo"], keep="last")

        st.markdown("### Pré-visualização")
        st.dataframe(novo_df, use_container_width=True)

        if st.button("✅ IMPORTAR E ATUALIZAR PRODUTOS"):
            produtos_atual = ler_excel(ARQ_PRODUTOS)

            if len(produtos_atual) == 0:
                salvar_excel(novo_df, ARQ_PRODUTOS)
                st.success(f"{len(novo_df)} produtos importados com sucesso.")
                st.rerun()

            produtos_atual["codigo"] = produtos_atual["codigo"].astype(str).str.strip()

            codigos_antigos = set(produtos_atual["codigo"].astype(str))
            codigos_novos = set(novo_df["codigo"].astype(str))

            atualizados = len(codigos_antigos.intersection(codigos_novos))
            cadastrados = len(codigos_novos - codigos_antigos)

            produtos_final = pd.concat([
                produtos_atual[~produtos_atual["codigo"].astype(str).isin(codigos_novos)],
                novo_df
            ], ignore_index=True)

            salvar_excel(produtos_final, ARQ_PRODUTOS)

            st.success(f"Importação concluída! Novos: {cadastrados} | Atualizados: {atualizados}")
            st.rerun()


# COMISSÕES
elif menu == "Comissões":
    st.markdown("<div class='titulo'>💰 Comissões</div>", unsafe_allow_html=True)

    pedidos = ler_excel(ARQ_PEDIDOS)

    if len(pedidos) == 0:
        st.info("Ainda não existem pedidos.")
    else:
        resumo = pedidos.groupby("vendedor")["total"].sum().reset_index()
        resumo["comissao_7%"] = resumo["total"] * COMISSAO
        st.dataframe(resumo, use_container_width=True)
