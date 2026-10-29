"""Servidor web: modelos, prévia, geração e envio."""
import hmac
import json
import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, Response, abort, jsonify, request, send_from_directory

from . import __version__, config, emails, modelos, render

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024


_USUARIO = os.getenv("PYTICIPANTES_USUARIO", "")
_SENHA = os.getenv("PYTICIPANTES_SENHA", "")
_AUTENTICACAO = bool(_USUARIO and _SENHA)  # opcional: protege o app quando exposto na rede


@app.before_request
def _autenticar():
    """HTTP Basic opcional (PYTICIPANTES_USUARIO/PYTICIPANTES_SENHA). /saude fica livre."""
    if not _AUTENTICACAO or request.path == "/saude":
        return None
    cred = request.authorization
    if (cred and hmac.compare_digest(cred.username or "", _USUARIO)
            and hmac.compare_digest(cred.password or "", _SENHA)):
        return None
    return Response("Autenticação necessária.", 401,
                    {"WWW-Authenticate": 'Basic realm="Pyticipantes"'})


@app.get("/saude")
def saude():
    return jsonify(status="ok", versao=__version__)


@app.before_request
def _somente_origem_local():
    """Bloqueia escritas vindas de outros sites (o servidor controla arquivos e e-mail)."""
    if request.method not in ("GET", "HEAD"):
        origem = request.headers.get("Origin")
        if origem and urlparse(origem).netloc != request.host:
            abort(403)


@app.errorhandler(Exception)
def _erro(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return jsonify(erro=e.description), e.code
    if isinstance(e, FileNotFoundError):
        return jsonify(erro="Não encontrado."), 404
    app.logger.exception(e)
    return jsonify(erro=str(e)), 400


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/exemplos/<nome>")
def exemplos(nome):
    """Planilha e fundo de exemplo para download."""
    if nome not in ("exemplo.csv", "fundo-exemplo.png"):
        abort(404)
    return send_from_directory(config.DIR_EXEMPLOS, nome, as_attachment=True)


@app.get("/docs/")
@app.get("/docs/<path:caminho>")
def documentacao(caminho="index.html"):
    """Documentação (MkDocs) gerada em src/pyticipantes/site; veja `make docs`."""
    pasta = Path(app.root_path) / "site"
    if not pasta.is_dir():
        return Response("Documentação não gerada. Rode `make docs` (ou reconstrua a imagem).", 404)
    if (pasta / caminho).is_dir():
        caminho = f"{caminho.rstrip('/')}/index.html"
    return send_from_directory(pasta, caminho)


# --- Modelos ----------------------------------------------------------------

@app.get("/api/modelos")
def api_listar():
    return jsonify(modelos.listar())


@app.post("/api/modelos")
def api_criar():
    nome = (request.json or {}).get("nome", "").strip() or "Novo certificado"
    return jsonify(modelos.criar(nome))


def _detalhe(modelo: dict) -> dict:
    try:
        df = modelos.ler_planilha(modelo)
        colunas, total, erro = list(df.columns), len(df), None
        amostra = df.head(5).to_dict("records")
    except Exception as e:
        colunas, total, erro, amostra = [], 0, f"Não foi possível ler a planilha: {e}", []
    return {"modelo": modelo, "colunas": colunas, "total": total,
            "amostra": amostra, "erro_planilha": erro, "fontes": render.fontes_disponiveis()}


@app.post("/api/modelos/importar")
def api_importar():
    return jsonify(modelos.importar(request.files["arquivo"]))


@app.get("/api/modelos/<id_>/exportar")
def api_exportar(id_):
    m = modelos.carregar(id_)
    return Response(modelos.exportar(id_), mimetype="application/zip", headers={
        "Content-Disposition": f'attachment; filename="layout_{config.slug(m["nome"])}.zip"'})


@app.get("/api/modelos/<id_>")
def api_detalhe(id_):
    return jsonify(_detalhe(modelos.carregar(id_)))


@app.put("/api/modelos/<id_>")
def api_salvar(id_):
    corpo = request.json
    corpo["id"] = id_
    return jsonify(_detalhe(modelos.salvar(corpo)))


@app.delete("/api/modelos/<id_>")
def api_excluir(id_):
    modelos.excluir(id_)
    return jsonify(ok=True)


@app.post("/api/modelos/<id_>/planilha")
def api_planilha(id_):
    m = modelos.salvar_arquivo(id_, "planilha", request.files["arquivo"], config.EXT_PLANILHA)
    return jsonify(_detalhe(m))


@app.post("/api/modelos/<id_>/fundo")
def api_fundo(id_):
    m = modelos.salvar_arquivo(id_, "fundo", request.files["arquivo"], config.EXT_FUNDO)
    return jsonify(_detalhe(m))


@app.get("/api/modelos/<id_>/fundo")
def api_ver_fundo(id_):
    m = modelos.carregar(id_)
    if not m["fundo"]:
        abort(404)
    return send_from_directory(modelos.dir_modelo(id_), m["fundo"])


@app.post("/api/fontes")
def api_fonte():
    arq = request.files["arquivo"]
    if not (arq.filename or "").lower().endswith(".ttf"):
        raise ValueError("Envie um arquivo .ttf")
    config.DIR_FONTES.mkdir(parents=True, exist_ok=True)
    arq.save(config.DIR_FONTES / (config.slug(Path(arq.filename).stem, "fonte") + ".ttf"))
    return jsonify(render.fontes_disponiveis())


# --- Prévia e geração -------------------------------------------------------

@app.post("/api/modelos/<id_>/previa")
def api_previa(id_):
    corpo = request.json
    modelo = {**corpo["modelo"], "id": id_}
    atual = modelos.carregar(id_)
    modelo["fundo"], modelo["planilha"] = atual["fundo"], atual["planilha"]
    linhas = modelos.linhas(modelo)
    dados = linhas[min(int(corpo.get("linha", 0)), len(linhas) - 1)] if linhas else {}
    return Response(render.renderizar(modelo, dados), mimetype="application/pdf")


def _manifesto(id_: str) -> Path:
    return modelos.dir_saida(id_) / "certificados.json"


def _ler_manifesto(id_: str) -> list[dict]:
    arq = _manifesto(id_)
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else []


def _gravar_manifesto(id_: str, itens: list[dict]) -> None:
    _manifesto(id_).write_text(json.dumps(itens, ensure_ascii=False, indent=2), encoding="utf-8")


@app.post("/api/modelos/<id_>/gerar")
def api_gerar(id_):
    corpo = {**request.json, "id": id_}
    limite = corpo.pop("limite", None)  # None = todos
    modelo = modelos.salvar(corpo)
    linhas = modelos.linhas(modelo)
    if limite:
        linhas = linhas[:max(int(limite), 1)]
    if not linhas:
        raise ValueError("A planilha não tem linhas. Envie uma planilha no passo 1.")

    pasta = modelos.dir_saida(id_)
    pasta.mkdir(parents=True, exist_ok=True)
    for antigo in pasta.glob("*.pdf"):
        antigo.unlink()

    col_email = modelo["coluna_email"].strip().lower()
    itens = []
    for i, dados in enumerate(linhas, start=1):
        base = config.slug(modelos.substituir(modelo["nome_arquivo"], dados), "certificado")
        arquivo = f"{i:03d}_{base}.pdf"
        (pasta / arquivo).write_bytes(render.renderizar(modelo, dados))
        email = next((v for k, v in dados.items() if k.lower() == col_email), "")
        primeiro = next(iter(dados.values()), "")
        nome = next((v for k, v in dados.items() if k.lower() == "nome"), primeiro)
        itens.append({"arquivo": arquivo, "linha": i, "nome": nome, "email": email,
                      "dados": dados, "enviado_em": None, "erro": None})
    _gravar_manifesto(id_, itens)
    return jsonify(itens)


@app.get("/api/modelos/<id_>/certificados")
def api_certificados(id_):
    return jsonify(_ler_manifesto(id_))


@app.get("/api/modelos/<id_>/arquivo/<nome>")
def api_arquivo(id_, nome):
    return send_from_directory(modelos.dir_saida(id_), nome, mimetype="application/pdf")


@app.post("/api/modelos/<id_>/abrir-pasta")
def api_abrir_pasta(id_):
    pasta = modelos.dir_saida(id_)
    pasta.mkdir(parents=True, exist_ok=True)
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(pasta)])
    elif sys.platform == "win32":
        os.startfile(pasta)  # noqa: S606
    else:
        subprocess.Popen(["xdg-open", str(pasta)])
    return jsonify(ok=True)


