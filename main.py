import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, render_template, send_from_directory, session, request, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.auth import auth_bp
from src.routes.seller import seller_bp
from src.routes.admin import admin_bp
import os

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:password@localhost/painel_vendas"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave_secreta_do_painel_de_vendas'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas

# Inicializar o banco de dados
db.init_app(app)

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(seller_bp)
app.register_blueprint(admin_bp)

# Rota para servir arquivos estáticos
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

# Middleware para injetar ID do vendedor nas requisições
@app.before_request
def inject_seller_id():
    if 'user_id' in session and request.path.startswith('/api/seller/'):
        if request.method == 'GET':
            # Adicionar seller_id aos argumentos da URL
            request.args = request.args.copy()
            request.args['seller_id'] = session['user_id']
        elif request.is_json:
            # Adicionar seller_id ao corpo JSON
            data = request.get_json()
            if isinstance(data, dict):
                data['seller_id'] = session['user_id']
                request.data = jsonify(data).data

# Criar tabelas se não existirem
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
