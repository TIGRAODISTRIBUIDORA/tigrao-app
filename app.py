import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tigrão App",
    page_icon="🐯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PASTA_DADOS = "dados"
ARQ_CLIENTES = f"{PASTA_DADOS}/clientes.xlsx"
ARQ_PRODUTOS = f"{PASTA_DADOS}/produtos.xlsx"
ARQ_PEDIDOS = f"{PASTA_DADOS}/pedidos.xlsx"
ARQ_USUARIOS = f"{PASTA_DADOS}/usuarios.xlsx"

COMISSAO_PADRAO = 0.07


# =========================
# HTML SEGURO
# =========================

def html(codigo):
    """
    Usa st.html quando disponível.
    Isso evita o problema do Streamlit mostrar <div> como texto na tela.
    """
    try:
        st.html(codigo)
    except Exception:
        st.markdown(codigo, unsafe_allow_html=True)


# =========================
# BANCO
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
# CSS
# =========================

def css():
    html("""
    <style>
    header, footer, [data-testid="stSidebar"] {
        display:none !important;
    }

    [data-testid="stAppViewContainer"] {
        background:#f4f5f7 !important;
    }

    .block-container {
        max-width:480px !important;
        padding:0 12px 110px 12px !important;
        margin:auto !important;
    }

    * {
        font-family:Arial, sans-serif;
        box-sizing:border-box;
    }

    .topo {
        background:#111;
        margin:0 -12px 0 -12px;
        padding:18px 18px 0 18px;
        border-radius:0 0 30px 30px;
        box-shadow:0 8px 24px rgba(0,0,0,.25);
        overflow:hidden;
    }

    .topo-linha {
        display:flex;
        align-items:center;
        justify-content:space-between;
    }

    .hamb {
        color:#ff8500 !important;
        font-size:28px;
        font-weight:1000;
    }

    .logo {
        text-align:center;
        color:white !important;
        font-size:25px;
        font-weight:1000;
        line-height:1;
        letter-spacing:1px;
    }

    .logo-sub {
        color:#ff8500 !important;
        font-size:10px;
        letter-spacing:5px;
        margin-top:5px;
        font-weight:1000;
    }

    .perfil {
        border:2px solid #ff8500;
        border-radius:20px;
        color:white !important;
        padding:7px 9px;
        font-weight:1000;
        font-size:11px;
    }

    .hero {
        margin:16px -18px 0 -18px;
        padding:28px 22px 72px 22px;
        background:linear-gradient(135deg,#ff8500,#ff9d1c);
        position:relative;
        overflow:hidden;
    }

    .hero:after {
        content:"🐯";
        position:absolute;
        right:18px;
        top:0px;
        font-size:120px;
        opacity:.14;
    }

    .hero-title {
        color:#111 !important;
        font-size:31px;
        font-weight:1000;
        margin:0;
        position:relative;
        z-index:2;
    }

    .hero-sub {
        color:#111 !important;
        font-size:16px;
        font-weight:800;
        margin-top:8px;
        position:relative;
        z-index:2;
    }

    .content {
        margin-top:-48px;
        position:relative;
        z-index:5;
    }

    .cards {
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:10px;
    }

    .metric {
        background:white;
        border-radius:20px;
        padding:14px 10px;
        text-align:center;
        box-shadow:0 8px 20px rgba(15,23,42,.12);
        min-height:125px;
    }

    .metric.full {
        grid-column:1 / 3;
    }

    .metric-icon {
        width:48px;
        height:48px;
        background:#111;
        border-radius:15px;
        display:inline-flex;
        align-items:center;
        justify-content:center;
        color:#ff8500 !important;
        font-size:26px;
        margin-bottom:8px;
    }

    .metric-title {
        color:#777 !important;
        font-size:12px;
        font-weight:1000;
    }

    .metric-value {
        color:#111 !important;
        font-size:20px;
        font-weight:1000;
        margin-top:6px;
        word-break:break-word;
    }

    .metric-sub {
        color:#ff8500 !important;
        font-size:12px;
        font-weight:900;
        margin-top:6px;
    }

    .section-title {
        margin-top:24px;
        color:#111 !important;
        font-size:24px;
        font-weight:1000;
    }

    .line-orange {
        width:48px;
        height:4px;
        background:#ff8500;
        border-radius:8px;
        margin:6px 0 12px 0;
    }

    .box {
        background:white;
        border-radius:22px;
        padding:16px;
        box-shadow:0 8px 20px rgba(15,23,42,.10);
        margin-bottom:14px;
    }

    .pedido-card {
        background:white;
        border-radius:20px;
        padding:15px;
        box-shadow:0 8px 20px rgba(15,23,42,.10);
        margin-bottom:12px;
        border-left:5px solid #ff8500;
        color:#111 !important;
    }

    .pedido-card b {
        color:#111 !important;
    }

    .pedido-card small {
        color:#64748b !important;
    }

    .produto-card {
        border:2px solid #ff8500;
        border-radius:18px;
        padding:12px;
        margin:10px 0;
        background:white;
        font-weight:800;
        color:#111;
    }

    .produto-card b {
        color:#0b8de3 !important;
    }

    .total-item {
        background:#0b8de3;
        border-radius:20px;
        padding:16px;
        text-align:center;
        margin:12px 0;
    }

    .total-label {
        color:white !important;
        font-size:12px;
        font-weight:1000;
    }

    .total-value {
        color:white !important;
        font-size:30px;
        font-weight:1000;
        margin-top:6px;
    }

    .resumo {
        background:#111827;
        border-radius:20px;
        padding:16px;
        margin-top:14px;
    }

    .resumo-row {
        display:flex;
        justify-content:space-between;
        font-weight:1000;
        margin-bottom:9px;
    }

    .resumo-row span {
        color:white !important;
    }

    .resumo-total {
        border-top:1px solid rgba(255,255,255,.25);
        padding-top:11px;
        font-size:20px;
    }

    .tigrao-nav {
        position:fixed;
        bottom:0;
        left:50%;
        transform:translateX(-50%);
        width:100%;
        max-width:480px;
        background:#111;
        border-radius:24px 24px 0 0;
        padding:8px 6px 10px 6px;
        z-index:999999;
        display:flex;
        flex-direction:row;
        justify-content:space-around;
        align-items:center;
        box-shadow:0 -8px 24px rgba(0,0,0,.35);
    }

    .tigrao-nav a {
        text-decoration:none !important;
        color:white !important;
        font-size:10px;
        font-weight:900;
        text-align:center;
        flex:1;
        padding:5px 0;
        border-radius:14px;
        display:block;
        line-height:1.15;
    }

    .tigrao-nav .ico {
        font-size:22px;
        display:block;
        line-height:1.1;
        margin-bottom:2px;
    }

    .tigrao-nav .ativo {
        background:#ff8500;
        color:#111 !important;
    }

    .stButton > button {
        border-radius:16px !important;
        min-height:46px !important;
        font-weight:900 !important;
        border:none !important;
        background:#0b8de3 !important;
        color:white !important;
    }

    input, textarea {
        border-radius:16px !important;
        min-height:48px !important;
        font-weight:800 !important;
    }

    div[data-baseweb="select"] > div {
        border-radius:16px !important;
        min-height:48px !important;
    }

    div[data-testid="stDataFrame"] {
        border-radius:18px !important;
        overflow:hidden !important;
    }

    div[data-testid="stHorizontalBlock"] .stButton > button {
        min-height:44px !important;
        font-size:20px !important;
        padding:4px !important;
    }
    </style>
    """)


