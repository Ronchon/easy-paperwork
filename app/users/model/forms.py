from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField

class LoginForm(FlaskForm):
	loginWithGoogle = SubmitField(label='Login with Google')

class PasswordForm(FlaskForm):
	password = PasswordField(label='Password')
	submit = SubmitField(label='Submit')