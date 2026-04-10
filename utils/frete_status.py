STATUS_OPTIONS = [
    "EM_CADASTRO",
    "CARREGADO",
    "EM_TRANSITO",
    "ENTREGUE",
    "QUEBRADO",
    "CANCELADO",
]

DEFAULT_STATUS = "EM_CADASTRO"

_STATUS_ALIASES = {
    "PENDENTE": "EM_CADASTRO",
    "EM_CADASTRO": "EM_CADASTRO",
    "CARREGANDO": "CARREGADO",
    "CARREGADO": "CARREGADO",
    "EM ROTA": "EM_TRANSITO",
    "EM_ROTA": "EM_TRANSITO",
    "EM TRANSITO": "EM_TRANSITO",
    "EM_TRANSITO": "EM_TRANSITO",
    "AGUARDANDO DESCARGA": "EM_TRANSITO",
    "AGUARDANDO_DESCARGA": "EM_TRANSITO",
    "ENTREGUE": "ENTREGUE",
    "QUEBRADO": "QUEBRADO",
    "CANCELADO": "CANCELADO",
}


def normalize_status(status: str | None) -> str:
    """Padroniza valores antigos ou livres para os status aceitos."""
    normalized = str(status or "").strip().upper()
    normalized = normalized.replace("-", "_")
    normalized = " ".join(normalized.split())
    normalized = normalized.replace(" ", "_")
    return _STATUS_ALIASES.get(normalized, DEFAULT_STATUS)


def is_valid_status(status: str | None) -> bool:
    """Indica se o valor informado ja esta no conjunto permitido."""
    return str(status or "").strip().upper() in STATUS_OPTIONS
