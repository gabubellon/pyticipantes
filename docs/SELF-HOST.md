# Self-host

Como rodar o Pyticipantes em um servidor ou máquina compartilhada.

## 1. Subir

```bash
git clone https://github.com/gabubellon/pyticipantes.git
cd pyticipantes
cp .env.example .env        # ajuste porta, usuário e senha
make run
```

## 2. Proteger o acesso

O app **não tem login por padrão** e controla arquivos e envio de e-mail. Nunca o exponha na
internet sem proteção. Há duas formas:

### Opção A — senha embutida (HTTP Basic)

No `.env`:

```
PYTICIPANTES_USUARIO=admin
PYTICIPANTES_SENHA=uma-senha-longa
PYTICIPANTES_BIND=0.0.0.0
```

O `/saude` (healthcheck) continua livre. Use **HTTPS** na frente (opção B), pois Basic sem TLS
trafega a senha em texto claro.

### Opção B — proxy reverso com HTTPS (recomendado)

Mantenha `PYTICIPANTES_BIND=127.0.0.1` e publique via proxy, por exemplo Caddy:

```
certificados.exemplo.com {
    basic_auth {
        admin <hash gerado por: caddy hash-password>
    }
    reverse_proxy 127.0.0.1:8000
}
```

## 3. Dados e backup

| Pasta | Conteúdo | Backup |
|---|---|---|
| `data/` | Layouts, planilhas, fontes, backups e lixeira | **Sim, sempre** |
| `saida/` | PDFs, controle de envio e `envios.log` | Sim, se quiser o histórico |

Ambas são volumes do compose (`./data`, `./saida`); copiar essas pastas basta.

## 4. Atualizar

```bash
git pull
make restart
```

Evite reiniciar enquanto um envio de e-mail estiver em andamento: o envio é interrompido (quem já
recebeu fica registrado e é pulado no reenvio).

## 5. Saúde e logs

- `GET /saude` retorna `{"status":"ok","versao":"..."}` e é usado no `HEALTHCHECK` da imagem.
- `make logs` acompanha o servidor; o histórico de e-mails fica em `saida/<modelo>/envios.log`.

## 6. Sem Docker

```bash
pip install .
PYTICIPANTES_HOST=0.0.0.0 PYTICIPANTES_USUARIO=admin PYTICIPANTES_SENHA=... pyticipantes
```

Use `systemd` ou similar para manter rodando. O app é um único processo (o andamento dos envios
fica em memória), então **não use vários workers**.