# =========================
# NAVEGAÇÃO
# =========================

def get_page():
    return st.session_state.get("page", "dashboard")


def ir_para(page):
    st.session_state.page = page
    st.rerun()


def menu_html():
    """
    Menu feito com botões do Streamlit, sem links HTML.
    Isso corrige o problema de deslogar ao clicar no menu.
    """
    html("""
    <div style="height:14px;"></div>
    """)

    col1, col2, col3, col4, col5 = st.columns(5, gap="small")

    atual = get_page()

    def label(pagina, icone):
        return f"{icone}" if atual != pagina else f"✅{icone}"

    with col1:
        if st.button(label("dashboard", "🏠"), key="nav_dashboard", use_container_width=True):
            ir_para("dashboard")

    with col2:
        if st.button(label("novo", "🛒"), key="nav_novo", use_container_width=True):
            ir_para("novo")

    with col3:
        if st.button(label("pedidos", "📋"), key="nav_pedidos", use_container_width=True):
            ir_para("pedidos")

    with col4:
        if st.button(label("comissao", "💰"), key="nav_comissao", use_container_width=True):
            ir_para("comissao")

    with col5:
        if st.button(label("mais", "☰"), key="nav_mais", use_container_width=True):
            ir_para("mais")


def topo(titulo, subtitulo):
    perfil = st.session_state.get("perfil", "VENDEDOR")

    html(f"""
    <div class="topo">
        <div class="topo-linha">
            <div class="hamb">☰</div>
            <div class="logo">
                🐯 TIGRÃO
                <div class="logo-sub">DISTRIBUIDORA</div>
            </div>
            <div class="perfil">👤 {perfil}</div>
        </div>

        <div class="hero">
            <div class="hero-title">{titulo}</div>
            <div class="hero-sub">{subtitulo}</div>
        </div>
    </div>
    <div class="content">
    """)


