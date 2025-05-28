import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.ad_expense import AdExpense
from flask import Flask
import sqlalchemy
import os

# Criar uma aplicação Flask temporária para executar as migrações
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///painel_vendas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Remover banco de dados existente e recriar do zero
with app.app_context():
    # Verificar se o arquivo do banco de dados existe e removê-lo
    db_path = os.path.join(os.path.dirname(__file__), 'painel_vendas.db')
    if os.path.exists(db_path):
        print(f"Removendo banco de dados existente: {db_path}")
        os.remove(db_path)
        print("Banco de dados removido com sucesso")
    
    # Criar todas as tabelas do zero
    print("Criando tabelas do banco de dados...")
    db.create_all()
    print("Tabelas criadas com sucesso")
    
    # Criar usuário admin padrão
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("Criando usuário admin padrão...")
        admin = User(
            email='admin@example.com',
            password='admin123',  # Em produção, usar senha hash
            name='Administrador',
            role='admin',
            commission_rate=0.0,
            commission_type='liquido',
            can_view_total_sales=True,
            can_view_ad_expenses=True,
            can_view_gateway_fee=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
    
    print("Migração concluída com sucesso!")
