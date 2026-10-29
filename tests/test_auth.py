import base64
import importlib


def test_basic_auth_protege_o_app(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTICIPANTES_DATA", str(tmp_path))
    monkeypatch.setenv("PYTICIPANTES_USUARIO", "admin")
    monkeypatch.setenv("PYTICIPANTES_SENHA", "segredo")
    from pyticipantes import app as app_mod
    importlib.reload(app_mod)
    c = app_mod.app.test_client()
    assert c.get("/saude").status_code == 200          # healthcheck sempre livre
    assert c.get("/api/modelos").status_code == 401
    ok = base64.b64encode(b"admin:segredo").decode()
    assert c.get("/api/modelos", headers={"Authorization": f"Basic {ok}"}).status_code == 200
    ruim = base64.b64encode(b"admin:errada").decode()
    assert c.get("/api/modelos", headers={"Authorization": f"Basic {ruim}"}).status_code == 401
