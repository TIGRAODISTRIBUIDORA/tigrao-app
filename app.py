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
