"""
Ações de atualização de usuários no AD.
Funções para buscar e modificar atributos de usuários.
"""

from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SUBTREE
import services.authenticate as auth
import logging

logger = logging.getLogger(__name__)

# Constante AD para desabilitar usuário (flag userAccountControl)
# 2 = ACCOUNTDISABLE
DISABLE_FLAG = 2

def is_user_enabled(username):
    """
    Verifica se um usuário está habilitado no AD.
    
    Args:
        username: sAMAccountName ou userPrincipalName do usuário
    
    Returns:
        (encontrado: bool, habilitado: bool)
    """
    user_dn = auth.find_user_dn(username)
    if not user_dn:
        return False, False

    # Verificar se o usuário está na OU autorizada
    if not user_dn.endswith(auth.AD_BASE_DN):
        return False, False

    server = Server(auth.AD_SERVER, use_ssl=auth.AD_USE_SSL, get_info=ALL)
    try:
        conn = Connection(
            server,
            user=auth.AD_SERVICE_USER,
            password=auth.AD_SERVICE_PASS,
            auto_bind=True
        )
        
        conn.search(
            search_base=user_dn,
            search_filter='(objectClass=*)',
            search_scope=SUBTREE,
            attributes=['userAccountControl']
        )
        
        if not conn.entries:
            conn.unbind()
            return False, False
        
        current_flag = int(conn.entries[0].userAccountControl.value)
        # Se o bit ACCOUNTDISABLE está ativo, usuário está desabilitado
        is_disabled = bool(current_flag & DISABLE_FLAG)
        conn.unbind()
        
        return True, not is_disabled  # Retorna (encontrado, habilitado)
    
    except Exception as e:
        logger.exception(f'Erro ao verificar status do usuário {username}')
        return False, False

def get_upn_from_dn(dn):
    """
    Busca o userPrincipalName (UPN) de um usuário a partir do seu DN.
    
    Args:
        dn: Distinguished Name do usuário
    
    Returns:
        userPrincipalName (string) ou None se não encontrado
    """
    if not dn:
        return None
    
    server = Server(auth.AD_SERVER, use_ssl=auth.AD_USE_SSL, get_info=ALL)
    try:
        conn = Connection(
            server,
            user=auth.AD_SERVICE_USER,
            password=auth.AD_SERVICE_PASS,
            auto_bind=True
        )
        
        conn.search(
            search_base=dn,
            search_filter='(objectClass=*)',
            search_scope=SUBTREE,
            attributes=['userPrincipalName']
        )
        
        if conn.entries:
            upn = conn.entries[0].userPrincipalName.value
            conn.unbind()
            return upn
        
        conn.unbind()
    except Exception as e:
        logger.exception(f'Erro ao buscar UPN do DN {dn}')
    
    return None

def disable_user(username):
    """
    Desabilita um usuário no AD.
    
    Args:
        username: sAMAccountName ou userPrincipalName do usuário
    
    Returns:
        (sucesso: bool, mensagem: str)
    """
    user_dn = auth.find_user_dn(username)
    if not user_dn:
        return False, f'Usuário {username} não encontrado'
    
    server = Server(auth.AD_SERVER, use_ssl=auth.AD_USE_SSL, get_info=ALL)
    try:
        conn = Connection(
            server,
            user=auth.AD_SERVICE_USER,
            password=auth.AD_SERVICE_PASS,
            auto_bind=True
        )
        
        # Buscar o valor atual de userAccountControl
        conn.search(
            search_base=user_dn,
            search_filter='(objectClass=*)',
            search_scope=SUBTREE,
            attributes=['userAccountControl']
        )
        
        if not conn.entries:
            conn.unbind()
            return False, 'Falha ao buscar userAccountControl do usuário'
        
        current_flag = int(conn.entries[0].userAccountControl.value)
        
        # Ativar o flag ACCOUNTDISABLE (bit 1)
        new_flag = current_flag | DISABLE_FLAG
        
        # Atualizar o atributo
        changes = {'userAccountControl': [(MODIFY_REPLACE, [str(new_flag)])]}
        conn.modify(user_dn, changes)
        
        if conn.result['description'] == 'success':
            conn.unbind()
            return True, f'Usuário {username} desabilitado com sucesso'
        else:
            conn.unbind()
            return False, f'Erro ao desabilitar usuário: {conn.result}'
    
    except Exception as e:
        logger.exception(f'Erro ao desabilitar usuário {username}')
        return False, f'Erro ao desabilitar usuário: {str(e)}'

def enable_user(username):
    """
    Habilita um usuário no AD (remove flag ACCOUNTDISABLE).
    
    Args:
        username: sAMAccountName ou userPrincipalName do usuário
    
    Returns:
        (sucesso: bool, mensagem: str)
    """
    user_dn = auth.find_user_dn(username)
    if not user_dn:
        return False, f'Usuário {username} não encontrado'
    
    server = Server(auth.AD_SERVER, use_ssl=auth.AD_USE_SSL, get_info=ALL)
    try:
        conn = Connection(
            server,
            user=auth.AD_SERVICE_USER,
            password=auth.AD_SERVICE_PASS,
            auto_bind=True
        )
        
        # Buscar o valor atual de userAccountControl
        conn.search(
            search_base=user_dn,
            search_filter='(objectClass=*)',
            search_scope=SUBTREE,
            attributes=['userAccountControl']
        )
        
        if not conn.entries:
            conn.unbind()
            return False, 'Falha ao buscar userAccountControl do usuário'
        
        current_flag = int(conn.entries[0].userAccountControl.value)
        
        # Remover o flag ACCOUNTDISABLE (bit 1)
        new_flag = current_flag & ~DISABLE_FLAG
        
        # Atualizar o atributo
        changes = {'userAccountControl': [(MODIFY_REPLACE, [str(new_flag)])]}
        conn.modify(user_dn, changes)
        
        if conn.result['description'] == 'success':
            conn.unbind()
            return True, f'Usuário {username} habilitado com sucesso'
        else:
            conn.unbind()
            return False, f'Erro ao habilitar usuário: {conn.result}'
    
    except Exception as e:
        logger.exception(f'Erro ao habilitar usuário {username}')
        return False, f'Erro ao habilitar usuário: {str(e)}'
    
