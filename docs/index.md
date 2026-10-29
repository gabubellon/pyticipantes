# Pyticipantes

App web para criar certificados em PDF a partir de uma planilha, com prévia ao vivo,
geração em lote e envio por e-mail com log. Roda no seu computador ou servidor (self-hosted): seus dados não saem dele.

## Documentação

| Guia | Para quê |
|---|---|
| [Instalação e execução](INSTALACAO.md) | Subir o app com Docker ou Python |
| [Self-host](SELF-HOST.md) | Servidor, senha, HTTPS, backup e atualização |
| [Guia de uso](USO.md) | Passo a passo: planilha, layout, geração e envio |
| [Envio por e-mail](ENVIO-EMAIL.md) | Gmail/Workspace, limites, reenvio e leitura do log |
| [Exemplos para teste](EXEMPLOS.md) | Baixar planilha e imagem de fundo prontas |
| [Referência de campos e filtros](CAMPOS.md) | `{nome\|titulo}`, formatação e exemplos |

## Fluxo em 30 segundos

1. **Planilha** — uma linha por certificado, cabeçalho na primeira linha.
2. **Layout** — fundo, textos, fontes e posição, com prévia ao vivo.
3. **Gerar** — um PDF por linha em `saida/<certificado>/`.
4. **Enviar** — SMTP com senha de app, reenvio só dos pendentes e log salvo em disco.
