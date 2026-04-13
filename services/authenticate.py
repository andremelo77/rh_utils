from ldap3 import Server, Connection, ALL, NTLM, SUBTREE
from dotenv import load_dotenv
import os
import logging
from services.secrets import get_ad_service_credentials

load_dotenv()

# Carregar configuração do AD a partir do .env (disponível como variáveis de módulo)
AD_SERVER = os.getenv('AD_SERVER')
AD_USE_SSL = os.getenv('AD_USE_SSL', 'True').lower() in ('1', 'true', 'yes')
AD_BASE_DN = os.getenv('AD_BASE_DN')
AD_ALLOWED_GROUP_DN = os.getenv('AD_ALLOWED_GROUP_DN')

# Senha mestre para descriptografia (DEVE estar em variável de ambiente segura)
MASTER_PASSWORD = os.getenv('MASTER_PASSWORD')

# Credenciais do serviço AD (carregadas de forma segura)
AD_SERVICE_USER, AD_SERVICE_PASS = get_ad_service_credentials(MASTER_PASSWORD) if MASTER_PASSWORD else (None, None)

logger = logging.getLogger(__name__)

def ad_config():
    """Retorna a configuração do AD lida do ambiente."""
    # Validar que credenciais foram carregadas
    if not AD_SERVICE_USER or not AD_SERVICE_PASS:
        error_msg = "Credenciais do AD Service não foram carregadas. Verifique MASTER_PASSWORD e arquivos de segredos."
        logger.error(error_msg)
        raise ValueError(error_msg)

    return {
        'AD_SERVER': AD_SERVER,
        'AD_USE_SSL': AD_USE_SSL,
        'AD_SERVICE_USER': AD_SERVICE_USER,
        'AD_SERVICE_PASS': AD_SERVICE_PASS,
        'AD_BASE_DN': AD_BASE_DN,
    }

def find_user_dn(username):
    """Usa conta de serviço para procurar o DN do usuário por sAMAccountName ou userPrincipalName."""
    if not AD_SERVER or not AD_BASE_DN or not AD_SERVICE_USER or not AD_SERVICE_PASS:
        logger.error('Configuração do AD incompleta; verifique variáveis de ambiente')
        return None

    server = Server(AD_SERVER, use_ssl=AD_USE_SSL, get_info=ALL)
    try:
        conn = Connection(server, user=AD_SERVICE_USER, password=AD_SERVICE_PASS, auto_bind=True)
    except Exception:
        logger.exception('Falha ao conectar com a conta de serviço')
        return None

    search_filter = f"(|(sAMAccountName={username})(userPrincipalName={username}))"
    try:
        conn.search(search_base='DC=wks,DC=local', search_filter=search_filter, search_scope=SUBTREE, attributes=['distinguishedName'])
        if conn.entries:
            return conn.entries[0].distinguishedName.value
    except Exception:
        logger.exception('Erro na pesquisa LDAP')
    finally:
        try:
            conn.unbind()
        except Exception:
            pass

    return None

def is_user_in_allowed_group(user_dn):
    """Verifica se o usuário pertence ao grupo autorizado."""
    if not AD_ALLOWED_GROUP_DN:
        return True

    if not AD_SERVER or not AD_SERVICE_USER or not AD_SERVICE_PASS:
        logger.error('Configuração do AD incompleta para verificação de grupo')
        return False

    server = Server(AD_SERVER, use_ssl=AD_USE_SSL, get_info=ALL)
    try:
        conn = Connection(server, user=AD_SERVICE_USER, password=AD_SERVICE_PASS, auto_bind=True)
        # Usa pesquisa transitive para membership aninhada em AD
        search_filter = (
            '(&'
            '(objectClass=group)'
            f'(distinguishedName={AD_ALLOWED_GROUP_DN})'
            f'(member:1.2.840.113556.1.4.1941:={user_dn})'
            ')'
        )
        conn.search(search_base='DC=wks,DC=local', search_filter=search_filter, search_scope=SUBTREE, attributes=['distinguishedName'])
        found = bool(conn.entries)
        conn.unbind()
        return found
    except Exception:
        logger.exception('Erro ao verificar associação de grupo do usuário')
        return False


def authenticate_user(username, password):
    """Retorna True se as credenciais estiverem corretas e o usuário estiver autorizado."""
    if not AD_SERVER:
        logger.error('AD_SERVER não está configurado')
        return False

    server = Server(AD_SERVER, use_ssl=AD_USE_SSL, get_info=ALL)

    # Tentar bind direto usando username (UPN ou DOMAIN\\user conforme informado)
    try:
        conn = Connection(server, user=username, password=password, auto_bind=True)
        conn.unbind()
        user_dn = find_user_dn(username)
        return user_dn and is_user_in_allowed_group(user_dn)
    except Exception:
        pass

    # Fallback: procurar DN e fazer bind com DN
    user_dn = find_user_dn(username)
    if not user_dn:
        return False

    try:
        conn = Connection(server, user=user_dn, password=password, auto_bind=True)
        conn.unbind()
        return is_user_in_allowed_group(user_dn)
    except Exception:
        return False
    