def get_manager_dn(manager_username):
    """
    Busca o DN de um usuário que será usado como manager (liderança).
    
    Args:
        manager_username: sAMAccountName ou userPrincipalName do gerenciador
    
    Returns:
        DN do usuário (string) ou None se não encontrado
    """
    if not manager_username:
        return None
    
    manager_dn = auth.find_user_dn(manager_username)
    if not manager_dn:
        logger.warning(f'Manager {manager_username} não encontrado no AD')
        return None
    
    return manager_dn

def find_user(username):
    """
    Busca um usuário no AD por sAMAccountName ou userPrincipalName.
    Retorna um dict com DN, sAMAccountName e atributos básicos, ou None se não encontrado.
    """
    user_dn = auth.find_user_dn(username)
    if not user_dn:
        logger.warning(f'Usuário {username} não encontrado no AD')
        return None

    # Verificar se o usuário está na OU autorizada
    if not user_dn.endswith(auth.AD_BASE_DN):
        logger.warning(f'Usuário {username} fora do escopo autorizado ({auth.AD_BASE_DN})')
        return None

    # Conectar e buscar atributos do usuário
    server = Server(auth.AD_SERVER, use_ssl=auth.AD_USE_SSL, get_info=ALL)
    try:
        conn = Connection(
            server,
            user=auth.AD_SERVICE_USER,
            password=auth.AD_SERVICE_PASS,
            auto_bind=True
        )
        conn.search(
            search_base=user_dn,
            search_filter='(objectClass=*)',
            search_scope=SUBTREE,
            attributes=['distinguishedName', 'sAMAccountName', 'title', 'department', 'manager']
        )
        if conn.entries:
            entry = conn.entries[0]
            manager_dn = entry.manager.value if entry.manager.value else ''
            manager_upn = get_upn_from_dn(manager_dn) if manager_dn else ''
            
            result = {
                'dn': entry.distinguishedName.value,
                'username': entry.sAMAccountName.value,
                'title': entry.title.value if entry.title.value else '',
                'department': entry.department.value if entry.department.value else '',
                'manager': manager_upn,  # UPN ao invés de DN
            }
            conn.unbind()
            return result
        conn.unbind()
    except Exception as e:
        logger.exception(f'Erro ao buscar atributos do usuário {username}')
    return None

def update_user_fields(username, fields_to_update):
    """
    Atualiza campos específicos de um usuário no AD.
    
    Args:
        username: sAMAccountName ou userPrincipalName do usuário
        fields_to_update: dict com chaves 'cargo', 'departamento', 'lider' e valores a setar
            Exemplo: {'cargo': 'Engenheiro', 'departamento': 'TI', 'lider': 'gerente@empresa.com'}
    
    Returns:
        (sucesso: bool, mensagem: str)
    """
    if not fields_to_update:
        return False, 'Nenhum campo para atualizar'

    user_dn = auth.find_user_dn(username)
    if not user_dn:
        return False, f'Usuário {username} não encontrado'

    # Verificar se o usuário está na OU autorizada para modificações
    if not user_dn.endswith(auth.AD_BASE_DN):
        return False, f'Usuário {username} não autorizado para modificação (fora do escopo {auth.AD_BASE_DN})'

    # Mapeamento de nomes de campo LDAP
    ldap_field_map = {
        'cargo': 'title',
        'departamento': 'department',
        'lider': 'manager',
    }

    # Construir dict de modificações LDAP
    changes = {}
    for form_field, ldap_attr in ldap_field_map.items():
        if form_field in fields_to_update and fields_to_update[form_field]:
            value = fields_to_update[form_field]
            
            # Se é o campo de manager, buscar o DN
            if ldap_attr == 'manager':
                manager_dn = get_manager_dn(value)
                if not manager_dn:
                    return False, f'Manager "{value}" não encontrado no AD'
                value = manager_dn
            
            changes[ldap_attr] = [(MODIFY_REPLACE, [value])]

    if not changes:
        return False, 'Nenhum campo válido para atualizar'

    # Conectar e fazer modificação
    server = Server(auth.AD_SERVER, use_ssl=auth.AD_USE_SSL, get_info=ALL)
    try:
        conn = Connection(
            server,
            user=auth.AD_SERVICE_USER,
            password=auth.AD_SERVICE_PASS,
            auto_bind=True
        )
        conn.modify(user_dn, changes)
        if conn.result['description'] == 'success':
            conn.unbind()
            return True, f'Usuário {username} atualizado com sucesso'
        else:
            conn.unbind()
            return False, f'Erro ao atualizar usuário: {conn.result}'
    except Exception as e:
        logger.exception(f'Erro ao modificar usuário {username}')
        return False, f'Erro ao modificar usuário: {str(e)}'