def fim():
    html("</div>")


# =========================
# LOGIN
# =========================

def login():
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if st.session_state.logado:
        return

    html("""
    <div style="height:45px;"></div>
    <div style="text-align:center;">
        <div style="font-size:70px;">🐯</div>
        <div style="font-size:44px;font-weight:1000;color:#111;">TIGRÃO</div>
        <div style="color:#ff8500;font-weight:1000;letter-spacing:5px;margin-top:8px;">DISTRIBUIDORA</div>
    </div>
    <div style="height:25px;"></div>
    """)

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
            st.session_state.carrinho = []

            st.session_state.page = "dashboard"
            st.rerun()

    st.stop()


# =========================
# TELAS
# =========================

def dashboard():
    topo("Dashboard", "Resumo da operação")

    pedidos = filtrar_por_usuario(ler_excel(ARQ_PEDIDOS))

    if len(pedidos):
        pedidos["total"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0)

    total_pedidos = pedidos["pedido"].nunique() if len(pedidos) else 0
    total_vendas = pedidos["total"].sum() if len(pedidos) else 0
    total_comissao = total_vendas * st.session_state.get("comissao", COMISSAO_PADRAO)

    html(f"""
    <div class="cards">
        <div class="metric">
            <div class="metric-icon">📋</div>
            <div class="metric-title">PEDIDOS</div>
            <div class="metric-value">{total_pedidos}</div>
            <div class="metric-sub">Lançados</div>
        </div>

        <div class="metric">
            <div class="metric-icon">💰</div>
            <div class="metric-title">COMISSÃO</div>
            <div class="metric-value">{dinheiro(total_comissao)}</div>
            <div class="metric-sub">7%</div>
        </div>

        <div class="metric full">
            <div class="metric-icon">💲</div>
            <div class="metric-title">VENDAS</div>
            <div class="metric-value">{dinheiro(total_vendas)}</div>
            <div class="metric-sub">Total vendido</div>
        </div>
    </div>
    """)

    html('<div class="section-title">🕘 Últimos pedidos</div><div class="line-orange"></div>')

    resumo = resumo_pedidos(pedidos).sort_values("pedido", ascending=False).head(5)

    if len(resumo) == 0:
        st.info("Nenhum pedido lançado.")
    else:
        for _, row in resumo.iterrows():
            html(f"""
            <div class="pedido-card">
                <b>Pedido #{row["pedido"]}</b><br>
                {row["cliente"]}<br>
                <small>{row["data"]}</small><br>
                <b style="color:#ff8500">{dinheiro(row["total"])}</b> — {row["status"]}
            </div>
            """)

    fim()


