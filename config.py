import os
basedir = os.path.abspath(os.path.dirname(__file__))

#General configuration
WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
QUEUE_FOLDER = 'C:/Users/ablanchin/Documents/Perso/Dev/easy-paperwork/storage/queue/'
ARCHIVE_FOLDER= 'C:/Users/ablanchin/Documents/Perso/Dev/easy-paperwork/storage/archive/'
PWD_HASH = 'pbkdf2:sha256:50000$XcEPxGsZ$65753ebe942979a8be77caf2f10988be05f3616381a754ea499ac3501f1682e9'

#Session configuration
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = 'C:/Users/ablanchin/Documents/Perso/Dev/easy-paperwork/storage/sessions/'

#Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'easypaperwork.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False