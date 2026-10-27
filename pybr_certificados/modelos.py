"""Armazenamento dos modelos de certificado e leitura das planilhas."""
import json
import re
import io
import shutil
import time
import uuid
import zipfile
from pathlib import Path

import pandas as pd

from . import config

MARCADOR = re.compile(r"\{([^{}]+)\}")

FONTES_PADRAO = [
    "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
    "Courier", "Courier-Bold",
]


def modelo_padrao(nome: str, id_: str) -> dict:
    cor = "#185666"
    def bloco(texto, tam, y, fonte="Helvetica"):
        return {"texto": texto, "fonte": fonte, "tamanho": tam, "cor": cor,
                "alinhamento": "centro", "x": 10, "y": y, "largura": 80}
    return {
        "id": id_, "nome": nome, "pagina": "paisagem",
        "nome_arquivo": "{nome}", "coluna_email": "email",
        "fundo": None, "planilha": None,
        "blocos": [
            bloco("CERTIFICADO DE PARTICIPAÇÃO", 28, 25, "Helvetica-Bold"),
            bloco("{nome}", 24, 38, "Helvetica-Bold"),
            bloco("Participou de {evento}, com carga horária de {hora}.", 16, 50),
            bloco("Realizado em {data} no local {local}.", 16, 62),
            bloco("Python Brasil", 12, 85),
        ],
        "email": {
            "servidor": "smtp.gmail.com", "porta": 587, "usuario": "", "remetente": "",
            "cc": "", "assunto": "Certificado - {evento}",
            "corpo": "Olá {nome},\n\nSegue em anexo o seu certificado de {evento}.\n\nAtenciosamente,\nOrganização",
        },
    }


# --- Caminhos ---------------------------------------------------------------

def dir_modelo(id_: str) -> Path:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", id_):
        raise ValueError("id inválido")
    return config.DIR_MODELOS / id_


def dir_saida(id_: str) -> Path:
    dir_modelo(id_)  # valida o id
    return config.DIR_SAIDA / id_


# --- CRUD -------------------------------------------------------------------

def listar() -> list[dict]:
    itens = []
    for arq in sorted(config.DIR_MODELOS.glob("*/modelo.json")):
        m = json.loads(arq.read_text(encoding="utf-8"))
        itens.append({"id": m["id"], "nome": m["nome"]})
    return itens


def carregar(id_: str) -> dict:
    arq = dir_modelo(id_) / "modelo.json"
    if not arq.exists():
        raise FileNotFoundError(id_)
    return json.loads(arq.read_text(encoding="utf-8"))


def _backup(modelo: dict, manter: int = 30) -> None:
    """Guarda uma cópia do layout a cada mudança real (os últimos `manter`)."""
    pasta = config.DIR_BACKUPS / modelo["id"]
    pasta.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(modelo, ensure_ascii=False, indent=2)
    copias = sorted(pasta.glob("*.json"))
    if copias and copias[-1].read_text(encoding="utf-8") == texto:
        return
    (pasta / f"{time.strftime('%Y%m%d-%H%M%S')}.json").write_text(texto, encoding="utf-8")
    for velha in copias[: max(len(copias) + 1 - manter, 0)]:
        velha.unlink()


def salvar(modelo: dict) -> dict:
    """Salva o modelo preservando os arquivos (fundo/planilha) já enviados."""
    atual = carregar(modelo["id"])
    for campo in ("id", "fundo", "planilha"):
        modelo[campo] = atual[campo]
    (dir_modelo(modelo["id"]) / "modelo.json").write_text(
        json.dumps(modelo, ensure_ascii=False, indent=2), encoding="utf-8")
    _backup(modelo)
    return modelo


def exportar(id_: str) -> bytes:
    """Layout em .zip (modelo.json + fundo). A planilha não entra: tem dados pessoais."""
    m = carregar(id_)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modelo.json", json.dumps({**m, "planilha": None}, ensure_ascii=False, indent=2))
        if m["fundo"]:
            z.write(dir_modelo(id_) / m["fundo"], m["fundo"])
    return buf.getvalue()


def importar(arquivo) -> dict:
    """Cria um novo certificado a partir de um layout exportado (.zip ou .json)."""
    nome = (arquivo.filename or "").lower()
    if nome.endswith(".zip"):
        with zipfile.ZipFile(arquivo) as z:
            dados = json.loads(z.read("modelo.json"))
            fundo = z.read(dados["fundo"]) if dados.get("fundo") else None
    elif nome.endswith(".json"):
        dados, fundo = json.load(arquivo), None
    else:
        raise ValueError("Envie um arquivo .zip ou .json exportado pelo app.")
    base = modelo_padrao(dados.get("nome", "Importado"), "x")
    novo = criar(f"{base['nome']} (importado)")
    for campo in ("pagina", "nome_arquivo", "coluna_email", "blocos", "email"):
        if campo in dados:
            novo[campo] = dados[campo]
    pasta = dir_modelo(novo["id"])
    if fundo:
        ext = Path(dados["fundo"]).suffix.lower()
        if ext in config.EXT_FUNDO:
            (pasta / f"fundo{ext}").write_bytes(fundo)
            novo["fundo"] = f"fundo{ext}"
    novo["email"]["usuario"] = novo["email"].get("usuario", "")
    (pasta / "modelo.json").write_text(json.dumps(novo, ensure_ascii=False, indent=2), encoding="utf-8")
    _backup(novo)
    return novo


