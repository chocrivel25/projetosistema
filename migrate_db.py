import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
from flask import Flask
import sqlalchemy

# Criar uma aplicação Flask temporária para executar as migrações
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///painel_vendas.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Função para adicionar coluna se não existir
def add_column_if_not_exists(table_name, column_name, column_type):
    with app.app_context():
        try:
            # Usar texto SQL direto para adicionar coluna
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            db.session.execute(sqlalchemy.text(sql))
            db.session.commit()
            print(f"Coluna {column_name} adicionada com sucesso à tabela {table_name}")
        except Exception as e:
            print(f"Erro ao adicionar coluna {column_name}: {e}")
            db.session.rollback()

# Executar migrações
with app.app_context():
    # Criar tabelas se não existirem
    db.create_all()
    
    # Adicionar novas colunas à tabela users
    add_column_if_not_exists('users', 'commission_type', 'VARCHAR(20) DEFAULT "liquido"')
    add_column_if_not_exists('users', 'can_view_gateway_fee', 'BOOLEAN DEFAULT 0')
    
    # Adicionar novas colunas à tabela sales
    add_column_if_not_exists('sales', 'gateway_fee', 'FLOAT DEFAULT 0')
    add_column_if_not_exists('sales', 'ad_cost', 'FLOAT DEFAULT 0')
    add_column_if_not_exists('sales', 'payment_received', 'BOOLEAN DEFAULT 0')
    add_column_if_not_exists('sales', 'payment_date', 'DATETIME')
    add_column_if_not_exists('sales', 'payment_confirmed_by_seller', 'BOOLEAN DEFAULT 0')
    add_column_if_not_exists('sales', 'payment_confirmation_date', 'DATETIME')
    
    print("Migrações concluídas com sucesso!")
