from repository.frete_repo import (
    atualizar_status_frete as atualizar_status_frete_repo,
    buscar_frete_por_id as buscar_frete_por_id_repo,
    inserir_frete,
    listar_fretes as listar_fretes_repo,
)
from utils.frete_status import DEFAULT_STATUS, STATUS_OPTIONS, normalize_status


def criar_frete(dados: dict) -> int:
    """Normaliza os dados basicos e delega a gravacao para o repositorio."""
    status = normalize_status(dados.get("status"))
    valor_frete = float(dados.get("valor_frete", 0) or 0)
    valor_pago = float(dados.get("valor_pago", 0) or 0)
    payload = {
        "contratante_id": int(dados.get("contratante_id", 0) or 0),
        "origem": str(dados.get("origem", "")).strip(),
        "destino": str(dados.get("destino", "")).strip(),
        "motorista_id": int(dados.get("motorista_id", 0) or 0),
        "caminhao_id": int(dados.get("caminhao_id", 0) or 0),
        "valor_frete": valor_frete,
        "valor_pago": valor_pago,
        "comissao": calcular_comissao(valor_frete, valor_pago),
        "status": status or DEFAULT_STATUS,
        "observacoes": str(dados.get("observacoes", "")).strip(),
    }

    return inserir_frete(payload)


def listar_fretes() -> list[dict]:
    """Retorna os fretes cadastrados."""
    return listar_fretes_repo()


def atualizar_status_frete(frete_id: int, status: str) -> bool:
    """Atualiza o status de um frete usando apenas valores padronizados."""
    status_normalizado = normalize_status(status)
    if status_normalizado not in STATUS_OPTIONS:
        raise ValueError("Status de frete invalido.")

    return atualizar_status_frete_repo(int(frete_id), status_normalizado)


def obter_detalhe_frete(frete_id: int) -> dict | None:
    """Retorna o detalhe do frete preparado para exibicao na interface."""
    detalhe = buscar_frete_por_id_repo(int(frete_id))
    if not detalhe:
        return None

    detalhe["documentos"] = int(detalhe.get("documentos", 0) or 0)
    detalhe["created_at_display"] = _format_datetime(detalhe.get("created_at"))
    detalhe["valor_frete_display"] = f"R$ {float(detalhe.get('valor_frete', 0) or 0):,.2f}"
    detalhe["valor_pago_display"] = f"R$ {float(detalhe.get('valor_pago', 0) or 0):,.2f}"
    detalhe["comissao_display"] = f"R$ {float(detalhe.get('comissao', 0) or 0):,.2f}"

    placa = str(detalhe.get("placa", "") or "").strip()
    modelo = str(detalhe.get("caminhao_modelo", "") or "").strip()
    if modelo:
        detalhe["caminhao_descricao"] = f"{placa} / {modelo}"
    else:
        detalhe["caminhao_descricao"] = placa or "Nao informado"

    return detalhe


def calcular_comissao(valor_frete: float | int, valor_pago: float | int | None) -> float:
    """Calcula a comissao/lucro bruto simples do frete."""
    valor_frete = float(valor_frete or 0)
    valor_pago = float(valor_pago or 0)
    return valor_frete - valor_pago


def _format_datetime(value: str | None) -> str:
    """Formata timestamp do banco para leitura humana simples."""
    if not value:
        return ""

    normalized = str(value).replace("T", " ")
    try:
        date_part, time_part = normalized.split(" ", maxsplit=1)
        year, month, day = date_part.split("-")
        hour, minute, *_ = time_part.split(":")
        return f"{day}/{month}/{year} {hour}:{minute}"
    except ValueError:
        return str(value)
