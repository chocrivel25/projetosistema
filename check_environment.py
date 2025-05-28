import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
import sqlalchemy
from sqlalchemy import inspect, text
import pymysql

# Criar uma aplicação Flask temporária para executar as migrações
app = Flask(__name__)

# Verificar a configuração atual no arquivo main.py
try:
    with open('src/main.py', 'r') as f:
        main_content = f.read()
        print("Configuração atual em src/main.py:")
        for line in main_content.split('\n'):
            if 'SQLALCHEMY_DATABASE_URI' in line:
                print(f"  {line}")
except Exception as e:
    print(f"Erro ao ler src/main.py: {e}")

# Verificar todos os bancos de dados MySQL disponíveis
try:
    # Conectar ao MySQL sem especificar o banco de dados
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='password'
    )
    
    # Criar cursor
    cursor = conn.cursor()
    
    # Listar todos os bancos de dados
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    
    print("\nBancos de dados MySQL disponíveis:")
    for db in databases:
        print(f"  - {db[0]}")
    
    # Verificar especificamente o banco painel_vendas
    cursor.execute("SHOW DATABASES LIKE 'painel_vendas'")
    result = cursor.fetchone()
    
    if result:
        print("\nBanco de dados 'painel_vendas' encontrado.")
        
        # Usar o banco de dados
        cursor.execute("USE painel_vendas")
        
        # Verificar tabelas
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print("Tabelas no banco 'painel_vendas':")
        for table in tables:
            print(f"  - {table[0]}")
            
            # Verificar estrutura da tabela
            cursor.execute(f"DESCRIBE {table[0]}")
            columns = cursor.fetchall()
            
            print(f"    Colunas da tabela {table[0]}:")
            for col in columns:
                print(f"      - {col[0]}: {col[1]}")
    else:
        print("\nBanco de dados 'painel_vendas' NÃO encontrado.")
    
    # Fechar conexão
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"Erro ao verificar bancos de dados MySQL: {e}")
    if 'conn' in locals() and conn:
        conn.close()

print("\nVerificação de ambiente concluída.")
