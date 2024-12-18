from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, EmailField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired(), Length(max=256)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    message = TextAreaField('Message', validators=[DataRequired(), Length(min=10, max=1000)])

class QuoteForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    insurance_type = SelectField('Insurance Type', 
        choices=[
            ('auto', 'Auto Insurance'),
            ('home', 'Home Insurance'),
            ('life', 'Life Insurance'),
            ('umbrella', 'Umbrella Insurance'),
            ('business', 'Business Insurance')
        ],
        validators=[DataRequired()])
    details = TextAreaField('Additional Details', validators=[Length(max=1000)])

class AutoInsuranceCalculatorForm(FlaskForm):
    vehicle_year = SelectField('Vehicle Year', 
        choices=[(str(year), str(year)) for year in range(2024, 1990, -1)],
        validators=[DataRequired()])
    vehicle_make = StringField('Vehicle Make', validators=[DataRequired(), Length(max=50)])
    vehicle_model = StringField('Vehicle Model', validators=[DataRequired(), Length(max=50)])
    driver_age = SelectField('Driver Age',
        choices=[(str(age), str(age)) for age in range(16, 91)],
        validators=[DataRequired()])
    driving_history = SelectField('Driving History',
        choices=[
            ('clean', 'Clean Record'),
            ('minor', 'Minor Violations'),
            ('major', 'Major Violations')
        ],
        validators=[DataRequired()])
    coverage_type = SelectField('Coverage Type',
        choices=[
            ('liability', 'Liability Only'),
            ('collision', 'Collision'),
            ('comprehensive', 'Comprehensive')
        ],
        validators=[DataRequired()])
    deductible = SelectField('Deductible Amount',
        choices=[
            ('500', '$500'),
            ('1000', '$1,000'),
            ('2500', '$2,500')
        ],
        validators=[DataRequired()])
    submit = SubmitField('Calculate Premium')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    address = StringField('Address', validators=[DataRequired(), Length(max=256)])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Save Changes')

    def __init__(self, original_email=None, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')


class BlogPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    summary = TextAreaField('Summary', validators=[Length(max=300)])
    category = SelectField('Category', 
        choices=[
            ('auto', 'Auto Insurance'),
            ('home', 'Home Insurance'),
            ('life', 'Life Insurance'),
            ('business', 'Business Insurance'),
            ('general', 'General Insurance Tips')
        ],
        validators=[DataRequired()])
    featured_image = StringField('Featured Image URL', validators=[Length(max=200)])
    meta_description = TextAreaField('Meta Description', validators=[Length(max=160)])
    meta_keywords = StringField('Meta Keywords', validators=[Length(max=200)])
    published = BooleanField('Publish')
    submit = SubmitField('Save Post')


