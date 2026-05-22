.PHONY: help build up down logs shell restart clean test lint

# Colors for output
BLUE := \033[0;36m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Mostrar esta mensagem de ajuda
	@echo "$(BLUE)=== RH Pro - Docker Makefile ===$(NC)"
	@echo ""
	@echo "$(GREEN)Uso:$(NC) make [comando]"
	@echo ""
	@echo "$(GREEN)Comandos disponíveis:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Exemplos:$(NC)"
	@echo "  make build        # Build da imagem"
	@echo "  make up           # Iniciar containers"
	@echo "  make down         # Parar containers"
	@echo "  make logs         # Ver logs em tempo real"

build: ## Build da imagem Docker
	@echo "$(BLUE)🔨 Building Docker image...$(NC)"
	docker-compose build

build-prod: ## Build da imagem para produção
	@echo "$(BLUE)🔨 Building production Docker image...$(NC)"
	docker build -t rh-pro:latest .

up: ## Iniciar containers (background)
	@echo "$(BLUE)🚀 Starting containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Containers iniciados$(NC)"
	@echo "$(BLUE)→ Acesse: http://localhost:5000$(NC)"

up-prod: ## Iniciar containers em produção
	@echo "$(BLUE)🚀 Starting production containers...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✓ Production containers iniciados$(NC)"

down: ## Parar e remover containers
	@echo "$(BLUE)⏹️  Stopping containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Containers parados$(NC)"

down-prod: ## Parar containers de produção
	@echo "$(BLUE)⏹️  Stopping production containers...$(NC)"
	docker-compose -f docker-compose.prod.yml down
	@echo "$(GREEN)✓ Production containers parados$(NC)"

restart: ## Reiniciar containers
	@echo "$(BLUE)🔄 Restarting containers...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ Containers reiniciados$(NC)"

logs: ## Ver logs em tempo real
	@echo "$(BLUE)📋 Showing logs (Ctrl+C para sair)...$(NC)"
	docker-compose logs -f rh_pro

logs-prod: ## Ver logs de produção
	@echo "$(BLUE)📋 Showing production logs...$(NC)"
	docker-compose -f docker-compose.prod.yml logs -f rh_pro

logs-all: ## Ver logs de todos os containers
	@echo "$(BLUE)📋 Showing all logs...$(NC)"
	docker-compose logs -f

shell: ## Entrar em shell no container
	@echo "$(BLUE)🐚 Entering container shell...$(NC)"
	docker-compose exec rh_pro bash

shell-prod: ## Entrar em shell no container de produção
	@echo "$(BLUE)🐚 Entering production container shell...$(NC)"
	docker-compose -f docker-compose.prod.yml exec rh_pro bash

status: ## Verificar status dos containers
	@echo "$(BLUE)📊 Container status:$(NC)"
	docker-compose ps

clean: ## Remover containers, volumes e imagens não usadas
	@echo "$(BLUE)🧹 Cleaning Docker resources...$(NC)"
	docker-compose down -v
	docker system prune -f
	@echo "$(GREEN)✓ Limpeza concluída$(NC)"

clean-prod: ## Limpar recursos de produção
	@echo "$(BLUE)🧹 Cleaning production Docker resources...$(NC)"
	docker-compose -f docker-compose.prod.yml down -v
	@echo "$(GREEN)✓ Production limpeza concluída$(NC)"

test: ## Testar conectividade da aplicação
	@echo "$(BLUE)🧪 Testing application...$(NC)"
	@docker-compose exec rh_pro bash -c "curl -f http://localhost:5000/ > /dev/null 2>&1 && echo '$(GREEN)✓ Application is responding$(NC)' || echo '$(RED)✗ Application not responding$(NC)'"

test-ad: ## Testar conexão com Active Directory
	@echo "$(BLUE)🧪 Testing AD connection...$(NC)"
	docker-compose exec rh_pro python -c "from services import authenticate; print('$(GREEN)✓ AD configuration loaded$(NC)')" 2>&1 || echo "$(RED)✗ AD connection failed$(NC)"

validate: ## Validar configuração
	@echo "$(BLUE)✓ Validating configuration...$(NC)"
	@test -f .env || (echo "$(RED)✗ .env file not found$(NC)" && exit 1)
	@test -f requirements.txt || (echo "$(RED)✗ requirements.txt not found$(NC)" && exit 1)
	@test -f Dockerfile || (echo "$(RED)✗ Dockerfile not found$(NC)" && exit 1)
	@grep -q SECRET_KEY .env || (echo "$(RED)✗ SECRET_KEY not set in .env$(NC)" && exit 1)
	@echo "$(GREEN)✓ All validations passed$(NC)"

config: ## Mostrar configuração do docker-compose
	@echo "$(BLUE)Docker Compose configuration:$(NC)"
	docker-compose config

config-prod: ## Mostrar configuração de produção
	@echo "$(BLUE)Production Docker Compose configuration:$(NC)"
	docker-compose -f docker-compose.prod.yml config

env-check: ## Verificar variáveis de ambiente
	@echo "$(BLUE)Environment variables in container:$(NC)"
	docker-compose exec rh_pro env | grep -E "FLASK|AD_|SECRET|MASTER|PORT" || echo "$(RED)No environment variables found$(NC)"

python-check: ## Verificar versão do Python
	@echo "$(BLUE)Python version:$(NC)"
	docker-compose exec rh_pro python --version

pip-list: ## Listar pacotes instalados
	@echo "$(BLUE)Installed packages:$(NC)"
	docker-compose exec rh_pro pip list

install-package: ## Instalar pacote (use: make install-package PKG=nome-do-pacote)
	@if [ -z "$(PKG)" ]; then \
		echo "$(RED)Erro: Especifique o pacote com PKG=nome-do-pacote$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Installing $(PKG)...$(NC)"
	docker-compose exec rh_pro pip install $(PKG)
	@echo "$(GREEN)✓ $(PKG) installed$(NC)"

push-image: ## Push da imagem para registry (use: make push-image REGISTRY=seu-registry TAG=v1.0.0)
	@if [ -z "$(REGISTRY)" ] || [ -z "$(TAG)" ]; then \
		echo "$(RED)Erro: Especifique REGISTRY e TAG$(NC)"; \
		exit 1; \
	fi
	@echo "$(BLUE)Tagging image...$(NC)"
	docker tag rh-pro:latest $(REGISTRY)/rh-pro:$(TAG)
	@echo "$(BLUE)Pushing image...$(NC)"
	docker push $(REGISTRY)/rh-pro:$(TAG)
	@echo "$(GREEN)✓ Image pushed$(NC)"

# Aliases convenientes
b: build
u: up
d: down
l: logs
s: shell
t: test

.DEFAULT_GOAL := help