def criar(nome: str) -> dict:
    id_ = f"{config.slug(nome, 'modelo')}-{uuid.uuid4().hex[:4]}"
    pasta = dir_modelo(id_)
    pasta.mkdir(parents=True)
    modelo = modelo_padrao(nome, id_)
    if config.EXEMPLO.exists():
        shutil.copy(config.EXEMPLO, pasta / "planilha.csv")
        modelo["planilha"] = "planilha.csv"
    fundos = sorted(p for p in config.DIR_ASSETS.glob("*") if p.suffix.lower() in config.EXT_FUNDO)
    if fundos:  # fundo de exemplo, trocável na interface
        shutil.copy(fundos[0], pasta / f"fundo{fundos[0].suffix.lower()}")
        modelo["fundo"] = f"fundo{fundos[0].suffix.lower()}"
    (pasta / "modelo.json").write_text(
        json.dumps(modelo, ensure_ascii=False, indent=2), encoding="utf-8")
    return modelo


def excluir(id_: str) -> None:
    """Move o certificado para a lixeira (data/lixeira) em vez de apagar de vez."""
    config.DIR_LIXEIRA.mkdir(parents=True, exist_ok=True)
    pasta = dir_modelo(id_)
    if pasta.exists():
        shutil.move(str(pasta), config.DIR_LIXEIRA / f"{id_}-{time.strftime('%Y%m%d-%H%M%S')}")
    shutil.rmtree(dir_saida(id_), ignore_errors=True)


def salvar_arquivo(id_: str, campo: str, arquivo, extensoes: set) -> dict:
    """Guarda a planilha ou o fundo enviado e registra no modelo."""
    ext = Path(arquivo.filename or "").suffix.lower()
    if ext not in extensoes:
        raise ValueError(f"Formato inválido. Use: {', '.join(sorted(extensoes))}")
    modelo = carregar(id_)
    pasta = dir_modelo(id_)
    if modelo[campo]:
        (pasta / modelo[campo]).unlink(missing_ok=True)
    destino = f"{campo}{ext}"
    arquivo.save(pasta / destino)
    modelo[campo] = destino
    (pasta / "modelo.json").write_text(
        json.dumps(modelo, ensure_ascii=False, indent=2), encoding="utf-8")
    return modelo


# --- Planilha ---------------------------------------------------------------

def ler_planilha(modelo: dict) -> pd.DataFrame:
    if not modelo["planilha"]:
        return pd.DataFrame()
    caminho = dir_modelo(modelo["id"]) / modelo["planilha"]
    if caminho.suffix.lower() == ".csv":
        for enc in ("utf-8-sig", "latin-1"):
            try:
                df = pd.read_csv(caminho, sep=None, engine="python", dtype=str, encoding=enc)
                break
            except UnicodeDecodeError:
                continue
    else:
        df = pd.read_excel(caminho, dtype=str)
    df.columns = [str(c).strip() for c in df.columns]
    return df.fillna("").apply(lambda col: col.str.strip())


def linhas(modelo: dict) -> list[dict]:
    return ler_planilha(modelo).to_dict("records")


# --- Filtros de formatação: {coluna|filtro|outro} ---------------------------

PARTICULAS = {"de", "da", "do", "das", "dos", "e", "di", "du", "van", "von", "del", "la"}


def _partes(v: str) -> list[str]:
    return v.split()


def _titulo(v: str) -> str:
    palavras = [p[:1].upper() + p[1:].lower() for p in _partes(v)]
    return " ".join(w.lower() if i and w.lower() in PARTICULAS else w for i, w in enumerate(palavras))


def _abreviar(v: str) -> str:
    """Primeiro nome + iniciais dos nomes do meio + último sobrenome: Gabriel A. B. Bellon."""
    p = _partes(v)
    if len(p) <= 2:
        return v
    meio = [f"{x[0].upper()}." for x in p[1:-1] if x.lower() not in PARTICULAS]
    return " ".join([p[0], *meio, p[-1]])


def _iniciais(v: str) -> str:
    return "".join(x[0].upper() for x in _partes(v) if x.lower() not in PARTICULAS)


FILTROS = {
    "maiusculo": str.upper,
    "minusculo": str.lower,
    "titulo": _titulo,
    "primeiro": lambda v: (_partes(v) or [""])[0],
    "ultimo": lambda v: (_partes(v) or [""])[-1],
    "primeiro_ultimo": lambda v: " ".join(_partes(v)[:1] + _partes(v)[-1:]) if len(_partes(v)) > 1 else v,
    "abreviar": _abreviar,
    "iniciais": _iniciais,
}


def substituir(texto: str, dados: dict, escapar=None) -> str:
    """Troca {coluna} ou {coluna|filtro|...} pelo valor da linha.

    O nome da coluna não diferencia maiúsculas/minúsculas. Marcadores desconhecidos
    (coluna ou filtro) permanecem no texto, para ficarem visíveis na prévia.
    """
    chaves = {k.lower(): v for k, v in dados.items()}

    def trocar(m):
        coluna, *filtros = [x.strip() for x in m.group(1).split("|")]
        valor = chaves.get(coluna.lower())
        if valor is None or any(f.lower() not in FILTROS for f in filtros):
            return m.group(0)
        for f in filtros:
            valor = FILTROS[f.lower()](valor)
        return escapar(valor) if escapar else valor

    return MARCADOR.sub(trocar, texto)
