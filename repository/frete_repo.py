import sqlite3

from database.db import get_connection, init_db


def inserir_frete(dados: dict) -> int:
    """Insere um frete e retorna o id gerado."""
    init_db()

    query = """
        INSERT INTO fretes (
            contratante_id,
            origem,
            destino,
            motorista_id,
            caminhao_id,
            valor_frete,
            valor_pago,
            comissao,
            status,
            observacoes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    valores = (
        dados["contratante_id"],
        dados["origem"],
        dados["destino"],
        dados["motorista_id"],
        dados["caminhao_id"],
        dados["valor_frete"],
        dados["valor_pago"],
        dados["comissao"],
        dados["status"],
        dados["observacoes"],
    )

    try:
        with get_connection() as connection:
            cursor = connection.execute(query, valores)
            connection.commit()
            return int(cursor.lastrowid)
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao inserir frete no banco de dados.") from exc


def listar_fretes() -> list[dict]:
    """Lista os fretes cadastrados, mais recentes primeiro."""
    init_db()

    query = """
        SELECT
            f.id,
            f.contratante_id,
            COALESCE(c.nome, 'Nao informado') AS contratante,
            f.origem,
            f.destino,
            f.motorista_id,
            COALESCE(m.nome, 'Nao informado') AS motorista,
            f.caminhao_id,
            COALESCE(cam.placa, 'Nao informada') AS placa,
            COALESCE(cam.modelo, '') AS caminhao_modelo,
            f.valor_frete,
            COALESCE(f.valor_pago, 0) AS valor_pago,
            COALESCE(f.comissao, 0) AS comissao,
            f.status,
            COALESCE(f.observacoes, '') AS observacoes,
            COALESCE(doc.documentos, 0) AS documentos,
            f.created_at
        FROM fretes f
        LEFT JOIN contratantes c ON c.id = f.contratante_id
        LEFT JOIN motoristas m ON m.id = f.motorista_id
        LEFT JOIN caminhoes cam ON cam.id = f.caminhao_id
        LEFT JOIN (
            SELECT frete_id, COUNT(*) AS documentos
            FROM frete_documentos
            GROUP BY frete_id
        ) doc ON doc.frete_id = f.id
    """
    order_by = " ORDER BY datetime(f.created_at) DESC, f.id DESC"

    try:
        with get_connection() as connection:
            rows = connection.execute(query + order_by).fetchall()
            return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao listar fretes do banco de dados.") from exc


def buscar_frete_por_id(frete_id: int) -> dict | None:
    """Busca um frete especifico com dados completos e nomes relacionados."""
    init_db()

    query = """
        SELECT
            f.id,
            f.contratante_id,
            COALESCE(c.nome, 'Nao informado') AS contratante,
            f.origem,
            f.destino,
            f.motorista_id,
            COALESCE(m.nome, 'Nao informado') AS motorista,
            f.caminhao_id,
            COALESCE(cam.placa, 'Nao informada') AS placa,
            COALESCE(cam.modelo, '') AS caminhao_modelo,
            f.valor_frete,
            COALESCE(f.valor_pago, 0) AS valor_pago,
            COALESCE(f.comissao, 0) AS comissao,
            f.status,
            COALESCE(f.observacoes, '') AS observacoes,
            COALESCE(doc.documentos, 0) AS documentos,
            f.created_at
        FROM fretes f
        LEFT JOIN contratantes c ON c.id = f.contratante_id
        LEFT JOIN motoristas m ON m.id = f.motorista_id
        LEFT JOIN caminhoes cam ON cam.id = f.caminhao_id
        LEFT JOIN (
            SELECT frete_id, COUNT(*) AS documentos
            FROM frete_documentos
            GROUP BY frete_id
        ) doc ON doc.frete_id = f.id
        WHERE f.id = ?
    """

    try:
        with get_connection() as connection:
            row = connection.execute(query, (frete_id,)).fetchone()
            return dict(row) if row else None
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao buscar detalhe do frete.") from exc


def atualizar_status_frete(frete_id: int, status: str) -> bool:
    """Atualiza o status de um frete existente."""
    init_db()

    try:
        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE fretes
                SET status = ?
                WHERE id = ?
                """,
                (status, frete_id),
            )
            connection.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as exc:
        raise RuntimeError("Erro ao atualizar status do frete.") from exc
