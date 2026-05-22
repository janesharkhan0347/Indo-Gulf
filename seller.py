from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from models import Product, Category, RFQ
from forms import ProductForm, ProfileForm
from utils import save_image, make_unique_slug

seller_bp = Blueprint('seller', __name__)


def seller_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'seller':
            abort(403)
        if not current_user.is_approved:
            flash('Your seller account is pending admin approval.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


@seller_bp.route('/dashboard')
@login_required
@seller_required
def dashboard():
    products   = Product.query.filter_by(seller_id=current_user.id).all()
    rfqs       = RFQ.query.filter_by(seller_id=current_user.id)\
                          .order_by(RFQ.created_at.desc()).limit(10).all()
    total_views= sum(p.views for p in products)
    return render_template('seller_dashboard.html',
                           products=products,
                           rfqs=rfqs,
                           total_views=total_views)


@seller_bp.route('/product/add', methods=['GET', 'POST'])
@login_required
@seller_required
def add_product():
    form = ProductForm()
    form.category_id.choices = [(c.id, f"{c.icon} {c.name}")
                                 for c in Category.query.all()]
    if form.validate_on_submit():
        image_file = 'default_product.png'
        if form.image.data and form.image.data.filename:
            saved = save_image(form.image.data, 'products')
            if saved:
                image_file = saved
        slug = make_unique_slug(form.title.data, Product)
        product = Product(
            title=form.title.data.strip(),
            slug=slug,
            description=form.description.data.strip(),
            price=form.price.data,
            unit=form.unit.data,
            moq=form.moq.data,
            export_countries=form.export_countries.data,
            availability=form.availability.data,
            image=image_file,
            seller_id=current_user.id,
            category_id=form.category_id.data
        )
        db.session.add(product)
        db.session.commit()
        flash('Product listed successfully!', 'success')
        return redirect(url_for('seller.dashboard'))
    return render_template('add_product.html', form=form, title='Add Product')


@seller_bp.route('/product/edit/<int:pid>', methods=['GET', 'POST'])
@login_required
@seller_required
def edit_product(pid):
    product = Product.query.get_or_404(pid)
    if product.seller_id != current_user.id:
        abort(403)
    form = ProductForm(obj=product)
    form.category_id.choices = [(c.id, f"{c.icon} {c.name}")
                                 for c in Category.query.all()]
    if form.validate_on_submit():
        if form.image.data and form.image.data.filename:
            saved = save_image(form.image.data, 'products')
            if saved:
                product.image = saved
        product.title            = form.title.data.strip()
        product.slug             = make_unique_slug(form.title.data, Product, product.id)
        product.description      = form.description.data.strip()
        product.price            = form.price.data
        product.unit             = form.unit.data
        product.moq              = form.moq.data
        product.export_countries = form.export_countries.data
        product.availability     = form.availability.data
        product.category_id      = form.category_id.data
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('seller.dashboard'))
    return render_template('add_product.html', form=form, title='Edit Product', product=product)


@seller_bp.route('/product/delete/<int:pid>', methods=['POST'])
@login_required
@seller_required
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    if product.seller_id != current_user.id:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('seller.dashboard'))


@seller_bp.route('/rfqs')
@login_required
@seller_required
def rfqs():
    all_rfqs = RFQ.query.filter_by(seller_id=current_user.id)\
                        .order_by(RFQ.created_at.desc()).all()
    return render_template('seller_rfqs.html', rfqs=all_rfqs)


@seller_bp.route('/rfq/update/<int:rid>/<status>', methods=['POST'])
@login_required
@seller_required
def update_rfq(rid, status):
    rfq = RFQ.query.get_or_404(rid)
    if rfq.seller_id != current_user.id:
        abort(403)
    if status in ('replied', 'closed'):
        rfq.status = status
        db.session.commit()
        flash(f'RFQ marked as {status}.', 'success')
    return redirect(url_for('seller.rfqs'))


@seller_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@seller_required
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
        return redirect(url_for('seller.profile'))
    return render_template('profile.html', form=form)