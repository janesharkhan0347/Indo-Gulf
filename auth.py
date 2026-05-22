from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from models import User
from forms import LoginForm, BuyerRegisterForm, SellerRegisterForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user)
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            if not user.is_active_acc:
                flash('Your account has been suspended.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or _redirect_url(user))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)


@auth_bp.route('/register')
def register():
    return render_template('register_choice.html')


@auth_bp.route('/register/buyer', methods=['GET', 'POST'])
def register_buyer():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = BuyerRegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register_buyer'))
        pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            password=pw,
            role='buyer',
            is_approved=True,
            company_name=form.company_name.data.strip(),
            country=form.country.data,
            phone=form.phone.data.strip()
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created! Welcome to IndoGulf.', 'success')
        return redirect(url_for('buyer.dashboard'))
    return render_template('register_buyer.html', form=form)


@auth_bp.route('/register/seller', methods=['GET', 'POST'])
def register_seller():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SellerRegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register_seller'))
        pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            name=form.name.data.strip(),
            email=form.email.data.lower().strip(),
            password=pw,
            role='seller',
            is_approved=False,         # needs admin approval
            company_name=form.company_name.data.strip(),
            gst_number=form.gst_number.data.strip(),
            iec_code=form.iec_code.data.strip(),
            country=form.country.data,
            phone=form.phone.data.strip()
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration submitted! Admin will approve your seller account shortly.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('register_seller.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


def _redirect_by_role(user):
    return redirect(_redirect_url(user))


def _redirect_url(user):
    if user.role == 'admin':
        return url_for('admin.dashboard')
    elif user.role == 'seller':
        return url_for('seller.dashboard')
    return url_for('buyer.dashboard')