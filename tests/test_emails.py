import smtplib
from pathlib import Path

from pyticipantes import emails

CFG = {"servidor": "x", "porta": 587, "usuario": "u@x.com", "remetente": "", "cc": "",
       "assunto": "Oi {nome}", "corpo": "Texto"}


class FalsoSMTP:
    """SMTP que cai na 1ª mensagem (421) e funciona depois de reconectar."""
    conexoes = 0
    enviados: list[str] = []

    def __init__(self, *a, **k):
        FalsoSMTP.conexoes += 1
        self.falhar = FalsoSMTP.conexoes == 1

    def starttls(self): ...
    def login(self, *a): ...
    def quit(self): ...

    def sendmail(self, remetente, destinos, texto):
        if self.falhar:
            raise smtplib.SMTPResponseException(421, b"4.3.0 Temporary System Problem")
        FalsoSMTP.enviados.append(destinos[0])


def _item(tmp_path: Path, nome: str, **extra):
    (tmp_path / f"{nome}.pdf").write_bytes(b"%PDF")
    return {"arquivo": f"{nome}.pdf", "nome": nome, "email": f"{nome}@x.com",
            "dados": {"nome": nome}, "enviado_em": None, "erro": None, **extra}


def test_reconecta_tenta_de_novo_e_pula_enviados(tmp_path, monkeypatch):
    monkeypatch.setattr(smtplib, "SMTP", FalsoSMTP)
    monkeypatch.setattr(emails.time, "sleep", lambda s: None)
    itens = [_item(tmp_path, "ana"), _item(tmp_path, "bia", enviado_em="2026-01-01T00:00:00")]
    envio = {"log": [], "fim": False, "arquivo_log": str(tmp_path / "envios.log")}
    emails._executar(envio, CFG, "senha", itens, tmp_path, lambda: None)
    assert FalsoSMTP.enviados == ["ana@x.com"]          # reenviou após o 421; bia foi pulada
    assert itens[0]["enviado_em"] and itens[0]["erro"] is None
    assert envio["fim"]
    assert "OK" in (tmp_path / "envios.log").read_text(encoding="utf-8")
