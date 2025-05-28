from flask import Blueprint, request, jsonify, session
from src.models.user import User, db
from werkzeug.security import check_password_hash
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        # Obter dados do corpo da requisição
        if request.is_json:
            data = request.get_json()
        else:
            # Tentar decodificar o corpo da requisição como JSON
            try:
                data = json.loads(request.data.decode('utf-8'))
            except:
                # Se falhar, tentar obter do formulário
                data = request.form.to_dict()
        
        email = data.get('email')
        password = data.get('password')
        
        print(f"Tentativa de login: {email}")
        
        # Buscar usuário pelo email
        user = User.query.filter_by(email=email).first()
        
        # Verificar se o usuário existe e a senha está correta
        if user and user.check_password(password):
            # Verificar se o usuário está ativo
            if not user.active:
                print(f"Usuário {email} está desativado")
                return jsonify({'error': 'Usuário desativado'}), 403
            
            # Criar sessão
            session['user_id'] = user.id
            session['user_role'] = user.role
            
            print(f"Login bem-sucedido: {email}, role: {user.role}")
            
            # Retornar dados do usuário
            return jsonify({
                'success': True,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'role': user.role,
                    'commission_rate': user.commission_rate,
                    'commission_type': user.commission_type,
                    'can_see_ads': user.can_see_ads,
                    'can_see_gateway_fee': user.can_see_gateway_fee,
                    'can_see_other_sales': user.can_see_other_sales
                }
            })
        else:
            print(f"Falha no login: {email} - Credenciais inválidas")
            return jsonify({'success': False, 'error': 'Email ou senha incorretos'}), 401
    except Exception as e:
        print(f"Erro no login: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        # Limpar sessão
        session.clear()
        return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@auth_bp.route('/api/auth/check-session', methods=['GET'])
def check_session():
    try:
        # Verificar se o usuário está logado
        if 'user_id' in session:
            user_id = session['user_id']
            user = User.query.get(user_id)
            
            if user:
                return jsonify({
                    'authenticated': True,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'role': user.role,
                        'commission_rate': user.commission_rate,
                        'commission_type': user.commission_type,
                        'can_see_ads': user.can_see_ads,
                        'can_see_gateway_fee': user.can_see_gateway_fee,
                        'can_see_other_sales': user.can_see_other_sales
                    }
                })
        
        return jsonify({'authenticated': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
