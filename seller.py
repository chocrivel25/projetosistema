from flask import Blueprint, request, jsonify
from src.models.user import User, db
from src.models.sale import Sale
from src.models.expense import Expense
from src.models.ad_expense import AdExpense
from src.models.payment import Payment
from datetime import datetime, timedelta
import json

seller_bp = Blueprint('seller', __name__)

@seller_bp.route('/api/seller/dashboard', methods=['GET'])
def seller_dashboard():
    try:
        # Obter ID do vendedor da sessão
        seller_id = request.args.get('seller_id')
        period = request.args.get('period', '30')
        days = int(period)
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Total de vendas do vendedor
        sales = Sale.query.filter(Sale.seller_id == seller_id, Sale.date >= start_date).all()
        total_sales = sum(sale.total_value for sale in sales)
        
        # Total de comissões
        total_commission = sum(sale.commission_value for sale in sales)
        
        # Total de taxas de gateway
        total_gateway_fee = sum(sale.gateway_fee for sale in sales)
        
        # Total de gastos com anúncios
        ad_expenses = AdExpense.query.filter(AdExpense.seller_id == seller_id, AdExpense.date >= start_date).all()
        total_ad_expense = sum(expense.value for expense in ad_expenses)
        
        return jsonify({
            'total_sales': total_sales,
            'total_commission': total_commission,
            'total_gateway_fee': total_gateway_fee,
            'total_ad_expense': total_ad_expense
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/sales', methods=['GET'])
def get_sales():
    try:
        # Obter ID do vendedor da sessão
        seller_id = request.args.get('seller_id')
        period = request.args.get('period', '30')
        days = int(period)
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Buscar vendas do vendedor
        sales = Sale.query.filter(Sale.seller_id == seller_id, Sale.date >= start_date).all()
        
        return jsonify([{
            'id': sale.id,
            'client': sale.client,
            'product': sale.product,
            'quantity': sale.quantity,
            'total_value': sale.total_value,
            'gateway_fee': sale.gateway_fee,
            'ad_expense': sale.ad_expense,
            'commission_value': sale.commission_value,
            'date': sale.date.strftime('%Y-%m-%d'),
            'status': sale.status
        } for sale in sales])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/sales', methods=['POST'])
def create_sale():
    try:
        data = request.json
        seller_id = data.get('seller_id')
        
        # Buscar informações do vendedor
        seller = User.query.get(seller_id)
        if not seller:
            return jsonify({'error': 'Vendedor não encontrado'}), 404
        
        # Calcular taxa de gateway (9%)
        gateway_fee = data['total_value'] * 0.09
        
        # Obter custo de anúncio (se fornecido)
        ad_expense = data.get('ad_expense', 0)
        
        # Calcular comissão com base no tipo de comissão do vendedor
        commission_value = 0
        if seller.commission_type == 'net':
            # Comissão sobre valor líquido (após taxas e anúncios)
            net_value = data['total_value'] - gateway_fee - ad_expense
            commission_value = net_value * (seller.commission_rate / 100)
        else:  # gross
            # Comissão sobre valor bruto (sem descontos)
            commission_value = data['total_value'] * (seller.commission_rate / 100)
        
        # Criar nova venda
        new_sale = Sale(
            seller_id=seller_id,
            client=data['client'],
            product=data['product'],
            quantity=data['quantity'],
            total_value=data['total_value'],
            gateway_fee=gateway_fee,
            ad_expense=ad_expense,
            commission_value=commission_value,
            date=datetime.now(),
            status='confirmed'
        )
        
        db.session.add(new_sale)
        db.session.commit()
        
        return jsonify({
            'id': new_sale.id,
            'client': new_sale.client,
            'product': new_sale.product,
            'quantity': new_sale.quantity,
            'total_value': new_sale.total_value,
            'gateway_fee': new_sale.gateway_fee,
            'ad_expense': new_sale.ad_expense,
            'commission_value': new_sale.commission_value,
            'date': new_sale.date.strftime('%Y-%m-%d'),
            'status': new_sale.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/sales/<int:sale_id>', methods=['PUT'])
def update_sale(sale_id):
    try:
        data = request.json
        seller_id = data.get('seller_id')
        
        # Buscar venda
        sale = Sale.query.get(sale_id)
        if not sale:
            return jsonify({'error': 'Venda não encontrada'}), 404
        
        # Verificar se a venda pertence ao vendedor
        if sale.seller_id != seller_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar informações do vendedor
        seller = User.query.get(seller_id)
        if not seller:
            return jsonify({'error': 'Vendedor não encontrado'}), 404
        
        # Atualizar dados da venda
        if 'client' in data:
            sale.client = data['client']
        if 'product' in data:
            sale.product = data['product']
        if 'quantity' in data:
            sale.quantity = data['quantity']
        if 'total_value' in data:
            sale.total_value = data['total_value']
            # Recalcular taxa de gateway
            sale.gateway_fee = sale.total_value * 0.09
        if 'ad_expense' in data:
            sale.ad_expense = data['ad_expense']
        
        # Recalcular comissão
        if seller.commission_type == 'net':
            # Comissão sobre valor líquido (após taxas e anúncios)
            net_value = sale.total_value - sale.gateway_fee - sale.ad_expense
            sale.commission_value = net_value * (seller.commission_rate / 100)
        else:  # gross
            # Comissão sobre valor bruto (sem descontos)
            sale.commission_value = sale.total_value * (seller.commission_rate / 100)
        
        db.session.commit()
        
        return jsonify({
            'id': sale.id,
            'client': sale.client,
            'product': sale.product,
            'quantity': sale.quantity,
            'total_value': sale.total_value,
            'gateway_fee': sale.gateway_fee,
            'ad_expense': sale.ad_expense,
            'commission_value': sale.commission_value,
            'date': sale.date.strftime('%Y-%m-%d'),
            'status': sale.status
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/ad-expenses', methods=['GET'])
def get_ad_expenses():
    try:
        # Obter ID do vendedor da sessão
        seller_id = request.args.get('seller_id')
        period = request.args.get('period', '30')
        days = int(period)
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Buscar gastos com anúncios do vendedor
        expenses = AdExpense.query.filter(AdExpense.seller_id == seller_id, AdExpense.date >= start_date).all()
        
        return jsonify([{
            'id': expense.id,
            'value': expense.value,
            'date': expense.date.strftime('%Y-%m-%d'),
            'description': expense.description
        } for expense in expenses])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/ad-expenses', methods=['POST'])
def create_ad_expense():
    try:
        data = request.json
        seller_id = data.get('seller_id')
        
        # Criar novo gasto com anúncio
        new_expense = AdExpense(
            seller_id=seller_id,
            value=data['value'],
            date=datetime.now(),
            description=data.get('description', '')
        )
        
        db.session.add(new_expense)
        db.session.commit()
        
        return jsonify({
            'id': new_expense.id,
            'value': new_expense.value,
            'date': new_expense.date.strftime('%Y-%m-%d'),
            'description': new_expense.description
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/ad-expenses/<int:expense_id>', methods=['PUT'])
def update_ad_expense(expense_id):
    try:
        data = request.json
        seller_id = data.get('seller_id')
        
        # Buscar gasto com anúncio
        expense = AdExpense.query.get(expense_id)
        if not expense:
            return jsonify({'error': 'Gasto com anúncio não encontrado'}), 404
        
        # Verificar se o gasto pertence ao vendedor
        if expense.seller_id != seller_id:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Atualizar dados do gasto
        if 'value' in data:
            expense.value = data['value']
        if 'description' in data:
            expense.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'id': expense.id,
            'value': expense.value,
            'date': expense.date.strftime('%Y-%m-%d'),
            'description': expense.description
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/expenses', methods=['GET'])
def get_expenses():
    try:
        # Obter ID do vendedor da sessão
        seller_id = request.args.get('seller_id')
        period = request.args.get('period', '30')
        days = int(period)
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Buscar gastos do vendedor
        expenses = Expense.query.filter(Expense.seller_id == seller_id, Expense.date >= start_date).all()
        
        return jsonify([{
            'id': expense.id,
            'value': expense.value,
            'category': expense.category,
            'date': expense.date.strftime('%Y-%m-%d'),
            'description': expense.description
        } for expense in expenses])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/expenses', methods=['POST'])
def create_expense():
    try:
        data = request.json
        seller_id = data.get('seller_id')
        
        # Criar novo gasto
        new_expense = Expense(
            seller_id=seller_id,
            value=data['value'],
            category=data.get('category', 'other'),
            date=datetime.now(),
            description=data.get('description', '')
        )
        
        db.session.add(new_expense)
        db.session.commit()
        
        return jsonify({
            'id': new_expense.id,
            'value': new_expense.value,
            'category': new_expense.category,
            'date': new_expense.date.strftime('%Y-%m-%d'),
            'description': new_expense.description
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/payments/history', methods=['GET'])
def get_payment_history():
    try:
        # Obter ID do vendedor da sessão
        seller_id = request.args.get('seller_id')
        
        # Buscar pagamentos do vendedor
        payments = Payment.query.filter_by(seller_id=seller_id).all()
        
        return jsonify([{
            'id': payment.id,
            'amount': payment.amount,
            'date': payment.date.strftime('%Y-%m-%d'),
            'status': payment.status,
            'confirmed_date': payment.confirmed_date.strftime('%Y-%m-%d') if payment.confirmed_date else None
        } for payment in payments])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/payments/summary', methods=['GET'])
def get_payment_summary():
    try:
        # Obter ID do vendedor da sessão
        seller_id = request.args.get('seller_id')
        
        # Buscar vendas do vendedor
        sales = Sale.query.filter_by(seller_id=seller_id).all()
        total_commission = sum(sale.commission_value for sale in sales)
        
        # Buscar pagamentos confirmados
        confirmed_payments = Payment.query.filter_by(seller_id=seller_id, status='confirmed').all()
        total_received = sum(payment.amount for payment in confirmed_payments)
        
        # Calcular valor pendente
        pending_amount = total_commission - total_received
        
        return jsonify({
            'total_commission': total_commission,
            'total_received': total_received,
            'pending_amount': pending_amount
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/payments/confirm/<int:payment_id>', methods=['PUT'])
def confirm_payment(payment_id):
    try:
        # Obter ID do vendedor da sessão
        seller_id = request.args.get('seller_id')
        
        # Buscar pagamento
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Pagamento não encontrado'}), 404
        
        # Verificar se o pagamento pertence ao vendedor
        if payment.seller_id != int(seller_id):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Verificar se o pagamento já foi confirmado
        if payment.status != 'pending':
            return jsonify({'error': 'Pagamento já foi processado'}), 400
        
        # Confirmar pagamento
        payment.status = 'confirmed'
        payment.confirmed_date = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'id': payment.id,
            'amount': payment.amount,
            'date': payment.date.strftime('%Y-%m-%d'),
            'status': payment.status,
            'confirmed_date': payment.confirmed_date.strftime('%Y-%m-%d')
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@seller_bp.route('/api/seller/reports', methods=['GET'])
def get_reports():
    try:
        # Obter ID do vendedor da sessão
        seller_id = request.args.get('seller_id')
        
        # Obter período do relatório
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
        
        # Buscar vendas do vendedor no período
        sales = Sale.query.filter(
            Sale.seller_id == seller_id,
            Sale.date >= start_date,
            Sale.date <= end_date
        ).all()
        
        return jsonify([{
            'id': sale.id,
            'client': sale.client,
            'product': sale.product,
            'quantity': sale.quantity,
            'total_value': sale.total_value,
            'gateway_fee': sale.gateway_fee,
            'ad_expense': sale.ad_expense,
            'commission_value': sale.commission_value,
            'date': sale.date.strftime('%Y-%m-%d'),
            'status': sale.status
        } for sale in sales])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
