from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='seller')  # admin, seller
    commission_rate = db.Column(db.Float, nullable=False, default=10.0)
    commission_type = db.Column(db.String(10), nullable=False, default='net')  # net, gross
    can_see_ads = db.Column(db.Boolean, nullable=False, default=False)
    can_see_gateway_fee = db.Column(db.Boolean, nullable=False, default=False)
    can_see_other_sales = db.Column(db.Boolean, nullable=False, default=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    
    def __init__(self, name, email, password, role='seller', commission_rate=10.0, 
                 commission_type='net', can_see_ads=False, can_see_gateway_fee=False, 
                 can_see_other_sales=False, active=True):
        self.name = name
        self.email = email
        self.set_password(password)
        self.role = role
        self.commission_rate = commission_rate
        self.commission_type = commission_type
        self.can_see_ads = can_see_ads
        self.can_see_gateway_fee = can_see_gateway_fee
        self.can_see_other_sales = can_see_other_sales
        self.active = active
    
    def set_password(self, password):
        # Em produção, usar bcrypt ou outro algoritmo seguro
        # Por simplicidade, estamos apenas armazenando a senha diretamente
        # NUNCA faça isso em um ambiente real!
        self.password = password
    
    def check_password(self, password):
        return self.password == password
