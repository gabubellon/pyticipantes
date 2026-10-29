"""Caminhos e utilitários compartilhados."""
import os
import re
import unicodedata
from pathlib import Path

PACOTE = Path(__file__).resolve().parent
# Dados do usuário ficam fora do pacote: por padrão em ./data e ./saida (relativo a onde o app
# é iniciado). PYTICIPANTES_DATA e PYTICIPANTES_SAIDA apontam para outras pastas (e isolam testes).
DIR_DADOS = Path(os.getenv("PYTICIPANTES_DATA", "data")).resolve()
DIR_MODELOS = DIR_DADOS / "modelos"
DIR_FONTES = DIR_DADOS / "fontes"
DIR_BACKUPS = DIR_DADOS / "backups"   # histórico automático de cada layout
DIR_LIXEIRA = DIR_DADOS / "lixeira"   # certificados excluídos (recuperáveis)
DIR_SAIDA = Path(os.getenv("PYTICIPANTES_SAIDA", "saida")).resolve()
# Planilha e fundo de exemplo (versionados, baixáveis no app e na documentação)
DIR_EXEMPLOS = PACOTE / "exemplos"
EXEMPLO = DIR_EXEMPLOS / "exemplo.csv"
FUNDO_EXEMPLO = DIR_EXEMPLOS / "fundo-exemplo.png"

EXT_PLANILHA = {".xlsx", ".xls", ".csv"}
EXT_FUNDO = {".png", ".jpg", ".jpeg"}


def slug(texto: str, padrao: str = "arquivo") -> str:
    """Texto seguro para nome de arquivo/id (sem acentos, só [A-Za-z0-9_-])."""
    s = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    s = re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_")
    return s or padrao
