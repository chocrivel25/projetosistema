import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
import sqlalchemy
from sqlalchemy import inspect, text
import pymysql

# Criar uma aplicação Flask temporária para executar as migrações
app = Flask(__name__)

# Configurar SQLAlchemy para usar o banco MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:password@localhost:3306/painel_vendas"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar modelos após configurar app
from src.models.user import db

db.init_app(app)

# Função para verificar e criar índices e foreign keys
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
        
        # Verificar índices e foreign keys para cada tabela
        for table in tables:
            print(f"\nÍndices da tabela {table}:")
            indices = inspector.get_indexes(table)
            for index in indices:
                print(f"- {index['name']}: {index['column_names']}")
            
            print(f"\nForeign keys da tabela {table}:")
            fks = inspector.get_foreign_keys(table)
            for fk in fks:
                print(f"- {fk.get('name', 'unnamed')}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # Verificar se todos os índices necessários existem
        # Para tabela sales
        if 'sales' in tables:
            indices_sales = {idx['name']: idx['column_names'] for idx in inspector.get_indexes('sales')}
            if not any('seller_id' in cols for cols in indices_sales.values()):
                print("\nCriando índice para seller_id na tabela sales...")
                conn.execute(text("CREATE INDEX idx_sale_seller ON sales (seller_id)"))
                print("Índice criado com sucesso")
        
        # Para tabela expenses
        if 'expenses' in tables:
            indices_expenses = {idx['name']: idx['column_names'] for idx in inspector.get_indexes('expenses')}
            if not any('user_id' in cols for cols in indices_expenses.values()):
                print("\nCriando índice para user_id na tabela expenses...")
                conn.execute(text("CREATE INDEX idx_expense_user ON expenses (user_id)"))
                print("Índice criado com sucesso")
        
        # Para tabela ad_expenses
        if 'ad_expenses' in tables:
            indices_ad_expenses = {idx['name']: idx['column_names'] for idx in inspector.get_indexes('ad_expenses')}
            if not any('seller_id' in cols for cols in indices_ad_expenses.values()):
                print("\nCriando índice para seller_id na tabela ad_expenses...")
                conn.execute(text("CREATE INDEX idx_ad_expense_seller ON ad_expenses (seller_id)"))
                print("Índice criado com sucesso")
        
        # Verificar foreign keys e criar se necessário
        # Para tabela sales
        if 'sales' in tables:
            fks_sales = inspector.get_foreign_keys('sales')
            if not any(fk['referred_table'] == 'users' and 'seller_id' in fk['constrained_columns'] for fk in fks_sales):
                print("\nCriando foreign key para seller_id na tabela sales...")
                conn.execute(text("ALTER TABLE sales ADD CONSTRAINT fk_sales_seller FOREIGN KEY (seller_id) REFERENCES users(id)"))
                print("Foreign key criada com sucesso")
        
        # Para tabela expenses
        if 'expenses' in tables:
            fks_expenses = inspector.get_foreign_keys('expenses')
            if not any(fk['referred_table'] == 'users' and 'user_id' in fk['constrained_columns'] for fk in fks_expenses):
                print("\nCriando foreign key para user_id na tabela expenses...")
                conn.execute(text("ALTER TABLE expenses ADD CONSTRAINT fk_expenses_user FOREIGN KEY (user_id) REFERENCES users(id)"))
                print("Foreign key criada com sucesso")
        
        # Para tabela ad_expenses
        if 'ad_expenses' in tables:
            fks_ad_expenses = inspector.get_foreign_keys('ad_expenses')
            if not any(fk['referred_table'] == 'users' and 'seller_id' in fk['constrained_columns'] for fk in fks_ad_expenses):
                print("\nCriando foreign key para seller_id na tabela ad_expenses...")
                conn.execute(text("ALTER TABLE ad_expenses ADD CONSTRAINT fk_ad_expenses_seller FOREIGN KEY (seller_id) REFERENCES users(id)"))
                print("Foreign key criada com sucesso")
        
        conn.close()
        print("\nValidação e correção de índices e foreign keys concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a validação/correção de índices e foreign keys: {e}")
        if 'conn' in locals() and conn:
            conn.close()
