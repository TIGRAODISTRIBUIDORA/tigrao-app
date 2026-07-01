import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tigrão Premium",
    page_icon="🐯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

PASTA_DADOS = "dados"
ARQ_CLIENTES = f"{PASTA_DADOS}/clientes.xlsx"
ARQ_PRODUTOS = f"{PASTA_DADOS}/produtos.xlsx"
ARQ_PEDIDOS = f"{PASTA_DADOS}/pedidos.xlsx"
ARQ_USUARIOS = f"{PASTA_DADOS}/usuarios.xlsx"

COMISSAO_PADRAO = 0.07


# =========================
# BANCO DE DADOS
# =========================

def criar_banco():
    os.makedirs(PASTA_DADOS, exist_ok=True)

    if not os.path.exists(ARQ_USUARIOS):
        pd.DataFrame([
            {"usuario": "admin", "senha": "admin123", "nome": "Administrador", "perfil": "ADMIN", "comissao": 0.07},
            {"usuario": "vendedor", "senha": "123", "nome": "Vendedor", "perfil": "VENDEDOR", "comissao": 0.07},
        ]).to_excel(ARQ_USUARIOS, index=False)

    if not os.path.exists(ARQ_CLIENTES):
        pd.DataFrame([
            {"codigo": 1, "cliente": "NELSON DAS GALAXIAS", "cnpj": "", "telefone": "", "cidade": ""},
            {"codigo": 2, "cliente": "DROGANNE MEDICAMENTOS E PERFUMARIA LTDA", "cnpj": "", "telefone": "", "cidade": ""},
            {"codigo": 3, "cliente": "NATURA TERRA COMERCIO E SERVICOS LTDA", "cnpj": "", "telefone": "", "cidade": ""},
        ]).to_excel(ARQ_CLIENTES, index=False)

    if not os.path.exists(ARQ_PRODUTOS):
        pd.DataFrame([
            {"codigo": "68.0", "produto": "BENETONICO 500M", "un": "UN", "preco": 10.21, "fornecedor": "ARTE NATIVA"},
            {"codigo": "103.0", "produto": "APIS FRESH SPRAY EXTRA FORTE 35ML", "un": "UN", "preco": 5.82, "fornecedor": "ARTE NATIVA"},
            {"codigo": "178.0", "produto": "BALDONI EXTRATO DE PROPOLIS VERDE 30ML", "un": "UN", "preco": 20.89, "fornecedor": "BALDONI"},
        ]).to_excel(ARQ_PRODUTOS, index=False)

    if not os.path.exists(ARQ_PEDIDOS):
        pd.DataFrame(columns=[
            "pedido", "data", "vendedor", "cliente", "codigo", "produto",
            "un", "quantidade", "preco", "desconto", "subtotal", "total", "status"
        ]).to_excel(ARQ_PEDIDOS, index=False)


def ler_excel(caminho):
    try:
        return pd.read_excel(caminho)
    except Exception:
        return pd.DataFrame()


def salvar_excel(df, caminho):
    df.to_excel(caminho, index=False)


def dinheiro(valor):
    try:
        return f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def safe_float(valor):
    try:
        return float(valor)
    except Exception:
        return 0.0


def numero_pedido():
    pedidos = ler_excel(ARQ_PEDIDOS)
    if len(pedidos) == 0 or "pedido" not in pedidos.columns:
        return 1

    maior = pd.to_numeric(pedidos["pedido"], errors="coerce").max()
    return 1 if pd.isna(maior) else int(maior) + 1


def resumo_pedidos(pedidos):
    if len(pedidos) == 0 or "pedido" not in pedidos.columns:
        return pd.DataFrame(columns=["pedido", "data", "vendedor", "cliente", "total", "status"])

    pedidos = pedidos.copy()
    pedidos["total"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0)

    return pedidos.groupby("pedido", as_index=False).agg({
        "data": "first",
        "vendedor": "first",
        "cliente": "first",
        "total": "sum",
        "status": "first",
    })


def filtrar_por_usuario(pedidos):
    if len(pedidos) == 0:
        return pedidos

    if st.session_state.get("perfil") != "ADMIN":
        vendedor = st.session_state.get("nome", "")
        pedidos = pedidos[pedidos["vendedor"].astype(str) == vendedor].copy()

    return pedidos


# =========================
# ESTILO PREMIUM MOBILE
# =========================

