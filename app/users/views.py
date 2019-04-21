from flask import Blueprint
from app.users.model.login import LoginView, PasswordView
from app import directory

#Blueprint for users
users_bp = Blueprint('users', __name__, template_folder='templates')

#Login route 
users_bp.add_url_rule(
	directory.Login.url, 
	view_func=LoginView.as_view(directory.Login.view))

#Password route
users_bp.add_url_rule(
	directory.Password.url, 
	view_func=PasswordView.as_view(directory.Password.view))