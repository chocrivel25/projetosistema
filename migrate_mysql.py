import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.ad_expense import AdExpense
from flask import Flask
import sqlalchemy
import uuid
import pymysql

# Criar uma aplicação Flask temporária para executar as migrações
app = Flask(__name__)

# Primeiro, tentar criar o banco de dados se não existir
try:
    # Conectar ao MySQL sem especificar o banco de dados
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='password'
    )
    
    # Criar cursor
    cursor = conn.cursor()
    
    # Verificar se o banco de dados existe
    cursor.execute("SHOW DATABASES LIKE 'painel_vendas'")
    result = cursor.fetchone()
    
    # Se o banco não existir, criar
    if not result:
        print("Banco de dados 'painel_vendas' não encontrado. Criando...")
        cursor.execute("CREATE DATABASE painel_vendas")
        print("Banco de dados criado com sucesso!")
    else:
        print("Banco de dados 'painel_vendas' já existe.")
    
    # Fechar conexão
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro ao verificar/criar banco de dados: {e}")
    sys.exit(1)

# Configurar SQLAlchemy para usar o banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:password@localhost:3306/painel_vendas"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Função para adicionar coluna se não existir
def add_column_if_not_exists(table_name, column_name, column_type):
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            sql = f"""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'painel_vendas' 
            AND TABLE_NAME = '{table_name}' 
            AND COLUMN_NAME = '{column_name}'
            """
            result = db.session.execute(sqlalchemy.text(sql)).scalar()
            
            if result == 0:
                # Coluna não existe, adicionar
                sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                db.session.execute(sqlalchemy.text(sql))
                db.session.commit()
                print(f"Coluna {column_name} adicionada com sucesso à tabela {table_name}")
            else:
                print(f"Coluna {column_name} já existe na tabela {table_name}")
        except Exception as e:
            print(f"Erro ao adicionar coluna {column_name}: {e}")
            db.session.rollback()

# Executar migrações
with app.app_context():
    try:
        # Verificar se as tabelas existem
        tables = ['users', 'sales', 'expenses', 'ad_expenses']
        for table in tables:
            sql = f"""
            SELECT COUNT(*) 
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'painel_vendas' 
            AND TABLE_NAME = '{table}'
            """
            result = db.session.execute(sqlalchemy.text(sql)).scalar()
            
            if result == 0:
                print(f"Tabela {table} não existe, será criada automaticamente")
        
        # Criar tabelas se não existirem
        db.create_all()
        print("Tabelas criadas/atualizadas com sucesso")
        
        # Adicionar novas colunas à tabela users
        add_column_if_not_exists('users', 'commission_type', 'VARCHAR(20) DEFAULT "liquido"')
        add_column_if_not_exists('users', 'can_view_gateway_fee', 'BOOLEAN DEFAULT 0')
        
        # Adicionar novas colunas à tabela sales
        add_column_if_not_exists('sales', 'gateway_fee', 'FLOAT DEFAULT 0')
        add_column_if_not_exists('sales', 'ad_cost', 'FLOAT DEFAULT 0')
        add_column_if_not_exists('sales', 'payment_received', 'BOOLEAN DEFAULT 0')
        add_column_if_not_exists('sales', 'payment_date', 'DATETIME NULL')
        add_column_if_not_exists('sales', 'payment_confirmed_by_seller', 'BOOLEAN DEFAULT 0')
        add_column_if_not_exists('sales', 'payment_confirmation_date', 'DATETIME NULL')
        
        # Verificar se existe usuário admin
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("Criando usuário admin padrão...")
            from werkzeug.security import generate_password_hash
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
        
        print("Migrações concluídas com sucesso!")
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        db.session.rollback()
