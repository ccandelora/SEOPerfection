import os
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import logging
from forms import ContactForm, QuoteForm

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "prime-insurance-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///prime_insurance.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

db.init_app(app)

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
