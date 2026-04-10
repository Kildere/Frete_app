from repository.motorista_repo import inserir, listar


def criar_motorista(dados: dict) -> int:
    """Normaliza os dados basicos do motorista."""
    payload = {
        "nome": str(dados.get("nome", "")).strip(),
        "telefone": str(dados.get("telefone", "")).strip(),
        "cnh": str(dados.get("cnh", "")).strip().upper(),
    }
    return inserir(payload)


def listar_motoristas() -> list[dict]:
    """Retorna os motoristas cadastrados."""
    return listar()
