#!/usr/bin/env python3
"""
Script de configuração inicial das credenciais AD Service.
Execute este script uma vez para configurar as credenciais de forma segura.

Uso:
    python setup_credentials.py
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.secrets import setup_ad_service_credentials

def main():
    print("🔐 Configuração Segura de Credenciais AD Service")
    print("=" * 50)
    print()
    print("Este script irá:")
    print("1. Solicitar uma senha mestre para criptografia")
    print("2. Solicitar as credenciais da conta de serviço AD")
    print("3. Salvar tudo de forma encriptada em arquivos locais")
    print()
    print("⚠️  IMPORTANTE:")
    print("   - A senha mestre deve ser guardada em local SEGURO")
    print("   - Ela será necessária para descriptografar as credenciais")
    print("   - Configure MASTER_PASSWORD no arquivo .env com esta senha")
    print("   - Os arquivos secrets.enc e key.enc NÃO devem ser versionados")
    print()

    # Solicitar senha mestre
    while True:
        master_pass = input("Digite uma senha mestre forte: ").strip()
        confirm_pass = input("Confirme a senha mestre: ").strip()

        if not master_pass:
            print("❌ Senha mestre não pode ser vazia!")
            continue

        if master_pass != confirm_pass:
            print("❌ Senhas não coincidem. Tente novamente.")
            continue

        break

    print()
    print("✅ Senha mestre configurada!")
    print()

    # Configurar credenciais AD
    try:
        setup_ad_service_credentials(master_pass)
        print()
        print("🎉 Configuração concluída com sucesso!")
        print()
        print("Próximos passos:")
        print("1. Adicione MASTER_PASSWORD ao seu arquivo .env")
        print("2. Certifique-se de que .env não está versionado (.gitignore)")
        print("3. Teste a aplicação")

    except Exception as e:
        print(f"❌ Erro durante configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()