# Checklist de Preparação para Docker

## ✅ Arquivos Criados

- [ ] `Dockerfile` - Imagem Docker multi-stage
- [ ] `docker-compose.yml` - Orquestração de containers (desenvolvimento)
- [ ] `docker-compose.prod.yml` - Orquestração de containers (produção)
- [ ] `.dockerignore` - Arquivos excluídos do build
- [ ] `.env.example` - Template de variáveis de ambiente
- [ ] `.env.production.example` - Template para produção
- [ ] `entrypoint.sh` - Script de inicialização
- [ ] `README.Docker.md` - Documentação completa
- [ ] `Makefile` - Comandos convenientes (este arquivo)

---

## 🔧 Configuração Necessária

### 1. Preparar Variáveis de Ambiente

```bash
# Copiar template
cp .env.example .env

# Editar com suas configurações reais
# IMPORTANTE: Alterar os seguintes valores:
# - SECRET_KEY (gerar chave segura)
# - AD_SERVER (seu controlador de domínio)
# - AD_BASE_DN (sua estrutura de OU)
# - AD_ALLOWED_GROUP_DN (seu grupo autorizado)
# - MASTER_PASSWORD (senha para secrets.enc)

nano .env
```

### 2. Gerar Arquivos de Segredos

```bash
# Se ainda não existem, gerar secrets.enc e key.enc
python setup_credentials.py
```

### 3. Testar Configuração Localmente

```bash
# Verificar se tudo funciona antes do Docker
python app.py  # ou
flask run
```

---

## 🐳 Build e Deploy

### Build da Imagem

```bash
# Build padrão
docker-compose build

# Build com progresso detalhado
docker-compose build --progress=plain

# Build sem cache (recompila tudo)
docker-compose build --no-cache
```

### Iniciar a Aplicação

```bash
# Iniciar em background
docker-compose up -d

# Iniciar com logs
docker-compose up

# Iniciar em background e seguir logs
docker-compose up -d && docker-compose logs -f
```

### Testar Conectividade

```bash
# Verificar se a aplicação está rodando
curl http://localhost:5000

# Ver logs
docker-compose logs rh_pro

# Entrar no container
docker-compose exec rh_pro bash

# Testar conexão com AD
docker-compose exec rh_pro python -c "from services import authenticate; print('AD configurado')"
```

---

## 📋 Checklist Pré-Deploy

### Segurança

- [ ] `SECRET_KEY` alterado (não usar padrão)
- [ ] `MASTER_PASSWORD` configurado e seguro
- [ ] Arquivo `.env` adicionado ao `.gitignore`
- [ ] `secrets.enc` e `key.enc` gerados
- [ ] Permissões de arquivo seguras (`chmod 600` em production)
- [ ] SSL/TLS habilitado para LDAP (`AD_USE_SSL=True`)
- [ ] Usuário não-root confirmado no Dockerfile

### Funcionalidade

- [ ] Aplicação inicia sem erros: `docker-compose up`
- [ ] Conectividade com AD testada
- [ ] Login funciona corretamente
- [ ] Nenhuma variável sensível em logs: `docker-compose logs | grep -i password`
- [ ] Health check retorna sucesso: `curl http://localhost:5000/health`

### Documentação

- [ ] `.env.production.example` preenchido com exemplo real
- [ ] `README.Docker.md` revisado e atualizado
- [ ] Instruções de deployment documentadas
- [ ] Variáveis de ambiente documentadas
- [ ] Contato de suporte/dúvidas documentado

### Infraestrutura

- [ ] Docker e Docker Compose instalados
- [ ] Espaço em disco suficiente
- [ ] Conectividade com AD confirmada
- [ ] Portas 5000 (ou PORT) disponíveis
- [ ] Rede Docker funcionando corretamente

---

## 🚀 Próximos Passos

### Desenvolvimento Local

```bash
# 1. Configurar
cp .env.example .env
python setup_credentials.py

# 2. Build
docker-compose build

# 3. Iniciar
docker-compose up -d

# 4. Verificar
curl http://localhost:5000
docker-compose logs -f
```

### Deploy em Produção

```bash
# 1. Usar arquivo .env.prod
cp .env.production.example .env.prod

# 2. Build com tag
docker build -t rh-pro:v1.0.0 .

# 3. Iniciar com docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

# 4. Configurar backup de volumes
# 5. Configurar monitoramento
# 6. Configurar alertas
```

---

## 🆘 Troubleshooting

### Erro: "Credenciais do AD Service não foram carregadas"

```bash
# Verificar MASTER_PASSWORD
echo $MASTER_PASSWORD
docker-compose exec rh_pro env | grep MASTER

# Regenerar secrets.enc
rm secrets.enc key.enc
python setup_credentials.py
docker-compose restart rh_pro
```

### Erro: "Connection refused" no AD

```bash
# Verificar variáveis
docker-compose exec rh_pro env | grep AD_

# Testar conectividade
docker-compose exec rh_pro ping your-ad-server.local
docker-compose exec rh_pro telnet your-ad-server.local 389
```

### Container não inicia

```bash
# Ver logs detalhados
docker-compose logs rh_pro

# Verificar se porta está em uso
lsof -i :5000
netstat -tlnp | grep 5000

# Tentar rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up
```

---

## 📞 Informações Úteis

- **Documentação Docker**: https://docs.docker.com
- **Flask Documentation**: https://flask.palletsprojects.com
- **Gunicorn Documentation**: https://gunicorn.org
- **Python-dotenv**: https://python-dotenv.readthedocs.io

---

## 🔄 Comandos Rápidos

```bash
# Build
make build

# Iniciar
make up

# Logs
make logs

# Parar
make down

# Shell no container
make shell

# Ver todas as opções
make help
```

---

**Última atualização**: 2026-05-22
**Status**: ✅ Pronto para deploy
