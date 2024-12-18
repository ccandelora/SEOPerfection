import os
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import logging
from forms import ContactForm, QuoteForm, LoginForm, RegistrationForm, EditProfileForm
from forms import ContactForm, QuoteForm, LoginForm, RegistrationForm, EditProfileForm, AutoInsuranceCalculatorForm
from urllib.parse import urlparse
from flask_socketio import SocketIO, emit
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)

from database import db

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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

from models import User, Policy, BlogPost, PostLike, SavedPost
from forms import LoginForm, RegistrationForm, ContactForm, QuoteForm, BlogPostForm

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('onboarding'))
    
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

@app.route('/onboarding')
@login_required
def onboarding():
    if current_user.onboarding_completed:
        return redirect(url_for('profile'))
    return render_template('auth/onboarding.html')

@app.route('/onboarding/save-profile', methods=['POST'])
@login_required
def save_onboarding_profile():
    data = request.get_json()
    current_user.phone = data.get('phone')
    current_user.address = data.get('address')
    current_user.onboarding_step = 2
    db.session.commit()
    return jsonify({'success': True})

@app.route('/onboarding/complete', methods=['POST'])
@login_required
def complete_onboarding():
    current_user.onboarding_completed = True
    db.session.commit()
    return jsonify({'success': True})

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

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_email=current_user.email)
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
        form.address.data = current_user.address
        form.email.data = current_user.email
    return render_template('auth/edit_profile.html', title='Edit Profile', form=form)

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

@app.route('/calculators/auto', methods=['GET', 'POST'])
def auto_insurance_calculator():
    form = AutoInsuranceCalculatorForm()
    estimated_premium = None
    
    if form.validate_on_submit():
        # Basic premium calculation logic
        base_premium = 100  # Base monthly premium
        
        # Vehicle age factor
        vehicle_age = 2024 - int(form.vehicle_year.data)
        age_factor = 1 + (vehicle_age * 0.02)  # 2% increase per year of age
        
        # Driver age factor
        driver_age = int(form.driver_age.data)
        if driver_age < 25:
            driver_factor = 1.5
        elif driver_age > 65:
            driver_factor = 1.3
        else:
            driver_factor = 1.0
            
        # Driving history factor
        history_factors = {
            'clean': 1.0,
            'minor': 1.25,
            'major': 1.8
        }
        history_factor = history_factors[form.driving_history.data]
        
        # Coverage factor
        coverage_factors = {
            'liability': 1.0,
            'collision': 1.4,
            'comprehensive': 1.8
        }
        coverage_factor = coverage_factors[form.coverage_type.data]
        
        # Deductible factor
        deductible_factors = {
            '500': 1.2,
            '1000': 1.0,
            '2500': 0.8
        }
        deductible_factor = deductible_factors[form.deductible.data]
        
        # Calculate final premium
        estimated_premium = (base_premium * age_factor * driver_factor * 
                           history_factor * coverage_factor * deductible_factor)
        
        # Round to 2 decimal places
        estimated_premium = round(estimated_premium, 2)
        
        flash('Premium calculated successfully!', 'success')
    
    return render_template('calculators/auto.html', form=form, estimated_premium=estimated_premium)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@socketio.on('connect')
def handle_connect():
    emit('response', {'data': 'Connected to chat server'})

@socketio.on('send_message')
def handle_message(data):
    try:
        message = models.ChatMessage(
            user_id=current_user.id if current_user.is_authenticated else None,
            content=data['message'],
            chat_session=data.get('session_id', 'default'),
            is_user_message=True
        )
        db.session.add(message)
        db.session.commit()
        
        # Emit the message back to all clients with customization options
        emit('new_message', {
            'message': message.content,
            'timestamp': message.created_at.strftime('%-I:%M %p').lower() + ' est',
            'is_user': True,
            'options': {
                'theme': 'modern',
                'type': ''  # Can be info, warning, success
            }
        }, broadcast=True)
        
        # Simulate support response after a brief delay
        socketio.sleep(1)
        support_message = "Thank you for contacting Prime Insurance Services. How can we assist you with your insurance needs today? Our team typically responds within a few minutes during business hours (9 AM - 5 PM EST)."
        support_chat = models.ChatMessage(
            user_id=current_user.id if current_user.is_authenticated else None,
            content=support_message,
            chat_session=data.get('session_id', 'default'),
            is_user_message=False
        )
        db.session.add(support_chat)
        db.session.commit()
        
        # Emit support response to all clients
        emit('new_message', {
            'message': support_message,
            'timestamp': datetime.now().strftime('%-I:%M %p').lower() + ' est',
            'is_user': False
        }, broadcast=True)
    except Exception as e:
        print(f"Error handling message: {str(e)}")
        db.session.rollback()

