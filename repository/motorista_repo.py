import sqlite3

from database.db import get_connection, init_db


def inserir(dados: dict) -> int:
    """Insere um motorista e retorna o id gerado."""
    init_db()

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO motoristas (nome, telefone, cnh)
                VALUES (?, ?, ?)
                """,
                (dados["nome"], dados["telefone"], dados["cnh"]),
            )
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao inserir motorista no banco de dados.") from exc


def listar() -> list[dict]:
    """Lista os motoristas cadastrados."""
    init_db()

    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, nome, telefone, cnh
                FROM motoristas
                ORDER BY nome ASC, id ASC
                """
            ).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao listar motoristas do banco de dados.") from exc