def novo_pedido():
    topo("Novo Pedido", "Lançamento pelo celular")

    clientes = ler_excel(ARQ_CLIENTES)
    produtos = ler_excel(ARQ_PRODUTOS)

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    html('<div class="box">')

    busca_cliente = st.text_input("Buscar cliente", placeholder="Digite nome, código ou iniciais")

    clientes_filtrados = clientes.copy()
    if len(clientes_filtrados) and busca_cliente.strip():
        termo = busca_cliente.strip().lower()
        clientes_filtrados = clientes[
            clientes["cliente"].astype(str).str.lower().str.contains(termo, na=False) |
            clientes["codigo"].astype(str).str.lower().str.contains(termo, na=False) |
            clientes["cnpj"].astype(str).str.lower().str.contains(termo, na=False)
        ]

    lista_clientes = clientes_filtrados["cliente"].astype(str).tolist() if len(clientes_filtrados) else ["CLIENTE NÃO ENCONTRADO"]
    cliente = st.selectbox("Cliente", lista_clientes)

    busca_produto = st.text_input("Buscar produto", placeholder="Digite código ou nome do produto")

    produtos_filtrados = produtos.copy()
    if len(produtos_filtrados) and busca_produto.strip():
        termo = busca_produto.strip().lower()
        produtos_filtrados = produtos[
            produtos["produto"].astype(str).str.lower().str.contains(termo, na=False) |
            produtos["codigo"].astype(str).str.lower().str.contains(termo, na=False)
        ]

    opcoes = ["Selecione o produto"]

    for _, row in produtos_filtrados.iterrows():
        opcoes.append(f'{row["codigo"]} - {row["produto"]} | {dinheiro(row["preco"])}')

    produto_txt = st.selectbox("Produto", opcoes)

    produto = None
    if produto_txt != "Selecione o produto":
        idx = opcoes.index(produto_txt) - 1
        produto = produtos_filtrados.iloc[idx].to_dict()

    if produto:
        html(f"""
        <div class="produto-card">
            <b>{produto["produto"]}</b><br>
            Código: {produto["codigo"]}<br>
            Fornecedor: {produto.get("fornecedor", "")}<br>
            Preço: <b>{dinheiro(produto["preco"])}</b>
        </div>
        """)

    qtd = st.number_input("Quantidade", min_value=0, value=0, step=1)
    desc = st.number_input("% Desconto", min_value=0.0, value=0.0, step=1.0)

    preco = safe_float(produto["preco"]) if produto else 0
    subtotal = preco * qtd
    total_item = subtotal - (subtotal * desc / 100)

    html(f"""
    <div class="total-item">
        <div class="total-label">TOTAL DO ITEM</div>
        <div class="total-value">{dinheiro(total_item)}</div>
    </div>
    """)

    if st.button("➕ ADICIONAR AO CARRINHO", use_container_width=True):
        if not produto:
            st.warning("Selecione um produto.")
        elif qtd <= 0:
            st.warning("Informe a quantidade.")
        elif cliente == "CLIENTE NÃO ENCONTRADO":
            st.warning("Selecione um cliente válido.")
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
            st.success("Produto adicionado.")
            time.sleep(0.4)
            st.rerun()

    html('</div>')

    carrinho(cliente)

    fim()


def carrinho(cliente):
    html('<div class="section-title">🛒 Carrinho</div><div class="line-orange"></div>')

    if len(st.session_state.carrinho) == 0:
        st.info("Nenhum produto adicionado.")
        return

    for i, item in enumerate(st.session_state.carrinho):
        html(f"""
        <div class="pedido-card">
            <b>{item["produto"]}</b><br>
            Qtd: {item["quantidade"]} | Unit: {dinheiro(item["preco"])}<br>
            Total: <b style="color:#ff8500">{dinheiro(item["total"])}</b>
        </div>
        """)

        if st.button(f"🗑 Remover item {i+1}", key=f"del_{i}", use_container_width=True):
            st.session_state.carrinho.pop(i)
            st.rerun()

    subtotal = sum(safe_float(x["subtotal"]) for x in st.session_state.carrinho)
    total = sum(safe_float(x["total"]) for x in st.session_state.carrinho)
    desconto = subtotal - total

    html(f"""
    <div class="resumo">
        <div class="resumo-row"><span>Subtotal</span><span>{dinheiro(subtotal)}</span></div>
        <div class="resumo-row"><span>Desconto</span><span>{dinheiro(desconto)}</span></div>
        <div class="resumo-row resumo-total"><span>Total</span><span>{dinheiro(total)}</span></div>
    </div>
    """)

    if st.button("✅ FINALIZAR PEDIDO", use_container_width=True):
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
        st.success(f"Pedido nº {numero} salvo com sucesso!")
        time.sleep(1)
        ir_para("pedidos")

    if st.button("🧹 LIMPAR CARRINHO", use_container_width=True):
        st.session_state.carrinho = []
        st.rerun()


