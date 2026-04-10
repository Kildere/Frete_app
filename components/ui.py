import streamlit as st


STATUS_LABELS = {
    "EM_CADASTRO": "Em cadastro",
    "CARREGADO": "Carregado",
    "EM_TRANSITO": "Em transito",
    "ENTREGUE": "Entregue",
    "QUEBRADO": "Quebrado",
    "CANCELADO": "Cancelado",
}


def page_header(title: str, subtitle: str, note: str | None = None) -> None:
    """Renderiza o cabecalho padrao das paginas principais."""
    with st.container():
        st.title(title)
        st.caption(subtitle)
        if note:
            st.info(note)


def section_header(title: str, subtitle: str | None = None) -> None:
    """Renderiza um titulo de secao com subtitulo opcional."""
    with st.container():
        st.markdown(f"### {title}")
        if subtitle:
            st.caption(subtitle)


def metric_card(label: str, value, help_text: str | None = None) -> None:
    """Renderiza uma metrica simples com apoio textual opcional."""
    with st.container():
        st.metric(label, value)
        if help_text:
            st.caption(help_text)


def info_block(title: str, content: str | list[str], caption: str | None = None) -> None:
    """Renderiza um bloco textual simples e legivel."""
    with st.container():
        st.markdown(f"**{title}**")
        if isinstance(content, list):
            for line in content:
                st.write(line)
        else:
            st.write(content)
        if caption:
            st.caption(caption)


def format_status_label(status: str | None) -> str:
    """Converte status interno em rotulo mais amigavel."""
    return STATUS_LABELS.get(str(status or "").strip().upper(), str(status or "") or "-")
