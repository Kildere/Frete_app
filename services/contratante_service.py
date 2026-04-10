from repository.contratante_repo import inserir, listar


def criar_contratante(dados: dict) -> int:
    """Normaliza os dados basicos do contratante."""
    payload = {
        "nome": str(dados.get("nome", "")).strip(),
        "tipo": str(dados.get("tipo", "")).strip(),
        "telefone": str(dados.get("telefone", "")).strip(),
    }
    return inserir(payload)


def listar_contratantes() -> list[dict]:
    """Retorna os contratantes cadastrados."""
    return listar()
