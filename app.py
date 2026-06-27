import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os

st.set_page_config(page_title="Tigrão - Bloco Pedidos", page_icon="🐯", layout="centered")

st.title("🐯 Tigrão Distribuidora")
st.write("### 📦 Bloco 1: Gestão e Faturamento de Pedidos")

CAMINHO_VENDAS = "vendas_tigrao.xlsx"
CAMINHO_USUARIOS = "usuarios_banco.xlsx"

SENHA_NELSON_MESTRE = "TigraoNelson2026"
EMAIL_DONO = "sodemilecem23@gmail.com"

if not os.path.exists(CAMINHO_USUARIOS):
    pd.DataFrame([
        {"Email": EMAIL_DONO, "Senha": "123", "Nome": "Nelson Dono"},
        {"Email": "joaquim@tigrao.com", "Senha": "123", "Nome": "Joaquim Silva"},
        {"Email": "pedro@tigrao.com", "Senha": "123", "Nome": "Pedro Santos"},
        {"Email": "carlos@tigrao.com", "Senha": "123", "Nome": "Carlos Oliveira"}
    ]).to_excel(CAMINHO_USUARIOS, index=False)

df_usuarios = pd.read_excel(CAMINHO_USUARIOS)

if not os.path.exists(CAMINHO_VENDAS):
    pd.DataFrame(columns=[
        "Data_Hora", "Vendedor", "Cliente", "Produto",
        "Quantidade", "Total", "Pagamento", "Status"
    ]).to_excel(CAMINHO_VENDAS, index=False)

df_pedidos = pd.read_excel(CAMINHO_VENDAS)

if "vendedor_nome" not in st.session_state:
    st.session_state["vendedor_nome"] = ""

if "vendedor_email" not in st.session_state:
    st.session_state["vendedor_email"] = ""

produtos_fixos = {
    "Bananada Natural (Fardo)": 36.00,
    "Cerveja Lata 350ml (Fardo)": 42.00,
    "Refrigerante 2L (Fardo)": 48.00
}

if st.session_state["vendedor_nome"] == "":
    st.subheader("🔐 Ativação Única do Aplicativo")
    st.write("Insira seu e-mail e senha corporativa para liberar o aparelho.")

    email_input = st.text_input("E-mail do Vendedor:")
    senha_input = st.text_input("Senha de Acesso:", type="password")

    if st.button("🚀 Ativar Aplicativo neste Celular"):
        email_limpo = email_input.strip().lower()
        senha_limpa = senha_input.strip()

        usuario_validar = df_usuarios[
            (df_usuarios["Email"].astype(str).str.lower() == email_limpo) &
            (df_usuarios["Senha"].astype(str) == senha_limpa)
        ]

        if not usuario_validar.empty:
            st.session_state["vendedor_nome"] = usuario_validar.iloc[0]["Nome"]
            st.session_state["vendedor_email"] = email_limpo
            st.success(f"Dispositivo ativado com sucesso para {st.session_state['vendedor_nome']}!")
            st.rerun()
        else:
            st.error("❌ E-mail ou Senha incorretos. Verifique com a administração do Tigrão.")

