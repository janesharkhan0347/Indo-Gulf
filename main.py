from flask import Blueprint, render_template, request, redirect, url_for
from models import Product, Category, User
from app import db
from sqlalchemy import or_

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    featured = Product.query.filter_by(is_featured=True, is_approved=True, availability=True)\
                            .order_by(Product.created_at.desc()).limit(8).all()
    categories = Category.query.all()
    top_sellers = User.query.filter_by(role='seller', is_approved=True)\
                            .limit(6).all()
    return render_template('index.html',
                           featured=featured,
                           categories=categories,
                           top_sellers=top_sellers)


@main_bp.route('/products')
def products():
    page       = request.args.get('page', 1, type=int)
    cat_slug   = request.args.get('category', '')
    country    = request.args.get('country', '')
    min_price  = request.args.get('min_price', 0, type=float)
    max_price  = request.args.get('max_price', 99999, type=float)
    min_moq    = request.args.get('min_moq', 0, type=int)
    sort       = request.args.get('sort', 'newest')

    q = Product.query.filter_by(is_approved=True, availability=True)

    if cat_slug:
        cat = Category.query.filter_by(slug=cat_slug).first()
        if cat:
            q = q.filter_by(category_id=cat.id)

    if country:
        q = q.filter(Product.export_countries.contains(country))

    q = q.filter(Product.price >= min_price, Product.price <= max_price)
    q = q.filter(Product.moq >= min_moq)

    if sort == 'price_asc':
        q = q.order_by(Product.price.asc())
    elif sort == 'price_desc':
        q = q.order_by(Product.price.desc())
    elif sort == 'popular':
        q = q.order_by(Product.views.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    products   = q.paginate(page=page, per_page=12, error_out=False)
    categories = Category.query.all()
    return render_template('products.html',
                           products=products,
                           categories=categories,
                           selected_cat=cat_slug,
                           selected_country=country)


@main_bp.route('/product/<slug>')
def product_detail(slug):
    product = Product.query.filter_by(slug=slug, is_approved=True).first_or_404()
    product.views += 1
    db.session.commit()
    related = Product.query.filter(
        Product.category_id == product.category_id,
        Product.id != product.id,
        Product.is_approved == True
    ).limit(4).all()
    from forms import RFQForm
    rfq_form = RFQForm()
    return render_template('product_detail.html',
                           product=product,
                           related=related,
                           rfq_form=rfq_form)


@main_bp.route('/category/<slug>')
def category(slug):
    cat      = Category.query.filter_by(slug=slug).first_or_404()
    page     = request.args.get('page', 1, type=int)
    products = Product.query.filter_by(category_id=cat.id, is_approved=True)\
                            .paginate(page=page, per_page=12, error_out=False)
    return render_template('categories.html',
                           cat=cat,
                           products=products)


@main_bp.route('/categories')
def all_categories():
    categories = Category.query.all()
    return render_template('all_categories.html', categories=categories)


@main_bp.route('/search')
def search():
    q          = request.args.get('q', '').strip()
    page       = request.args.get('page', 1, type=int)
    results    = []
    if q:
        results = Product.query.filter(
            Product.is_approved == True,
            or_(
                Product.title.ilike(f'%{q}%'),
                Product.description.ilike(f'%{q}%')
            )
        ).paginate(page=page, per_page=12, error_out=False)
    return render_template('search_results.html', results=results, query=q)


@main_bp.route('/seller/<int:seller_id>')
def seller_profile(seller_id):
    seller   = User.query.filter_by(id=seller_id, role='seller', is_approved=True).first_or_404()
    products = Product.query.filter_by(seller_id=seller_id, is_approved=True).all()
    return render_template('seller_public.html', seller=seller, products=products)