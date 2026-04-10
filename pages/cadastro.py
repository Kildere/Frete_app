import pandas as pd
import streamlit as st

from components.ui import page_header, section_header
from services.demo_service import ensure_demo_data
from services.contratante_service import criar_contratante, listar_contratantes


st.set_page_config(
    page_title="Cadastro | AgTransporte",
    layout="wide",
)


def render_form() -> None:
    """Renderiza o formulario de contratantes."""
    ensure_demo_data()

    page_header(
        "Cadastro de contratantes",
        "Mantenha a base de clientes e parceiros organizada para usar nos fretes.",
    )

    if st.session_state.pop("contratante_salvo", False):
        st.success("Contratante salvo com sucesso.")

    with st.form("form_cadastro", clear_on_submit=True):
        section_header("Dados do contratante", "Preencha somente as informacoes essenciais.")
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome")
            telefone = st.text_input("Telefone")
        with col2:
            tipo = st.selectbox("Tipo", ["Pessoa Fisica", "Pessoa Juridica"])

        submitted = st.form_submit_button("Salvar contratante", use_container_width=True)

    if submitted:
        if not nome.strip():
            st.error("Informe o nome do contratante.")
        else:
            try:
                criar_contratante(
                    {
                        "nome": nome,
                        "tipo": tipo,
                        "telefone": telefone,
                    }
                )
            except RuntimeError as exc:
                st.error(str(exc))
            else:
                st.session_state["contratante_salvo"] = True
                st.rerun()

    try:
        contratantes = listar_contratantes()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    section_header("Contratantes cadastrados", "Consulta rapida da base atual.")
    if not contratantes:
        st.info("Nenhum contratante cadastrado ainda.")
        st.caption("Use o formulario acima para registrar o primeiro contratante.")
        return

    st.dataframe(pd.DataFrame(contratantes), use_container_width=True, hide_index=True)


render_form()
