from io import BytesIO
from pathlib import Path
import shutil

from config import DEMO_MODE
from database.db import get_connection, init_db
from services.caminhao_service import criar_caminhao
from services.contratante_service import criar_contratante
from services.documento_service import salvar_documento
from services.frete_service import criar_frete, listar_fretes
from services.motorista_service import criar_motorista


class UploadedFileMock(BytesIO):
    """Arquivo em memoria para popular documentos de demonstracao."""

    def __init__(self, content: bytes, name: str):
        super().__init__(content)
        self.name = name


def ensure_demo_data() -> None:
    """Garante uma base minima de demonstracao quando o banco estiver vazio."""
    if not DEMO_MODE:
        return

    init_db()
    if listar_fretes():
        return

    _seed_demo_data()


def reload_demo_data() -> None:
    """Recarrega os dados de demonstracao de forma controlada."""
    if not DEMO_MODE:
        return

    init_db()
    _reset_demo_base()
    _seed_demo_data()


def _seed_demo_data() -> None:
    """Popula o banco com dados de exemplo para apresentacao."""
    contratantes = [
        criar_contratante({"nome": "Industria Vale Norte", "tipo": "Pessoa Juridica", "telefone": "(11) 4000-1001"}),
        criar_contratante({"nome": "Distribuidora Atlas", "tipo": "Pessoa Juridica", "telefone": "(19) 4000-2002"}),
        criar_contratante({"nome": "Comercial Horizonte", "tipo": "Pessoa Juridica", "telefone": "(41) 4000-3003"}),
    ]
    motoristas = [
        criar_motorista({"nome": "Carlos Souza", "telefone": "(11) 98888-1001", "cnh": "ABC12345"}),
        criar_motorista({"nome": "Ana Martins", "telefone": "(19) 97777-2002", "cnh": "DEF67890"}),
        criar_motorista({"nome": "Joao Pedro", "telefone": "(41) 96666-3003", "cnh": "GHI54321"}),
    ]
    caminhoes = [
        criar_caminhao({"placa": "BRA2E19", "modelo": "Volvo FH", "tipo": "Truck"}),
        criar_caminhao({"placa": "QXP8A41", "modelo": "Scania R450", "tipo": "Carreta"}),
        criar_caminhao({"placa": "FTR9K72", "modelo": "Mercedes Actros", "tipo": "Bitrem"}),
    ]

    fretes = [
        criar_frete(
            {
                "contratante_id": contratantes[0],
                "origem": "Guarulhos/SP",
                "destino": "Campinas/SP",
                "motorista_id": motoristas[0],
                "caminhao_id": caminhoes[0],
                "valor_frete": 4800,
                "valor_pago": 3100,
                "status": "EM_TRANSITO",
                "observacoes": "Entrega agendada para o fim da tarde.",
            }
        ),
        criar_frete(
            {
                "contratante_id": contratantes[1],
                "origem": "Jundiai/SP",
                "destino": "Ribeirao Preto/SP",
                "motorista_id": motoristas[1],
                "caminhao_id": caminhoes[1],
                "valor_frete": 3600,
                "valor_pago": 2200,
                "status": "CARREGADO",
                "observacoes": "Carga liberada e aguardando janela de saida.",
            }
        ),
        criar_frete(
            {
                "contratante_id": contratantes[2],
                "origem": "Curitiba/PR",
                "destino": "Joinville/SC",
                "motorista_id": motoristas[2],
                "caminhao_id": caminhoes[2],
                "valor_frete": 2900,
                "valor_pago": 1800,
                "status": "ENTREGUE",
                "observacoes": "Comprovante assinado no destino.",
            }
        ),
        criar_frete(
            {
                "contratante_id": contratantes[0],
                "origem": "Osasco/SP",
                "destino": "Belo Horizonte/MG",
                "motorista_id": motoristas[1],
                "caminhao_id": caminhoes[1],
                "valor_frete": 6200,
                "valor_pago": 3900,
                "status": "EM_CADASTRO",
                "observacoes": "Aguardando conferencia final da coleta.",
            }
        ),
    ]

    _seed_demo_documents(fretes)


def _seed_demo_documents(frete_ids: list[int]) -> None:
    """Cria alguns documentos de exemplo para parte dos fretes."""
    salvar_documento(
        frete_ids[0],
        "NFE",
        UploadedFileMock(b"NFe demo do frete 1", "nfe_demo_frete_1.pdf"),
    )
    salvar_documento(
        frete_ids[0],
        "TICKET",
        UploadedFileMock(b"Ticket demo do frete 1", "ticket_demo_frete_1.jpg"),
    )
    salvar_documento(
        frete_ids[2],
        "COMPROVANTE_ENTREGA",
        UploadedFileMock(b"Comprovante demo do frete 3", "comprovante_demo_frete_3.pdf"),
    )


def _reset_demo_base() -> None:
    """Limpa a base e os uploads para recarregar a demonstracao."""
    with get_connection() as connection:
        connection.execute("DELETE FROM frete_documentos")
        connection.execute("DELETE FROM fretes")
        connection.execute("DELETE FROM contratantes")
        connection.execute("DELETE FROM motoristas")
        connection.execute("DELETE FROM caminhoes")
        connection.execute(
            """
            DELETE FROM sqlite_sequence
            WHERE name IN ('frete_documentos', 'fretes', 'contratantes', 'motoristas', 'caminhoes')
            """
        )
        connection.commit()

    uploads_root = Path(__file__).resolve().parent.parent / "uploads"
    for folder in uploads_root.glob("frete_*"):
        if folder.is_dir():
            shutil.rmtree(folder, ignore_errors=True)
