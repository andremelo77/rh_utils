# Guia de Deploy - RH Pro com Docker

## Pré-requisitos

- Docker instalado (versão 20.10+)
- Docker Compose instalado (versão 2.0+)
- Acesso ao repositório da aplicação

## 🚀 Quick Start (5 minutos)

### 1. Preparar Configuração

```bash
# Copiar template de variáveis
cp .env.example .env

# Editar com suas configurações
nano .env
# Alterar: SECRET_KEY, AD_SERVER, AD_BASE_DN, AD_ALLOWED_GROUP_DN, MASTER_PASSWORD
```

### 2. Gerar Segredos

```bash
# Gerar arquivos encriptados de credenciais
python setup_credentials.py
```

### 3. Build e Start

```bash
# Build da imagem
docker-compose build

# Iniciar aplicação
docker-compose up -d

# Verificar
curl http://localhost:5000
docker-compose logs -f
```

## 📦 Estrutura de Arquivos Criados

| Arquivo | Propósito |
|---------|-----------|
| `Dockerfile` | Build multi-stage otimizado |
| `docker-compose.yml` | Orquestração - desenvolvimento |
| `docker-compose.prod.yml` | Orquestração - produção |
| `.dockerignore` | Arquivos excluídos do build |
| `entrypoint.sh` | Script de inicialização com suporte a variáveis |
| `.env.example` | Template de variáveis de ambiente |
| `.env.production.example` | Template para produção |
| `Makefile` | Comandos convenientes |
| `README.Docker.md` | Documentação detalhada |
| `DOCKER_CHECKLIST.md` | Checklist de verificação |
| `DEPLOYMENT_GUIDE.md` | Este arquivo |

## 🔐 Configuração de Segurança

### Variáveis Críticas em .env

```bash
# Gerar SECRET_KEY segura (execute no shell):
python -c "import secrets; print(secrets.token_hex(32))"

# Copiar o resultado e colar em .env
SECRET_KEY=<resultado_do_comando_acima>

# Definir MASTER_PASSWORD (mínimo 24 caracteres)
MASTER_PASSWORD=MudarIssoParaUmaSenhaForteMínimo24Caracteres
```

### Arquivo .gitignore Atualizado

Certifique-se que está presente:

```
.env
secrets.enc
key.enc
.venv/
__pycache__/
*.pyc
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────┐
│     Cliente (Navegador)              │
└──────────────┬──────────────────────┘
               │
               │ HTTP (porta 5000)
               ▼
┌──────────────────────────────────────┐
│   Docker Container: rh_pro           │
│  ┌────────────────────────────────┐  │
│  │   Gunicorn (WSGI Server)       │  │
│  │   - 4 workers                  │  │
│  │   - Porta 5000                 │  │
│  └──────┬─────────────────────────┘  │
│         │                            │
│  ┌──────▼─────────────────────────┐  │
│  │   Flask Application            │  │
│  │   - Routes & Handlers          │  │
│  │   - CSRF Protection            │  │
│  │   - Session Management         │  │
│  └──────┬─────────────────────────┘  │
│         │                            │
│  ┌──────▼─────────────────────────┐  │
│  │   Services                     │  │
│  │   - authenticate.py (LDAP)     │  │
│  │   - actions.py (Negócio)       │  │
│  │   - secrets.py (Encriptação)   │  │
│  └──────┬─────────────────────────┘  │
│         │                            │
└─────────┼────────────────────────────┘
          │
          │ LDAPS (porta 636)
          ▼
    ┌─────────────────┐
    │  AD / LDAP      │
    │  Server         │
    └─────────────────┘
```

## ⚙️ Operações Comuns

### Iniciar

```bash
# Iniciar em background
docker-compose up -d

# Iniciar e ver logs
docker-compose up

# Usar Makefile (recomendado)
make up
make logs
```

### Verificar Status

```bash
# Status dos containers
docker-compose ps

# Verificar se aplicação responde
curl http://localhost:5000

# Ver logs
docker-compose logs -f rh_pro

# Entrar no container
docker-compose exec rh_pro bash
```

### Parar

```bash
# Parar containers
docker-compose stop

# Parar e remover
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

### Atualizar Código

```bash
# Se mudou código (não requirements.txt)
docker-compose restart rh_pro

# Se mudou requirements.txt
docker-compose build
docker-compose up -d
```

## 📊 Variáveis de Ambiente

### Obrigatórias

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `SECRET_KEY` | Chave secreta para sessões | (32 hex chars) |
| `AD_SERVER` | Servidor do AD | dc01.empresa.local |
| `AD_BASE_DN` | Base DN do AD | OU=Users,DC=emp,DC=local |
| `MASTER_PASSWORD` | Senha para secrets.enc | (25+ chars) |

### Opcionais

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `PORT` | 5000 | Porta de escuta |
| `FLASK_ENV` | production | Ambiente (production/development) |
| `FLASK_DEBUG` | False | Modo debug |
| `AD_USE_SSL` | True | Usar LDAPS |
| `LOG_LEVEL` | INFO | Nível de logging |
| `GUNICORN_WORKERS` | 4 | Workers do Gunicorn |

## 🆘 Troubleshooting

### Erro: "Secret files not found"

```bash
python setup_credentials.py
docker-compose restart rh_pro
```

### Erro: "Cannot connect to AD"

```bash
# Verificar variáveis
docker-compose exec rh_pro env | grep AD_

# Testar conexão
docker-compose exec rh_pro ping your-ad-server.local
```

### Container não inicia

```bash
# Ver erro específico
docker-compose logs rh_pro

# Recompile tudo
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Porta já em uso

```bash
# Verificar o que está usando porta 5000
lsof -i :5000

# Ou mudar porta em .env
echo "PORT=8000" >> .env
docker-compose up -d
```

## 🔄 CI/CD Integration

### GitHub Actions

```yaml
name: Build and Push Docker Image

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: docker/setup-buildx-action@v2
      - uses: docker/login-action@v2
        with:
          registry: ${{ secrets.DOCKER_REGISTRY }}
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      - uses: docker/build-push-action@v4
        with:
          context: .
          push: true
          tags: |
            ${{ secrets.DOCKER_REGISTRY }}/rh-pro:latest
            ${{ secrets.DOCKER_REGISTRY }}/rh-pro:${{ github.sha }}
```

## 🎯 Checklist Final

- [ ] `.env` configurado com valores reais
- [ ] `secrets.enc` e `key.enc` gerados
- [ ] `docker-compose build` funciona
- [ ] `docker-compose up` funciona
- [ ] `curl http://localhost:5000` retorna HTML
- [ ] Login com AD funciona
- [ ] Logs não mostram segredos
- [ ] Arquivo `.gitignore` inclui `.env`
- [ ] Variáveis de produção revisadas
- [ ] Backups configurados

## 📚 Referências

- [Dockerfile Best Practices](https://docs.docker.com/develop/dockerfile_best-practices/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Flask + Gunicorn Deployment](https://docs.gunicorn.org/en/stable/deploy.html)
- [Security Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## 🤝 Suporte

Para dúvidas ou problemas:

1. Verifique os logs: `docker-compose logs -f`
2. Consulte o [README.Docker.md](README.Docker.md)
3. Revise o [DOCKER_CHECKLIST.md](DOCKER_CHECKLIST.md)
4. Abra uma issue no repositório

---

**Última atualização**: 2026-05-22
**Status**: ✅ Pronto para produção
