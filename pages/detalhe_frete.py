import pandas as pd
import streamlit as st

from components.ui import format_status_label, info_block, metric_card, page_header, section_header
from services.demo_service import ensure_demo_data
from services.documento_service import listar_documentos_por_frete
from services.frete_service import listar_fretes, obter_detalhe_frete


st.set_page_config(
    page_title="Detalhe do Frete | AgTransporte",
    layout="wide",
)


def render_page() -> None:
    """Renderiza a ficha operacional completa de um frete."""
    ensure_demo_data()

    page_header(
        "Ficha do frete",
        "Consulte em uma unica area o andamento, o financeiro e os documentos vinculados ao frete.",
    )

    try:
        fretes = listar_fretes()
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if not fretes:
        st.info("Nenhum frete cadastrado ainda.")
        st.caption("Abra a tela de fretes para registrar a primeira operacao e depois volte para esta ficha.")
        return

    frete_ids = [frete["id"] for frete in fretes]
    frete_options = {
        frete["id"]: f"#{frete['id']} | {frete['contratante']} | {frete['destino']} | {format_status_label(frete['status'])}"
        for frete in fretes
    }

    selected_default = _resolve_selected_frete_id(frete_ids)

    section_header("Selecionar frete", "Escolha pela lista ou carregue diretamente pelo ID.")
    col1, col2 = st.columns(2)
    with col1:
        selected_frete_id = st.selectbox(
            "Frete",
            options=frete_ids,
            index=frete_ids.index(selected_default),
            format_func=lambda frete_id: frete_options[frete_id],
        )
    with col2:
        frete_id_manual = st.number_input(
            "ID direto",
            min_value=1,
            value=int(selected_default),
            step=1,
        )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Carregar frete da lista", use_container_width=True):
            st.session_state["frete_detalhe_id"] = int(selected_frete_id)
    with col2:
        if st.button("Carregar frete pelo ID", use_container_width=True):
            st.session_state["frete_detalhe_id"] = int(frete_id_manual)

    frete_id = int(st.session_state.get("frete_detalhe_id", selected_default))
    if frete_id not in frete_ids:
        st.warning("O frete informado nao foi encontrado. Exibindo o frete selecionado na lista.")
        frete_id = selected_frete_id
        st.session_state["frete_detalhe_id"] = selected_frete_id

    try:
        detalhe = obter_detalhe_frete(frete_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if not detalhe:
        st.warning("Frete nao encontrado.")
        return

    st.session_state["frete_detalhe_id"] = detalhe["id"]

    _render_identificacao(detalhe)
    _render_operacional(detalhe)
    _render_financeiro(detalhe)
    _render_observacoes(detalhe)
    _render_documentos(detalhe["id"])


def _resolve_selected_frete_id(frete_ids: list[int]) -> int:
    """Escolhe o frete padrao para abrir a tela."""
    stored = st.session_state.get("frete_detalhe_id")
    if stored in frete_ids:
        return int(stored)
    return frete_ids[0]


def _render_identificacao(detalhe: dict) -> None:
    """Renderiza o bloco de identificacao principal."""
    section_header("Identificacao do frete", "Resumo rapido para consulta operacional.")
    col1, col2 = st.columns(2)
    with col1:
        metric_card("Frete", f"#{detalhe['id']}")
        metric_card("Status", format_status_label(detalhe["status"]))
    with col2:
        metric_card("Criado em", detalhe["created_at_display"] or "-")
        metric_card("Documentos vinculados", detalhe["documentos"])


def _render_operacional(detalhe: dict) -> None:
    """Renderiza os blocos de contratante, rota e operacao."""
    section_header("Dados operacionais", "Informacoes principais da viagem e dos envolvidos.")
    col1, col2 = st.columns(2)
    with col1:
        info_block("Contratante", detalhe["contratante"], caption=f"ID interno: {detalhe['contratante_id']}")
        info_block("Rota", [f"Origem: {detalhe['origem']}", f"Destino: {detalhe['destino']}"])
    with col2:
        info_block(
            "Operacao",
            [
                f"Motorista: {detalhe['motorista']}",
                f"Veiculo: {detalhe['caminhao_descricao']}",
            ],
            caption=f"Motorista #{detalhe['motorista_id']} | Caminhao #{detalhe['caminhao_id']}",
        )


def _render_financeiro(detalhe: dict) -> None:
    """Renderiza o bloco financeiro basico."""
    section_header("Financeiro", "Resumo financeiro simples do frete.")
    col1, col2 = st.columns(2)
    with col1:
        metric_card("Valor do frete", detalhe["valor_frete_display"])
        metric_card("Valor pago", detalhe["valor_pago_display"])
    with col2:
        metric_card("Comissao", detalhe["comissao_display"])
        metric_card("Status atual", format_status_label(detalhe["status"]))


def _render_observacoes(detalhe: dict) -> None:
    """Renderiza as observacoes operacionais."""
    section_header("Observacoes", "Anotacoes e recados operacionais registrados para este frete.")
    observacoes = detalhe["observacoes"] or "Nenhuma observacao registrada."
    info_block("Anotacoes", observacoes)


def _render_documentos(frete_id: int) -> None:
    """Renderiza o bloco de documentos vinculados ao frete."""
    section_header("Documentos vinculados", "Consulta simples dos arquivos relacionados a este frete.")

    try:
        documentos = listar_documentos_por_frete(frete_id)
    except RuntimeError as exc:
        st.error(str(exc))
        return

    if not documentos:
        st.info("Nenhum documento vinculado a este frete.")
        st.caption("Use a tela de fretes para anexar NFe, ticket ou comprovante quando necessario.")
        return

    dataframe = pd.DataFrame(documentos)
    dataframe["enviado_em"] = pd.to_datetime(dataframe["enviado_em"], errors="coerce")
    dataframe["enviado_em"] = dataframe["enviado_em"].dt.strftime("%d/%m/%Y %H:%M").fillna("")

    st.dataframe(
        dataframe.rename(
            columns={
                "tipo_documento": "Tipo",
                "nome_arquivo": "Arquivo",
                "enviado_em": "Enviado em",
                "caminho_arquivo": "Caminho",
            }
        )[["Tipo", "Arquivo", "Enviado em", "Caminho"]],
        use_container_width=True,
        hide_index=True,
    )
    st.caption("No celular, deslize horizontalmente para visualizar o caminho completo do arquivo.")


render_page()
