from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import User, Product, RFQ, Category
from utils import seed_categories

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users':    User.query.count(),
        'total_sellers':  User.query.filter_by(role='seller').count(),
        'total_buyers':   User.query.filter_by(role='buyer').count(),
        'pending_sellers':User.query.filter_by(role='seller', is_approved=False).count(),
        'total_products': Product.query.count(),
        'total_rfqs':     RFQ.query.count(),
        'pending_rfqs':   RFQ.query.filter_by(status='pending').count(),
    }
    recent_sellers = User.query.filter_by(role='seller')\
                               .order_by(User.created_at.desc()).limit(10).all()
    recent_products= Product.query.order_by(Product.created_at.desc()).limit(10).all()
    return render_template('admin_dashboard.html',
                           stats=stats,
                           recent_sellers=recent_sellers,
                           recent_products=recent_products)


@admin_bp.route('/sellers')
@login_required
@admin_required
def sellers():
    sellers = User.query.filter_by(role='seller').order_by(User.created_at.desc()).all()
    return render_template('admin_sellers.html', sellers=sellers)


@admin_bp.route('/seller/approve/<int:uid>', methods=['POST'])
@login_required
@admin_required
def approve_seller(uid):
    user = User.query.get_or_404(uid)
    user.is_approved = True
    db.session.commit()
    flash(f'{user.name} approved as seller.', 'success')
    return redirect(url_for('admin.sellers'))


@admin_bp.route('/seller/reject/<int:uid>', methods=['POST'])
@login_required
@admin_required
def reject_seller(uid):
    user = User.query.get_or_404(uid)
    user.is_approved = False
    user.is_active_acc = False
    db.session.commit()
    flash(f'{user.name} has been rejected.', 'warning')
    return redirect(url_for('admin.sellers'))


@admin_bp.route('/products')
@login_required
@admin_required
def products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin_products.html', products=products)


@admin_bp.route('/product/delete/<int:pid>', methods=['POST'])
@login_required
@admin_required
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.products'))


@admin_bp.route('/product/feature/<int:pid>', methods=['POST'])
@login_required
@admin_required
def feature_product(pid):
    product = Product.query.get_or_404(pid)
    product.is_featured = not product.is_featured
    db.session.commit()
    flash(f'Product {"featured" if product.is_featured else "unfeatured"}.', 'success')
    return redirect(url_for('admin.products'))


@admin_bp.route('/rfqs')
@login_required
@admin_required
def rfqs():
    all_rfqs = RFQ.query.order_by(RFQ.created_at.desc()).all()
    return render_template('admin_rfqs.html', rfqs=all_rfqs)


@admin_bp.route('/seed-categories', methods=['POST'])
@login_required
@admin_required
def do_seed_categories():
    seed_categories()
    flash('Categories seeded!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=all_users)


@admin_bp.route('/user/toggle/<int:uid>', methods=['POST'])
@login_required
@admin_required
def toggle_user(uid):
    user = User.query.get_or_404(uid)
    if user.role == 'admin':
        flash('Cannot suspend admin.', 'danger')
        return redirect(url_for('admin.users'))
    user.is_active_acc = not user.is_active_acc
    db.session.commit()
    flash(f'User {"activated" if user.is_active_acc else "suspended"}.', 'success')
    return redirect(url_for('admin.users'))