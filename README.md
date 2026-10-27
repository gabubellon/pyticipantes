# Gerador de Certificados

App web local para criar certificados em PDF a partir de uma planilha, com prévia ao vivo,
geração em lote e envio por e-mail com log. Pode ter vários modelos de certificado.

## Como usar

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pybr_certificados          # abre http://127.0.0.1:8000
```

1. **Dados** — envie uma planilha `.xlsx`, `.xls` ou `.csv`. Cada coluna vira um marcador.
2. **Design e prévia** — edite os textos, escolha fonte, tamanho, cor, alinhamento e posição,
   envie a imagem de fundo (e fontes `.ttf`). A prévia atualiza ao vivo para a linha escolhida.
3. **Gerar e listar** — gera um PDF por linha em `saida/<modelo>/`, lista os arquivos (clique
   para abrir) e permite abrir a pasta.
4. **Enviar e-mail** — configure o SMTP, assunto e corpo, marque os certificados e acompanhe o
   log em tempo real. A tabela guarda quem já recebeu.

### Docker

```bash
make run        # sobe em http://127.0.0.1:8000
make down       # desliga
make restart    # religa (desliga e sobe de novo)
make rebuild    # religa reconstruindo a imagem sem cache
make logs       # acompanha os logs
make status     # mostra se está rodando
```

(Equivale a `docker compose up -d --build` / `docker compose down`.)

`data/` (modelos, fontes, backups, lixeira) e `saida/` são montados como volumes, então nada se perde ao recriar o
container. A porta é publicada apenas em `127.0.0.1`. O botão "Abrir pasta" não funciona dentro
do container: use a pasta `saida/` do projeto.

### Marcadores

Use `{coluna}` em qualquer texto, no nome do arquivo, no assunto e no corpo do e-mail. O nome
da coluna não diferencia maiúsculas de minúsculas e pode ter espaços (`{carga horária}`).
Marcadores sem coluna correspondente permanecem visíveis no texto. Os textos aceitam
`<b>`, `<i>` e `<u>`.

#### Formatação do nome (filtros)

Acrescente `|filtro` ao marcador. Dá para combinar vários, na ordem: `{nome|titulo|abreviar}`.
Exemplo com `gabriel ALVES bezerra de souza bellon`:

| Filtro | Resultado |
|---|---|
| `maiusculo` | GABRIEL ALVES BEZERRA DE SOUZA BELLON |
| `minusculo` | gabriel alves bezerra de souza bellon |
| `titulo` | Gabriel Alves Bezerra de Souza Bellon |
| `primeiro` | gabriel |
| `ultimo` | bellon |
| `primeiro_ultimo` | gabriel bellon |
| `abreviar` | gabriel A. B. S. bellon (use `titulo\|abreviar` → Gabriel A. B. S. Bellon) |
| `iniciais` | GABSB |

Partículas (de, da, do, dos…) são ignoradas nas iniciais. No passo 2 há um seletor de formato
que já insere o filtro ao clicar no campo.

O modelo padrão espera as colunas `nome`, `evento`, `hora`, `data`, `local` e `email`
(veja `data/exemplo.csv`), mas você pode ter quantas colunas quiser e reescrever os textos.

### E-mail (Gmail)

Use uma [senha de app](https://myaccount.google.com/apppasswords), não a senha da conta.
A senha é usada só durante o envio e **nunca é gravada em disco**.

## Onde ficam seus layouts (e como não perdê-los)

Cada certificado é salvo automaticamente em `data/modelos/<id>/modelo.json` (+ fundo e planilha).
Além disso:

- **Backups automáticos:** cada mudança no layout gera uma cópia em `data/backups/<id>/` (últimas 30).
- **Lixeira:** "Excluir" move o certificado para `data/lixeira/` em vez de apagar.
- **Exportar/importar:** no passo 2, "Salvar layout em arquivo" baixa um `.zip` (layout + fundo, sem a
  planilha) e "Carregar layout" cria um novo certificado a partir dele. Guarde esse arquivo onde quiser.

**Não apague a pasta `data/`** — é onde tudo mora. `PYBR_DATA=/outra/pasta` muda esse local.

## Estrutura

```
pybr_certificados/
├── app.py        # servidor Flask (API)
├── modelos.py    # modelos, planilhas e marcadores
├── render.py     # desenho do PDF (reportlab)
├── emails.py     # envio SMTP em segundo plano com log
└── static/       # interface (index.html + app.js)
assets/           # imagens de fundo de exemplo (copiadas para novos modelos)
data/exemplo.csv  # planilha de exemplo
data/modelos/     # seus modelos (ignorado pelo git)
saida/            # PDFs gerados (ignorado pelo git)
```

## Privacidade

O servidor escuta apenas em `127.0.0.1`. Modelos, planilhas e PDFs contêm dados pessoais e estão
no `.gitignore`.
