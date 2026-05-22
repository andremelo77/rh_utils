#!/usr/bin/env python3
"""
Script de Validação - Docker Setup para RH Pro

Valida se todos os requisitos e configurações estão corretos
antes de fazer deploy em Docker.

Uso: python validate_docker_setup.py
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Tuple, List

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(message: str):
    """Imprime mensagem de sucesso."""
    print(f"{Colors.GREEN}✓{Colors.RESET} {message}")

def print_error(message: str):
    """Imprime mensagem de erro."""
    print(f"{Colors.RED}✗{Colors.RESET} {message}")

def print_warning(message: str):
    """Imprime mensagem de aviso."""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {message}")

def print_info(message: str):
    """Imprime mensagem de informação."""
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {message}")

def check_docker() -> Tuple[bool, str]:
    """Verifica se Docker está instalado e rodando."""
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        return False, "Docker não respondendo"
    except FileNotFoundError:
        return False, "Docker não encontrado"
    except Exception as e:
        return False, str(e)

def check_docker_compose() -> Tuple[bool, str]:
    """Verifica se Docker Compose está instalado."""
    try:
        result = subprocess.run(['docker-compose', '--version'],
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version = result.stdout.strip()
            return True, version
        return False, "Docker Compose não respondendo"
    except FileNotFoundError:
        return False, "Docker Compose não encontrado"
    except Exception as e:
        return False, str(e)

def check_file_exists(filepath: str, is_required: bool = True) -> Tuple[bool, str]:
    """Verifica se um arquivo existe."""
    path = Path(filepath)
    if path.exists():
        return True, f"Encontrado: {filepath}"
    elif is_required:
        return False, f"Obrigatório: {filepath} não encontrado"
    else:
        return True, f"Opcional: {filepath} não encontrado (OK)"

def check_env_file() -> Tuple[bool, str]:
    """Verifica se .env está configurado."""
    if not Path('.env').exists():
        return False, ".env não encontrado - execute: cp .env.example .env"
    
    # Verificar variáveis obrigatórias
    with open('.env', 'r') as f:
        content = f.read()
    
    required_vars = [
        'SECRET_KEY',
        'AD_SERVER',
        'AD_BASE_DN',
        'AD_ALLOWED_GROUP_DN',
        'MASTER_PASSWORD'
    ]
    
    missing = []
    default_values = ['your-', 'ALTERAR_ISSO']
    
    for var in required_vars:
        if var not in content:
            missing.append(var)
        else:
            # Verificar se tem valor real (não default)
            for line in content.split('\n'):
                if line.startswith(var + '='):
                    value = line.split('=', 1)[1].strip()
                    if any(default in value for default in default_values):
                        missing.append(f"{var} (valor default)")
    
    if missing:
        return False, f"Variáveis não configuradas ou com valores default: {', '.join(missing)}"
    
    return True, ".env configurado com todas as variáveis obrigatórias"

def check_secrets() -> Tuple[bool, str]:
    """Verifica se arquivos de segredos existem."""
    secrets_exist = Path('secrets.enc').exists()
    key_exist = Path('key.enc').exists()
    
    if secrets_exist and key_exist:
        return True, "Arquivos de segredos encontrados"
    elif not secrets_exist and not key_exist:
        return False, "Arquivos de segredos não encontrados - execute: python setup_credentials.py"
    else:
        return False, "Arquivo de segredos incompleto (falta secrets.enc ou key.enc)"

def check_docker_files() -> Tuple[bool, str]:
    """Verifica se todos os arquivos Docker necessários existem."""
    required_files = [
        'Dockerfile',
        'docker-compose.yml',
        '.dockerignore',
        'entrypoint.sh',
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        return False, f"Arquivos Docker não encontrados: {', '.join(missing)}"
    
    return True, "Todos os arquivos Docker encontrados"

def check_requirements() -> Tuple[bool, str]:
    """Verifica se requirements.txt existe."""
    if not Path('requirements.txt').exists():
        return False, "requirements.txt não encontrado"
    
    try:
        with open('requirements.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
        if lines:
            return True, f"requirements.txt OK ({len(lines)} pacotes)"
        else:
            return False, "requirements.txt vazio"
    except Exception as e:
        return False, f"Erro ao ler requirements.txt: {str(e)}"

def check_app_py() -> Tuple[bool, str]:
    """Verifica se app.py existe e contém endpoint /health."""
    if not Path('app.py').exists():
        return False, "app.py não encontrado"
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        if '/health' in content:
            return True, "app.py OK (com endpoint /health)"
        else:
            return False, "app.py não contém endpoint /health"
    except Exception as e:
        return False, f"Erro ao ler app.py: {str(e)}"

def check_gitignore() -> Tuple[bool, str]:
    """Verifica se .gitignore exclui arquivos sensíveis."""
    if not Path('.gitignore').exists():
        return False, ".gitignore não encontrado"
    
    try:
        with open('.gitignore', 'r') as f:
            content = f.read().lower()
        
        sensitive_files = ['.env', 'secrets.enc', 'key.enc']
        missing = []
        
        for file in sensitive_files:
            if file not in content:
                missing.append(file)
        
        if missing:
            return False, f".gitignore não exclui: {', '.join(missing)}"
        
        return True, ".gitignore exclui corretamente arquivos sensíveis"
    except Exception as e:
        return False, f"Erro ao ler .gitignore: {str(e)}"

def main():
    """Executa todas as validações."""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("  Docker Setup Validation - RH Pro")
    print(f"{'='*60}{Colors.RESET}\n")
    
    checks = [
        ("Docker instalado", check_docker),
        ("Docker Compose instalado", check_docker_compose),
        ("Dockerfile", lambda: check_file_exists('Dockerfile')),
        ("docker-compose.yml", lambda: check_file_exists('docker-compose.yml')),
        (".dockerignore", lambda: check_file_exists('.dockerignore')),
        ("entrypoint.sh", lambda: check_file_exists('entrypoint.sh')),
        ("Arquivos Docker completos", check_docker_files),
        ("requirements.txt", check_requirements),
        ("app.py com /health", check_app_py),
        (".env configurado", check_env_file),
        ("secrets.enc e key.enc", check_secrets),
        (".gitignore seguro", check_gitignore),
    ]
    
    results = []
    
    for check_name, check_func in checks:
        try:
            success, message = check_func()
            results.append((check_name, success, message))
            
            if success:
                print_success(f"{check_name}: {message}")
            else:
                print_error(f"{check_name}: {message}")
        except Exception as e:
            print_error(f"{check_name}: Erro na validação - {str(e)}")
            results.append((check_name, False, str(e)))
    
    # Resumo
    print(f"\n{Colors.BLUE}{'='*60}")
    print("  Resumo")
    print(f"{'='*60}{Colors.RESET}\n")
    
    success_count = sum(1 for _, success, _ in results if success)
    total_count = len(results)
    
    print(f"Validações: {success_count}/{total_count}")
    
    if success_count == total_count:
        print_success("Todas as validações passaram!")
        print_info("\nPróximos passos:")
        print_info("1. Revisar configurações em .env")
        print_info("2. Executar: docker-compose build")
        print_info("3. Executar: docker-compose up -d")
        print_info("4. Verificar: docker-compose logs -f")
        return 0
    else:
        print_error(f"{total_count - success_count} validação(ões) falharam!")
        print_warning("\nPor favor, corrija os erros acima antes de fazer deploy.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
