from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email

class RegisterForm(FlaskForm):
	username = StringField('Username', \
		validators=[DataRequired(), Length(min=5, max=25)])
	email = StringField('Email', \
		validators=[DataRequired(), Email(), Length(min=5, max=40)])
	password = PasswordField('Password', \
		validators=[DataRequired(), Length(min=5, max=40)])
	confirm = PasswordField('Repeat Password', \
		validators=[DataRequired(), EqualTo('password', message='Passwords must match')])

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])