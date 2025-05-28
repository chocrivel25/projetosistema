from src.models.user import db
from datetime import datetime

class AdExpense(db.Model):
    __tablename__ = 'ad_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    description = db.Column(db.String(255), nullable=True)
    
    def __init__(self, seller_id, value, date=None, description=''):
        self.seller_id = seller_id
        self.value = value
        self.date = date if date else datetime.now()
        self.description = description
