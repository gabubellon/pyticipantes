# Campos e filtros

Use `{coluna}` em qualquer texto do certificado, no nome do arquivo, no assunto e no corpo do e-mail.

- O nome da coluna não diferencia maiúsculas de minúsculas e pode ter espaços: `{carga horária}`.
- Campo sem coluna correspondente continua visível no texto (fácil de notar na prévia).
- Os textos aceitam `<b>negrito</b>`, `<i>itálico</i>` e `<u>sublinhado</u>`.

## Filtros

Acrescente `|filtro`. Combine na ordem: `{nome|titulo|abreviar}`.
Exemplo com `joão MANOELA da silva santos souza`:

| Filtro | Resultado |
|---|---|
| `maiusculo` | JOÃO MANOELA DA SILVA SANTOS SOUZA |
| `minusculo` | joão manoela da silva santos souza |
| `titulo` | João Manoela da Silva Santos Souza |
| `primeiro` | joão |
| `ultimo` | souza |
| `primeiro_ultimo` | joão souza |
| `abreviar` | joão M. S. S. souza |
| `iniciais` | JMSSS |

`{nome|titulo|abreviar}` dá **João M. S. S. Souza**. Partículas (de, da, do, dos…) são
ignoradas nas iniciais.

## Colunas usadas pelo modelo padrão

`nome`, `evento`, `hora`, `data`, `local` e `email` (veja [Exemplos para teste](EXEMPLOS.md)). Você pode ter
quantas colunas quiser e reescrever os textos.
