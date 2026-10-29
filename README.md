# Pyticipantes

Gere **certificados de participação em PDF** a partir de uma planilha, com prévia ao vivo, geração
em lote e envio por e-mail com log. Roda no seu computador ou no seu servidor (**self-hosted**):
os dados dos participantes nunca saem da sua máquina.

📖 **Documentação:** [docs/index.md](docs/index.md) · [Guia de uso](docs/USO.md) ·
[Self-host](docs/SELF-HOST.md) · [Envio por e-mail](docs/ENVIO-EMAIL.md)

## Começando

### Com Docker ou Podman (recomendado)

```bash
git clone https://github.com/gabubellon/pyticipantes.git
cd pyticipantes
make run            # ou: docker compose up -d --build
```

Abra **http://127.0.0.1:8000**. A documentação fica em `/docs/` no próprio app.

### Com Python (>= 3.10)

```bash
git clone https://github.com/gabubellon/pyticipantes.git
cd pyticipantes
python -m venv .venv && source .venv/bin/activate
pip install .
pyticipantes                # abre http://127.0.0.1:8000
```

Não tem planilha à mão? Use os [exemplos para teste](docs/EXEMPLOS.md) (planilha + imagem de fundo),
também disponíveis para download dentro do app.

## O que faz

1. **Dados** — envie `.xlsx`, `.xls` ou `.csv`; cada coluna vira um marcador `{coluna}`.
2. **Design e prévia** — textos, fontes, cores, posição e imagem de fundo, com prévia ao vivo.
3. **Gerar** — um PDF por linha em `saida/<modelo>/`.
4. **Enviar** — SMTP (ex.: Gmail com senha de app), reenvio só dos pendentes, retry automático e
   log permanente em `saida/<modelo>/envios.log`.

Marcadores aceitam filtros de nome, como `{nome|titulo|abreviar}`; veja
[Campos e filtros](docs/CAMPOS.md).

## Self-host

Por padrão o app só escuta em `127.0.0.1`. Para publicá-lo num servidor, defina usuário e senha
(`PYTICIPANTES_USUARIO` / `PYTICIPANTES_SENHA`) ou use um proxy reverso com autenticação e HTTPS.
Passo a passo, backup e atualização em [docs/SELF-HOST.md](docs/SELF-HOST.md).

| Variável | Padrão | Efeito |
|---|---|---|
| `PYTICIPANTES_PORTA` | `8000` | Porta |
| `PYTICIPANTES_HOST` | `127.0.0.1` | Interface de escuta (`0.0.0.0` no Docker) |
| `PYTICIPANTES_BIND` | `127.0.0.1` | Interface publicada no host pelo compose |
| `PYTICIPANTES_USUARIO` / `PYTICIPANTES_SENHA` | vazio | Liga HTTP Basic |
| `PYTICIPANTES_DATA` | `./data` | Modelos, fontes, backups, lixeira |
| `PYTICIPANTES_SAIDA` | `./saida` | PDFs, manifesto e `envios.log` |

Veja [.env.example](.env.example). **Não apague `data/`**: é onde ficam seus layouts.

## Desenvolvimento

```bash
make install    # pip install -e . --group dev --group docs  (pip >= 25.1)
make test       # pytest
make lint       # ruff (PEP 8)
make docs-serve # documentação em http://127.0.0.1:8001/docs/
```

```
src/pyticipantes/
├── app.py        # servidor Flask (API) + autenticação opcional
├── modelos.py    # modelos, planilhas e marcadores
├── render.py     # desenho do PDF (reportlab)
├── emails.py     # envio SMTP em segundo plano, com retry e log
├── exemplos/     # planilha e fundo de exemplo (baixáveis)
└── static/       # interface (index.html + app.js)
docs/             # documentação (MkDocs)
tests/            # pytest
```

Dependências e ferramentas ficam em [pyproject.toml](pyproject.toml) (PEP 621; grupos `dev` e `docs`
via PEP 735).

## Licença

[AGPL-3.0](LICENSE): uso gratuito; cópias e versões modificadas (inclusive oferecidas como serviço)
precisam manter a origem e publicar o código sob a mesma licença. Para usar sem essas obrigações,
veja a [licença comercial](COMMERCIAL.md). Contribuições: [CONTRIBUTING.md](CONTRIBUTING.md).

## Privacidade

Modelos, planilhas e PDFs contêm dados pessoais e estão no `.gitignore`. A senha SMTP é usada só
durante o envio e nunca é gravada.