def css():
    st.markdown("""
    <style>
    header, footer, [data-testid="stSidebar"] {
        display:none !important;
    }

    [data-testid="stAppViewContainer"] {
        background:#f5f6f8 !important;
    }

    .block-container {
        max-width:520px !important;
        padding:0 14px 34px 14px !important;
        margin:auto !important;
    }

    * {
        font-family:Arial, sans-serif;
        box-sizing:border-box;
    }

    .topbar {
        background:linear-gradient(180deg,#111827,#0b0f16);
        border-radius:0 0 24px 24px;
        padding:18px 16px;
        margin:0 -14px 16px -14px;
        color:white;
        box-shadow:0 6px 20px rgba(0,0,0,.25);
    }

    .topbar-row {
        display:flex;
        align-items:center;
        justify-content:space-between;
    }

    .hamb {
        color:#ff8500;
        font-size:31px;
        font-weight:1000;
    }

    .brand {
        text-align:center;
        line-height:1;
    }

    .brand-main {
        color:white;
        font-size:28px;
        font-weight:1000;
        letter-spacing:1px;
    }

    .brand-sub {
        color:#ff8500;
        font-size:11px;
        font-weight:1000;
        letter-spacing:3px;
        margin-top:4px;
    }

    .profile-pill {
        border:3px solid #ff8500;
        border-radius:22px;
        padding:8px 10px;
        color:white;
        font-size:12px;
        font-weight:1000;
    }

    .page-title {
        display:flex;
        gap:12px;
        align-items:center;
        margin:14px 0 14px 0;
    }

    .page-icon {
        width:56px;
        height:56px;
        background:#138fe5;
        color:white;
        display:flex;
        align-items:center;
        justify-content:center;
        border-radius:13px;
        font-size:31px;
        box-shadow:0 6px 18px rgba(19,143,229,.35);
    }

    .page-title h1 {
        margin:0;
        padding:0;
        color:#111;
        font-size:29px;
        font-weight:1000;
        line-height:1;
    }

    .page-title p {
        margin:6px 0 0 0;
        color:#6b7280;
        font-size:16px;
        font-weight:700;
    }

    .premium-card {
        background:white;
        border-radius:20px;
        padding:16px;
        box-shadow:0 6px 20px rgba(15,23,42,.10);
        margin-bottom:14px;
        border:1px solid rgba(15,23,42,.06);
    }

    .section-head {
        display:flex;
        align-items:center;
        gap:9px;
        color:#111;
        font-size:18px;
        font-weight:1000;
        margin:6px 0 12px 0;
    }

    .blue-icon {
        color:#138fe5;
        font-size:25px;
    }

    .orange-line {
        width:44px;
        height:4px;
        border-radius:10px;
        background:#ff8500;
        margin:4px 0 14px 0;
    }

    .item-total {
        background:white;
        border:1px solid #e5e7eb;
        border-radius:17px;
        padding:15px;
        margin:12px 0;
    }

    .item-total-label {
        color:#4b5563;
        font-weight:1000;
        font-size:14px;
    }

    .item-total-value {
        color:#138fe5;
        font-size:36px;
        font-weight:1000;
        margin-top:4px;
    }

    .pedido-card {
        background:white;
        border-radius:18px;
        padding:15px;
        box-shadow:0 6px 18px rgba(15,23,42,.10);
        margin-bottom:12px;
        border-left:6px solid #ff8500;
        color:#111;
    }

    .pedido-card b {
        color:#111 !important;
    }

    .pedido-card small {
        color:#64748b;
    }

    .valor {
        color:#138fe5 !important;
        font-size:20px;
        font-weight:1000;
    }

    .resumo-card {
        background:white;
        border-radius:18px;
        padding:15px;
        box-shadow:0 6px 18px rgba(15,23,42,.08);
        margin:14px 0;
        border:1px solid rgba(15,23,42,.08);
    }

    .resumo-title {
        color:#111;
        font-weight:1000;
        font-size:17px;
        margin-bottom:10px;
    }

    .resumo-row {
        display:flex;
        justify-content:space-between;
        padding:8px 0;
        border-bottom:1px dashed #e5e7eb;
        font-size:16px;
    }

    .resumo-row:last-child {
        border-bottom:0;
        font-weight:1000;
        font-size:18px;
    }

    .resumo-total {
        color:#138fe5;
        font-weight:1000;
        font-size:24px;
    }

    div[data-testid="stMetric"] {
        background:white;
        padding:15px;
        border-radius:18px;
        box-shadow:0 6px 18px rgba(15,23,42,.09);
        border:1px solid rgba(15,23,42,.06);
    }

    div[data-testid="stMetricLabel"] {
        font-weight:1000;
        color:#4b5563;
    }

    div[data-testid="stMetricValue"] {
        color:#138fe5;
        font-weight:1000;
    }

    .stButton > button {
        border-radius:16px !important;
        min-height:52px !important;
        font-weight:1000 !important;
        border:none !important;
        background:#138fe5 !important;
        color:white !important;
        box-shadow:0 5px 14px rgba(19,143,229,.28);
    }

    .stButton > button:hover {
        background:#0b7fd1 !important;
        color:white !important;
    }

    div[data-testid="stHorizontalBlock"] .stButton > button {
        min-height:55px !important;
        font-size:15px !important;
    }

    input, textarea {
        border-radius:14px !important;
        min-height:48px !important;
        font-weight:700 !important;
    }

    div[data-baseweb="select"] > div {
        border-radius:14px !important;
        min-height:48px !important;
    }

    .login-box {
        background:white;
        border-radius:22px;
        padding:20px;
        box-shadow:0 8px 24px rgba(15,23,42,.10);
        margin-top:20px;
    }

    @media(max-width:420px) {
        .brand-main {
            font-size:23px;
        }

        .profile-pill {
            font-size:10px;
            padding:7px 8px;
        }

        .page-title h1 {
            font-size:26px;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# =========================
# SESSÃO / NAVEGAÇÃO
# =========================

def iniciar_sessao():
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if "page" not in st.session_state:
        st.session_state.page = "dashboard"

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    if "form_key" not in st.session_state:
        st.session_state.form_key = 0

    if "cliente_selecionado" not in st.session_state:
        st.session_state.cliente_selecionado = None

    if "produto_selecionado" not in st.session_state:
        st.session_state.produto_selecionado = None


def ir_para(page):
    st.session_state.page = page
    st.rerun()


def topo(titulo, subtitulo, icone="📦"):
    perfil = st.session_state.get("perfil", "VENDEDOR")

    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-row">
            <div class="hamb">☰</div>
            <div class="brand">
                <div class="brand-main">🐯 TIGRÃO</div>
                <div class="brand-sub">DISTRIBUIDORA</div>
            </div>
            <div class="profile-pill">👤 {perfil}</div>
        </div>
    </div>

    <div class="page-title">
        <div class="page-icon">{icone}</div>
        <div>
            <h1>{titulo}</h1>
            <p>{subtitulo}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def menu_nativo():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    labels = {
        "dashboard": "🏠\nInício",
        "novo": "🛒\nNovo Pedido",
        "pedidos": "📋\nPedidos",
        "comissao": "💰\nComissão",
        "mais": "☰\nMais",
    }

    col1, col2, col3, col4, col5 = st.columns(5, gap="small")

    with col1:
        texto = "✅ Início" if st.session_state.page == "dashboard" else "🏠 Início"
        if st.button(texto, key="nav_inicio", use_container_width=True):
            ir_para("dashboard")

    with col2:
        texto = "✅ Novo" if st.session_state.page == "novo" else "🛒 Novo"
        if st.button(texto, key="nav_novo", use_container_width=True):
            ir_para("novo")

    with col3:
        texto = "✅ Pedidos" if st.session_state.page == "pedidos" else "📋 Pedidos"
        if st.button(texto, key="nav_pedidos", use_container_width=True):
            ir_para("pedidos")

    with col4:
        texto = "✅ Com." if st.session_state.page == "comissao" else "💰 Com."
        if st.button(texto, key="nav_comissao", use_container_width=True):
            ir_para("comissao")

    with col5:
        texto = "✅ Mais" if st.session_state.page == "mais" else "☰ Mais"
        if st.button(texto, key="nav_mais", use_container_width=True):
            ir_para("mais")


def secao(titulo, icone=""):
    st.markdown(f"""
    <div class="section-head">
        <span class="blue-icon">{icone}</span>
        <span>{titulo}</span>
    </div>
    <div class="orange-line"></div>
    """, unsafe_allow_html=True)


def abrir_card():
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)


def fechar_card():
    st.markdown('</div>', unsafe_allow_html=True)


# =========================
# LOGIN
# =========================

def login():
    if st.session_state.logado:
        return

    st.markdown("""
    <div class="topbar">
        <div class="brand">
            <div class="brand-main">🐯 TIGRÃO</div>
            <div class="brand-sub">DISTRIBUIDORA</div>
        </div>
    </div>
    <div class="login-box">
    """, unsafe_allow_html=True)

    st.subheader("Entrar no sistema")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("ENTRAR", use_container_width=True):
        usuarios = ler_excel(ARQ_USUARIOS)

        if len(usuarios) == 0:
            st.error("Base de usuários não encontrada.")
            st.stop()

        usuarios["usuario"] = usuarios["usuario"].astype(str).str.strip().str.lower()
        usuarios["senha"] = usuarios["senha"].astype(str).str.strip()

        achou = usuarios[
            (usuarios["usuario"] == usuario.strip().lower()) &
            (usuarios["senha"] == senha.strip())
        ]

        if len(achou) == 0:
            st.error("Usuário ou senha inválidos.")
        else:
            user = achou.iloc[0]

            st.session_state.logado = True
            st.session_state.usuario = str(user["usuario"])
            st.session_state.nome = str(user["nome"])
            st.session_state.perfil = str(user["perfil"]).upper()
            st.session_state.comissao = float(user.get("comissao", COMISSAO_PADRAO))
            st.session_state.page = "dashboard"
            st.session_state.carrinho = []
            st.rerun()

    st.info("Admin: admin / admin123  |  Vendedor: vendedor / 123")

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# =========================
# TELAS
# =========================

def dashboard():
    topo("Dashboard", "Resumo da operação", "📊")

    pedidos = filtrar_por_usuario(ler_excel(ARQ_PEDIDOS))

    if len(pedidos):
        pedidos["total"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0)

    total_pedidos = pedidos["pedido"].nunique() if len(pedidos) else 0
    total_vendas = pedidos["total"].sum() if len(pedidos) else 0
    total_comissao = total_vendas * st.session_state.get("comissao", COMISSAO_PADRAO)

    c1, c2 = st.columns(2)
    c1.metric("📋 Pedidos", total_pedidos)
    c2.metric("💰 Comissão", dinheiro(total_comissao))
    st.metric("💲 Vendas", dinheiro(total_vendas))

    secao("ÚLTIMOS PEDIDOS", "🕘")

    resumo = resumo_pedidos(pedidos).sort_values("pedido", ascending=False).head(5)

    if len(resumo) == 0:
        st.info("Nenhum pedido lançado.")
    else:
        for _, row in resumo.iterrows():
            st.markdown(f"""
            <div class="pedido-card">
                <b>Pedido #{row["pedido"]}</b><br>
                Cliente: {row["cliente"]}<br>
                <small>{row["data"]}</small><br>
                <span class="valor">{dinheiro(row["total"])}</span> — {row["status"]}
            </div>
            """, unsafe_allow_html=True)


def selecionar_cliente(codigo, nome, cidade):
    st.session_state.cliente_selecionado = {
        "codigo": codigo,
        "cliente": nome,
        "cidade": cidade,
    }
    st.rerun()


def trocar_cliente():
    st.session_state.cliente_selecionado = None
    st.rerun()


def selecionar_produto(produto_dict):
    st.session_state.produto_selecionado = produto_dict
    st.rerun()


def trocar_produto():
    st.session_state.produto_selecionado = None
    st.rerun()


def novo_pedido():
    topo("Novo Pedido", "Lançamento de pedido", "🛒")

    clientes = ler_excel(ARQ_CLIENTES)
    produtos = ler_excel(ARQ_PRODUTOS)

    if "cliente_selecionado" not in st.session_state:
        st.session_state.cliente_selecionado = None

    if "produto_selecionado" not in st.session_state:
        st.session_state.produto_selecionado = None

    abrir_card()

    # =========================
    # CLIENTE ÚNICO
    # =========================
    secao("CLIENTE", "👤")

    cliente_escolhido = st.session_state.cliente_selecionado

    if cliente_escolhido:
        st.markdown(f"""
        <div class="pedido-card">
            <b>✅ Cliente selecionado</b><br>
            👤 {cliente_escolhido["cliente"]}<br>
            Código: {cliente_escolhido["codigo"]}<br>
            Cidade: {cliente_escolhido.get("cidade", "")}
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 TROCAR CLIENTE", use_container_width=True):
            trocar_cliente()

        cliente = cliente_escolhido["cliente"]

    else:
        busca_cliente = st.text_input(
            "Cliente",
            placeholder="Digite nome, código, CNPJ ou iniciais",
            label_visibility="collapsed",
            key=f"busca_cliente_unica_{st.session_state.form_key}",
        )

        cliente = None

        clientes_filtrados = clientes.copy()

        if len(clientes_filtrados) and busca_cliente.strip():
            termo = busca_cliente.strip().lower()

            clientes_filtrados = clientes[
                clientes["cliente"].astype(str).str.lower().str.contains(termo, na=False) |
                clientes["codigo"].astype(str).str.lower().str.contains(termo, na=False) |
                clientes["cnpj"].astype(str).str.lower().str.contains(termo, na=False) |
                clientes["cidade"].astype(str).str.lower().str.contains(termo, na=False)
            ]

            clientes_filtrados = clientes_filtrados.head(8)

            if len(clientes_filtrados) == 0:
                st.warning("Nenhum cliente encontrado.")
            else:
                st.caption("Toque no cliente para selecionar:")

                for i, row in clientes_filtrados.iterrows():
                    nome_cliente = str(row.get("cliente", ""))
                    codigo_cliente = str(row.get("codigo", ""))
                    cidade_cliente = str(row.get("cidade", ""))

                    st.markdown(f"""
                    <div class="pedido-card">
                        <b>👤 {nome_cliente}</b><br>
                        Código: {codigo_cliente}<br>
                        Cidade: {cidade_cliente}
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(
                        f"✅ Selecionar cliente {codigo_cliente}",
                        key=f"sel_cliente_{codigo_cliente}_{i}",
                        use_container_width=True,
                    ):
                        selecionar_cliente(codigo_cliente, nome_cliente, cidade_cliente)

        else:
            st.info("Digite para localizar o cliente. Exemplo: NEL, DRO, NATURA, código ou CNPJ.")

    # =========================
    # PRODUTO ÚNICO
    # =========================
    secao("PRODUTO", "📦")

    produto = st.session_state.produto_selecionado

    if produto:
        st.markdown(f"""
        <div class="pedido-card">
            <b>✅ Produto selecionado</b><br>
            📦 {produto["produto"]}<br>
            Código: {produto["codigo"]}<br>
            Fornecedor: {produto.get("fornecedor", "")}<br>
            Preço: <span class="valor">{dinheiro(produto["preco"])}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 TROCAR PRODUTO", use_container_width=True):
            trocar_produto()

    else:
        busca_produto = st.text_input(
            "Produto",
            placeholder="Digite código, produto ou iniciais",
            label_visibility="collapsed",
            key=f"busca_produto_unica_{st.session_state.form_key}",
        )

        produtos_filtrados = produtos.copy()

        if len(produtos_filtrados) and busca_produto.strip():
            termo = busca_produto.strip().lower()

            produtos_filtrados = produtos[
                produtos["produto"].astype(str).str.lower().str.contains(termo, na=False) |
                produtos["codigo"].astype(str).str.lower().str.contains(termo, na=False) |
                produtos["fornecedor"].astype(str).str.lower().str.contains(termo, na=False)
            ]

            produtos_filtrados = produtos_filtrados.head(10)

            if len(produtos_filtrados) == 0:
                st.warning("Nenhum produto encontrado.")
            else:
                st.caption("Toque no produto para selecionar:")

                for i, row in produtos_filtrados.iterrows():
                    produto_dict = row.to_dict()
                    codigo_produto = str(row.get("codigo", ""))
                    nome_produto = str(row.get("produto", ""))
                    fornecedor = str(row.get("fornecedor", ""))

                    st.markdown(f"""
                    <div class="pedido-card">
                        <b>📦 {nome_produto}</b><br>
                        Código: {codigo_produto}<br>
                        Fornecedor: {fornecedor}<br>
                        Preço: <span class="valor">{dinheiro(row.get("preco", 0))}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(
                        f"✅ Selecionar produto {codigo_produto}",
                        key=f"sel_produto_{codigo_produto}_{i}",
                        use_container_width=True,
                    ):
                        selecionar_produto(produto_dict)

        else:
            st.info("Digite para localizar o produto. Exemplo: MEL, 178, PRÓPOLIS ou BENETONICO.")

    # =========================
    # QUANTIDADE / DESCONTO
    # =========================
    c1, c2 = st.columns(2)

    with c1:
        secao("QUANTIDADE", "#")
        qtd = st.number_input(
            "Quantidade",
            min_value=0,
            value=0,
            step=1,
            label_visibility="collapsed",
            key=f"qtd_{st.session_state.form_key}",
        )

    with c2:
        secao("DESC. %", "🏷️")
        desc = st.number_input(
            "Desconto",
            min_value=0.0,
            value=0.0,
            step=1.0,
            label_visibility="collapsed",
            key=f"desc_{st.session_state.form_key}",
        )

    preco = safe_float(produto["preco"]) if produto else 0
    subtotal = preco * qtd
    total_item = subtotal - (subtotal * desc / 100)

    st.markdown(f"""
    <div class="item-total">
        <div class="item-total-label">💳 TOTAL DO ITEM</div>
        <div class="item-total-value">{dinheiro(total_item)}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕ ADICIONAR AO CARRINHO", use_container_width=True):
        if not cliente:
            st.warning("Selecione um cliente.")
        elif not produto:
            st.warning("Selecione um produto.")
        elif qtd <= 0:
            st.warning("Informe a quantidade.")
        else:
            st.session_state.carrinho.append({
                "codigo": produto["codigo"],
                "produto": produto["produto"],
                "un": produto.get("un", "UN"),
                "quantidade": qtd,
                "preco": preco,
                "desconto": desc,
                "subtotal": subtotal,
                "total": total_item,
            })

            st.session_state.produto_selecionado = None
            st.session_state.form_key += 1

            st.success("Produto adicionado ao carrinho.")
            time.sleep(0.4)
            st.rerun()

    fechar_card()

    carrinho(cliente)

def carrinho(cliente):
    abrir_card()
    secao("CARRINHO", "🛒")

    if len(st.session_state.carrinho) == 0:
        st.info("🛒 Nenhum produto adicionado. Adicione produtos acima para montar o pedido.")
        fechar_card()
        return

    for i, item in enumerate(st.session_state.carrinho):
        st.markdown(f"""
        <div class="pedido-card">
            <b>{item["produto"]}</b><br>
            Qtd: {item["quantidade"]} | Unit: {dinheiro(item["preco"])}<br>
            Total: <span class="valor">{dinheiro(item["total"])}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🗑 REMOVER ITEM {i+1}", key=f"del_{i}", use_container_width=True):
            st.session_state.carrinho.pop(i)
            st.rerun()

    fechar_card()

    subtotal = sum(safe_float(x["subtotal"]) for x in st.session_state.carrinho)
    total = sum(safe_float(x["total"]) for x in st.session_state.carrinho)
    desconto = subtotal - total

    st.markdown(f"""
    <div class="resumo-card">
        <div class="resumo-title">📄 RESUMO DO PEDIDO</div>
        <div class="resumo-row"><span>Subtotal</span><span>{dinheiro(subtotal)}</span></div>
        <div class="resumo-row"><span>Desconto</span><span style="color:#dc2626;">{dinheiro(desconto)}</span></div>
        <div class="resumo-row"><span>Total do Pedido</span><span class="resumo-total">{dinheiro(total)}</span></div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("🗑 LIMPAR", use_container_width=True):
            st.session_state.carrinho = []
            st.session_state.form_key += 1
            st.rerun()

    with c2:
        if st.button("✅ FINALIZAR", use_container_width=True):
            pedidos = ler_excel(ARQ_PEDIDOS)
            numero = numero_pedido()
            data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            vendedor = st.session_state.get("nome", "Vendedor")

            linhas = []

            for item in st.session_state.carrinho:
                linhas.append({
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
                    "status": "PENDENTE",
                })

            pedidos = pd.concat([pedidos, pd.DataFrame(linhas)], ignore_index=True)
            salvar_excel(pedidos, ARQ_PEDIDOS)

            st.session_state.carrinho = []
            st.session_state.cliente_selecionado = None
            st.session_state.produto_selecionado = None
            st.session_state.form_key += 1
            st.success(f"Pedido nº {numero} salvo com sucesso!")
            time.sleep(1)
            ir_para("pedidos")


def pedidos_tela():
    topo("Pedidos", "Histórico de pedidos", "📋")

    pedidos = filtrar_por_usuario(ler_excel(ARQ_PEDIDOS))
    resumo = resumo_pedidos(pedidos).sort_values("pedido", ascending=False)

    if len(resumo) == 0:
        st.info("Nenhum pedido lançado.")
        return

    for _, row in resumo.iterrows():
        st.markdown(f"""
        <div class="pedido-card">
            <b>Pedido #{row["pedido"]}</b><br>
            Cliente: {row["cliente"]}<br>
            Vendedor: {row["vendedor"]}<br>
            Data: {row["data"]}<br>
            Total: <span class="valor">{dinheiro(row["total"])}</span><br>
            Status: <b>{row["status"]}</b>
        </div>
        """, unsafe_allow_html=True)

        if str(row["status"]).upper() == "PENDENTE":
            if st.button(f"✏️ EDITAR PEDIDO {row['pedido']}", key=f"edit_{row['pedido']}", use_container_width=True):
                st.session_state.pedido_editando = int(row["pedido"])
                ir_para("editar")


def editar_pedido():
    topo("Editar Pedido", "Alterar pedido pendente", "✏️")

    numero = st.session_state.get("pedido_editando")
    pedidos = ler_excel(ARQ_PEDIDOS)
    dados = pedidos[pedidos["pedido"] == numero].copy()

    if len(dados) == 0:
        st.error("Pedido não encontrado.")
        return

    status = str(dados["status"].iloc[0]).upper()

    if status == "FATURADO" and st.session_state.get("perfil") != "ADMIN":
        st.error("Pedido faturado não pode ser alterado pelo vendedor.")
        return

    st.info(f"Pedido #{numero} - {dados['cliente'].iloc[0]}")

    novos = []

    for idx, row in dados.iterrows():
        abrir_card()
        st.markdown(f"### {row['produto']}")

        c1, c2 = st.columns(2)
        qtd = c1.number_input("Qtd", min_value=0, value=int(row["quantidade"]), step=1, key=f"edit_qtd_{idx}")
        desc = c2.number_input("Desc. %", min_value=0.0, value=safe_float(row["desconto"]), step=1.0, key=f"edit_desc_{idx}")
        excluir = st.checkbox("Excluir item", key=f"exc_{idx}")

        preco = safe_float(row["preco"])
        subtotal = preco * qtd
        total = subtotal - (subtotal * desc / 100)

        st.write(f"Total: **{dinheiro(total)}**")

        if not excluir and qtd > 0:
            item = row.to_dict()
            item["quantidade"] = qtd
            item["desconto"] = desc
            item["subtotal"] = subtotal
            item["total"] = total
            novos.append(item)

        fechar_card()

    if st.button("💾 SALVAR ALTERAÇÕES", use_container_width=True):
        if len(novos) == 0:
            st.warning("Pedido não pode ficar sem itens.")
        else:
            pedidos = pedidos[pedidos["pedido"] != numero]
            pedidos = pd.concat([pedidos, pd.DataFrame(novos)], ignore_index=True)
            salvar_excel(pedidos, ARQ_PEDIDOS)

            st.success("Pedido atualizado.")
            time.sleep(0.8)
            ir_para("pedidos")

    if st.button("⬅️ VOLTAR", use_container_width=True):
        ir_para("pedidos")


def comissao_tela():
    topo("Comissão", "Resumo da comissão", "💰")

    pedidos = filtrar_por_usuario(ler_excel(ARQ_PEDIDOS))

    if len(pedidos):
        pedidos["total"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0)

    vendas = pedidos["total"].sum() if len(pedidos) else 0
    comissao = vendas * st.session_state.get("comissao", COMISSAO_PADRAO)

    st.metric("💲 Vendas", dinheiro(vendas))
    st.metric("💰 Comissão", dinheiro(comissao))


def admin_tela():
    topo("Administração", "Área do administrador", "⚙️")

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso permitido somente para administrador.")
        return

    if st.button("👥 USUÁRIOS", use_container_width=True):
        ir_para("admin_usuarios")

    if st.button("🏪 CLIENTES", use_container_width=True):
        ir_para("admin_clientes")

    if st.button("📦 PRODUTOS", use_container_width=True):
        ir_para("admin_produtos")


def admin_usuarios():
    topo("Usuários", "Cadastro de vendedores", "👥")

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        return

    usuarios = ler_excel(ARQ_USUARIOS)

    with st.form("form_usuario"):
        nome = st.text_input("Nome")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha")
        perfil = st.selectbox("Perfil", ["VENDEDOR", "ADMIN"])
        comissao = st.number_input("Comissão", value=0.07, step=0.01)

        salvar = st.form_submit_button("💾 SALVAR", use_container_width=True)

    if salvar:
        if nome and usuario and senha:
            novo = pd.DataFrame([{
                "usuario": usuario.strip().lower(),
                "senha": senha.strip(),
                "nome": nome.strip(),
                "perfil": perfil,
                "comissao": comissao,
            }])
            usuarios = pd.concat([usuarios, novo], ignore_index=True)
            salvar_excel(usuarios, ARQ_USUARIOS)
            st.success("Usuário cadastrado.")
            time.sleep(0.5)
            st.rerun()
        else:
            st.warning("Preencha todos os campos.")

    st.dataframe(usuarios, use_container_width=True)

    if st.button("⬅️ VOLTAR", use_container_width=True):
        ir_para("admin")


def admin_clientes():
    topo("Clientes", "Cadastro de clientes", "🏪")

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        return

    clientes = ler_excel(ARQ_CLIENTES)

    with st.form("form_cliente"):
        cliente = st.text_input("Cliente")
        cnpj = st.text_input("CNPJ")
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")

        salvar = st.form_submit_button("💾 SALVAR", use_container_width=True)

    if salvar:
        if cliente:
            codigo = 1
            if len(clientes):
                maior = pd.to_numeric(clientes["codigo"], errors="coerce").max()
                codigo = 1 if pd.isna(maior) else int(maior) + 1

            novo = pd.DataFrame([{
                "codigo": codigo,
                "cliente": cliente.strip().upper(),
                "cnpj": cnpj.strip(),
                "telefone": telefone.strip(),
                "cidade": cidade.strip().upper(),
            }])

            clientes = pd.concat([clientes, novo], ignore_index=True)
            salvar_excel(clientes, ARQ_CLIENTES)
            st.success("Cliente cadastrado.")
            time.sleep(0.5)
            st.rerun()
        else:
            st.warning("Informe o nome do cliente.")

    st.dataframe(clientes, use_container_width=True)

    if st.button("⬅️ VOLTAR", use_container_width=True):
        ir_para("admin")


def admin_produtos():
    topo("Produtos", "Cadastro de produtos", "📦")

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        return

    produtos = ler_excel(ARQ_PRODUTOS)

    with st.form("form_produto"):
        codigo = st.text_input("Código")
        produto = st.text_input("Produto")
        un = st.text_input("Unidade", value="UN")
        preco = st.number_input("Preço", min_value=0.0, step=0.01)
        fornecedor = st.text_input("Fornecedor")

        salvar = st.form_submit_button("💾 SALVAR", use_container_width=True)

    if salvar:
        if codigo and produto:
            novo = pd.DataFrame([{
                "codigo": codigo.strip(),
                "produto": produto.strip().upper(),
                "un": un.strip().upper(),
                "preco": preco,
                "fornecedor": fornecedor.strip().upper(),
            }])
            produtos = pd.concat([produtos, novo], ignore_index=True)
            salvar_excel(produtos, ARQ_PRODUTOS)
            st.success("Produto cadastrado.")
            time.sleep(0.5)
            st.rerun()
        else:
            st.warning("Informe código e produto.")

    st.dataframe(produtos, use_container_width=True)

    if st.button("⬅️ VOLTAR", use_container_width=True):
        ir_para("admin")


def mais_tela():
    topo("Mais", "Opções do sistema", "☰")

    st.info(f"Usuário: {st.session_state.get('nome')} | Perfil: {st.session_state.get('perfil')}")

    if st.session_state.get("perfil") == "ADMIN":
        if st.button("⚙️ ADMINISTRAÇÃO", use_container_width=True):
            ir_para("admin")

    if st.button("🚪 SAIR", use_container_width=True):
        st.session_state.clear()
        st.rerun()


# =========================
# APP
# =========================

criar_banco()
css()
iniciar_sessao()
login()

page = st.session_state.page

if page == "dashboard":
    dashboard()
elif page == "novo":
    novo_pedido()
elif page == "pedidos":
    pedidos_tela()
elif page == "editar":
    editar_pedido()
elif page == "comissao":
    comissao_tela()
elif page == "admin":
    admin_tela()
elif page == "admin_usuarios":
    admin_usuarios()
elif page == "admin_clientes":
    admin_clientes()
elif page == "admin_produtos":
    admin_produtos()
elif page == "mais":
    mais_tela()
else:
    dashboard()

menu_nativo()
