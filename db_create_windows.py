#!venv/Scripts/python
from app import app
from config import SQLALCHEMY_DATABASE_URI
from app import db
import os.path
db.create_all()
