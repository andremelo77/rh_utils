"""
Gerenciamento seguro de segredos usando criptografia simétrica (Fernet).
Este módulo criptografa senhas e outros segredos em arquivos, mantendo-os seguros.
"""

import ast
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

# Arquivos para armazenar segredos encriptados
SECRETS_FILE = os.path.join(os.path.dirname(__file__), '..', 'secrets.enc')
KEY_FILE = os.path.join(os.path.dirname(__file__), '..', 'key.enc')

def generate_key(password: str, salt: bytes = None) -> bytes:
    """
    Gera uma chave de criptografia a partir de uma senha usando PBKDF2.

    Args:
        password: Senha mestre para derivar a chave
        salt: Salt opcional (gerado automaticamente se None)

    Returns:
        Chave de criptografia em bytes
    """
    if salt is None:
        salt = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def save_encrypted_secret(secret_name: str, secret_value: str, master_password: str):
    """
    Salva um segredo de forma encriptada.

    Args:
        secret_name: Nome do segredo (ex: 'ad_service_password')
        secret_value: Valor do segredo
        master_password: Senha mestre para criptografia
    """
    try:
        # Carregar ou gerar chave
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'rb') as f:
                key = f.read()
        else:
            key = generate_key(master_password)
            with open(KEY_FILE, 'wb') as f:
                f.write(key)

        fernet = Fernet(key)

        # Carregar segredos existentes ou criar novo dict
        secrets = {}
        if os.path.exists(SECRETS_FILE):
            with open(SECRETS_FILE, 'rb') as f:
                encrypted_data = f.read()
            try:
                decrypted_data = fernet.decrypt(encrypted_data).decode()
                try:
                    secrets = json.loads(decrypted_data)
                except json.JSONDecodeError:
                    secrets = ast.literal_eval(decrypted_data)
                    if not isinstance(secrets, dict):
                        raise ValueError('Formato de segredos inválido')
            except Exception:
                logger.warning("Falha ao descriptografar segredos existentes, criando novo arquivo")

        # Adicionar/atualizar segredo
        secrets[secret_name] = secret_value

        # Encriptar e salvar
        secrets_str = json.dumps(secrets)
        encrypted_data = fernet.encrypt(secrets_str.encode())

        with open(SECRETS_FILE, 'wb') as f:
            f.write(encrypted_data)

        logger.info(f"Segredo '{secret_name}' salvo com sucesso")

    except Exception as e:
        logger.error(f"Erro ao salvar segredo: {e}")
        raise

def get_encrypted_secret(secret_name: str, master_password: str) -> str:
    """
    Recupera um segredo descriptografado.

    Args:
        secret_name: Nome do segredo
        master_password: Senha mestre para descriptografia

    Returns:
        Valor do segredo ou None se não encontrado
    """
    try:
        if not os.path.exists(KEY_FILE) or not os.path.exists(SECRETS_FILE):
            logger.error("Arquivos de chave ou segredos não encontrados")
            return None

        # Carregar chave
        with open(KEY_FILE, 'rb') as f:
            key = f.read()

        fernet = Fernet(key)

        # Carregar e descriptografar segredos
        with open(SECRETS_FILE, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = fernet.decrypt(encrypted_data).decode()
        try:
            secrets = json.loads(decrypted_data)
        except json.JSONDecodeError:
            secrets = ast.literal_eval(decrypted_data)
            if not isinstance(secrets, dict):
                raise ValueError('Formato de segredos inválido')

        return secrets.get(secret_name)

    except Exception as e:
        logger.error(f"Erro ao recuperar segredo '{secret_name}': {e}")
        return None

def setup_ad_service_credentials(master_password: str):
    """
    Função utilitária para configurar as credenciais do AD Service.
    Use esta função uma vez para salvar a senha de forma segura.
    """
    print("=== Configuração de Credenciais AD Service ===")
    print("Esta senha será usada para encriptar as credenciais do AD.")
    print("Guarde-a em local seguro (não versionado)!")
    print()

    service_user = input("Usuário da conta de serviço (ex: conta@dominio.com): ").strip()
    service_pass = input("Senha da conta de serviço: ").strip()

    if not service_user or not service_pass:
        print("❌ Usuário e senha são obrigatórios!")
        return

    try:
        # Salvar credenciais
        save_encrypted_secret('ad_service_user', service_user, master_password)
        save_encrypted_secret('ad_service_password', service_pass, master_password)

        print("✅ Credenciais salvas com sucesso!")
        print(f"Arquivos criados: {SECRETS_FILE}, {KEY_FILE}")

    except Exception as e:
        print(f"❌ Erro ao salvar credenciais: {e}")

def get_ad_service_credentials(master_password: str) -> tuple:
    """
    Recupera as credenciais do AD Service de forma segura.

    Returns:
        tuple: (username, password) ou (None, None) se erro
    """
    username = get_encrypted_secret('ad_service_user', master_password)
    password = get_encrypted_secret('ad_service_password', master_password)

    if not username or not password:
        logger.error("Credenciais do AD Service não encontradas ou inválidas")
        return None, None

    return username, password

# Função para desenvolvimento/teste
if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python secrets.py <senha_mestre>")
        print("Para configurar credenciais: python secrets.py setup <senha_mestre>")
        sys.exit(1)

    master_pass = sys.argv[1]

    if len(sys.argv) == 3 and sys.argv[1] == "setup":
        master_pass = sys.argv[2]
        setup_ad_service_credentials(master_pass)
    else:
        # Teste de recuperação
        user, pwd = get_ad_service_credentials(master_pass)
        if user and pwd:
            print(f"✅ Credenciais recuperadas: {user}")
        else:
            print("❌ Falha ao recuperar credenciais")