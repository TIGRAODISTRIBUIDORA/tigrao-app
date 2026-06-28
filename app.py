import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Tigrão Distribuidora",
    page_icon="🐯",
    layout="wide"
)

# =========================
# CONFIGURAÇÕES
# =========================
PASTA_DADOS = "dados_tigrao"
ARQ_PRODUTOS = f"{PASTA_DADOS}/produtos.xlsx"
ARQ_PEDIDOS = f"{PASTA_DADOS}/pedidos.xlsx"
ARQ_CLIENTES = f"{PASTA_DADOS}/clientes.xlsx"

os.makedirs(PASTA_DADOS, exist_ok=True)

USUARIO_ADMIN = "admin"
SENHA_ADMIN = "tigrao123"

# =========================
# BANCO DE DADOS INICIAL
# =========================
def criar_bancos():
    if not os.path.exists(ARQ_PRODUTOS):
        produtos = pd.DataFrame([
            {"codigo": 187, "produto": "37 ERVAS 500MG 100 CAPSULAS", "un": "UN", "preco": 20.77},
            {"codigo": 188, "produto": "37 ERVAS 500MG 60 CAPSULAS", "un": "UN", "preco": 13.90},
            {"codigo": 189, "produto": "37 ERVAS 500MG 120 CAPSULAS", "un": "UN", "preco": 25.90},
        ])
        produtos.to_excel(ARQ_PRODUTOS, index=False)

    if not os.path.exists(ARQ_PEDIDOS):
        pedidos = pd.DataFrame(columns=[
            "pedido", "data", "vendedor", "cliente", "codigo",
            "produto", "un", "quantidade", "preco", "desconto",
            "subtotal", "total", "status"
        ])
        pedidos.to_excel(ARQ_PEDIDOS, index=False)

    if not os.path.exists(ARQ_CLIENTES):
        clientes = pd.DataFrame([
            {"cliente": "CLIENTE PADRÃO", "cnpj": "", "telefone": "", "cidade": ""}
        ])
        clientes.to_excel(ARQ_CLIENTES, index=False)

criar_bancos()

def carregar_produtos():
    return pd.read_excel(ARQ_PRODUTOS)

def carregar_pedidos():
    return pd.read_excel(ARQ_PEDIDOS)

def salvar_pedidos(df):
    df.to_excel(ARQ_PEDIDOS, index=False)

# =========================
# ESTILO
# =========================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #111827 0%, #05070a 55%, #020304 100%);
    color: white;
}

[data-testid="stSidebar"] {
    background: #060b10;
    border-right: 1px solid #1f2937;
}

h1, h2, h3, h4, p, label {
    color: #ffffff !important;
}

.titulo {
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 25px;
}

