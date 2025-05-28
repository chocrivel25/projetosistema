import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask
import sqlalchemy
from sqlalchemy import inspect, text

# Criar uma aplicação Flask temporária para executar as migrações
app = Flask(__name__)

# Configurar SQLAlchemy para usar o banco MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:password@localhost:3306/painel_vendas"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importar modelos após configurar app
from src.models.user import db

db.init_app(app)

# Atualizar o arquivo main.py para apontar para o banco correto
try:
    with open('src/main.py', 'r') as f:
        main_content = f.read()
    
    # Substituir a configuração do banco de dados
    new_content = main_content.replace(
        "app.config['SQLALCHEMY_DATABASE_URI'] = f\"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}\"",
        "app.config['SQLALCHEMY_DATABASE_URI'] = f\"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'painel_vendas')}\""
    )
    
    with open('src/main.py', 'w') as f:
        f.write(new_content)
    
    print("Arquivo src/main.py atualizado com sucesso para apontar para o banco 'painel_vendas'")
    
except Exception as e:
    print(f"Erro ao atualizar src/main.py: {e}")

print("\nAtualização de configuração concluída.")
