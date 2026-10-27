"""Desenho do certificado em PDF a partir de um modelo e de uma linha de dados."""
import io
from html import escape

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape, portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from . import config, modelos

ALINHAMENTOS = {"esquerda": TA_LEFT, "centro": TA_CENTER,
                "direita": TA_RIGHT, "justificado": TA_JUSTIFY}


def fontes_disponiveis() -> list[str]:
    """Fontes padrão do PDF + TTFs enviados (registrados sob demanda)."""
    config.DIR_FONTES.mkdir(parents=True, exist_ok=True)
    extras = []
    for ttf in sorted(config.DIR_FONTES.glob("*.ttf")):
        if ttf.stem not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(ttf.stem, str(ttf)))
        extras.append(ttf.stem)
    return modelos.FONTES_PADRAO + extras


def _html(valor: str) -> str:
    return escape(valor)


def renderizar(modelo: dict, dados: dict) -> bytes:
    """Gera o PDF (bytes) de um certificado."""
    disponiveis = fontes_disponiveis()
    tamanho = landscape(A4) if modelo["pagina"] == "paisagem" else portrait(A4)
    largura, altura = tamanho

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=tamanho)

    if modelo["fundo"]:
        c.drawImage(str(modelos.dir_modelo(modelo["id"]) / modelo["fundo"]),
                    0, 0, width=largura, height=altura, mask="auto")

    for b in modelo["blocos"]:
        fonte = b["fonte"] if b["fonte"] in disponiveis else "Helvetica"
        tam = float(b["tamanho"])
        estilo = ParagraphStyle("b", fontName=fonte, fontSize=tam, leading=tam * 1.3,
                                alignment=ALINHAMENTOS.get(b["alinhamento"], TA_CENTER),
                                textColor=HexColor(b["cor"]))
        texto = modelos.substituir(b["texto"], dados, escapar=_html)
        # o texto do modelo aceita marcação (<b>, <i>, <u>); se ficar inválida, vira texto puro
        try:
            p = Paragraph(texto.replace("\n", "<br/>"), estilo)
        except Exception:
            p = Paragraph(escape(texto).replace("\n", "<br/>"), estilo)
        w = largura * float(b["largura"]) / 100
        _, h = p.wrap(w, altura)
        p.drawOn(c, largura * float(b["x"]) / 100, altura - altura * float(b["y"]) / 100 - h)

    c.showPage()
    c.save()
    return buf.getvalue()
