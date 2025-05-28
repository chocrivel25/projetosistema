from src.models.user import db
from datetime import datetime

class Sale(db.Model):
    __tablename__ = 'sales'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    client = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    total_value = db.Column(db.Float, nullable=False)
    gateway_fee = db.Column(db.Float, nullable=False, default=0)
    ad_expense = db.Column(db.Float, nullable=False, default=0)
    commission_value = db.Column(db.Float, nullable=False, default=0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False, default='confirmed')  # pending, confirmed, cancelled
    
    def __init__(self, seller_id, client, product, quantity, total_value, 
                 gateway_fee=0, ad_expense=0, commission_value=0, date=None, status='confirmed'):
        self.seller_id = seller_id
        self.client = client
        self.product = product
        self.quantity = quantity
        self.total_value = total_value
        self.gateway_fee = gateway_fee
        self.ad_expense = ad_expense
        self.commission_value = commission_value
        self.date = date if date else datetime.now()
        self.status = status
