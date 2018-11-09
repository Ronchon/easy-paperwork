import os
basedir = os.path.abspath(os.path.dirname(__file__))

#General configuration
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
QUEUE_FOLDER = './storage/queue/'
ARCHIVE_FOLDER= './storage/archive/'

#Session configuration
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = './storage/sessions/'

#Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'easypaperwork.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
