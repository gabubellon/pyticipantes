# Usa docker se existir; senão podman (ex.: DOCKER=podman make run)
DOCKER ?= $(shell command -v docker || command -v podman)
COMPOSE = $(DOCKER) compose

.PHONY: help run up down restart rebuild logs status

help: ## Lista os comandos
	@grep -E '^[a-z]+:.*##' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-9s %s\n", $$1, $$2}'

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
