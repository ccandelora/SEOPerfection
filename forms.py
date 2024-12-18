from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, EmailField, PasswordField, SubmitField
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