.card {
    background: linear-gradient(180deg, #111820, #080d12);
    border: 1px solid #263241;
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 18px;
}

.sugestao {
    background: #0d141b;
    border: 1px solid #263241;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 8px;
    font-size: 20px;
}

.codigo {
    color: #ff7a00;
    font-weight: 800;
}

.preco {
    color: #ff7a00;
    font-weight: 800;
    float: right;
}

.produto-selecionado {
    border: 1px solid #ff7a00;
    border-radius: 14px;
    padding: 18px;
    background: #0d141b;
    font-size: 20px;
    margin-bottom: 18px;
}

.resumo {
    background: #0d141b;
    border: 1px solid #263241;
    border-radius: 16px;
    padding: 22px;
    text-align: center;
}

.valor-laranja {
    color: #ff7a00;
    font-size: 28px;
    font-weight: 800;
}

.valor-verde {
    color: #22c55e;
    font-size: 28px;
    font-weight: 800;
}

div.stButton > button {
    background: linear-gradient(90deg, #ff7a00, #ff5a00);
    color: white;
    border: none;
    border-radius: 12px;
    height: 52px;
    font-size: 18px;
    font-weight: 800;
}

div.stButton > button:hover {
    background: linear-gradient(90deg, #ff8c1a, #ff6a00);
    color: white;
}

input {
    background-color: #0d141b !important;
    color: white !important;
    border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# LOGIN
# =========================
if "logado" not in st.session_state:
    st.session_state.logado = False

if "carrinho" not in st.session_state:
    st.session_state.carrinho = []

if not st.session_state.logado:
    st.markdown("<h1 style='text-align:center;'>🐯 TIGRÃO DISTRIBUIDORA</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align:center;'>Sistema de Pedidos</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])

    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")

        if st.button("ENTRAR"):
            if usuario == USUARIO_ADMIN and senha == SENHA_ADMIN:
                st.session_state.logado = True
                st.session_state.usuario = "Administrador"
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos.")

        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# =========================
# MENU LATERAL
# =========================
st.sidebar.markdown("## 🐯 TIGRÃO")
st.sidebar.markdown("### DISTRIBUIDORA")

menu = st.sidebar.radio(
    "Menu",
    [
        "Dashboard",
        "Novo Pedido",
        "Pedidos Lançados",
        "Clientes",
        "Produtos",
        "Comissões",
        "Importar Retorno",
        "Sair"
    ]
)

if menu == "Sair":
    st.session_state.logado = False
    st.rerun()

# =========================
# DASHBOARD
# =========================
if menu == "Dashboard":
    pedidos = carregar_pedidos()

    st.markdown("<div class='titulo'>📊 Dashboard</div>", unsafe_allow_html=True)

    total_vendas = pedidos["total"].sum() if len(pedidos) else 0
    total_pedidos = pedidos["pedido"].nunique() if len(pedidos) else 0
    comissao = total_vendas * 0.07

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown(f"<div class='resumo'>Pedidos<br><div class='valor-laranja'>{total_pedidos}</div></div>", unsafe_allow_html=True)

    with c2:
        st.markdown(f"<div class='resumo'>Vendas<br><div class='valor-laranja'>R$ {total_vendas:,.2f}</div></div>", unsafe_allow_html=True)

    with c3:
        st.markdown(f"<div class='resumo'>Comissão 7%<br><div class='valor-verde'>R$ {comissao:,.2f}</div></div>", unsafe_allow_html=True)

# =========================
# NOVO PEDIDO
# =========================
elif menu == "Novo Pedido":
    produtos = carregar_produtos()

    st.markdown("<div class='titulo'>🛒 Novo Pedido</div>", unsafe_allow_html=True)

    busca = st.text_input("🔍 Código ou nome do produto", placeholder="Código ou nome do produto...")

    if busca:
        filtro = produtos[
            produtos["produto"].str.contains(busca, case=False, na=False) |
            produtos["codigo"].astype(str).str.contains(busca, case=False, na=False)
        ]
    else:
        filtro = produtos.head(3)

    st.markdown("### Sugestões de produtos")

    produto_escolhido = None

    for _, row in filtro.head(5).iterrows():
        col1, col2 = st.columns([5, 1])

        with col1:
            st.markdown(
                f"""
                <div class='sugestao'>
                    <span class='codigo'>{row['codigo']}</span> - {row['produto']}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            if st.button(f"Selecionar {row['codigo']}"):
                st.session_state.produto_selecionado = row.to_dict()
                st.rerun()

    if "produto_selecionado" in st.session_state:
        p = st.session_state.produto_selecionado

        st.markdown("### ✅ Produto selecionado")

        st.markdown(
            f"""
            <div class='produto-selecionado'>
                💊 {p['codigo']} - {p['produto']}
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2 = st.columns(2)

        with c1:
            codigo = st.text_input("Código", value=str(p["codigo"]), disabled=True)

        with c2:
            un = st.text_input("Un", value=str(p["un"]), disabled=True)

        c3, c4 = st.columns(2)

        with c3:
            quantidade = st.number_input("Quantidade", min_value=1, value=1, step=1)

        with c4:
            desconto = st.number_input("% Desconto", min_value=0.0, value=0.0, step=1.0)

        preco = float(p["preco"])
        subtotal = preco * quantidade
        valor_desconto = subtotal * (desconto / 100)
        total = subtotal - valor_desconto

        c5, c6 = st.columns(2)

        with c5:
            st.text_input("Preço Unitário", value=f"R$ {preco:.2f}", disabled=True)

        with c6:
            st.text_input("Total", value=f"R$ {total:.2f}", disabled=True)

        if st.button("➕ ADICIONAR AO PEDIDO"):
            st.session_state.carrinho.append({
                "codigo": p["codigo"],
                "produto": p["produto"],
                "un": p["un"],
                "quantidade": quantidade,
                "preco": preco,
                "desconto": desconto,
                "subtotal": subtotal,
                "total": total
            })
            st.success("Produto adicionado ao pedido.")
            st.rerun()

    st.markdown("---")
    st.markdown(f"### Produtos no pedido ({len(st.session_state.carrinho)})")

    if len(st.session_state.carrinho) == 0:
        st.markdown(
            """
            <div class='card' style='text-align:center; color:#aaa;'>
                🛒 Nenhum produto adicionado ainda.
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        df_carrinho = pd.DataFrame(st.session_state.carrinho)
        st.dataframe(df_carrinho, use_container_width=True)

    itens = len(st.session_state.carrinho)
    subtotal_geral = sum(item["subtotal"] for item in st.session_state.carrinho)
    total_geral = sum(item["total"] for item in st.session_state.carrinho)
    desconto_geral = subtotal_geral - total_geral

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.markdown(f"<div class='resumo'>Itens<br><div class='valor-laranja'>{itens}</div></div>", unsafe_allow_html=True)

    with r2:
        st.markdown(f"<div class='resumo'>Subtotal<br><div class='valor-laranja'>R$ {subtotal_geral:.2f}</div></div>", unsafe_allow_html=True)

    with r3:
        st.markdown(f"<div class='resumo'>Desconto<br><div class='valor-verde'>R$ {desconto_geral:.2f}</div></div>", unsafe_allow_html=True)

    with r4:
        st.markdown(f"<div class='resumo'>Total<br><div class='valor-laranja'>R$ {total_geral:.2f}</div></div>", unsafe_allow_html=True)

    st.markdown("---")

    cliente = st.text_input("Cliente", value="CLIENTE PADRÃO")
    vendedor = st.text_input("Vendedor", value=st.session_state.usuario)

    cfinal1, cfinal2 = st.columns(2)

    with cfinal1:
        if st.button("✅ FINALIZAR PEDIDO"):
            if len(st.session_state.carrinho) == 0:
                st.warning("Adicione pelo menos um produto.")
            else:
                pedidos = carregar_pedidos()
                numero_pedido = 1 if len(pedidos) == 0 else int(pedidos["pedido"].max()) + 1
                data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                novos = []

                for item in st.session_state.carrinho:
                    novos.append({
                        "pedido": numero_pedido,
                        "data": data_atual,
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
                salvar_pedidos(pedidos)

                st.session_state.carrinho = []
                st.success(f"Pedido nº {numero_pedido} salvo com sucesso!")
                st.rerun()

    with cfinal2:
        if st.button("🗑️ LIMPAR PEDIDO"):
            st.session_state.carrinho = []
            st.rerun()

# =========================
# PEDIDOS LANÇADOS
# =========================
elif menu == "Pedidos Lançados":
    st.markdown("<div class='titulo'>📋 Pedidos Lançados</div>", unsafe_allow_html=True)

    pedidos = carregar_pedidos()

    if len(pedidos) == 0:
        st.info("Nenhum pedido lançado ainda.")
    else:
        st.dataframe(pedidos, use_container_width=True)

# =========================
# CLIENTES
# =========================
elif menu == "Clientes":
    st.markdown("<div class='titulo'>👥 Clientes</div>", unsafe_allow_html=True)

    clientes = pd.read_excel(ARQ_CLIENTES)

    with st.expander("Cadastrar novo cliente"):
        nome = st.text_input("Nome do cliente")
        cnpj = st.text_input("CNPJ")
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")

        if st.button("Salvar Cliente"):
            novo = pd.DataFrame([{
                "cliente": nome,
                "cnpj": cnpj,
                "telefone": telefone,
                "cidade": cidade
            }])
            clientes = pd.concat([clientes, novo], ignore_index=True)
            clientes.to_excel(ARQ_CLIENTES, index=False)
            st.success("Cliente cadastrado.")
            st.rerun()

    st.dataframe(clientes, use_container_width=True)

# =========================
# PRODUTOS
# =========================
elif menu == "Produtos":
    st.markdown("<div class='titulo'>📦 Produtos</div>", unsafe_allow_html=True)

    produtos = carregar_produtos()

    with st.expander("Cadastrar novo produto"):
        codigo = st.number_input("Código", min_value=1, step=1)
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
            produtos.to_excel(ARQ_PRODUTOS, index=False)
            st.success("Produto cadastrado.")
            st.rerun()

    consulta = st.text_input("Consultar produto")

    if consulta:
        produtos_filtrados = produtos[
            produtos["produto"].str.contains(consulta, case=False, na=False) |
            produtos["codigo"].astype(str).str.contains(consulta, case=False, na=False)
        ]
        st.dataframe(produtos_filtrados, use_container_width=True)
    else:
        st.dataframe(produtos, use_container_width=True)

# =========================
# COMISSÕES
# =========================
elif menu == "Comissões":
    st.markdown("<div class='titulo'>💰 Comissões</div>", unsafe_allow_html=True)

    pedidos = carregar_pedidos()

    if len(pedidos) == 0:
        st.info("Nenhuma comissão disponível.")
    else:
        resumo = pedidos.groupby("vendedor")["total"].sum().reset_index()
        resumo["comissao_7%"] = resumo["total"] * 0.07
        st.dataframe(resumo, use_container_width=True)

# =========================
# IMPORTAR RETORNO
# =========================
elif menu == "Importar Retorno":
    st.markdown("<div class='titulo'>📥 Importar Retorno de Faturamento</div>", unsafe_allow_html=True)

    st.info("Aqui você poderá importar uma planilha Excel com o status FATURADO ou NÃO FATURADO.")

    arquivo = st.file_uploader("Enviar planilha Excel", type=["xlsx"])

    if arquivo:
        retorno = pd.read_excel(arquivo)
        st.dataframe(retorno, use_container_width=True)
        st.success("Planilha carregada com sucesso.")
