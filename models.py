from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(150), unique=True, nullable=False)
    password      = db.Column(db.String(255), nullable=False)
    role          = db.Column(db.String(20), default='buyer')   # admin / seller / buyer
    is_approved   = db.Column(db.Boolean, default=False)
    is_active_acc = db.Column(db.Boolean, default=True)
    company_name  = db.Column(db.String(200))
    gst_number    = db.Column(db.String(50))
    iec_code      = db.Column(db.String(50))
    country       = db.Column(db.String(100))
    phone         = db.Column(db.String(30))
    logo          = db.Column(db.String(255), default='default_logo.png')
    about         = db.Column(db.Text)
    website       = db.Column(db.String(255))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    products      = db.relationship('Product', backref='seller', lazy=True,
                                    foreign_keys='Product.seller_id')
    sent_rfqs     = db.relationship('RFQ', backref='buyer', lazy=True,
                                    foreign_keys='RFQ.buyer_id')
    received_rfqs = db.relationship('RFQ', backref='seller_user', lazy=True,
                                    foreign_keys='RFQ.seller_id')
    favorites     = db.relationship('Favorite', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email} [{self.role}]>'


class Category(db.Model):
    __tablename__ = 'categories'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), unique=True, nullable=False)
    slug        = db.Column(db.String(100), unique=True, nullable=False)
    icon        = db.Column(db.String(10), default='📦')
    description = db.Column(db.Text)
    products    = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'

    id              = db.Column(db.Integer, primary_key=True)
    title           = db.Column(db.String(255), nullable=False)
    slug            = db.Column(db.String(255), unique=True)
    description     = db.Column(db.Text, nullable=False)
    price           = db.Column(db.Float, nullable=False)
    unit            = db.Column(db.String(50), default='kg')
    moq             = db.Column(db.Integer, default=100)
    availability    = db.Column(db.Boolean, default=True)
    export_countries= db.Column(db.String(255), default='UAE,Saudi Arabia,Qatar,Oman,Kuwait,Bahrain')
    image           = db.Column(db.String(255), default='default_product.png')
    is_featured     = db.Column(db.Boolean, default=False)
    is_approved     = db.Column(db.Boolean, default=True)
    views           = db.Column(db.Integer, default=0)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    seller_id       = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id     = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    rfqs            = db.relationship('RFQ', backref='product', lazy=True)
    favorites       = db.relationship('Favorite', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.title}>'


class RFQ(db.Model):
    __tablename__ = 'rfqs'

    id          = db.Column(db.Integer, primary_key=True)
    quantity    = db.Column(db.Integer, nullable=False)
    unit        = db.Column(db.String(50))
    message     = db.Column(db.Text)
    status      = db.Column(db.String(30), default='pending')   # pending / replied / closed
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    buyer_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id  = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)

    def __repr__(self):
        return f'<RFQ #{self.id} [{self.status}]>'


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)