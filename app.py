import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tigrão App",
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
        usuarios = pd.DataFrame([
            {"usuario": "admin", "senha": "admin123", "nome": "Administrador", "perfil": "ADMIN", "comissao": 0.07},
            {"usuario": "vendedor", "senha": "123", "nome": "Vendedor", "perfil": "VENDEDOR", "comissao": 0.07},
        ])
        usuarios.to_excel(ARQ_USUARIOS, index=False)

    if not os.path.exists(ARQ_CLIENTES):
        clientes = pd.DataFrame([
            {"codigo": 1, "cliente": "NELSON DAS GALAXIAS", "cnpj": "", "telefone": "", "cidade": ""},
            {"codigo": 2, "cliente": "DROGANNE MEDICAMENTOS E PERFUMARIA LTDA", "cnpj": "", "telefone": "", "cidade": ""},
            {"codigo": 3, "cliente": "NATURA TERRA COMERCIO E SERVICOS LTDA", "cnpj": "", "telefone": "", "cidade": ""},
        ])
        clientes.to_excel(ARQ_CLIENTES, index=False)

    if not os.path.exists(ARQ_PRODUTOS):
        produtos = pd.DataFrame([
            {"codigo": "68.0", "produto": "BENETONICO 500M", "un": "UN", "preco": 10.21, "fornecedor": "ARTE NATIVA"},
            {"codigo": "103.0", "produto": "APIS FRESH SPRAY EXTRA FORTE 35ML", "un": "UN", "preco": 5.82, "fornecedor": "ARTE NATIVA"},
            {"codigo": "178.0", "produto": "BALDONI EXTRATO DE PROPOLIS VERDE 30ML", "un": "UN", "preco": 20.89, "fornecedor": "BALDONI"},
        ])
        produtos.to_excel(ARQ_PRODUTOS, index=False)

    if not os.path.exists(ARQ_PEDIDOS):
        pedidos = pd.DataFrame(columns=[
            "pedido", "data", "vendedor", "cliente", "codigo", "produto",
            "un", "quantidade", "preco", "desconto", "subtotal", "total", "status"
        ])
        pedidos.to_excel(ARQ_PEDIDOS, index=False)


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

    if pd.isna(maior):
        return 1

    return int(maior) + 1


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


# =========================
# CSS
# =========================

