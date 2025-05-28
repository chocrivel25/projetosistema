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

# Configurar SQLAlchemy para usar o banco MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:password@localhost:3306/painel_vendas"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar modelos após configurar app
from src.models.user import db, User
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.ad_expense import AdExpense

db.init_app(app)

# Função para verificar e criar tabelas
with app.app_context():
    try:
        # Verificar se o banco existe
        engine = db.engine
        conn = engine.connect()
        
        # Verificar estrutura das tabelas
        inspector = inspect(engine)
        
        # Verificar se as tabelas existem
        tables = inspector.get_table_names()
        print(f"Tabelas encontradas no banco: {tables}")
        
        if 'users' in tables:
            # Verificar tabela users
            print("\nEstrutura da tabela users:")
            columns = {col['name']: col['type'] for col in inspector.get_columns('users')}
            for col_name, col_type in columns.items():
                print(f"- {col_name}: {col_type}")
            
            # Verificar se as colunas necessárias existem
            required_columns = ['commission_type', 'can_view_gateway_fee']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"\nColunas ausentes na tabela users: {missing_columns}")
                
                # Adicionar colunas ausentes
                for col in missing_columns:
                    if col == 'commission_type':
                        conn.execute(text("ALTER TABLE users ADD COLUMN commission_type VARCHAR(20) DEFAULT 'liquido'"))
                        print(f"Coluna {col} adicionada à tabela users")
                    elif col == 'can_view_gateway_fee':
                        conn.execute(text("ALTER TABLE users ADD COLUMN can_view_gateway_fee BOOLEAN DEFAULT 0"))
                        print(f"Coluna {col} adicionada à tabela users")
            else:
                print("\nTodas as colunas necessárias existem na tabela users")
        
        if 'sales' in tables:
            # Verificar tabela sales
            print("\nEstrutura da tabela sales:")
            columns = {col['name']: col['type'] for col in inspector.get_columns('sales')}
            for col_name, col_type in columns.items():
                print(f"- {col_name}: {col_type}")
            
            # Verificar se as colunas necessárias existem
            required_columns = ['gateway_fee', 'ad_cost', 'payment_received', 'payment_date', 
                               'payment_confirmed_by_seller', 'payment_confirmation_date']
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                print(f"\nColunas ausentes na tabela sales: {missing_columns}")
                
                # Adicionar colunas ausentes
                for col in missing_columns:
                    if col == 'gateway_fee':
                        conn.execute(text("ALTER TABLE sales ADD COLUMN gateway_fee FLOAT DEFAULT 0"))
                    elif col == 'ad_cost':
                        conn.execute(text("ALTER TABLE sales ADD COLUMN ad_cost FLOAT DEFAULT 0"))
                    elif col == 'payment_received':
                        conn.execute(text("ALTER TABLE sales ADD COLUMN payment_received BOOLEAN DEFAULT 0"))
                    elif col == 'payment_date':
                        conn.execute(text("ALTER TABLE sales ADD COLUMN payment_date DATETIME"))
                    elif col == 'payment_confirmed_by_seller':
                        conn.execute(text("ALTER TABLE sales ADD COLUMN payment_confirmed_by_seller BOOLEAN DEFAULT 0"))
                    elif col == 'payment_confirmation_date':
                        conn.execute(text("ALTER TABLE sales ADD COLUMN payment_confirmation_date DATETIME"))
                    
                    print(f"Coluna {col} adicionada à tabela sales")
            else:
                print("\nTodas as colunas necessárias existem na tabela sales")
        
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
        
        conn.close()
        print("\nValidação e correção de schema concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a validação/correção do schema: {e}")
        if 'conn' in locals() and conn:
            conn.close()