# --- Envio de e-mail --------------------------------------------------------

@app.post("/api/modelos/<id_>/enviar")
def api_enviar(id_):
    corpo = request.json
    modelo = modelos.carregar(id_)
    modelo["email"] = corpo["email"]
    modelos.salvar(modelo)  # a senha nunca é gravada

    itens = _ler_manifesto(id_)
    escolhidos = set(corpo["arquivos"])
    selecionados = [i for i in itens if i["arquivo"] in escolhidos]
    if not selecionados:
        raise ValueError("Selecione ao menos um certificado.")
    if not corpo["email"]["usuario"] or not corpo.get("senha"):
        raise ValueError("Informe usuário e senha do SMTP.")

    def salvar_status():
        _gravar_manifesto(id_, itens)  # `selecionados` aponta para os mesmos dicts

    job = emails.iniciar(corpo["email"], corpo["senha"], selecionados,
                         modelos.dir_saida(id_), salvar_status)
    return jsonify(job=job)


@app.get("/api/envios/<job>")
def api_envio(job):
    envio = emails.ENVIOS.get(job)
    if not envio:
        abort(404)
    return jsonify(envio)


def servir(host: str = "127.0.0.1", porta: int = 8000) -> None:
    from waitress import serve

    config.DIR_MODELOS.mkdir(parents=True, exist_ok=True)
    url = f"http://{'127.0.0.1' if host in ('0.0.0.0', '::') else host}:{porta}"
    if host == "127.0.0.1" and not os.getenv("PYTICIPANTES_SEM_NAVEGADOR"):
        threading.Timer(1, lambda: webbrowser.open(url)).start()
    if host not in ("127.0.0.1", "localhost", "::1") and not _AUTENTICACAO:
        print("AVISO: acessível pela rede e sem senha. Defina PYTICIPANTES_USUARIO e "
              "PYTICIPANTES_SENHA ou ponha o app atrás de um proxy com autenticação.", flush=True)
    print(f"Pyticipantes {__version__} em {url}  (Ctrl+C para sair)", flush=True)
    serve(app, host=host, port=porta, threads=8)