@app.route('/chat/history')
@login_required
def chat_history():
    messages = models.ChatMessage.query.filter_by(
        user_id=current_user.id
    ).order_by(models.ChatMessage.created_at.desc()).limit(50).all()
    
    return jsonify([{
        'content': msg.content,
        'timestamp': msg.created_at.strftime('%-I:%M %p').lower() + ' est',
        'is_user': msg.is_user_message
    } for msg in messages])


# Blog routes
@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(published=True).order_by(
        BlogPost.created_at.desc()
    ).paginate(page=page, per_page=10, error_out=False)
    return render_template('blog/index.html', posts=posts)

@app.route('/blog/<string:slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template('blog/post.html', post=post)


@app.route('/blog/<string:slug>/like', methods=['POST'])
@login_required
def like_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    existing_like = PostLike.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        action = 'unliked'
    else:
        like = PostLike(user_id=current_user.id, post_id=post.id)
        db.session.add(like)
        action = 'liked'
    
    db.session.commit()
    return jsonify({
        'success': True,
        'action': action,
        'likes_count': post.likes.count()
    })

@app.route('/blog/<string:slug>/save', methods=['POST'])
@login_required
def save_post(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    existing_save = SavedPost.query.filter_by(user_id=current_user.id, post_id=post.id).first()
    
    if existing_save:
        db.session.delete(existing_save)
        action = 'unsaved'
    else:
        save = SavedPost(user_id=current_user.id, post_id=post.id)
        db.session.add(save)
        action = 'saved'
    
    db.session.commit()
    return jsonify({
        'success': True,
        'action': action
    })
    return redirect(url_for('blog_post', slug=slug))

@app.route('/blog/create', methods=['GET', 'POST'])
@login_required
def create_blog_post():
    if not current_user.is_authenticated or not current_user.is_editor():
        flash('You must be an editor to create blog posts.', 'error')
        return redirect(url_for('blog'))
    
    form = BlogPostForm()
    if form.validate_on_submit():
        slug = form.title.data.lower().replace(' ', '-')
        post = BlogPost(
            title=form.title.data,
            slug=slug,
            content=form.content.data,
            summary=form.summary.data,
            category=form.category.data,
            featured_image=form.featured_image.data,
            meta_description=form.meta_description.data,
            meta_keywords=form.meta_keywords.data,
            published=form.published.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Blog post created successfully!', 'success')
        return redirect(url_for('blog_post', slug=post.slug))
    
    return render_template('blog/create.html', form=form)

@app.route('/blog/<string:slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_blog_post(slug):
    if not current_user.is_editor():
        flash('You must be an editor to edit blog posts.', 'error')
        return redirect(url_for('blog'))
        
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    
    if post.author != current_user:
        flash('You do not have permission to edit this post.', 'error')
        return redirect(url_for('blog'))
    
    form = BlogPostForm(obj=post)
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.summary = form.summary.data
        post.category = form.category.data
        post.featured_image = form.featured_image.data
        post.meta_description = form.meta_description.data
        post.meta_keywords = form.meta_keywords.data
        post.published = form.published.data
        db.session.commit()
        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('blog_post', slug=post.slug))
    
    return render_template('blog/edit.html', form=form, post=post)

@app.route('/admin/users')
@login_required
def manage_users():
    if not current_user.is_editor():
        flash('You must be an editor to access this page.', 'error')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('auth/manage_users.html', users=users)

@app.route('/admin/users/<int:user_id>/promote', methods=['POST'])
@login_required
def promote_to_editor(user_id):
    if not current_user.is_editor():
        flash('You must be an editor to promote users.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    if user.role == 'editor':
        flash('User is already an editor.', 'info')
    else:
        user.role = 'editor'
        db.session.commit()
        flash(f'Successfully promoted {user.username} to editor.', 'success')
    
    return redirect(url_for('manage_users'))

with app.app_context():
    import models
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)