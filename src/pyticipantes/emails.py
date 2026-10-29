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


ESPERA_ENTRE_ENVIOS = 2.0   # Gmail/Workspace corta rajadas; ~30 msgs/min é seguro
TENTATIVAS = 3
ESPERA_TEMPORARIO = (60, 180)  # espera (s) antes da 2ª e 3ª tentativas após erro 4xx/queda
MAX_FALHAS_SEGUIDAS = 5


def _log(envio: dict, nivel: str, msg: str) -> None:
    linha = {"hora": datetime.now().strftime("%H:%M:%S"), "nivel": nivel, "msg": msg}
    envio["log"].append(linha)
    arq = envio.get("arquivo_log")
    if arq:  # grava na hora: o log sobrevive a reinício do servidor
        try:
            with open(arq, "a", encoding="utf-8") as f:
                agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{agora}] {nivel.upper():5} {msg}\n")
        except OSError:
            pass


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


def _conectar(envio: dict, cfg: dict, senha: str) -> smtplib.SMTP:
    _log(envio, "info", f"Conectando a {cfg['servidor']}:{cfg['porta']}...")
    server = smtplib.SMTP(cfg["servidor"], int(cfg["porta"]), timeout=60)
    server.starttls()
    server.login(cfg["usuario"], senha)
    _log(envio, "info", "Autenticado.")
    return server


def _fechar(server) -> None:
    try:
        server.quit()
    except Exception:
        pass


def _temporario(e: Exception) -> bool:
    """Erros que valem nova tentativa: queda de conexão, timeout ou resposta 4xx."""
    if isinstance(e, (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, OSError)):
        return True
    if isinstance(e, smtplib.SMTPResponseException):
        return 400 <= e.smtp_code < 500
    if isinstance(e, smtplib.SMTPRecipientsRefused):
        return False
    return "connect()" in str(e)


def _executar(envio: dict, cfg: dict, senha: str, itens: list[dict], pasta, salvar_status) -> None:
    remetente = cfg["remetente"] or cfg["usuario"]
    cc = [e.strip() for e in cfg["cc"].split(",") if e.strip()]
    server = None
    falhas_seguidas = 0
    enviados = 0
    try:
        for item in itens:
            if not item["email"]:
                _log(envio, "aviso", f"{item['nome']}: sem e-mail, ignorado.")
                continue
            if item.get("enviado_em"):
                _log(envio, "aviso", f"{item['nome']} → {item['email']}: já enviado em "
                                     f"{item['enviado_em']}, pulado.")
                continue
            ok = False
            for tentativa in range(1, TENTATIVAS + 1):
                try:
                    if server is None:
                        server = _conectar(envio, cfg, senha)
                    pdf = (pasta / item["arquivo"]).read_bytes()
                    msg = montar(cfg, remetente, item, pdf)
                    server.sendmail(remetente, [item["email"], *cc], msg.as_string())
                    item["enviado_em"] = datetime.now().isoformat(timespec="seconds")
                    item["erro"] = None
                    _log(envio, "ok", f"{item['nome']} → {item['email']}")
                    ok = True
                    break
                except smtplib.SMTPAuthenticationError as e:
                    raise RuntimeError(f"Autenticação recusada: {e}") from e
                except Exception as e:
                    item["erro"] = str(e)
                    if server is not None:
                        _fechar(server)
                        server = None  # reconecta na próxima tentativa
                    if _temporario(e) and tentativa < TENTATIVAS:
                        espera = ESPERA_TEMPORARIO[tentativa - 1]
                        _log(envio, "aviso",
                             f"{item['nome']} → {item['email']}: {e} "
                             f"(tentativa {tentativa}/{TENTATIVAS}, aguardando {espera}s)")
                        time.sleep(espera)
                        continue
                    _log(envio, "erro", f"{item['nome']} → {item['email']}: {e}")
                    break
            salvar_status()
            if ok:
                enviados += 1
                falhas_seguidas = 0
            else:
                falhas_seguidas += 1
                if falhas_seguidas >= MAX_FALHAS_SEGUIDAS:
                    _log(envio, "erro",
                         f"{falhas_seguidas} falhas seguidas: envio interrompido para "
                         "não queimar a reputação/cota. Aguarde e reenvie os pendentes "
                         "(os já enviados são pulados).")
                    break
            time.sleep(ESPERA_ENTRE_ENVIOS)
    except Exception as e:
        _log(envio, "erro", f"Envio interrompido: {e}")
    finally:
        if server is not None:
            _fechar(server)
        salvar_status()
    _log(envio, "info", f"Envio finalizado. {enviados} enviado(s) nesta rodada.")
    envio["fim"] = True


def iniciar(cfg: dict, senha: str, itens: list[dict], pasta, salvar_status) -> str:
    id_ = uuid.uuid4().hex[:8]
    envio = {"log": [], "fim": False, "arquivo_log": str(pasta / "envios.log")}
    ENVIOS[id_] = envio
    threading.Thread(target=_executar, args=(envio, cfg, senha, itens, pasta, salvar_status),
                     daemon=True).start()
    return id_
