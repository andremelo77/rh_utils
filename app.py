from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError, generate_csrf
from functools import wraps
import services.authenticate as auth
import services.actions as actions
import os
import json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret')
app.permanent_session_lifetime = timedelta(minutes=3)
app.config['SESSION_REFRESH_EACH_REQUEST'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['WTF_CSRF_TIME_LIMIT'] = None
csrf = CSRFProtect(app)
app.jinja_env.globals['csrf_token'] = generate_csrf

def no_cache(f):
    """Decorator para desabilitar cache em rotas protegidas."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        response = make_response(response)

        # Adicionar headers anti-cache
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

def login_required(f):
    """Decorator para validar se o usuário está autenticado."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            #flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return no_cache(f)(*args, **kwargs)
    return decorated_function

def api_login_required(f):
    """Decorator para validar autenticação em endpoints de API."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return {'error': 'Não autenticado. Faça login novamente.'}, 401
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def session_timeout():
    session.permanent = True
    if 'user' in session:
        now = datetime.utcnow()
        last_activity = session.get('last_activity')
        if last_activity:
            try:
                last_activity = datetime.fromisoformat(last_activity)
            except ValueError:
                last_activity = now
            if now - last_activity > app.permanent_session_lifetime:
                session.clear()
                return redirect(url_for('login'))
        session['last_activity'] = now.isoformat()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Usuário e senha são obrigatórios.', 'warning')
            return render_template('login.html')

        ok = auth.authenticate_user(username, password)
        if ok:
            session.permanent = True
            session['user'] = username
            session['last_activity'] = datetime.utcnow().isoformat()
            return redirect(url_for('mudar_campos'))
        else:
            flash('Credenciais inválidas ou usuário não autorizado.', 'error')
            return render_template('login.html')

    return render_template('login.html')

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('Erro de segurança. Recarregue a página e tente novamente.', 'error')
    return render_template('login.html'), 400

@app.route('/logout')
def logout():
    """Realiza logout limpo: limpa sessão e desabilita cache."""
    session.clear()
    response = redirect(url_for('login'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
@login_required
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/mudar_campos', methods=['GET', 'POST'])
@login_required
def mudar_campos():
    if request.method == 'POST':
        username = request.form.get('user', '').strip()
        if not username:
            flash('Usuário obrigatório', 'error')
            return redirect(url_for('mudar_campos'))

        # Coletar campos a atualizar (somente os que têm checkbox marcado)
        fields_to_update = {}
        if request.form.get('chk_cargo'):
            fields_to_update['cargo'] = request.form.get('cargo', '').strip()
        if request.form.get('chk_departamento'):
            fields_to_update['departamento'] = request.form.get('departamento', '').strip()
        if request.form.get('chk_lider'):
            fields_to_update['lider'] = request.form.get('lider', '').strip()

        if not fields_to_update:
            flash('Nenhum campo foi selecionado para atualizar', 'warning')
            return redirect(url_for('mudar_campos'))

        # Chamar a função de atualização
        sucesso, mensagem = actions.update_user_fields(username, fields_to_update)
        if sucesso:
            flash(mensagem, 'success')
            return redirect(url_for('mudar_campos'))
        else:
            flash(mensagem, 'error')
        return redirect(url_for('mudar_campos'))
    return render_template('mudar_campos.html')

@app.route('/api/user_status', methods=['GET'])
@api_login_required
def api_user_status():
    """API: Retorna status e dados do usuário."""
    username = request.args.get('username', '').strip()
    if not username:
        return {'error': 'Usuário obrigatório'}, 400
    
    user_data = actions.find_user(username)
    if not user_data:
        return {'error': f'Usuário {username} não encontrado'}, 404
    
    encontrado, habilitado = actions.is_user_enabled(username)
    
    return {
        'username': user_data['username'],
        'cargo': user_data['title'],
        'departamento': user_data['department'],
        'lideranca': user_data['manager'],
        'habilitado': habilitado,
    }, 200

@app.route('/api/toggle_user_status', methods=['POST'])
@api_login_required
def api_toggle_user_status():
    """API: Habilita ou desabilita usuário com base no status atual."""
    data = request.get_json(silent=True)
    if not data:
        return {'error': 'JSON inválido ou não enviado'}, 400

    username = data.get('username', '').strip()
    if not username:
        return {'error': 'Usuário obrigatório'}, 400
    
    encontrado, habilitado = actions.is_user_enabled(username)
    if not encontrado:
        return {'error': f'Usuário {username} não encontrado'}, 404
    
    # Se habilitado, desabilita; se desabilitado, habilita
    if habilitado:
        sucesso, mensagem = actions.disable_user(username)
    else:
        sucesso, mensagem = actions.enable_user(username)
    
    if sucesso:
        novo_status_habilitado = not habilitado
        return {'sucesso': True, 'habilitado': novo_status_habilitado, 'mensagem': mensagem}, 200
    else:
        return {'error': mensagem}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
