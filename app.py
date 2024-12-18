import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
from forms import ContactForm, QuoteForm, LoginForm, RegistrationForm
from urllib.parse import urlparse

# Set up logging
logging.basicConfig(level=logging.DEBUG)

from database import db

app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "prime-insurance-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///prime_insurance.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

db.init_app(app)

from models import User, Policy

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
        
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('profile')
        return redirect(next_page)
    
    return render_template('auth/login.html', title='Sign In', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now registered!', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html', title='Register', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    policies = current_user.policies.all()
    return render_template('auth/profile.html', title='My Profile', policies=policies)

# Route handlers
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        flash('Thank you for your message. We will contact you shortly!', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html', form=form)

@app.route('/quote', methods=['GET', 'POST'])
def quote():
    form = QuoteForm()
    if form.validate_on_submit():
        flash('Thank you for requesting a quote. Our team will reach out soon!', 'success')
        return redirect(url_for('index'))
    return render_template('quote.html', form=form)

# Service routes
@app.route('/services/auto')
def auto_insurance():
    return render_template('services/auto.html')

@app.route('/services/home')
def home_insurance():
    return render_template('services/home.html')

@app.route('/services/life')
def life_insurance():
    return render_template('services/life.html')

@app.route('/services/umbrella')
def umbrella_insurance():
    return render_template('services/umbrella.html')

@app.route('/services/business')
def business_insurance():
    return render_template('services/business.html')

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

with app.app_context():
    import models
    db.create_all()