import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.models.user import db, User
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.ad_expense import AdExpense
from src.models.payment import Payment
from datetime import datetime

def recreate_database():
    """Recria o banco de dados e as tabelas"""
    try:
        # Remover todas as tabelas existentes
        db.drop_all()
        print("Tabelas removidas com sucesso.")
        
        # Criar todas as tabelas novamente
        db.create_all()
        print("Tabelas criadas com sucesso.")
        
        # Criar usuário admin padrão
        admin = User(
            name="Administrador",
            email="admin@example.com",
            password="admin123",
            role="admin",
            commission_rate=0,
            commission_type="net",
            can_see_ads=True,
            can_see_gateway_fee=True,
            can_see_other_sales=True,
            active=True
        )
        
        # Criar vendedor de exemplo
        seller = User(
            name="Vendedor Exemplo",
            email="vendedor@example.com",
            password="vendedor123",
            role="seller",
            commission_rate=10,
            commission_type="net",
            can_see_ads=False,
            can_see_gateway_fee=False,
            can_see_other_sales=False,
            active=True
        )
        
        # Adicionar usuários ao banco
        db.session.add(admin)
        db.session.add(seller)
        db.session.commit()
        
        print(f"Usuário admin criado: {admin.email}")
        print(f"Usuário vendedor criado: {seller.email}")
        
        # Criar algumas vendas de exemplo
        sale1 = Sale(
            seller_id=seller.id,
            client="Cliente Teste 1",
            product="Produto A",
            quantity=2,
            total_value=1000.00,
            gateway_fee=90.00,  # 9%
            ad_expense=100.00,
            commission_value=81.00,  # 10% do valor líquido (1000 - 90 - 100 = 810 * 10% = 81)
            date=datetime.now(),
            status="confirmed"
        )
        
        sale2 = Sale(
            seller_id=seller.id,
            client="Cliente Teste 2",
            product="Produto B",
            quantity=1,
            total_value=500.00,
            gateway_fee=45.00,  # 9%
            ad_expense=50.00,
            commission_value=40.50,  # 10% do valor líquido (500 - 45 - 50 = 405 * 10% = 40.5)
            date=datetime.now(),
            status="confirmed"
        )
        
        # Adicionar vendas ao banco
        db.session.add(sale1)
        db.session.add(sale2)
        
        # Criar gasto com anúncio de exemplo
        ad_expense = AdExpense(
            seller_id=seller.id,
            value=150.00,
            date=datetime.now(),
            description="Campanha Facebook Ads"
        )
        
        # Adicionar gasto com anúncio ao banco
        db.session.add(ad_expense)
        
        # Criar pagamento de exemplo
        payment = Payment(
            seller_id=seller.id,
            amount=81.00,
            date=datetime.now(),
            status="pending",
            confirmed_date=None
        )
        
        # Adicionar pagamento ao banco
        db.session.add(payment)
        
        # Commit final
        db.session.commit()
        
        print("Dados de exemplo criados com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao recriar banco de dados: {e}")
        db.session.rollback()
        return False

if __name__ == "__main__":
    # Importar a aplicação Flask para obter o contexto
    from src.main import app
    
    with app.app_context():
        print("Recriando banco de dados...")
        recreate_database()
