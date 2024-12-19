from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    phone = StringField('Phone Number')
    address = StringField('Address')
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number')
    address = StringField('Address')
    submit = SubmitField('Save Changes')

    def __init__(self, original_email=None, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class QuoteForm(FlaskForm):
    insurance_type = SelectField('Insurance Type', 
        choices=[
            ('auto', 'Auto Insurance'),
            ('home', 'Home Insurance'),
            ('life', 'Life Insurance'),
            ('business', 'Business Insurance')
        ],
        validators=[DataRequired()]
    )
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired()])
    details = TextAreaField('Additional Details')
    submit = SubmitField('Request Quote')

class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    summary = TextAreaField('Summary', validators=[DataRequired()])
    category = SelectField('Category', 
        choices=[
            ('insurance', 'Insurance'),
            ('finance', 'Finance'),
            ('lifestyle', 'Lifestyle')
        ]
    )
    featured_image = StringField('Featured Image URL')
    meta_description = TextAreaField('Meta Description')
    meta_keywords = StringField('Meta Keywords')
    published = BooleanField('Publish')
    submit = SubmitField('Save Post')

class AutoInsuranceCalculatorForm(FlaskForm):
    vehicle_year = StringField('Vehicle Year', validators=[DataRequired()])
    driver_age = StringField('Driver Age', validators=[DataRequired()])
    driving_history = SelectField('Driving History', 
        choices=[
            ('clean', 'Clean Record'),
            ('minor', 'Minor Violations'),
            ('major', 'Major Violations')
        ],
        validators=[DataRequired()]
    )
    coverage_type = SelectField('Coverage Type',
        choices=[
            ('liability', 'Liability Only'),
            ('collision', 'Collision'),
            ('comprehensive', 'Comprehensive')
        ],
        validators=[DataRequired()]
    )
    deductible = SelectField('Deductible',
        choices=[
            ('500', '$500'),
            ('1000', '$1000'),
            ('2500', '$2500')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Calculate Premium')


