from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, EmailField
from wtforms.validators import DataRequired, Email, Length

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
