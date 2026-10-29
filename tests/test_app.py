def test_saude(cliente):
    r = cliente.get("/saude")
    assert r.status_code == 200 and r.json["status"] == "ok"


def test_exemplos_para_download(cliente):
    assert cliente.get("/exemplos/exemplo.csv").status_code == 200
    assert cliente.get("/exemplos/fundo-exemplo.png").status_code == 200
    assert cliente.get("/exemplos/outro.txt").status_code == 404


def test_novo_modelo_nasce_com_exemplos(cliente):
    r = cliente.post("/api/modelos", json={"nome": "Teste"})
    assert r.status_code == 200
    assert r.json["planilha"] == "planilha.csv" and r.json["fundo"] == "fundo.png"
