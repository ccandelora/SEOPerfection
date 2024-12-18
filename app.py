import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_mail import Mail, Message

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)

# Configuration
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "prime_insurance_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///prime_insurance.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

db.init_app(app)
mail = Mail(app)

# Service categories
PERSONAL_INSURANCE = {
    'auto': 'Auto Insurance',
    'home': 'Home Insurance',
    'umbrella': 'Umbrella Insurance',
    'life': 'Life Insurance',
    'bundling': 'Insurance Bundling'
}

BUSINESS_INSURANCE = {
    'business': 'Business Owners Insurance',
    'commercial-auto': 'Commercial Auto Insurance',
    'workmen-comp': 'Workmen's Comp Insurance',
    'non-profit': 'Non-Profit Insurance',
    'tech': 'Tech Insurance',
    'cyber': 'Cyber Security Insurance'
}

@app.route('/')
def index():
    return render_template('index.html', 
                         personal_insurance=PERSONAL_INSURANCE,
                         business_insurance=BUSINESS_INSURANCE)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        try:
            msg = Message('New Contact Form Submission',
                         sender=email,
                         recipients=['Quotes@PrimeHomeAndAuto.com'])
            msg.body = f"Name: {name}\nEmail: {email}\nMessage: {message}"
            mail.send(msg)
            flash('Thank you for your message. We will get back to you soon!', 'success')
        except Exception as e:
            logging.error(f"Error sending email: {e}")
            flash('Sorry, there was an error sending your message. Please try again later.', 'error')
        
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/service/<category>/<service>')
def service(category, service):
    services = PERSONAL_INSURANCE if category == 'personal' else BUSINESS_INSURANCE
    if service not in services:
        return redirect(url_for('index'))
    
    return render_template('service.html', 
                         service_name=services[service],
                         service_type=service)

@app.route('/sitemap.xml')
def sitemap():
    return app.send_static_file('sitemap.xml')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

with app.app_context():
    import models
    db.create_all()
