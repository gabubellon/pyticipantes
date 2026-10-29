"""Copia os exemplos do pacote para o site gerado, para baixar pela documentação."""
import shutil
from pathlib import Path

ORIGEM = Path(__file__).resolve().parent.parent / "src" / "pyticipantes" / "exemplos"


def on_post_build(config, **kwargs):
    shutil.copytree(ORIGEM, Path(config["site_dir"]) / "exemplos", dirs_exist_ok=True)
