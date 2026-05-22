# ⚡ Quick Start - Docker Compose (5 minutos)

## 1️⃣ Preparar Variáveis

```bash
cp .env.example .env
nano .env
```

**Altere obrigatoriamente:**
- `SECRET_KEY` = Resultado de: `python -c "import secrets; print(secrets.token_hex(32))"`
- `AD_SERVER` = Seu domínio (ex: dc01.empresa.local)
- `AD_BASE_DN` = Sua OU (ex: OU=Usuarios,DC=empresa,DC=local)  
- `AD_ALLOWED_GROUP_DN` = Seu grupo (ex: CN=RH_Pro,OU=Grupos,DC=empresa,DC=local)
- `MASTER_PASSWORD` = Senha forte (mín. 24 chars)

## 2️⃣ Gerar Segredos

```bash
python setup_credentials.py
```

## 3️⃣ Iniciar

```bash
# Build
docker-compose build

# Iniciar
docker-compose up -d

# Ver se está OK
curl http://localhost:5000
```

## 🎯 Pronto!

Acesse: **http://localhost:5000**

---

## 📚 Documentação Completa

- [DOCKER_SETUP_SUMMARY.md](DOCKER_SETUP_SUMMARY.md) - Resumo completo do que foi feito
- [README.Docker.md](README.Docker.md) - Guia detalhado
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deploy passo-a-passo
- [DOCKER_CHECKLIST.md](DOCKER_CHECKLIST.md) - Checklist completo

## 🆘 Problemas?

```bash
# Ver logs
docker-compose logs -f

# Validar configuração
python validate_docker_setup.py

# Ver help de comandos
make help
```

---

**Tudo configurado e pronto! 🚀**
