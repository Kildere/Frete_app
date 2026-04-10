import re
from pathlib import Path

from repository.documento_repo import inserir_documento, listar_documentos_por_frete as listar_repo


UPLOADS_ROOT = Path(__file__).resolve().parent.parent / "uploads"
TIPO_DOCUMENTO_OPTIONS = [
    "NFE",
    "TICKET",
    "COMPROVANTE_ENTREGA",
    "OUTRO",
]


def salvar_documento(frete_id: int, tipo_documento: str, arquivo) -> int:
    """Salva o arquivo em disco e registra seus metadados no banco."""
    frete_id = int(frete_id)
    tipo_documento = str(tipo_documento or "").strip().upper()

    if frete_id <= 0:
        raise ValueError("Selecione um frete valido.")
    if tipo_documento not in TIPO_DOCUMENTO_OPTIONS:
        raise ValueError("Tipo de documento invalido.")
    if arquivo is None:
        raise ValueError("Selecione um arquivo para envio.")

    nome_seguro = _build_safe_filename(getattr(arquivo, "name", "documento"))
    destino_dir = UPLOADS_ROOT / f"frete_{frete_id}"
    destino_dir.mkdir(parents=True, exist_ok=True)

    destino_arquivo = _build_unique_path(destino_dir / nome_seguro)
    destino_arquivo.write_bytes(arquivo.getbuffer())

    caminho_relativo = destino_arquivo.relative_to(UPLOADS_ROOT.parent).as_posix()
    return inserir_documento(
        frete_id=frete_id,
        tipo_documento=tipo_documento,
        nome_arquivo=destino_arquivo.name,
        caminho_arquivo=caminho_relativo,
    )


def listar_documentos_por_frete(frete_id: int) -> list[dict]:
    """Retorna os documentos vinculados a um frete."""
    documentos = listar_repo(int(frete_id))
    for documento in documentos:
        documento["enviado_em"] = str(documento.get("enviado_em", "") or "")
    return documentos


def _build_safe_filename(filename: str) -> str:
    """Sanitiza o nome do arquivo preservando extensao quando existir."""
    original_name = Path(str(filename or "documento")).name
    suffix = "".join(ch for ch in Path(original_name).suffix.lower() if ch.isalnum() or ch == ".")
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", Path(original_name).stem).strip("._-")

    if not stem:
        stem = "documento"
    if not suffix:
        suffix = ".bin"

    return f"{stem}{suffix}"


def _build_unique_path(path: Path) -> Path:
    """Evita sobrescrever arquivos quando o nome ja existe no diretorio."""
    if not path.exists():
        return path

    counter = 2
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1
