import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
import sqlalchemy
from sqlalchemy import inspect, text
import pymysql
import uuid
from werkzeug.security import generate_password_hash

# Criar uma aplicação Flask temporária para executar as migrações
app = Flask(__name__)

# Configurar SQLAlchemy para usar SQLite local
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///painel_vendas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar modelos após configurar app
from src.models.user import db, User
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.ad_expense import AdExpense

db.init_app(app)

# Função para verificar e criar tabelas
with app.app_context():
    # Criar todas as tabelas
    db.create_all()
    print("Tabelas criadas/atualizadas com sucesso no SQLite")
    
    # Verificar estrutura das tabelas
    inspector = inspect(db.engine)
    
    # Verificar tabela users
    print("\nEstrutura da tabela users:")
    for column in inspector.get_columns('users'):
        print(f"- {column['name']}: {column['type']}")
    
    # Verificar tabela sales
    print("\nEstrutura da tabela sales:")
    for column in inspector.get_columns('sales'):
        print(f"- {column['name']}: {column['type']}")
    
    # Verificar tabela expenses
    print("\nEstrutura da tabela expenses:")
    for column in inspector.get_columns('expenses'):
        print(f"- {column['name']}: {column['type']}")
    
    # Verificar tabela ad_expenses
    print("\nEstrutura da tabela ad_expenses:")
    for column in inspector.get_columns('ad_expenses'):
        print(f"- {column['name']}: {column['type']}")
    
    # Verificar se existe usuário admin
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("\nCriando usuário admin padrão...")
        admin = User(
            id=str(uuid.uuid4()),
            email='admin@example.com',
            password=generate_password_hash('admin123'),
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
    else:
        print("\nUsuário admin já existe")
    
    print("\nValidação de schema concluída com sucesso!")
