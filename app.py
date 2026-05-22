import os
import sys

# 🔥 GOD-MODE FIX: Prevents Flask from creating a duplicate 'db' instance during circular imports
if __name__ == '__main__':
    sys.modules['app'] = sys.modules['__main__']

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from config import config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'), exist_ok=True)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.seller import seller_bp
    from routes.buyer import buyer_bp
    from routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(seller_bp, url_prefix='/seller')
    app.register_blueprint(buyer_bp, url_prefix='/buyer')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('404.html', message="Access Denied"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('404.html', message="Server Error"), 500

    # Create DB tables and seed admin
    with app.app_context():
        db.create_all()
        seed_admin(app)

    return app


def seed_admin(app):
    """Create default admin if not exists."""
    from models import User
    admin_email = app.config.get('ADMIN_EMAIL') or os.environ.get('ADMIN_EMAIL', 'admin@indogulf.com')
    admin_pass  = os.environ.get('ADMIN_PASSWORD', 'Admin@123')
    
    if not User.query.filter_by(email=admin_email).first():
        pw_hash = bcrypt.generate_password_hash(admin_pass).decode('utf-8')
        admin = User(
            name='IndoGulf Admin',
            email=admin_email,
            password=pw_hash,
            role='admin',
            is_approved=True,
            company_name='IndoGulf',
            country='India',
            phone='+919999999999'
        )
        db.session.add(admin)
        db.session.commit()
        print(f"[IndoGulf] Admin seeded: {admin_email}")


if __name__ == '__main__':
    app = create_app('development')
    app.run(host='0.0.0.0', port=7860, debug=True)