else:
    st.success(f"👤 CONECTADO: **{st.session_state['vendedor_nome'].upper()}**")

    if st.button("🔄 Desconectar deste aparelho"):
        st.session_state["vendedor_nome"] = ""
        st.session_state["vendedor_email"] = ""
        st.rerun()

    st.markdown("---")

    is_admin = st.session_state["vendedor_email"] == EMAIL_DONO

    if is_admin:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Passar Pedido",
            "🔎 Consultar Produto",
            "👑 Recebimento Nelson",
            "👥 Gestão da Equipe"
        ])
    else:
        tab1, tab2, tab3 = st.tabs([
            "📋 Passar Pedido",
            "🔎 Consultar Produto",
            "👑 Recebimento Nelson"
        ])

    with tab1:
        st.subheader("📋 Lançar Novo Pedido")

        cliente = st.selectbox(
            "Selecione o Cliente:",
            ["Supermercado Silva", "Mercado do João", "Conveniência Central"]
        )

        produto = st.selectbox("Selecione o Produto:", list(produtos_fixos.keys()))

        preco_un = produtos_fixos[produto]
        st.caption(f"Preço do fardo: R$ {preco_un:.2f}")

        quantidade = st.number_input(
            "Quantidade de Fardos:",
            min_value=1,
            value=1,
            step=1
        )

        total_pedido = preco_un * quantidade

        st.markdown(f"#### 💰 Total do Pedido: **R$ {total_pedido:.2f}**")

        forma_pagto = st.selectbox(
            "Forma de Pagamento:",
            ["Boleto 30 dias", "Pix", "Dinheiro"]
        )

        if st.button("🚀 Enviar Pedido para a Central", key="btn_enviar_pedido_venda"):
            novo_p = pd.DataFrame([{
                "Data_Hora": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Vendedor": st.session_state["vendedor_nome"],
                "Cliente": cliente,
                "Produto": produto,
                "Quantidade": int(quantidade),
                "Total": float(total_pedido),
                "Pagamento": forma_pagto,
                "Status": "Pendente"
            }])

            df_pedidos_atual = pd.read_excel(CAMINHO_VENDAS)
            df_final = pd.concat([df_pedidos_atual, novo_p], ignore_index=True)
            df_final.to_excel(CAMINHO_VENDAS, index=False)

            st.success("✅ Pedido gravado no Excel com sucesso!")
            st.balloons()
            st.rerun()

    with tab2:
        st.subheader("🔎 Consultar Produto")

        pesquisa_produto = st.text_input("Digite o nome do produto:")

        if pesquisa_produto.strip():
            termo = pesquisa_produto.strip().lower()

            resultados = {
                nome: preco
                for nome, preco in produtos_fixos.items()
                if termo in nome.lower()
            }

            if resultados:
                for nome, preco in resultados.items():
                    st.success(f"📦 {nome}")
                    st.write(f"💰 Preço do fardo: **R$ {preco:.2f}**")
                    st.markdown("---")
            else:
                st.warning("Nenhum produto encontrado.")
        else:
            st.info("Digite parte do nome do produto para pesquisar.")

    with tab3:
        st.subheader("🔒 Painel de Recebimento de Pedidos")

        liberar_painel = False

        if is_admin:
            liberar_painel = True
            st.info("👑 Reconhecido como Diretor. Senha interna dispensada.")
        else:
            senha_digitada = st.text_input(
                "Digite a Senha Master da Empresa:",
                type="password",
                key="campo_senha_master_nelson"
            )

            if senha_digitada == SENHA_NELSON_MESTRE:
                liberar_painel = True
            elif senha_digitada != "":
                st.error("❌ Senha master incorreta.")

        if liberar_painel:
            if os.path.exists(CAMINHO_VENDAS):
                df_pedidos_atualizado = pd.read_excel(CAMINHO_VENDAS)
            else:
                df_pedidos_atualizado = pd.DataFrame()

            if not df_pedidos_atualizado.empty:
                df_ordenado = df_pedidos_atualizado.sort_values(
                    by="Data_Hora",
                    ascending=False
                )

                pendentes = len(df_ordenado[df_ordenado["Status"] == "Pendente"])

                st.write(f"📢 Você tem **{pendentes}** pedido(s) pendente(s) para faturar no DISA.")

                buffer = io.BytesIO()

                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df_ordenado.to_excel(writer, index=False, sheet_name="Pedidos_Faturamento")

                st.download_button(
                    label="📥 Baixar Planilha Excel para Nota Fiscal (.xlsx)",
                    data=buffer.getvalue(),
                    file_name=f"faturamento_tigrao_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="btn_download_excel_nelson"
                )

                st.write("---")

                st.dataframe(
                    df_ordenado[[
                        "Data_Hora",
                        "Vendedor",
                        "Cliente",
                        "Produto",
                        "Quantidade",
                        "Total",
                        "Pagamento",
                        "Status"
                    ]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("ℹ️ Nenhum pedido foi recebido no sistema ainda.")

    if is_admin:
        with tab4:
            st.subheader("👑 Controle de Vendedores do Tigrão")

            st.write("➕ **Adicionar Novo Vendedor no Sistema:**")

            with st.form("form_add_vendedor"):
                v_nome = st.text_input("Nome Completo do Vendedor:")
                v_email = st.text_input("E-mail de Login:")
                v_senha = st.text_input("Senha Inicial:")
                btn_v = st.form_submit_button("💾 Salvar Novo Vendedor")

            if btn_v and v_nome.strip() and v_email.strip() and v_senha.strip():
                email_l_novo = v_email.strip().lower()

                if email_l_novo in df_usuarios["Email"].astype(str).str.lower().tolist():
                    st.error("❌ Este e-mail de vendedor já está cadastrado!")
                else:
                    novo_u_df = pd.DataFrame([{
                        "Email": email_l_novo,
                        "Senha": v_senha.strip(),
                        "Nome": v_nome.strip()
                    }])

                    df_usuarios_atualizado = pd.concat(
                        [df_usuarios, novo_u_df],
                        ignore_index=True
                    )

                    df_usuarios_atualizado.to_excel(CAMINHO_USUARIOS, index=False)

                    st.success(f"🎉 Vendedor '{v_nome}' cadastrado com sucesso!")
                    st.rerun()

            st.markdown("---")
            st.write("🗑️ **Excluir Vendedor do Sistema:**")

            lista_emails_excluir = [
                e for e in df_usuarios["Email"].tolist()
                if str(e).lower() != EMAIL_DONO
            ]

            if lista_emails_excluir:
                email_deletar = st.selectbox(
                    "Selecione o e-mail do funcionário que deseja remover:",
                    lista_emails_excluir
                )

                if st.button("❌ Confirmar Exclusão Definitiva"):
                    df_usuarios_novos = df_usuarios[
                        df_usuarios["Email"] != email_deletar
                    ]

                    df_usuarios_novos.to_excel(CAMINHO_USUARIOS, index=False)

                    st.success("🗑️ Funcionário removido do banco de dados com sucesso!")
                    st.rerun()
            else:
                st.info("Nenhum vendedor cadastrado para remoção.")

            st.markdown("---")
            st.write("📋 **Lista de Vendedores Cadastrados no Banco:**")

            st.dataframe(
                df_usuarios[["Nome", "Email", "Senha"]],
                use_container_width=True,
                hide_index=True
            )
with tab3:
        st.subheader("🔒 Painel de Recebimento de Pedidos")

        liberar_painel = False

        if is_admin:
            liberar_painel = True
            st.info("👑 Reconhecido como Diretor. Senha interna dispensada.")
        else:
            senha_digitada = st.text_input(
                "Digite a Senha Master da Empresa:",
                type="password",
                key="campo_senha_master_nelson"
            )

            if senha_digitada == SENHA_NELSON_MESTRE:
                liberar_painel = True
            elif senha_digitada != "":
                st.error("❌ Senha master incorreta.")

        if liberar_painel:
            df_pedidos_atualizado = pd.read_excel(CAMINHO_VENDAS)

            if not df_pedidos_atualizado.empty:
                df_ordenado = df_pedidos_atualizado.sort_values(
                    by="Numero_Pedido",
                    ascending=False
                )

                pendentes = len(df_ordenado[df_ordenado["Status"] == "Pendente"])

                st.write(f"📢 Você tem **{pendentes}** pedido(s) pendente(s) para faturar no DISA.")

                buffer = io.BytesIO()

                with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                    df_ordenado.to_excel(writer, index=False, sheet_name="Pedidos_Faturamento")

                st.download_button(
                    label="📥 Baixar Planilha Excel para Nota Fiscal (.xlsx)",
                    data=buffer.getvalue(),
                    file_name=f"faturamento_tigrao_{datetime.now().strftime('%d_%m_%Y')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="btn_download_excel_nelson"
                )

                st.write("---")

                st.dataframe(
                    df_ordenado[[
                        "Numero_Pedido",
                        "Data_Hora",
                        "Vendedor",
                        "Cliente",
                        "Produto",
                        "Quantidade",
                        "Total",
                        "Pagamento",
                        "Status",
                        "Numero_NF",
                        "Data_Faturamento"
                    ]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("ℹ️ Nenhum pedido foi recebido no sistema ainda.")

    if is_admin:
        with tab4:
            st.subheader("📤 Retorno do Faturamento")

            st.write("Aqui você sobe de volta a planilha Excel depois que faturar no DISA.")

            st.info("A planilha precisa ter pelo menos as colunas: Numero_Pedido, Status e Numero_NF.")

            arquivo_retorno = st.file_uploader(
                "📎 Enviar planilha de retorno do faturamento:",
                type=["xlsx"]
            )

            if arquivo_retorno is not None:
                try:
                    df_retorno = pd.read_excel(arquivo_retorno)

                    st.write("Pré-visualização da planilha enviada:")
                    st.dataframe(df_retorno, use_container_width=True, hide_index=True)

                    colunas_obrigatorias = ["Numero_Pedido", "Status"]

                    faltando = [
                        col for col in colunas_obrigatorias
                        if col not in df_retorno.columns
                    ]

                    if faltando:
                        st.error(f"❌ Faltam colunas obrigatórias: {faltando}")
                    else:
                        if st.button("✅ Atualizar Status dos Pedidos"):
                            df_base = pd.read_excel(CAMINHO_VENDAS)

                            atualizados = 0

                            for _, linha in df_retorno.iterrows():
                                numero = str(linha["Numero_Pedido"]).strip()

                                if numero in df_base["Numero_Pedido"].astype(str).values:
                                    idx = df_base[
                                        df_base["Numero_Pedido"].astype(str) == numero
                                    ].index

                                    df_base.loc[idx, "Status"] = str(linha["Status"]).strip()

                                    if "Numero_NF" in df_retorno.columns:
                                        df_base.loc[idx, "Numero_NF"] = str(linha["Numero_NF"]).strip()

                                    if "Data_Faturamento" in df_retorno.columns:
                                        df_base.loc[idx, "Data_Faturamento"] = str(linha["Data_Faturamento"]).strip()
                                    else:
                                        if str(linha["Status"]).strip().lower() == "faturado":
                                            df_base.loc[idx, "Data_Faturamento"] = datetime.now().strftime("%d/%m/%Y")

                                    if "Observacao" in df_retorno.columns:
                                        df_base.loc[idx, "Observacao"] = str(linha["Observacao"]).strip()

                                    atualizados += 1

                            df_base.to_excel(CAMINHO_VENDAS, index=False)

                            st.success(f"✅ {atualizados} pedido(s) atualizado(s) com sucesso!")
                            st.rerun()

                except Exception as e:
                    st.error(f"Erro ao ler a planilha: {e}")

        with tab5:
            st.subheader("👑 Controle de Vendedores do Tigrão")

            st.write("➕ **Adicionar Novo Vendedor no Sistema:**")

            with st.form("form_add_vendedor"):
                v_nome = st.text_input("Nome Completo do Vendedor:")
                v_email = st.text_input("E-mail de Login:")
                v_senha = st.text_input("Senha Inicial:")
                btn_v = st.form_submit_button("💾 Salvar Novo Vendedor")

            if btn_v and v_nome.strip() and v_email.strip() and v_senha.strip():
                email_l_novo = v_email.strip().lower()

                if email_l_novo in df_usuarios["Email"].astype(str).str.lower().tolist():
                    st.error("❌ Este e-mail de vendedor já está cadastrado!")
                else:
                    novo_u_df = pd.DataFrame([{
                        "Email": email_l_novo,
                        "Senha": v_senha.strip(),
                        "Nome": v_nome.strip()
                    }])

                    df_usuarios_atualizado = pd.concat(
                        [df_usuarios, novo_u_df],
                        ignore_index=True
                    )

                    df_usuarios_atualizado.to_excel(CAMINHO_USUARIOS, index=False)

                    st.success(f"🎉 Vendedor '{v_nome}' cadastrado com sucesso!")
                    st.rerun()

            st.markdown("---")
            st.write("🗑️ **Excluir Vendedor do Sistema:**")

            lista_emails_excluir = [
                e for e in df_usuarios["Email"].tolist()
                if str(e).lower() != EMAIL_DONO
            ]

            if lista_emails_excluir:
                email_deletar = st.selectbox(
                    "Selecione o e-mail do funcionário que deseja remover:",
                    lista_emails_excluir
                )

                if st.button("❌ Confirmar Exclusão Definitiva"):
                    df_usuarios_novos = df_usuarios[
                        df_usuarios["Email"] != email_deletar
                    ]

                    df_usuarios_novos.to_excel(CAMINHO_USUARIOS, index=False)

                    st.success("🗑️ Funcionário removido do banco de dados com sucesso!")
                    st.rerun()
            else:
                st.info("Nenhum vendedor cadastrado para remoção.")

            st.markdown("---")
            st.write("📋 **Lista de Vendedores Cadastrados no Banco:**")

            st.dataframe(
                df_usuarios[["Nome", "Email", "Senha"]],
                use_container_width=True,
                hide_index=True
            )
