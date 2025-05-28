import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.ad_expense import AdExpense
from src.models.payment import Payment
from sqlalchemy import inspect, MetaData, Table, Column, Integer, ForeignKey, text
from sqlalchemy.exc import SQLAlchemyError
import pymysql

def validate_foreign_keys():
    """Valida as chaves estrangeiras e índices no banco de dados"""
    try:
        # Conectar ao MySQL diretamente para inspeção
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='password',
            database='painel_vendas',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Verificar tabelas existentes
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [list(table.values())[0] for table in tables]
            print(f"Tabelas existentes: {table_names}")
            
            # Verificar foreign keys em cada tabela
            for table_name in table_names:
                if table_name in ['sales', 'ad_expenses', 'expenses', 'payments']:
                    # Verificar foreign keys
                    cursor.execute(f"""
                        SELECT 
                            COLUMN_NAME, 
                            REFERENCED_TABLE_NAME, 
                            REFERENCED_COLUMN_NAME
                        FROM 
                            INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                        WHERE 
                            TABLE_SCHEMA = 'painel_vendas' AND
                            TABLE_NAME = '{table_name}' AND
                            REFERENCED_TABLE_NAME IS NOT NULL
                    """)
                    foreign_keys = cursor.fetchall()
                    
                    print(f"\nForeign keys na tabela {table_name}:")
                    for fk in foreign_keys:
                        print(f"  - Coluna: {fk['COLUMN_NAME']}")
                        print(f"    Referencia: {fk['REFERENCED_TABLE_NAME']}.{fk['REFERENCED_COLUMN_NAME']}")
                    
                    # Verificar índices
                    cursor.execute(f"SHOW INDEX FROM {table_name}")
                    indices = cursor.fetchall()
                    
                    print(f"\nÍndices na tabela {table_name}:")
                    for idx in indices:
                        print(f"  - Nome: {idx['Key_name']}")
                        print(f"    Coluna: {idx['Column_name']}")
                        print(f"    Único: {idx['Non_unique'] == 0}")
            
            # Verificar colunas da tabela users
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            print("\nColunas da tabela users:")
            for column in columns:
                print(f"  - {column['Field']}: {column['Type']}")
        
        return True
    except Exception as e:
        print(f"Erro ao validar foreign keys: {e}")
        return False
    finally:
        connection.close()

def fix_foreign_keys():
    """Corrige as chaves estrangeiras e índices no banco de dados"""
    try:
        # Conectar ao MySQL diretamente para correções
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='password',
            database='painel_vendas',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Verificar tabelas existentes
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_names = [list(table.values())[0] for table in tables]
            
            # Adicionar índices para seller_id em todas as tabelas relacionadas
            for table_name in ['sales', 'ad_expenses', 'expenses', 'payments']:
                if table_name in table_names:
                    # Verificar se o índice já existe
                    cursor.execute(f"SHOW INDEX FROM {table_name} WHERE Column_name = 'seller_id'")
                    indices = cursor.fetchall()
                    
                    if not indices:
                        print(f"Adicionando índice para seller_id na tabela {table_name}")
                        try:
                            cursor.execute(f"CREATE INDEX idx_{table_name}_seller_id ON {table_name} (seller_id)")
                            connection.commit()
                        except Exception as e:
                            print(f"Erro ao criar índice em {table_name}: {e}")
                            # Verificar se a coluna existe
                            cursor.execute(f"DESCRIBE {table_name}")
                            columns = cursor.fetchall()
                            column_names = [col['Field'] for col in columns]
                            print(f"Colunas disponíveis em {table_name}: {column_names}")
                            
                            # Tentar com outro nome de coluna se seller_id não existir
                            if 'user_id' in column_names and 'seller_id' not in column_names:
                                print(f"Tentando criar índice em user_id para {table_name}")
                                cursor.execute(f"CREATE INDEX idx_{table_name}_user_id ON {table_name} (user_id)")
                                connection.commit()
        
        return True
    except Exception as e:
        print(f"Erro ao corrigir foreign keys: {e}")
        return False
    finally:
        connection.close()

if __name__ == "__main__":
    # Importar a aplicação Flask para obter o contexto
    from src.main import app
    
    with app.app_context():
        print("Validando foreign keys e índices...")
        validate_foreign_keys()
        
        print("\nCorrigindo foreign keys e índices...")
        fix_foreign_keys()
        
        print("\nValidando novamente após correções...")
        validate_foreign_keys()
