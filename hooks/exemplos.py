"""Publica os exemplos do pacote no site da documentação, para baixar pelas páginas."""
from pathlib import Path

from mkdocs.structure.files import File

ORIGEM = Path(__file__).resolve().parent.parent / "src" / "pyticipantes" / "exemplos"


def on_files(files, config, **kwargs):
    """Adiciona os exemplos como arquivos do site (links `downloads/...` passam a ser válidos)."""
    for arq in sorted(ORIGEM.iterdir()):
        files.append(File.generated(config, f"downloads/{arq.name}", abs_src_path=str(arq)))
    return files
