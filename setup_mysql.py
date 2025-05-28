import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db
import pymysql

def setup_mysql_database():
    """Configura o banco de dados MySQL para o painel de vendas"""
    try:
        # Conectar ao MySQL
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='password',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Verificar se o banco de dados existe
            cursor.execute("SHOW DATABASES LIKE 'painel_vendas'")
            result = cursor.fetchone()
            
            # Se não existir, criar o banco de dados
            if not result:
                cursor.execute("CREATE DATABASE painel_vendas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                print("Banco de dados 'painel_vendas' criado com sucesso.")
            else:
                print("Banco de dados 'painel_vendas' já existe.")
            
            # Usar o banco de dados
            cursor.execute("USE painel_vendas")
            
            # Verificar se as tabelas existem
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [list(table.values())[0] for table in tables]
            
            print(f"Tabelas existentes: {table_names}")
            
            # Se as tabelas já existirem, verificar se precisam ser recriadas
            if 'users' in table_names:
                # Verificar se há problemas de incompatibilidade
                try:
                    # Testar uma consulta simples
                    cursor.execute("SELECT id, name, email FROM users LIMIT 1")
                    print("Tabela 'users' está OK.")
                except Exception as e:
                    print(f"Erro ao consultar tabela 'users': {e}")
                    print("Recriando todas as tabelas...")
                    return False
            
            return True
    except Exception as e:
        print(f"Erro ao configurar banco de dados MySQL: {e}")
        return False
    finally:
        connection.close()

if __name__ == "__main__":
    # Configurar banco de dados MySQL
    print("Configurando banco de dados MySQL...")
    setup_result = setup_mysql_database()
    
    if setup_result:
        print("Banco de dados MySQL configurado com sucesso.")
    else:
        print("Falha na configuração do banco de dados MySQL.")
        
        # Importar a aplicação Flask para obter o contexto
        from src.main import app
        
        with app.app_context():
            # Recriar o banco de dados
            from recreate_database import recreate_database
            recreate_database()
