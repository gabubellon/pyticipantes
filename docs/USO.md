# Como usar o Gerador de Certificados

Guia rápido, passo a passo, para quem vai gerar e enviar certificados.

## 1. Abrir o app

```bash
make run          # com Docker/Podman
# ou, sem Docker:
pip install -r requirements.txt
python -m pybr_certificados
```

Abra **http://127.0.0.1:8000**. Para desligar: `make down` (ou `Ctrl+C`, sem Docker).
Seus dados ficam na pasta `data/` e nunca se perdem ao desligar.

## 2. Preparar a planilha

Crie um arquivo `.xlsx`, `.xls` ou `.csv` com **uma linha por certificado** e uma linha de cabeçalho:

| nome | email | evento | data | hora | local |
|---|---|---|---|---|---|
| Maria Souza | maria@exemplo.com | Tutorial de Python | 21 de Outubro | 4 horas | Auditório A |

- Os nomes das colunas são livres. Cada coluna vira um **campo** que você usa nos textos.
- Para enviar e-mail, uma coluna precisa ter o e-mail (por padrão `email`).
- Há um exemplo em `data/exemplo.csv`.

## 3. Os 4 passos

Na barra do topo escolha o certificado (ou crie outro em **+ Novo**) e siga os passos.

### Passo 1 — Planilha
Clique na área tracejada e escolha o arquivo. Confira a tabela de pré-visualização.
Aqui você também muda o **nome do certificado**.

### Passo 2 — Layout
- **Fundo:** envie uma imagem png ou jpg. **Orientação:** paisagem ou retrato.
- **Textos:** cada caixa é um texto do certificado. Escolha fonte, tamanho, cor e alinhamento.
  Em **Posição** ajuste onde ele fica (% da página, medido a partir do topo e da esquerda).
- **Campos:** escreva `{nome}`, `{evento}`... ou clique num chip da lista para inserir no texto.
- **Prévia:** à direita, atualiza sozinha. Mude o "Participante nº" para ver outras linhas.
- Use **+ Adicionar texto** para mais textos e ↑ ↓ para reordenar.

Tudo é salvo automaticamente.

#### Formatando nomes
Acrescente `|filtro` ao campo. Pode combinar: `{nome|titulo|abreviar}`.

| Filtro | Resultado para `gabriel ALVES bezerra de souza bellon` |
|---|---|
| `maiusculo` | GABRIEL ALVES BEZERRA DE SOUZA BELLON |
| `minusculo` | gabriel alves bezerra de souza bellon |
| `titulo` | Gabriel Alves Bezerra de Souza Bellon |
| `primeiro` | gabriel |
| `ultimo` | bellon |
| `primeiro_ultimo` | gabriel bellon |
| `abreviar` | gabriel A. B. S. bellon |
| `iniciais` | GABSB |

Dica: `{nome|titulo|abreviar}` → **Gabriel A. B. S. Bellon**. O seletor "Formato ao inserir"
já coloca o filtro para você ao clicar num campo.

Também dá para usar `<b>negrito</b>`, `<i>itálico</i>` e `<u>sublinhado</u>` nos textos.
Se um campo ou filtro estiver escrito errado, ele aparece como está na prévia, então é fácil notar.

### Passo 3 — Gerar
Escolha **Todos** ou **Apenas os N primeiros** (ótimo para testar) e clique em **Gerar**.
Os PDFs vão para `saida/<certificado>/`. Clique num nome da lista para abrir o PDF.

> Gerar de novo apaga os PDFs anteriores deste certificado.

### Passo 4 — Enviar por e-mail (opcional)
1. Informe seu **e-mail** e a **senha de app**. No Gmail crie uma em
   https://myaccount.google.com/apppasswords (não use a senha normal). A senha não é salva.
2. Escreva o **assunto** e o **texto**. Pode usar campos, ex.: `Olá {nome|primeiro},`.
3. Na lista de destinatários, use o filtro por nome ou e-mail, **Marcar visíveis** ou
   **Só pendentes visíveis** e marque quem vai receber.
4. Clique em **Enviar** e acompanhe o andamento. A tabela mostra quem já recebeu ou deu erro.

Faça um teste antes: gere com "Apenas os 1 primeiros", com seu próprio e-mail na planilha.

## 4. Não perder seus layouts

- Cada mudança gera um backup em `data/backups/` e "Excluir" move para `data/lixeira/`.
- No passo 2, **⬇ Salvar layout em arquivo** baixa um `.zip` (sem a planilha) e
  **⬆ Carregar layout** cria um certificado a partir dele. Guarde uma cópia fora do computador.
- Nunca apague a pasta `data/`.

## 5. Problemas comuns

| Problema | O que fazer |
|---|---|
| "Não foi possível ler a planilha" | Confira se é `.xlsx`, `.xls` ou `.csv` e se a primeira linha é o cabeçalho. |
| Aparece `{campo}` no certificado | O nome não bate com a coluna da planilha (maiúsculas não importam). |
| Texto cortado ou fora do lugar | Aumente a **Largura** ou ajuste **Topo/Esquerda** em Posição. |
| Falha de autenticação no envio | Use uma **senha de app**, não a senha da conta. |
| E-mail "sem e-mail" na lista | Ajuste a **Coluna com o e-mail** em Gerar → Opções. |
| Acentos estranhos num `.csv` | Salve o CSV como UTF-8. |
| `make run` falha | Veja `make logs`; confirme que Docker ou Podman está iniciado. |
