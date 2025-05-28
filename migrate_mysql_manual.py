import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
import pymysql
import uuid
from werkzeug.security import generate_password_hash

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
        # Remover tabelas existentes para evitar conflitos
        cursor.execute("USE painel_vendas")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DROP TABLE IF EXISTS sales")
        cursor.execute("DROP TABLE IF EXISTS expenses")
        cursor.execute("DROP TABLE IF EXISTS ad_expenses")
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print("Tabelas existentes removidas para recriação limpa")
    
    # Usar o banco de dados
    cursor.execute("USE painel_vendas")
    
    # Criar tabelas manualmente com índices corretos
    print("Criando tabelas com índices corretos...")
    
    # Tabela users
    cursor.execute("""
    CREATE TABLE users (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        email VARCHAR(120) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL,
        name VARCHAR(100) NOT NULL,
        role VARCHAR(20) NOT NULL DEFAULT 'vendedor',
        commission_rate FLOAT NOT NULL DEFAULT 0.0,
        commission_type VARCHAR(20) NOT NULL DEFAULT 'liquido',
        can_view_total_sales BOOLEAN DEFAULT FALSE,
        can_view_ad_expenses BOOLEAN DEFAULT FALSE,
        can_view_gateway_fee BOOLEAN DEFAULT FALSE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_user_id (id),
        INDEX idx_user_email (email)
    )
    """)
    print("Tabela users criada com sucesso")
    
    # Tabela sales
    cursor.execute("""
    CREATE TABLE sales (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        seller_id VARCHAR(36) NOT NULL,
        client_name VARCHAR(100),
        product VARCHAR(255) NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        total_value FLOAT NOT NULL,
        sale_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        gateway_fee FLOAT NOT NULL DEFAULT 0.0,
        ad_cost FLOAT NOT NULL DEFAULT 0.0,
        commission_rate FLOAT NOT NULL,
        commission_value FLOAT NOT NULL,
        payment_received BOOLEAN DEFAULT FALSE,
        payment_date DATETIME,
        payment_confirmed_by_seller BOOLEAN DEFAULT FALSE,
        payment_confirmation_date DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_sale_seller (seller_id),
        INDEX idx_sale_date (sale_date),
        FOREIGN KEY (seller_id) REFERENCES users(id)
    )
    """)
    print("Tabela sales criada com sucesso")
    
    # Tabela expenses
    cursor.execute("""
    CREATE TABLE expenses (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        user_id VARCHAR(36) NOT NULL,
        category VARCHAR(50) NOT NULL,
        description VARCHAR(255),
        value FLOAT NOT NULL,
        expense_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_expense_user (user_id),
        INDEX idx_expense_date (expense_date),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)
    print("Tabela expenses criada com sucesso")
    
    # Tabela ad_expenses
    cursor.execute("""
    CREATE TABLE ad_expenses (
        id VARCHAR(36) NOT NULL PRIMARY KEY,
        seller_id VARCHAR(36) NOT NULL,
        amount FLOAT NOT NULL,
        description VARCHAR(255),
        expense_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        payment_processed BOOLEAN DEFAULT FALSE,
        payment_date DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_ad_expense_seller (seller_id),
        INDEX idx_ad_expense_date (expense_date),
        FOREIGN KEY (seller_id) REFERENCES users(id)
    )
    """)
    print("Tabela ad_expenses criada com sucesso")
    
    # Verificar se existe usuário admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
    admin_count = cursor.fetchone()[0]
    
    if admin_count == 0:
        print("Criando usuário admin padrão...")
        admin_id = str(uuid.uuid4())
        admin_password = generate_password_hash('admin123')
        
        cursor.execute("""
        INSERT INTO users (id, email, password, name, role, commission_rate, commission_type, 
                          can_view_total_sales, can_view_ad_expenses, can_view_gateway_fee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (admin_id, 'admin@example.com', admin_password, 'Administrador', 'admin', 
              0.0, 'liquido', True, True, True))
        
        conn.commit()
        print("Usuário admin criado com sucesso!")
    else:
        print("Usuário admin já existe")
    
    # Fechar conexão
    conn.commit()
    cursor.close()
    conn.close()
    
    print("Migração concluída com sucesso!")
    
except Exception as e:
    print(f"Erro durante a migração: {e}")
    if 'conn' in locals() and conn:
        conn.close()
    sys.exit(1)