def css():
    st.markdown("""
    <style>
    header, footer, [data-testid="stSidebar"] {
        display:none !important;
    }

    [data-testid="stAppViewContainer"] {
        background:#f4f5f7 !important;
    }

    .block-container {
        max-width:980px !important;
        padding:0 0 115px 0 !important;
    }

    * {
        font-family:Arial, sans-serif;
        box-sizing:border-box;
    }

    .topo {
        background:#111;
        padding:22px 26px 0 26px;
        border-radius:0 0 34px 34px;
        box-shadow:0 8px 24px rgba(0,0,0,.25);
        overflow:hidden;
    }

    .topo-linha {
        display:flex;
        align-items:center;
        justify-content:space-between;
        color:white;
    }

    .hamb {
        color:#ff8500 !important;
        font-size:34px;
        font-weight:1000;
    }

    .logo {
        text-align:center;
        color:white !important;
        font-size:32px;
        font-weight:1000;
        letter-spacing:1px;
        line-height:1;
    }

    .logo-sub {
        color:#ff8500 !important;
        font-size:12px;
        letter-spacing:6px;
        margin-top:5px;
        font-weight:1000;
    }

    .perfil {
        border:3px solid #ff8500;
        border-radius:26px;
        color:white !important;
        padding:9px 12px;
        font-weight:1000;
        font-size:14px;
    }

    .hero {
        margin:20px -26px 0 -26px;
        padding:38px 36px 94px 36px;
        background:linear-gradient(135deg,#ff8500,#ff9d1c);
        position:relative;
        overflow:hidden;
    }

    .hero:after {
        content:"🐯";
        position:absolute;
        right:28px;
        top:5px;
        font-size:170px;
        opacity:.14;
    }

    .hero-title {
        color:#111 !important;
        font-size:44px;
        font-weight:1000;
        margin:0;
        position:relative;
        z-index:2;
    }

    .hero-sub {
        color:#111 !important;
        font-size:21px;
        font-weight:700;
        margin-top:10px;
        position:relative;
        z-index:2;
    }

    .content {
        padding:0 24px;
        margin-top:-62px;
        position:relative;
        z-index:5;
    }

    .cards {
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:16px;
    }

    .metric {
        background:white;
        border-radius:24px;
        padding:24px 14px;
        text-align:center;
        box-shadow:0 8px 24px rgba(15,23,42,.12);
        min-height:185px;
    }

    .metric-icon {
        width:76px;
        height:76px;
        background:#111;
        border-radius:20px;
        display:inline-flex;
        align-items:center;
        justify-content:center;
        color:#ff8500 !important;
        font-size:38px;
        margin-bottom:14px;
    }

    .metric-title {
        color:#777 !important;
        font-size:16px;
        font-weight:1000;
    }

    .metric-value {
        color:#111 !important;
        font-size:28px;
        font-weight:1000;
        margin-top:10px;
    }

    .metric-sub {
        color:#ff8500 !important;
        font-size:15px;
        font-weight:900;
        margin-top:10px;
    }

    .section-title {
        margin-top:34px;
        color:#111 !important;
        font-size:30px;
        font-weight:1000;
    }

    .line-orange {
        width:58px;
        height:4px;
        background:#ff8500;
        border-radius:8px;
        margin:8px 0 16px 0;
    }

    .box {
        background:white;
        border-radius:24px;
        padding:20px;
        box-shadow:0 8px 24px rgba(15,23,42,.10);
        margin-bottom:18px;
    }

    .produto-card {
        border:2px solid #ff8500;
        border-radius:18px;
        padding:14px;
        margin:12px 0;
        background:white;
        font-weight:800;
        color:#111;
    }

    .total-item {
        background:#0b8de3;
        border-radius:22px;
        padding:18px;
        text-align:center;
        margin:14px 0;
    }

    .total-item div {
        color:white !important;
    }

    .total-label {
        font-size:13px;
        font-weight:1000;
    }

    .total-value {
        font-size:34px;
        font-weight:1000;
        margin-top:8px;
    }

    .resumo {
        background:#111827;
        border-radius:22px;
        padding:18px;
        margin-top:16px;
    }

    .resumo-row {
        display:flex;
        justify-content:space-between;
        font-weight:1000;
        margin-bottom:10px;
        color:white;
    }

    .resumo-row span {
        color:white !important;
    }

    .resumo-total {
        border-top:1px solid rgba(255,255,255,.25);
        padding-top:12px;
        font-size:22px;
    }

    .bottom-space {
        height:95px;
    }

    .st-key-bottom_nav {
        position:fixed;
        left:50%;
        bottom:0;
        transform:translateX(-50%);
        width:100%;
        max-width:980px;
        background:#111;
        border-radius:28px 28px 0 0;
        padding:10px 18px 14px 18px;
        z-index:99999;
        box-shadow:0 -8px 24px rgba(0,0,0,.28);
    }

    .stButton > button {
        border-radius:16px !important;
        min-height:46px !important;
        font-weight:900 !important;
        border:none !important;
        background:#0b8de3 !important;
        color:white !important;
    }

    .st-key-bottom_nav .stButton > button {
        background:transparent !important;
        color:white !important;
        box-shadow:none !important;
        font-size:13px !important;
        padding:4px !important;
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

    @media(max-width:720px) {
        .block-container {
            max-width:100% !important;
        }

        .topo {
            padding:20px 18px 0 18px;
            border-radius:0 0 30px 30px;
        }

        .logo {
            font-size:24px;
        }

        .logo-sub {
            font-size:10px;
            letter-spacing:5px;
        }

        .perfil {
            font-size:12px;
            padding:8px 9px;
        }

        .hero {
            margin:18px -18px 0 -18px;
            padding:34px 26px 86px 26px;
        }

        .hero-title {
            font-size:36px;
        }

        .hero-sub {
            font-size:18px;
        }

        .content {
            padding:0 18px;
            margin-top:-60px;
        }

        .cards {
            grid-template-columns:1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)


# =========================
# LOGIN
# =========================

def login():
    if "logado" not in st.session_state:
        st.session_state.logado = False

    if st.session_state.logado:
        return

    st.markdown("""
    <div style="height:40px;"></div>
    <div style="text-align:center;">
        <div style="font-size:66px;">🐯</div>
        <div style="font-size:48px;font-weight:1000;color:#111;">TIGRÃO</div>
        <div style="color:#ff8500;font-weight:1000;letter-spacing:5px;margin-top:8px;">DISTRIBUIDORA</div>
    </div>
    <div style="height:25px;"></div>
    """, unsafe_allow_html=True)

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("ENTRAR", use_container_width=True):
        usuarios = ler_excel(ARQ_USUARIOS)

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
            st.session_state.menu = "Dashboard"
            st.session_state.carrinho = []
            st.session_state.form_key = 0
            st.rerun()

    st.stop()


# =========================
# UI
# =========================

def topo(titulo, subtitulo):
    perfil = st.session_state.get("perfil", "VENDEDOR")

    st.markdown(f"""
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
    """, unsafe_allow_html=True)


def abrir_conteudo():
    st.markdown('<div class="content">', unsafe_allow_html=True)


def fechar_conteudo():
    st.markdown('</div>', unsafe_allow_html=True)


def mudar_menu(nome):
    st.session_state.menu = nome
    st.rerun()


def menu_inferior():
    with st.container(key="bottom_nav"):
        itens = [
            ("Dashboard", "🏠 Dashboard"),
            ("Novo Pedido", "🛒 Novo"),
            ("Pedidos", "📋 Pedidos"),
            ("Comissão", "💰 Comissão"),
            ("Mais", "⋯ Mais"),
        ]

        cols = st.columns(len(itens))

        for col, (destino, texto) in zip(cols, itens):
            with col:
                if st.button(texto, key=f"nav_{destino}", use_container_width=True):
                    mudar_menu(destino)


# =========================
# TELAS PRINCIPAIS
# =========================

def dashboard():
    topo("Dashboard", "Visão geral da operação")
    abrir_conteudo()

    pedidos = ler_excel(ARQ_PEDIDOS)
    vendedor = st.session_state.get("nome", "")
    perfil = st.session_state.get("perfil", "VENDEDOR")

    if len(pedidos) and perfil != "ADMIN":
        pedidos_view = pedidos[pedidos["vendedor"].astype(str) == vendedor].copy()
    else:
        pedidos_view = pedidos.copy()

    if len(pedidos_view):
        pedidos_view["total"] = pd.to_numeric(pedidos_view["total"], errors="coerce").fillna(0)

    total_pedidos = pedidos_view["pedido"].nunique() if len(pedidos_view) else 0
    total_vendas = pedidos_view["total"].sum() if len(pedidos_view) else 0
    total_comissao = total_vendas * st.session_state.get("comissao", COMISSAO_PADRAO)

    st.markdown(f"""
    <div class="cards">
        <div class="metric">
            <div class="metric-icon">📋</div>
            <div class="metric-title">PEDIDOS</div>
            <div class="metric-value">{total_pedidos}</div>
            <div class="metric-sub">Total de pedidos</div>
        </div>
        <div class="metric">
            <div class="metric-icon">💲</div>
            <div class="metric-title">VENDAS</div>
            <div class="metric-value">{dinheiro(total_vendas)}</div>
            <div class="metric-sub">Valor vendido</div>
        </div>
        <div class="metric">
            <div class="metric-icon">%</div>
            <div class="metric-title">COMISSÃO</div>
            <div class="metric-value">{dinheiro(total_comissao)}</div>
            <div class="metric-sub">Comissão 7%</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">🕘 Últimos pedidos</div><div class="line-orange"></div>', unsafe_allow_html=True)

    resumo = resumo_pedidos(pedidos_view).tail(6).sort_values("pedido", ascending=False)

    if len(resumo) == 0:
        st.info("Nenhum pedido lançado.")
    else:
        for _, row in resumo.iterrows():
            st.markdown(f"""
            <div class="box">
                <b>Pedido #{row["pedido"]}</b><br>
                Cliente: {row["cliente"]}<br>
                Data: {row["data"]}<br>
                Total: <b style="color:#ff8500">{dinheiro(row["total"])}</b><br>
                Status: <b>{row["status"]}</b>
            </div>
            """, unsafe_allow_html=True)

    fechar_conteudo()


def novo_pedido():
    topo("Novo Pedido", "Lançamento rápido de pedidos")
    abrir_conteudo()

    clientes = ler_excel(ARQ_CLIENTES)
    produtos = ler_excel(ARQ_PRODUTOS)

    if "carrinho" not in st.session_state:
        st.session_state.carrinho = []

    if "form_key" not in st.session_state:
        st.session_state.form_key = 0

    st.markdown('<div class="box">', unsafe_allow_html=True)

    lista_clientes = clientes["cliente"].astype(str).tolist() if len(clientes) else ["CLIENTE PADRÃO"]
    cliente = st.selectbox("Cliente", lista_clientes, key="cliente_pedido")

    fornecedores = ["Todos"]
    if len(produtos) and "fornecedor" in produtos.columns:
        fornecedores += sorted(produtos["fornecedor"].fillna("").astype(str).unique().tolist())

    fornecedor = st.selectbox("Fornecedor", fornecedores, key="fornecedor_pedido")

    if fornecedor != "Todos":
        produtos_filtrados = produtos[produtos["fornecedor"].astype(str) == fornecedor].copy()
    else:
        produtos_filtrados = produtos.copy()

    opcoes_produtos = ["Selecione o produto"]

    for _, row in produtos_filtrados.iterrows():
        opcoes_produtos.append(f'{row["codigo"]} - {row["produto"]} | {dinheiro(row["preco"])}')

    produto_txt = st.selectbox("Produto", opcoes_produtos, key=f"produto_pedido_{st.session_state.form_key}")

    produto = None
    if produto_txt != "Selecione o produto":
        idx = opcoes_produtos.index(produto_txt) - 1
        produto = produtos_filtrados.iloc[idx].to_dict()

    if produto:
        st.markdown(f"""
        <div class="produto-card">
            <b>{produto["produto"]}</b><br>
            Código: {produto["codigo"]}<br>
            Fornecedor: {produto.get("fornecedor", "")}<br>
            Preço: <b>{dinheiro(produto["preco"])}</b>
        </div>
        """, unsafe_allow_html=True)

    qtd = st.number_input("Quantidade", min_value=0, value=0, step=1, key=f"qtd_pedido_{st.session_state.form_key}")
    desc = st.number_input("% Desconto", min_value=0.0, value=0.0, step=1.0, key=f"desc_pedido_{st.session_state.form_key}")

    preco = safe_float(produto["preco"]) if produto else 0
    subtotal = preco * qtd
    total = subtotal - (subtotal * desc / 100)

    st.markdown(f"""
    <div class="total-item">
        <div class="total-label">TOTAL DO ITEM</div>
        <div class="total-value">{dinheiro(total)}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕ ADICIONAR AO CARRINHO", use_container_width=True):
        if not produto:
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
                "total": total,
            })
            st.session_state.form_key += 1
            st.success("Produto adicionado.")
            time.sleep(0.3)
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    carrinho(cliente)

    fechar_conteudo()


def carrinho(cliente):
    st.markdown('<div class="section-title">📦 Carrinho</div><div class="line-orange"></div>', unsafe_allow_html=True)

    if len(st.session_state.carrinho) == 0:
        st.info("Nenhum produto adicionado.")
        return

    st.markdown('<div class="box">', unsafe_allow_html=True)

    for i, item in enumerate(st.session_state.carrinho):
        col1, col2, col3, col4, col5 = st.columns([0.4, 2.4, 0.7, 1, 1])

        with col1:
            if st.button("🗑", key=f"del_{i}"):
                st.session_state.carrinho.pop(i)
                st.rerun()

        with col2:
            st.write(f"**{item['produto']}**")
            st.caption(f"Cód: {item['codigo']}")

        with col3:
            st.write(int(item["quantidade"]))

        with col4:
            st.write(dinheiro(item["preco"]))

        with col5:
            st.write(dinheiro(item["total"]))

        st.divider()

    st.markdown("</div>", unsafe_allow_html=True)

    subtotal = sum([safe_float(x["subtotal"]) for x in st.session_state.carrinho])
    total = sum([safe_float(x["total"]) for x in st.session_state.carrinho])
    desconto = subtotal - total

    st.markdown(f"""
    <div class="resumo">
        <div class="resumo-row"><span>Subtotal</span><span>{dinheiro(subtotal)}</span></div>
        <div class="resumo-row"><span>Desconto</span><span>{dinheiro(desconto)}</span></div>
        <div class="resumo-row resumo-total"><span>Total</span><span>{dinheiro(total)}</span></div>
    </div>
    """, unsafe_allow_html=True)

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
        st.session_state.form_key += 1

        st.success(f"Pedido nº {numero} salvo com sucesso!")
        time.sleep(0.8)
        st.rerun()

    if st.button("🧹 LIMPAR CARRINHO", use_container_width=True):
        st.session_state.carrinho = []
        st.session_state.form_key += 1
        st.rerun()


def pedidos_tela():
    topo("Pedidos", "Pedidos lançados")
    abrir_conteudo()

    pedidos = ler_excel(ARQ_PEDIDOS)
    vendedor = st.session_state.get("nome", "")
    perfil = st.session_state.get("perfil", "VENDEDOR")

    if len(pedidos) and perfil != "ADMIN":
        pedidos = pedidos[pedidos["vendedor"].astype(str) == vendedor].copy()

    resumo = resumo_pedidos(pedidos).sort_values("pedido", ascending=False)

    if len(resumo) == 0:
        st.info("Nenhum pedido lançado.")
        fechar_conteudo()
        return

    for _, row in resumo.iterrows():
        status = str(row["status"]).upper()

        st.markdown(f"""
        <div class="box">
            <b>Pedido #{row["pedido"]}</b><br>
            Cliente: {row["cliente"]}<br>
            Data: {row["data"]}<br>
            Vendedor: {row["vendedor"]}<br>
            Total: <b style="color:#ff8500">{dinheiro(row["total"])}</b><br>
            Status: <b>{status}</b>
        </div>
        """, unsafe_allow_html=True)

        if status == "PENDENTE":
            if st.button(f"✏️ Editar pedido {row['pedido']}", key=f"edit_{row['pedido']}", use_container_width=True):
                st.session_state.pedido_editando = int(row["pedido"])
                st.session_state.menu = "Editar Pedido"
                st.rerun()

    fechar_conteudo()


def editar_pedido():
    topo("Editar Pedido", "Alterar pedido pendente")
    abrir_conteudo()

    numero = st.session_state.get("pedido_editando")
    pedidos = ler_excel(ARQ_PEDIDOS)
    dados = pedidos[pedidos["pedido"] == numero].copy()

    if len(dados) == 0:
        st.error("Pedido não encontrado.")
        fechar_conteudo()
        return

    status = str(dados["status"].iloc[0]).upper()

    if status == "FATURADO" and st.session_state.get("perfil") != "ADMIN":
        st.error("Pedido faturado não pode ser alterado pelo vendedor.")
        fechar_conteudo()
        return

    st.info(f"Pedido #{numero} - {dados['cliente'].iloc[0]}")

    novos = []

    for idx, row in dados.iterrows():
        st.markdown(f"### {row['produto']}")

        qtd = st.number_input("Quantidade", min_value=0, value=int(row["quantidade"]), step=1, key=f"edit_qtd_{idx}")
        desc = st.number_input("% Desconto", min_value=0.0, value=safe_float(row["desconto"]), step=1.0, key=f"edit_desc_{idx}")

        preco = safe_float(row["preco"])
        subtotal = preco * qtd
        total = subtotal - (subtotal * desc / 100)

        st.write(f"Total: **{dinheiro(total)}**")

        excluir = st.checkbox("Excluir item", key=f"excluir_{idx}")

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
            st.warning("Não é possível salvar pedido sem itens.")
            return

        pedidos = pedidos[pedidos["pedido"] != numero]
        pedidos = pd.concat([pedidos, pd.DataFrame(novos)], ignore_index=True)
        salvar_excel(pedidos, ARQ_PEDIDOS)

        st.success("Pedido atualizado.")
        time.sleep(0.8)
        st.session_state.menu = "Pedidos"
        st.rerun()

    if st.button("⬅️ VOLTAR", use_container_width=True):
        st.session_state.menu = "Pedidos"
        st.rerun()

    fechar_conteudo()


def comissao_tela():
    topo("Comissão", "Resumo da comissão")
    abrir_conteudo()

    pedidos = ler_excel(ARQ_PEDIDOS)
    vendedor = st.session_state.get("nome", "")

    if len(pedidos) and st.session_state.get("perfil") != "ADMIN":
        pedidos = pedidos[pedidos["vendedor"].astype(str) == vendedor].copy()

    if len(pedidos):
        pedidos["total"] = pd.to_numeric(pedidos["total"], errors="coerce").fillna(0)

    vendas = pedidos["total"].sum() if len(pedidos) else 0
    comissao = vendas * st.session_state.get("comissao", COMISSAO_PADRAO)

    st.markdown(f"""
    <div class="cards">
        <div class="metric">
            <div class="metric-icon">💲</div>
            <div class="metric-title">VENDAS</div>
            <div class="metric-value">{dinheiro(vendas)}</div>
            <div class="metric-sub">Total vendido</div>
        </div>
        <div class="metric">
            <div class="metric-icon">%</div>
            <div class="metric-title">COMISSÃO</div>
            <div class="metric-value">{dinheiro(comissao)}</div>
            <div class="metric-sub">Comissão 7%</div>
        </div>
        <div class="metric">
            <div class="metric-icon">🎯</div>
            <div class="metric-title">META</div>
            <div class="metric-value">0%</div>
            <div class="metric-sub">Em breve</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    fechar_conteudo()


def mais_tela():
    topo("Mais", "Outras opções")
    abrir_conteudo()

    st.markdown('<div class="box">', unsafe_allow_html=True)
    st.write(f"**Usuário:** {st.session_state.get('nome')}")
    st.write(f"**Perfil:** {st.session_state.get('perfil')}")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("perfil") == "ADMIN":
        if st.button("⚙️ ADMINISTRAÇÃO", use_container_width=True):
            st.session_state.menu = "Admin"
            st.rerun()

    if st.button("🚪 SAIR", key="btn_sair", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    fechar_conteudo()


# =========================
# ADMIN
# =========================

def admin_tela():
    topo("Administração", "Área do administrador")
    abrir_conteudo()

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso permitido somente para administrador.")
        fechar_conteudo()
        return

    st.markdown('<div class="box">', unsafe_allow_html=True)

    if st.button("👥 Cadastrar usuários", use_container_width=True):
        st.session_state.menu = "Admin Usuários"
        st.rerun()

    if st.button("🏪 Cadastrar clientes", use_container_width=True):
        st.session_state.menu = "Admin Clientes"
        st.rerun()

    if st.button("📦 Cadastrar produtos", use_container_width=True):
        st.session_state.menu = "Admin Produtos"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    fechar_conteudo()


def admin_usuarios():
    topo("Usuários", "Cadastro de vendedores")
    abrir_conteudo()

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        fechar_conteudo()
        return

    usuarios = ler_excel(ARQ_USUARIOS)

    with st.form("form_usuario"):
        nome = st.text_input("Nome do vendedor")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha")
        perfil = st.selectbox("Perfil", ["VENDEDOR", "ADMIN"])
        comissao = st.number_input("Comissão", value=0.07, step=0.01)

        salvar = st.form_submit_button("💾 SALVAR USUÁRIO", use_container_width=True)

    if salvar:
        if nome.strip() == "" or usuario.strip() == "" or senha.strip() == "":
            st.warning("Preencha nome, usuário e senha.")
        else:
            novo = pd.DataFrame([{
                "usuario": usuario.strip().lower(),
                "senha": senha.strip(),
                "nome": nome.strip(),
                "perfil": perfil,
                "comissao": comissao,
            }])

            usuarios = pd.concat([usuarios, novo], ignore_index=True)
            salvar_excel(usuarios, ARQ_USUARIOS)
            st.success("Usuário cadastrado com sucesso.")
            time.sleep(0.5)
            st.rerun()

    st.dataframe(usuarios, use_container_width=True)

    if st.button("⬅️ VOLTAR", use_container_width=True):
        st.session_state.menu = "Admin"
        st.rerun()

    fechar_conteudo()


def admin_clientes():
    topo("Clientes", "Cadastro de clientes")
    abrir_conteudo()

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        fechar_conteudo()
        return

    clientes = ler_excel(ARQ_CLIENTES)

    with st.form("form_cliente"):
        cliente = st.text_input("Nome do cliente")
        cnpj = st.text_input("CNPJ")
        telefone = st.text_input("Telefone")
        cidade = st.text_input("Cidade")

        salvar = st.form_submit_button("💾 SALVAR CLIENTE", use_container_width=True)

    if salvar:
        if cliente.strip() == "":
            st.warning("Informe o nome do cliente.")
        else:
            codigo = 1
            if len(clientes) and "codigo" in clientes.columns:
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
            st.success("Cliente cadastrado com sucesso.")
            time.sleep(0.5)
            st.rerun()

    st.dataframe(clientes, use_container_width=True)

    if st.button("⬅️ VOLTAR", use_container_width=True):
        st.session_state.menu = "Admin"
        st.rerun()

    fechar_conteudo()


def admin_produtos():
    topo("Produtos", "Cadastro de produtos")
    abrir_conteudo()

    if st.session_state.get("perfil") != "ADMIN":
        st.error("Acesso negado.")
        fechar_conteudo()
        return

    produtos = ler_excel(ARQ_PRODUTOS)

    with st.form("form_produto"):
        codigo = st.text_input("Código")
        produto = st.text_input("Produto")
        un = st.text_input("Unidade", value="UN")
        preco = st.number_input("Preço", min_value=0.0, step=0.01)
        fornecedor = st.text_input("Fornecedor")

        salvar = st.form_submit_button("💾 SALVAR PRODUTO", use_container_width=True)

    if salvar:
        if codigo.strip() == "" or produto.strip() == "":
            st.warning("Informe código e produto.")
        else:
            novo = pd.DataFrame([{
                "codigo": codigo.strip(),
                "produto": produto.strip().upper(),
                "un": un.strip().upper(),
                "preco": preco,
                "fornecedor": fornecedor.strip().upper(),
            }])

            produtos = pd.concat([produtos, novo], ignore_index=True)
            salvar_excel(produtos, ARQ_PRODUTOS)
            st.success("Produto cadastrado com sucesso.")
            time.sleep(0.5)
            st.rerun()

    st.dataframe(produtos, use_container_width=True)

    if st.button("⬅️ VOLTAR", use_container_width=True):
        st.session_state.menu = "Admin"
        st.rerun()

    fechar_conteudo()


# =========================
# APP
# =========================

criar_banco()
css()
login()

if "menu" not in st.session_state:
    st.session_state.menu = "Dashboard"

menu = st.session_state.menu

if menu == "Dashboard":
    dashboard()
elif menu == "Novo Pedido":
    novo_pedido()
elif menu == "Pedidos":
    pedidos_tela()
elif menu == "Editar Pedido":
    editar_pedido()
elif menu == "Comissão":
    comissao_tela()
elif menu == "Mais":
    mais_tela()
elif menu == "Admin":
    admin_tela()
elif menu == "Admin Usuários":
    admin_usuarios()
elif menu == "Admin Clientes":
    admin_clientes()
elif menu == "Admin Produtos":
    admin_produtos()

st.markdown('<div class="bottom-space"></div>', unsafe_allow_html=True)
menu_inferior()
