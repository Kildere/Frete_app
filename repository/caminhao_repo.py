import sqlite3

from database.db import get_connection, init_db


def inserir(dados: dict) -> int:
    """Insere um caminhao e retorna o id gerado."""
    init_db()

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO caminhoes (placa, modelo, tipo)
                VALUES (?, ?, ?)
                """,
                (dados["placa"], dados["modelo"], dados["tipo"]),
            )
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao inserir caminhao no banco de dados.") from exc


def listar() -> list[dict]:
    """Lista os caminhoes cadastrados."""
    init_db()

    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, placa, modelo, tipo
                FROM caminhoes
                ORDER BY placa ASC, id ASC
                """
            ).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao listar caminhoes do banco de dados.") from exc
