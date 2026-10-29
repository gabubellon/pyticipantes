import importlib

import pytest


@pytest.fixture()
def cliente(tmp_path, monkeypatch):
    """Cliente Flask com dados em pasta temporária: nunca toca nos modelos reais."""
    monkeypatch.setenv("PYTICIPANTES_DATA", str(tmp_path / "data"))
    monkeypatch.setenv("PYTICIPANTES_SAIDA", str(tmp_path / "saida"))
    from pyticipantes import app as app_mod
    from pyticipantes import config, emails, modelos, render

    for mod in (config, modelos, emails, render, app_mod):
        importlib.reload(mod)
    return app_mod.app.test_client()
