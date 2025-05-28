from src.models.user import db
from datetime import datetime

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, cancelled
    confirmed_date = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, seller_id, amount, date=None, status='pending', confirmed_date=None):
        self.seller_id = seller_id
        self.amount = amount
        self.date = date if date else datetime.now()
        self.status = status
        self.confirmed_date = confirmed_date
