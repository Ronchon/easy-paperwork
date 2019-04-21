from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
Session(app)

from app import database
from app import directory
from .users.views import users_bp
from .documents.views import documents_bp
 
# register the blueprints
app.register_blueprint(users_bp)
app.register_blueprint(documents_bp)