# Sistema RH - Autenticação Segura

Aplicação Flask para gerenciamento de usuários no Active Directory com autenticação segura.

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
# Adicione gunicorn ao requirements.txt
pip install gunicorn

# Execute com múltiplos workers
gunicorn -w 4 -b 0.0.0.0:8000 app:app
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

# Segurança
MASTER_PASSWORD=sua_senha_mestre_forte

# Active Directory
AD_SERVER=servidor-ad.empresa.local
AD_USE_SSL=True
AD_BASE_DN=OU=Usuarios,OU=Empresa,DC=empresa,DC=local
AD_ALLOWED_GROUP_DN=CN=Grupo_Autorizado,OU=Grupos,DC=empresa,DC=local
```

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