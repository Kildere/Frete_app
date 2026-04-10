import sqlite3

from database.db import get_connection, init_db


def inserir(dados: dict) -> int:
    """Insere um contratante e retorna o id gerado."""
    init_db()

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO contratantes (nome, tipo, telefone)
                VALUES (?, ?, ?)
                """,
                (dados["nome"], dados["tipo"], dados["telefone"]),
            )
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao inserir contratante no banco de dados.") from exc


def listar() -> list[dict]:
    """Lista os contratantes cadastrados."""
    init_db()

    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, nome, tipo, telefone
                FROM contratantes
                ORDER BY nome ASC, id ASC
                """
            ).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao listar contratantes do banco de dados.") from exc
