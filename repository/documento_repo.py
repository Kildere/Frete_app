import sqlite3

from database.db import get_connection, init_db


def inserir_documento(
    frete_id: int,
    tipo_documento: str,
    nome_arquivo: str,
    caminho_arquivo: str,
) -> int:
    """Registra os metadados de um documento vinculado ao frete."""
    init_db()

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO frete_documentos (
                    frete_id,
                    tipo_documento,
                    nome_arquivo,
                    caminho_arquivo
                ) VALUES (?, ?, ?, ?)
                """,
                (frete_id, tipo_documento, nome_arquivo, caminho_arquivo),
            )
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao registrar documento do frete no banco de dados.") from exc


def listar_documentos_por_frete(frete_id: int) -> list[dict]:
    """Lista os documentos de um frete, do mais recente para o mais antigo."""
    init_db()

    try:
        with get_connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    frete_id,
                    tipo_documento,
                    nome_arquivo,
                    caminho_arquivo,
                    enviado_em
                FROM frete_documentos
                WHERE frete_id = ?
                ORDER BY datetime(enviado_em) DESC, id DESC
                """,
                (frete_id,),
            ).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao listar documentos do frete.") from exc
