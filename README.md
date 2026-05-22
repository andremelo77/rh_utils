# Sistema RH - Autenticação Segura

Aplicação Flask para gerenciamento de usuários no Active Directory com autenticação segura.

> **NOVO:** Agora com suporte completo a Docker Compose! Veja [QUICK_START.md](QUICK_START.md) para começar em 5 minutos.

## Docker Compose (Recomendado)

**Forma mais rápida de começar:**

```bash
cp .env.example .env          # Configure variáveis
nano .env                      # Altere os valores
python setup_credentials.py    # Gere secrets
docker-compose build           # Build
docker-compose up -d           # Inicie
curl http://localhost:5000     # Teste
```

**Documentacao Docker:**
- [QUICK_START.md](QUICK_START.md) - 5 minutos para começar
- [README.Docker.md](README.Docker.md) - Guia detalhado
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deploy em producao
- [Makefile](Makefile) - Comandos convenientes: `make help`

---

## � Visão Geral

Sistema web para gerenciamento de usuários do Active Directory, com interface responsiva e controle de acesso baseado em grupos.

### Funcionalidades

- 🔐 **Autenticação AD**: Login via credenciais do domínio
- 👥 **Controle de Acesso**: Restrição por grupos AD
- 🔍 **Busca de Usuários**: Consulta dados no AD
- ✏️ **Modificação de Dados**: Atualização de cargo, departamento e líder
- 🎨 **Interface Moderna**: Design responsivo com tema corporativo
- ⏰ **Sessões Seguras**: Timeout automático e anti-cache

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Acesso ao servidor Active Directory
- Conta de serviço AD com permissões adequadas

### Passos de Instalação

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd rh_pro
   ```

2. **Configure ambiente virtual:**
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate
   ```

3. **Instale dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure credenciais AD:**
   ```bash
   python setup_credentials.py
   ```

5. **Configure variáveis de ambiente:**
   Edite o arquivo `.env` com suas configurações específicas.

## 🔐 Segurança de Credenciais

Este projeto usa criptografia para proteger as credenciais da conta de serviço do AD.

### Configuração Inicial de Segurança

1. **Execute o setup:**
   ```bash
   python setup_credentials.py
   ```

   Este script irá:
   - Solicitar uma senha mestre
   - Solicitar as credenciais da conta de serviço AD
   - Criar arquivos `secrets.enc` e `key.enc` com dados encriptados

2. **Configure variável de ambiente:**
   Edite o arquivo `.env` e adicione:
   ```env
   MASTER_PASSWORD=sua_senha_mestre_aqui
   ```

### Como Funciona a Criptografia

- **Senha mestre**: Usada para derivar chave de criptografia (PBKDF2)
- **Arquivo `key.enc`**: Contém a chave derivada (protegida)
- **Arquivo `secrets.enc`**: Contém credenciais encriptadas
- **Runtime**: Credenciais são descriptografadas apenas na memória

### Medidas de Segurança

✅ **Vantagens:**
- Credenciais nunca ficam em texto claro
- Arquivos encriptados podem ser versionados (se necessário)
- Chave de criptografia derivada de senha forte
- Sem dependências externas para criptografia

⚠️ **Importante:**
- Guarde a senha mestre em local seguro
- Nunca versione `secrets.enc` e `key.enc` (já estão no .gitignore)
- Use senha mestre forte e única

## ▶️ Execução

### Desenvolvimento
```bash
python app.py
```

### Produção (Recomendado)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Execute com múltiplos workers em Linux
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Deploy Linux recomendado
1. No Ubuntu Server, instale o Python e ferramentas necessárias:
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip nginx
   ```
2. Crie a venv e instale dependências:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure o arquivo `.env` com as variáveis do ambiente e a senha mestre.
4. Execute `python setup_credentials.py` para gerar `secrets.enc` e `key.enc`.
5. Use `gunicorn` em produção:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
6. Proteja a aplicação com `nginx` como proxy reverso e habilite HTTPS.

### Exemplo de serviço systemd
```ini
[Unit]
Description=RH Pro Flask App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/rh_pro
EnvironmentFile=/var/www/rh_pro/.env
ExecStart=/var/www/rh_pro/.venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Exemplo básico de proxy nginx
```nginx
server {
    listen 80;
    server_name exemplo.seudominio.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 📁 Estrutura do Projeto

```
rh_pro/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── .env                   # Configurações (NÃO versionar)
├── .gitignore            # Arquivos ignorados pelo Git
├── README.md             # Esta documentação
├── services/
│   ├── authenticate.py   # Autenticação e autorização AD
│   ├── actions.py        # Operações AD (busca/modificação)
│   └── secrets.py        # Gerenciamento de credenciais
├── templates/            # Templates HTML
│   ├── login.html        # Página de login
│   └── mudar_campos.html # Interface principal
└── static/               # Arquivos estáticos
    └── css/
        ├── base.css      # Estilos base
        └── login.css     # Estilos de login
```

## 🔧 Desenvolvimento

### Adicionando Novos Recursos
1. **Lógica de negócio**: Modifique arquivos em `services/`
2. **Interface**: Atualize templates em `templates/`
3. **Estilos**: Adicione/modifique CSS em `static/css/`

### Testes
```bash
# Execute a aplicação em modo desenvolvimento
python app.py

# Teste funcionalidades através da interface web
```

## 📝 Configuração do .env

```env
# Flask
SECRET_KEY=your-super-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=False

# Segurança
MASTER_PASSWORD=sua_senha_mestre_forte

# Active Directory
AD_SERVER=servidor-ad.empresa.local
AD_USE_SSL=True
AD_BASE_DN=OU=Usuarios,DC=empresa,DC=local
AD_SEARCH_BASE=DC=empresa,DC=local
AD_ALLOWED_GROUP_DN=CN=Grupo_Autorizado,OU=Grupos,DC=empresa,DC=local
```

> Em produção, defina `FLASK_ENV=production`, `FLASK_DEBUG=False` e um `SECRET_KEY` forte. O app exige `SECRET_KEY` em produção.

## 🤝 Contribuição

1. Faça fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📞 Suporte

Para questões ou problemas:
- Crie uma issue no repositório
- Documente claramente o problema e passos para reproduzir

## 📄 Licença

Este projeto é propriedade da empresa. Uso interno autorizado apenas.

### Estrutura de Arquivos

```
rh_pro/
├── .env                    # Configurações (MASTER_PASSWORD)
├── .gitignore             # Protege arquivos sensíveis
├── secrets.enc            # Credenciais encriptadas (NÃO VERSIONAR)
├── key.enc               # Chave de criptografia (NÃO VERSIONAR)
├── services/
│   ├── secrets.py        # Módulo de criptografia
│   ├── authenticate.py   # Autenticação AD
│   └── actions.py        # Ações no AD
└── setup_credentials.py  # Script de configuração
```

### Desenvolvimento

Para desenvolvimento local:
1. Execute `python setup_credentials.py`
2. Configure `MASTER_PASSWORD` no `.env`
3. Execute `python app.py`

### Produção

Para produção, considere:
- Usar um gerenciador de segredos seguro
- Rotação automática de credenciais
- Implantar com usuários e permissões mínimas

## 🚀 Executando a Aplicação

```bash
# Desenvolvimento
python app.py

# Produção (recomendado)
gunicorn --bind 0.0.0.0:5000 app:app
```