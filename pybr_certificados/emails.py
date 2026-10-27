"""Envio dos certificados por e-mail (SMTP) em segundo plano, com log."""
import smtplib
import threading
import time
import uuid
from datetime import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from . import modelos

ENVIOS: dict[str, dict] = {}


def _log(envio: dict, nivel: str, msg: str) -> None:
    envio["log"].append({"hora": datetime.now().strftime("%H:%M:%S"), "nivel": nivel, "msg": msg})


def montar(cfg: dict, remetente: str, item: dict, pdf_bytes: bytes) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = remetente
    msg["To"] = item["email"]
    msg["Subject"] = modelos.substituir(cfg["assunto"], item["dados"])
    if cfg["cc"]:
        msg["Cc"] = cfg["cc"]
    msg.attach(MIMEText(modelos.substituir(cfg["corpo"], item["dados"]), "plain", "utf-8"))
    anexo = MIMEApplication(pdf_bytes, _subtype="pdf")
    anexo.add_header("Content-Disposition", "attachment", filename=item["arquivo"])
    msg.attach(anexo)
    return msg


def _executar(envio: dict, cfg: dict, senha: str, itens: list[dict], pasta, salvar_status) -> None:
    remetente = cfg["remetente"] or cfg["usuario"]
    cc = [e.strip() for e in cfg["cc"].split(",") if e.strip()]
    try:
        _log(envio, "info", f"Conectando a {cfg['servidor']}:{cfg['porta']}...")
        with smtplib.SMTP(cfg["servidor"], int(cfg["porta"]), timeout=30) as server:
            server.starttls()
            server.login(cfg["usuario"], senha)
            _log(envio, "info", "Autenticado. Iniciando envios.")
            for item in itens:
                if not item["email"]:
                    _log(envio, "aviso", f"{item['nome']}: sem e-mail, ignorado.")
                    continue
                try:
                    pdf = (pasta / item["arquivo"]).read_bytes()
                    msg = montar(cfg, remetente, item, pdf)
                    server.sendmail(remetente, [item["email"], *cc], msg.as_string())
                    item["enviado_em"] = datetime.now().isoformat(timespec="seconds")
                    _log(envio, "ok", f"{item['nome']} → {item['email']}")
                except Exception as e:
                    item["erro"] = str(e)
                    _log(envio, "erro", f"{item['nome']} → {item['email']}: {e}")
                salvar_status()
                time.sleep(0.5)  # evita bloqueio por excesso de envios
    except Exception as e:
        _log(envio, "erro", f"Falha na conexão/autenticação: {e}")
    _log(envio, "info", "Envio finalizado.")
    envio["fim"] = True


def iniciar(cfg: dict, senha: str, itens: list[dict], pasta, salvar_status) -> str:
    id_ = uuid.uuid4().hex[:8]
    envio = {"log": [], "fim": False}
    ENVIOS[id_] = envio
    threading.Thread(target=_executar, args=(envio, cfg, senha, itens, pasta, salvar_status),
                     daemon=True).start()
    return id_
