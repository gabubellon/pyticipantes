# Envio por e-mail

## Configuração (Gmail / Google Workspace)

| Campo | Valor |
|---|---|
| Servidor | `smtp.gmail.com` |
| Porta | `587` (STARTTLS) |
| Usuário | seu e-mail completo |
| Senha | **senha de app**, não a senha da conta |

Crie a senha de app em <https://myaccount.google.com/apppasswords> (exige verificação em duas
etapas). Em contas Workspace o administrador pode precisar liberar essa opção. A senha é usada
só durante o envio e **nunca é gravada em disco**.

## Como enviar

1. Escreva assunto e texto (aceitam campos: `Olá {nome|primeiro},`).
2. Filtre a lista, use **Só pendentes visíveis** e marque quem vai receber.
3. Clique em **Enviar** e acompanhe o log. Teste antes com um único certificado para você mesmo.

## Como o envio se protege de bloqueios

- **Ritmo:** 1 e-mail a cada ~2 segundos (cerca de 30/min).
- **Reconexão automática:** se a conexão cai, ela é refeita.
- **Novas tentativas:** até 3 por e-mail, com espera de 60s e 180s em erros temporários (4xx, timeout).
- **Parada de segurança:** após 5 falhas seguidas o envio para. Aguarde e reenvie os pendentes.
- **Sem duplicar:** quem já recebeu (`enviado_em`) é pulado em qualquer reenvio.
- **Autenticação recusada:** o envio para na hora.

## Limites do Gmail

| Conta | Limite diário aproximado |
|---|---|
| Gmail pessoal | ~500 destinatários |
| Google Workspace | ~2.000 destinatários |

Ao estourar, o Google responde com erros como `421 4.3.0 Temporary System Problem` ou `550 5.4.5`.
Para listas grandes, envie em lotes (ex.: 200 por vez, com intervalo) e reenvie os pendentes depois.

## Reenviar após erro

1. **Não gere os certificados de novo.** Gerar apaga os PDFs e zera o controle de quem já recebeu.
2. Aguarde alguns minutos (ou o dia seguinte, se foi limite diário).
3. Use **Só pendentes visíveis** e envie de novo.

## O log

- Na tela: em tempo real durante o envio.
- Em disco: `saida/<certificado>/envios.log`, uma linha por evento, com data completa, sempre
  acrescentando (nunca sobrescreve). Sobrevive a reinício do servidor/container.

```
[2026-10-28 23:02:45] OK    Maria → maria@exemplo.com
[2026-10-28 23:04:27] AVISO Ana → ana@exemplo.com: (421, 4.3.0 ...) (tentativa 1/3, aguardando 60s)
[2026-10-28 23:09:00] INFO  Envio finalizado. 120 enviado(s) nesta rodada.
```

Níveis: `OK` enviado, `AVISO` pulado ou nova tentativa, `ERRO` falha definitiva, `INFO` andamento.

## Erros comuns

| Mensagem | Significado / ação |
|---|---|
| `421 4.3.0 Temporary System Problem` | Limite temporário do Google. O app espera e tenta de novo; se persistir, aguarde. |
| `Connection unexpectedly closed` / timeout | Conexão caiu. O app reconecta sozinho. |
| `535 Username and Password not accepted` | Use senha de app e confira o usuário. |
| `550 5.4.5 Daily user sending quota exceeded` | Cota diária estourada. Reenvie os pendentes amanhã. |
| `sem e-mail, ignorado` | A linha não tem e-mail; confira a coluna de e-mail. |
