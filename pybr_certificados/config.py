"""Caminhos e utilitários compartilhados."""
import os
import re
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# PYBR_DATA permite apontar os dados para outra pasta (usado em testes, para nunca tocar nos modelos reais)
DIR_DADOS = Path(os.getenv("PYBR_DATA", RAIZ / "data"))
DIR_MODELOS = DIR_DADOS / "modelos"
DIR_FONTES = DIR_DADOS / "fontes"
DIR_BACKUPS = DIR_DADOS / "backups"   # histórico automático de cada layout
DIR_LIXEIRA = DIR_DADOS / "lixeira"   # certificados excluídos (recuperáveis)
DIR_ASSETS = RAIZ / "assets"
DIR_SAIDA = Path(os.getenv("PYBR_SAIDA", RAIZ / "saida"))
EXEMPLO = RAIZ / "data" / "exemplo.csv"

EXT_PLANILHA = {".xlsx", ".xls", ".csv"}
EXT_FUNDO = {".png", ".jpg", ".jpeg"}


def slug(texto: str, padrao: str = "arquivo") -> str:
    """Texto seguro para nome de arquivo/id (sem acentos, só [A-Za-z0-9_-])."""
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s or padrao
