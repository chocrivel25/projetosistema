from src.models.user import db
from datetime import datetime

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    description = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(50), nullable=False, default='other')  # transport, internet, other
    
    def __init__(self, seller_id, value, category='other', date=None, description=''):
        self.seller_id = seller_id
        self.value = value
        self.category = category
        self.date = date if date else datetime.now()
        self.description = description
