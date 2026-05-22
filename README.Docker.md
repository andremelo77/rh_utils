# RH Pro - Docker Compose Setup

Este documento descreve como buildar e rodar a aplicação RH Pro usando Docker Compose.

## Pré-requisitos

- Docker (versão 20.10+)
- Docker Compose (versão 2.0+)

## Estrutura de Arquivos Docker

```
.
├── Dockerfile           # Imagem Docker multi-stage otimizada
├── docker-compose.yml   # Orquestração de containers
├── .dockerignore        # Arquivos excluídos da build
├── .env.example         # Template de variáveis de ambiente
├── .env                 # Variáveis de ambiente (NUNCA commitar!)
├── requirements.txt     # Dependências Python
└── app.py              # Aplicação Flask
```

## Configuração Inicial

### 1. Preparar as variáveis de ambiente

```bash
# Copiar o template
cp .env.example .env

# Editar o arquivo .env com suas configurações reais
# IMPORTANTE: Altere especialmente:
# - SECRET_KEY: gere uma chave segura com:
#   python -c "import secrets; print(secrets.token_hex(32))"
# - AD_SERVER: seu controlador de domínio
# - AD_BASE_DN: sua estrutura de OU
# - MASTER_PASSWORD: senha mestre para secrets.enc
nano .env
```

### 2. Arquivos de Segredos

Os arquivos `secrets.enc` e `key.enc` devem ser:

- **Gerados localmente** usando `setup_credentials.py`
- **Nunca commitados** no Git (já estão em .gitignore)
- **Montados como volumes read-only** no container

```bash
# Gerar os arquivos de segredos (se ainda não existirem)
python setup_credentials.py
```

## Build e Deploy

### Build da Imagem

```bash
# Build padrão
docker-compose build

# Build sem cache
docker-compose build --no-cache

# Build com progresso detalhado
docker-compose build --progress=plain
```

### Iniciar a Aplicação

```bash
# Iniciar em background
docker-compose up -d

# Iniciar com logs no console
docker-compose up

# Iniciar em background e ver logs
docker-compose up -d && docker-compose logs -f
```

### Parar a Aplicação

```bash
# Parar containers
docker-compose stop

# Parar e remover containers
docker-compose down

# Limpar volumes também
docker-compose down -v
```

## Operações Comuns

### Ver logs

```bash
# Todos os logs
docker-compose logs

# Logs em tempo real
docker-compose logs -f

# Últimas 100 linhas
docker-compose logs --tail=100

# Apenas do serviço rh_pro
docker-compose logs -f rh_pro
```

### Executar comando no container

```bash
# Shell interativo
docker-compose exec rh_pro bash

# Executar comando específico
docker-compose exec rh_pro python -c "import sys; print(sys.version)"

# Instalar pacote adicional
docker-compose exec rh_pro pip install novo-pacote
```

### Reconstruir após mudanças

```bash
# Se alterou requirements.txt
docker-compose build && docker-compose up -d

# Se alterou código Python (sem rebuild)
docker-compose restart rh_pro
```

## Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `FLASK_ENV` | `production` | Ambiente (production/development) |
| `FLASK_DEBUG` | `False` | Modo debug (nunca True em produção) |
| `SECRET_KEY` | - | **OBRIGATÓRIO**: chave secreta para sessões |
| `PORT` | `5000` | Porta da aplicação |
| `AD_SERVER` | - | Endereço do servidor AD |
| `AD_USE_SSL` | `True` | Usar SSL/TLS para LDAP |
| `AD_BASE_DN` | - | Base DN do Active Directory |
| `AD_ALLOWED_GROUP_DN` | - | DN do grupo autorizado |
| `MASTER_PASSWORD` | - | **OBRIGATÓRIO**: senha para descriptografia |

## Troubleshooting

### Container não inicia

```bash
# Ver logs de erro
docker-compose logs rh_pro

# Verificar se as variáveis de ambiente estão corretas
docker-compose config

# Tentar rebuild
docker-compose build --no-cache && docker-compose up
```

### Erro de conexão com AD

```bash
# Verificar conectividade de rede
docker-compose exec rh_pro ping your-ad-server.local

# Verificar variáveis de configuração
docker-compose exec rh_pro env | grep AD_
```

### Permissão negada em arquivos

Os containers rodam como usuário não-root (`appuser:1000`) por segurança.

```bash
# Ajustar permissões dos arquivos de secret localmente
chmod 600 secrets.enc key.enc
```

## Produção - Boas Práticas

### 1. Secrets Management

```bash
# Use um gerenciador de secrets em vez de .env:
# - HashiCorp Vault
# - AWS Secrets Manager
# - Azure Key Vault
# - Docker Secrets (para Docker Swarm)
```

### 2. Escalabilidade

```bash
# docker-compose.yml para produção com múltiplas instâncias:
version: '3.8'
services:
  rh_pro:
    # ... configuração ...
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
```

### 3. Reverse Proxy

Configure um nginx ou Apache na frente:

```dockerfile
# Use traefik ou nginx como reverse proxy
# Mais seguro que expor porta direta do Flask
```

### 4. Monitoring

```bash
# Adicionar health checks melhorados
# Implementar logging centralizado (ELK Stack, etc)
# Configurar alertas
```

## Workflow de Desenvolvimento

```bash
# 1. Fazer mudanças no código
nano app.py

# 2. Testar localmente
python app.py

# 3. Usar Docker Compose para replicar produção
docker-compose up

# 4. Reconstruir se mudou requirements.txt
docker-compose build && docker-compose up
```

## Remover tudo e começar do zero

```bash
docker-compose down -v  # Remove containers, networks e volumes
docker system prune     # Limpa imagens não usadas
```

## Próximos Passos

- [ ] Configurar `.env` com valores reais
- [ ] Gerar `secrets.enc` com `setup_credentials.py`
- [ ] Testar `docker-compose up`
- [ ] Validar conectividade com AD
- [ ] Implementar monitoring e logging
- [ ] Configurar backup de volumes
- [ ] Documentar variáveis de ambiente da sua organização
