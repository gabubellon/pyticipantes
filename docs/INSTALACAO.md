# Instalação e execução

## Com Docker (ou Podman)

```bash
make run        # sobe em http://127.0.0.1:8000
make status     # confere se está rodando
make logs       # acompanha os logs
make down       # desliga (data/ e saida/ são mantidos)
make restart    # desliga e sobe de novo
make rebuild    # reconstrói a imagem sem cache
```

> Atenção: `restart` e `rebuild` recriam o container. Se um envio de e-mail está em andamento,
> ele é interrompido. Espere terminar antes.

`data/` (modelos, fontes, backups, lixeira) e `saida/` (PDFs e `envios.log`) são volumes:
nada se perde ao recriar o container. A porta é publicada só em `127.0.0.1`.
O botão "Abrir pasta" não funciona dentro do container; use a pasta `saida/` do projeto.

## Sem Docker (Python >= 3.10)

```bash
python -m venv .venv && source .venv/bin/activate
pip install .
pyticipantes                  # abre http://127.0.0.1:8000
```

Opções: `pyticipantes --host 0.0.0.0 --porta 9000`. Também funciona `python -m pyticipantes`.

## Variáveis de ambiente

| Variável | Padrão | Efeito |
|---|---|---|
| `PYTICIPANTES_PORTA` | `8000` | Porta |
| `PYTICIPANTES_HOST` | `127.0.0.1` | Interface de escuta (no Docker: `0.0.0.0`) |
| `PYTICIPANTES_BIND` | `127.0.0.1` | Interface publicada no host pelo compose |
| `PYTICIPANTES_USUARIO` / `PYTICIPANTES_SENHA` | vazio | Liga HTTP Basic |
| `PYTICIPANTES_DATA` | `./data` | Modelos, fontes, backups e lixeira |
| `PYTICIPANTES_SAIDA` | `./saida` | PDFs, manifesto e `envios.log` |

Para expor o app fora do seu computador, leia [Self-host](SELF-HOST.md).

## Onde estão seus dados

```
data/modelos/<id>/modelo.json   layout, fundo e planilha de cada certificado
data/backups/<id>/              últimas 30 versões do layout
data/lixeira/                   certificados excluídos (recuperáveis)
saida/<id>/*.pdf                PDFs gerados
saida/<id>/envios.log           histórico permanente dos envios de e-mail
```

**Nunca apague `data/`.** Faça cópia do layout em "Salvar layout em arquivo" (passo 2).

## Desenvolvimento

```bash
make install   # pip install -e . --group dev --group docs  (requer pip >= 25.1)
make test
make lint
make docs-serve
```
