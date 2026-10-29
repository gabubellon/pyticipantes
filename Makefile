# Usa docker se existir; senão podman (ex.: DOCKER=podman make run)
DOCKER ?= $(shell command -v docker || command -v podman)
COMPOSE = $(DOCKER) compose

.PHONY: help run up down restart rebuild logs status install test lint fmt docs docs-serve

help: ## Lista os comandos
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-11s %s\n", $$1, $$2}'

run: ## Sobe o app (constrói a imagem se preciso) em http://127.0.0.1:8000
	$(COMPOSE) up -d --build
	@echo "App em http://127.0.0.1:8000"

up: run ## Alias de run

down: ## Desliga o app (os dados em data/ e saida/ são mantidos)
	$(COMPOSE) down

restart: ## Religa o app (desliga e sobe de novo)
	$(COMPOSE) down
	$(COMPOSE) up -d --build
	@echo "App em http://127.0.0.1:8000"

rebuild: ## Religa reconstruindo a imagem do zero (sem cache)
	$(COMPOSE) down
	$(COMPOSE) build --no-cache
	$(COMPOSE) up -d

logs: ## Mostra os logs em tempo real
	$(COMPOSE) logs -f

status: ## Mostra se está rodando
	$(COMPOSE) ps

install: ## Instala para desenvolvimento (editável + grupos dev e docs; requer pip >= 25.1)
	python -m pip install -U pip
	python -m pip install -e . --group dev --group docs

test: ## Roda os testes
	python -m pytest

lint: ## Verifica o estilo (PEP 8 via ruff)
	ruff check .

fmt: ## Corrige o estilo automaticamente
	ruff check --fix .

docs: ## Gera a documentação (MkDocs) em src/pyticipantes/site, servida em /docs/
	mkdocs build

docs-serve: ## Documentação com recarga automática em http://127.0.0.1:8001/docs/
	mkdocs serve -a 127.0.0.1:8001
