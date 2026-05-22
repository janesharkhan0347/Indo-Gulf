from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import Product, RFQ, Favorite, User
from forms import RFQForm, ProfileForm
from utils import save_image

buyer_bp = Blueprint('buyer', __name__)


def buyer_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ('buyer', 'admin'):
            abort(403)
        return f(*args, **kwargs)
    return decorated


@buyer_bp.route('/dashboard')
@login_required
@buyer_required
def dashboard():
    rfqs      = RFQ.query.filter_by(buyer_id=current_user.id)\
                         .order_by(RFQ.created_at.desc()).all()
    favorites = Favorite.query.filter_by(user_id=current_user.id).all()
    fav_products = [f.product for f in favorites]
    return render_template('buyer_dashboard.html', rfqs=rfqs, fav_products=fav_products)


@buyer_bp.route('/rfq/send/<int:product_id>', methods=['GET', 'POST'])
@login_required
def send_rfq(product_id):
    if current_user.role == 'seller':
        flash('Sellers cannot send RFQs. Please log in as a buyer.', 'warning')
        return redirect(url_for('main.product_detail',
                                slug=Product.query.get_or_404(product_id).slug))
    product = Product.query.get_or_404(product_id)
    form    = RFQForm()
    if form.validate_on_submit():
        rfq = RFQ(
            quantity=form.quantity.data,
            unit=form.unit.data,
            message=form.message.data.strip(),
            buyer_id=current_user.id,
            seller_id=product.seller_id,
            product_id=product.id
        )
        db.session.add(rfq)
        db.session.commit()
        flash('Your RFQ has been sent to the seller!', 'success')
        return redirect(url_for('buyer.dashboard'))
    return render_template('rfq.html', form=form, product=product)


@buyer_bp.route('/favorite/<int:product_id>', methods=['POST'])
@login_required
def toggle_favorite(product_id):
    existing = Favorite.query.filter_by(user_id=current_user.id,
                                        product_id=product_id).first()
    if existing:
        db.session.delete(existing)
        flash('Removed from favorites.', 'info')
    else:
        fav = Favorite(user_id=current_user.id, product_id=product_id)
        db.session.add(fav)
        flash('Added to favorites!', 'success')
    db.session.commit()
    return redirect(request.referrer or url_for('main.products'))


@buyer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@buyer_required
def profile():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        if form.logo.data and form.logo.data.filename:
            saved = save_image(form.logo.data, 'logos', max_size=(300, 300))
            if saved:
                current_user.logo = saved
        current_user.name         = form.name.data.strip()
        current_user.company_name = form.company_name.data.strip()
        current_user.phone        = form.phone.data.strip()
        current_user.about        = form.about.data.strip()
        current_user.website      = form.website.data.strip()
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('buyer.profile'))
    return render_template('profile.html', form=form)