def pedidos_tela():
    topo("Pedidos", "Histórico de pedidos")

    pedidos = filtrar_por_usuario(ler_excel(ARQ_PEDIDOS))
    resumo = resumo_pedidos(pedidos).sort_values("pedido", ascending=False)

    if len(resumo) == 0:
        st.info("Nenhum pedido lançado.")
    else:
        for _, row in resumo.iterrows():
            html(f"""
            <div class="pedido-card">
                <b>Pedido #{row["pedido"]}</b><br>
                Cliente: {row["cliente"]}<br>
                Vendedor: {row["vendedor"]}<br>
                Data: {row["data"]}<br>
                Total: <b style="color:#ff8500">{dinheiro(row["total"])}</b><br>
                Status: <b>{row["status"]}</b>
            </div>
            """)

            if str(row["status"]).upper() == "PENDENTE":
                if st.button(f"✏️ Editar pedido {row['pedido']}", key=f"edit_{row['pedido']}", use_container_width=True):
                    st.session_state.pedido_editando = int(row["pedido"])
                    ir_para("editar")

    fim()


def editar_pedido():
    topo("Editar Pedido", "Alterar pedido pendente")

    numero = st.session_state.get("pedido_editando")
    pedidos = ler_excel(ARQ_PEDIDOS)
    dados = pedidos[pedidos["pedido"] == numero].copy()

    if len(dados) == 0:
        st.error("Pedido não encontrado.")
        fim()
        return

    status = str(dados["status"].iloc[0]).upper()

    if status == "FATURADO" and st.session_state.get("perfil") != "ADMIN":
        st.error("Pedido faturado não pode ser alterado pelo vendedor.")
        fim()
        return

    st.info(f"Pedido #{numero} - {dados['cliente'].iloc[0]}")

    novos = []

    for idx, row in dados.iterrows():
        st.markdown(f"### {row['produto']}")

        qtd = st.number_input("Quantidade", min_value=0, value=int(row["quantidade"]), step=1, key=f"qtd_{idx}")
        desc = st.number_input("% Desconto", min_value=0.0, value=safe_float(row["desconto"]), step=1.0, key=f"desc_{idx}")
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

        st.divider()

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

    fim()


def comissao_tela():
    topo("Comissão", "Resumo da comissão")

    pedidos = filtrar_por_usuario(ler_excel(ARQ_PEDIDOS))

    if len(pedidos):
        pedidos["total"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0)

    vendas = pedidos["total"].sum() if len(pedidos) else 0
    comissao = vendas * st.session_state.get("comissao", COMISSAO_PADRAO)

    html(f"""
    <div class="cards">
        <div class="metric full">
            <div class="metric-icon">💲</div>
            <div class="metric-title">VENDAS</div>
            <div class="metric-value">{dinheiro(vendas)}</div>
            <div class="metric-sub">Total vendido</div>
        </div>

        <div class="metric full">
            <div class="metric-icon">💰</div>
            <div class="metric-title">COMISSÃO</div>
            <div class="metric-value">{dinheiro(comissao)}</div>
            <div class="metric-sub">7%</div>
        </div>
    </div>
    """)

    fim()


def admin_tela():
    topo("Administração", "Área do administrador")

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso permitido somente para administrador.")
        fim()
        return

    html('<div class="box">')

    if st.button("👥 Usuários", use_container_width=True):
        ir_para("admin_usuarios")

    if st.button("🏪 Clientes", use_container_width=True):
        ir_para("admin_clientes")

    if st.button("📦 Produtos", use_container_width=True):
        ir_para("admin_produtos")

    html('</div>')

    fim()


def admin_usuarios():
    topo("Usuários", "Cadastro de vendedores")

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        fim()
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

    fim()


def admin_clientes():
    topo("Clientes", "Cadastro de clientes")

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        fim()
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

    fim()


def admin_produtos():
    topo("Produtos", "Cadastro de produtos")

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        fim()
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

    fim()


def mais_tela():
    topo("Mais", "Opções do sistema")

    html('<div class="box">')
    st.write(f"**Usuário:** {st.session_state.get('nome')}")
    st.write(f"**Perfil:** {st.session_state.get('perfil')}")
    html('</div>')

    if st.session_state.get("perfil") == "ADMIN":
        if st.button("⚙️ ADMINISTRAÇÃO", use_container_width=True):
            ir_para("admin")

    if st.button("🚪 SAIR", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    fim()


# =========================
# APP
# =========================

criar_banco()
css()
login()

page = get_page()

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

menu_html()
