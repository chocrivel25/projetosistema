from flask import Blueprint, request, jsonify
from src.models.user import User, db
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.ad_expense import AdExpense
from src.models.payment import Payment
from datetime import datetime, timedelta
import json

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    try:
        period = request.args.get('period', '30')
        days = int(period)
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Total de vendas
        sales = Sale.query.filter(Sale.date >= start_date).all()
        total_sales = sum(sale.total_value for sale in sales)
        
        # Total de comissões
        total_commission = sum(sale.commission_value for sale in sales)
        
        # Total de taxas de gateway
        total_gateway_fee = sum(sale.gateway_fee for sale in sales)
        
        # Total de gastos com anúncios
        ad_expenses = AdExpense.query.filter(AdExpense.date >= start_date).all()
        total_ad_expense = sum(expense.value for expense in ad_expenses)
        
        # Vendas por vendedor
        sales_by_seller = {}
        for sale in sales:
            seller_id = sale.seller_id
            if seller_id not in sales_by_seller:
                sales_by_seller[seller_id] = 0
            sales_by_seller[seller_id] += sale.total_value
        
        # Formatando dados para o gráfico
        sellers = User.query.filter_by(role='seller').all()
        seller_names = {seller.id: seller.name for seller in sellers}
        
        chart_data = []
        for seller_id, total in sales_by_seller.items():
            if seller_id in seller_names:
                chart_data.append({
                    'name': seller_names[seller_id],
                    'value': total
                })
        
        return jsonify({
            'total_sales': total_sales,
            'total_commission': total_commission,
            'total_gateway_fee': total_gateway_fee,
            'total_ad_expense': total_ad_expense,
            'chart_data': chart_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/users', methods=['GET'])
def get_users():
    try:
        users = User.query.filter_by(role='seller').all()
        return jsonify([{
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'commission_rate': user.commission_rate,
            'commission_type': user.commission_type,
            'can_see_ads': user.can_see_ads,
            'can_see_gateway_fee': user.can_see_gateway_fee,
            'can_see_other_sales': user.can_see_other_sales,
            'active': user.active
        } for user in users])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        
        # Verificar se o email já existe
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        new_user = User(
            name=data['name'],
            email=data['email'],
            password=data['password'],  # Será criptografada no modelo
            role='seller',
            commission_rate=data['commission_rate'],
            commission_type=data['commission_type'],
            can_see_ads=data.get('can_see_ads', False),
            can_see_gateway_fee=data.get('can_see_gateway_fee', False),
            can_see_other_sales=data.get('can_see_other_sales', False),
            active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'id': new_user.id,
            'name': new_user.name,
            'email': new_user.email,
            'commission_rate': new_user.commission_rate,
            'commission_type': new_user.commission_type,
            'can_see_ads': new_user.can_see_ads,
            'can_see_gateway_fee': new_user.can_see_gateway_fee,
            'can_see_other_sales': new_user.can_see_other_sales,
            'active': new_user.active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Atualizar dados do usuário
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        if 'commission_rate' in data:
            user.commission_rate = data['commission_rate']
        if 'commission_type' in data:
            user.commission_type = data['commission_type']
        if 'can_see_ads' in data:
            user.can_see_ads = data['can_see_ads']
        if 'can_see_gateway_fee' in data:
            user.can_see_gateway_fee = data['can_see_gateway_fee']
        if 'can_see_other_sales' in data:
            user.can_see_other_sales = data['can_see_other_sales']
        if 'active' in data:
            user.active = data['active']
        
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'commission_rate': user.commission_rate,
            'commission_type': user.commission_type,
            'can_see_ads': user.can_see_ads,
            'can_see_gateway_fee': user.can_see_gateway_fee,
            'can_see_other_sales': user.can_see_other_sales,
            'active': user.active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Desativar usuário em vez de excluir
        user.active = False
        db.session.commit()
        
        return jsonify({'message': 'Usuário desativado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/payments', methods=['GET'])
def get_payments():
    try:
        payments = Payment.query.all()
        
        result = []
        for payment in payments:
            seller = User.query.get(payment.seller_id)
            result.append({
                'id': payment.id,
                'seller_id': payment.seller_id,
                'seller_name': seller.name if seller else 'Desconhecido',
                'amount': payment.amount,
                'date': payment.date.strftime('%Y-%m-%d'),
                'status': payment.status,
                'confirmed_date': payment.confirmed_date.strftime('%Y-%m-%d') if payment.confirmed_date else None
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/payments', methods=['POST'])
def create_payment():
    try:
        data = request.json
        
        new_payment = Payment(
            seller_id=data['seller_id'],
            amount=data['amount'],
            date=datetime.now(),
            status='pending',
            confirmed_date=None
        )
        
        db.session.add(new_payment)
        db.session.commit()
        
        seller = User.query.get(new_payment.seller_id)
        
        return jsonify({
            'id': new_payment.id,
            'seller_id': new_payment.seller_id,
            'seller_name': seller.name if seller else 'Desconhecido',
            'amount': new_payment.amount,
            'date': new_payment.date.strftime('%Y-%m-%d'),
            'status': new_payment.status,
            'confirmed_date': None
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/seller-summary', methods=['GET'])
def seller_summary():
    try:
        sellers = User.query.filter_by(role='seller', active=True).all()
        
        result = []
        for seller in sellers:
            # Vendas totais
            sales = Sale.query.filter_by(seller_id=seller.id).all()
            total_sales = sum(sale.total_value for sale in sales)
            
            # Comissões totais
            total_commission = sum(sale.commission_value for sale in sales)
            
            # Pagamentos realizados
            payments = Payment.query.filter_by(seller_id=seller.id, status='confirmed').all()
            total_paid = sum(payment.amount for payment in payments)
            
            # Valor pendente
            pending_amount = total_commission - total_paid
            
            result.append({
                'id': seller.id,
                'name': seller.name,
                'total_sales': total_sales,
                'total_commission': total_commission,
                'total_paid': total_paid,
                'pending_amount': pending_amount,
                'commission_rate': seller.commission_rate,
                'commission_type': seller.commission_type
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/ad-expenses', methods=['GET'])
def get_ad_expenses():
    try:
        ad_expenses = AdExpense.query.all()
        
        result = []
        for expense in ad_expenses:
            seller = User.query.get(expense.seller_id)
            result.append({
                'id': expense.id,
                'seller_id': expense.seller_id,
                'seller_name': seller.name if seller else 'Desconhecido',
                'value': expense.value,
                'date': expense.date.strftime('%Y-%m-%d'),
                'description': expense.description
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/ad-expenses', methods=['POST'])
def create_ad_expense():
    try:
        data = request.json
        
        new_expense = AdExpense(
            seller_id=data['seller_id'],
            value=data['value'],
            date=datetime.now(),
            description=data.get('description', '')
        )
        
        db.session.add(new_expense)
        db.session.commit()
        
        seller = User.query.get(new_expense.seller_id)
        
        return jsonify({
            'id': new_expense.id,
            'seller_id': new_expense.seller_id,
            'seller_name': seller.name if seller else 'Desconhecido',
            'value': new_expense.value,
            'date': new_expense.date.strftime('%Y-%m-%d'),
            'description': new_expense.description
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/reports/sales', methods=['GET'])
def sales_report():
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()
        
        sales = Sale.query.filter(Sale.date >= start_date, Sale.date <= end_date).all()
        
        result = []
        for sale in sales:
            seller = User.query.get(sale.seller_id)
            result.append({
                'id': sale.id,
                'date': sale.date.strftime('%Y-%m-%d'),
                'client': sale.client,
                'product': sale.product,
                'quantity': sale.quantity,
                'total_value': sale.total_value,
                'gateway_fee': sale.gateway_fee,
                'ad_expense': sale.ad_expense,
                'commission_value': sale.commission_value,
                'seller_id': sale.seller_id,
                'seller_name': seller.name if seller else 'Desconhecido'
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/reports/payments', methods=['GET'])
def payments_report():
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()
        
        payments = Payment.query.filter(Payment.date >= start_date, Payment.date <= end_date).all()
        
        result = []
        for payment in payments:
            seller = User.query.get(payment.seller_id)
            result.append({
                'id': payment.id,
                'date': payment.date.strftime('%Y-%m-%d'),
                'amount': payment.amount,
                'status': payment.status,
                'confirmed_date': payment.confirmed_date.strftime('%Y-%m-%d') if payment.confirmed_date else None,
                'seller_id': payment.seller_id,
                'seller_name': seller.name if seller else 'Desconhecido'
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/reports/ad-expenses', methods=['GET'])
def ad_expenses_report():
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()
        
        expenses = AdExpense.query.filter(AdExpense.date >= start_date, AdExpense.date <= end_date).all()
        
        result = []
        for expense in expenses:
            seller = User.query.get(expense.seller_id)
            result.append({
                'id': expense.id,
                'date': expense.date.strftime('%Y-%m-%d'),
                'value': expense.value,
                'description': expense.description,
                'seller_id': expense.seller_id,
                'seller_name': seller.name if seller else 'Desconhecido'
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/api/admin/export/sales', methods=['GET'])
def export_sales():
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        else:
            start_date = datetime.now() - timedelta(days=30)
            
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        else:
            end_date = datetime.now()
      
(Content truncated due to size limit. Use line ranges to read in chunks)