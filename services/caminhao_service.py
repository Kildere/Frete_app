from repository.caminhao_repo import inserir, listar


def criar_caminhao(dados: dict) -> int:
    """Normaliza os dados basicos do caminhao."""
    payload = {
        "placa": str(dados.get("placa", "")).strip().upper(),
        "modelo": str(dados.get("modelo", "")).strip(),
        "tipo": str(dados.get("tipo", "")).strip(),
    }
    return inserir(payload)


def listar_caminhoes() -> list[dict]:
    """Retorna os caminhoes cadastrados."""
    return listar()
