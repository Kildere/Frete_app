import sqlite3
from pathlib import Path

from utils.frete_status import DEFAULT_STATUS, normalize_status


DATABASE_PATH = Path(__file__).resolve().parent / "frete_app.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection(db_path: str | None = None) -> sqlite3.Connection:
    """Retorna uma conexao SQLite configurada para acesso por nome de coluna."""
    database_path = Path(db_path) if db_path else DATABASE_PATH
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=OFF")
    connection.execute("PRAGMA synchronous=OFF")
    connection.execute("PRAGMA temp_store=MEMORY")
    return connection


def init_db() -> None:
    """Cria as tabelas do projeto caso ainda nao existam."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")

    with get_connection() as connection:
        connection.executescript(schema)
        _migrate_fretes_table(connection)
        connection.commit()


def _migrate_fretes_table(connection: sqlite3.Connection) -> None:
    """Migra a tabela de fretes antiga para a estrutura baseada em IDs simples."""
    rows = connection.execute("PRAGMA table_info(fretes)").fetchall()
    if not rows:
        return

    columns = {row["name"] for row in rows}
    has_legacy_columns = {"contratante", "motorista", "placa"}.issubset(columns)
    has_modern_columns = {"contratante_id", "motorista_id", "caminhao_id"}.issubset(columns)
    has_observacoes = "observacoes" in columns
    has_financeiro = "valor_pago" in columns and "comissao" in columns

    if has_modern_columns and has_observacoes and has_financeiro and not has_legacy_columns:
        _normalize_frete_statuses(connection)
        _normalize_frete_financials(connection)
        return

    if has_legacy_columns:
        _seed_base_entities_from_legacy_fretes(connection)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS fretes_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contratante_id INTEGER,
            origem TEXT NOT NULL,
            destino TEXT NOT NULL,
            motorista_id INTEGER,
            caminhao_id INTEGER,
            valor_frete REAL NOT NULL,
            valor_pago REAL NOT NULL DEFAULT 0,
            comissao REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL,
            observacoes TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    if has_legacy_columns:
        connection.execute(
            """
            INSERT INTO fretes_new (
                id,
                contratante_id,
                origem,
                destino,
                motorista_id,
                caminhao_id,
                valor_frete,
                valor_pago,
                comissao,
                status,
                observacoes,
                created_at
            )
            SELECT
                f.id,
                c.id,
                f.origem,
                f.destino,
                m.id,
                cam.id,
                f.valor_frete,
                0,
                f.valor_frete,
                f.status,
                '',
                f.created_at
            FROM fretes f
            LEFT JOIN contratantes c ON c.nome = f.contratante
            LEFT JOIN motoristas m ON m.nome = f.motorista
            LEFT JOIN caminhoes cam ON cam.placa = f.placa
            ORDER BY f.id
            """
        )
    elif has_observacoes and has_financeiro:
        connection.execute(
            """
            INSERT INTO fretes_new (
                id,
                contratante_id,
                origem,
                destino,
                motorista_id,
                caminhao_id,
                valor_frete,
                valor_pago,
                comissao,
                status,
                observacoes,
                created_at
            )
            SELECT
                id,
                contratante_id,
                origem,
                destino,
                motorista_id,
                caminhao_id,
                valor_frete,
                COALESCE(valor_pago, 0),
                COALESCE(comissao, valor_frete - COALESCE(valor_pago, 0)),
                status,
                COALESCE(observacoes, ''),
                created_at
            FROM fretes
            ORDER BY id
            """
        )
    elif has_observacoes:
        connection.execute(
            """
            INSERT INTO fretes_new (
                id,
                contratante_id,
                origem,
                destino,
                motorista_id,
                caminhao_id,
                valor_frete,
                valor_pago,
                comissao,
                status,
                observacoes,
                created_at
            )
            SELECT
                id,
                contratante_id,
                origem,
                destino,
                motorista_id,
                caminhao_id,
                valor_frete,
                0,
                valor_frete,
                status,
                COALESCE(observacoes, ''),
                created_at
            FROM fretes
            ORDER BY id
            """
        )
    else:
        connection.execute(
            """
            INSERT INTO fretes_new (
                id,
                contratante_id,
                origem,
                destino,
                motorista_id,
                caminhao_id,
                valor_frete,
                valor_pago,
                comissao,
                status,
                observacoes,
                created_at
            )
            SELECT
                id,
                contratante_id,
                origem,
                destino,
                motorista_id,
                caminhao_id,
                valor_frete,
                0,
                valor_frete,
                status,
                '',
                created_at
            FROM fretes
            ORDER BY id
            """
        )

    connection.execute("DROP TABLE fretes")
    connection.execute("ALTER TABLE fretes_new RENAME TO fretes")
    _normalize_frete_statuses(connection)
    _normalize_frete_financials(connection)


def _seed_base_entities_from_legacy_fretes(connection: sqlite3.Connection) -> None:
    """Cria entidades base a partir dos dados textuais do frete antigo."""
    connection.execute(
        """
        INSERT INTO contratantes (nome, tipo, telefone)
        SELECT DISTINCT TRIM(contratante), '', ''
        FROM fretes
        WHERE TRIM(COALESCE(contratante, '')) <> ''
          AND TRIM(contratante) NOT IN (
              SELECT TRIM(nome) FROM contratantes
          )
        """
    )
    connection.execute(
        """
        INSERT INTO motoristas (nome, telefone, cnh)
        SELECT DISTINCT TRIM(motorista), '', ''
        FROM fretes
        WHERE TRIM(COALESCE(motorista, '')) <> ''
          AND TRIM(motorista) NOT IN (
              SELECT TRIM(nome) FROM motoristas
          )
        """
    )
    connection.execute(
        """
        INSERT INTO caminhoes (placa, modelo, tipo)
        SELECT DISTINCT UPPER(TRIM(placa)), '', ''
        FROM fretes
        WHERE TRIM(COALESCE(placa, '')) <> ''
          AND UPPER(TRIM(placa)) NOT IN (
              SELECT UPPER(TRIM(placa)) FROM caminhoes
          )
        """
    )


def _normalize_frete_statuses(connection: sqlite3.Connection) -> None:
    """Converte status antigos ou livres para o conjunto padronizado."""
    rows = connection.execute("SELECT id, status FROM fretes").fetchall()
    for row in rows:
        connection.execute(
            "UPDATE fretes SET status = ? WHERE id = ?",
            (normalize_status(row["status"]) or DEFAULT_STATUS, row["id"]),
        )


def _normalize_frete_financials(connection: sqlite3.Connection) -> None:
    """Garante consistencia basica dos campos financeiros do frete."""
    rows = connection.execute("SELECT id, valor_frete, valor_pago FROM fretes").fetchall()
    for row in rows:
        valor_frete = float(row["valor_frete"] or 0)
        valor_pago = float(row["valor_pago"] or 0)
        connection.execute(
            "UPDATE fretes SET valor_pago = ?, comissao = ? WHERE id = ?",
            (valor_pago, valor_frete - valor_pago, row["id"]),
        )
