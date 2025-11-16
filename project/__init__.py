'''
Fix:
# python -m pip install --upgrade pip
# python -m pip install --no-use-pep517 flask-bcrypt
'''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from project.CZWebService import CZWebService
import os

app = Flask(__name__)

# Load configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-secret-key-for-development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE']=90

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['KEY_PATH'] = "./project/static/data/key"
#app.config['KEY_PATH'] = "D:\dev\paydee.devop\mpidevbox\project\static\data\key"
app.config['MPI_URL'] = os.environ.get('MPI_URL', 'https://devlink2.paydee.co/mpi')

app.config['MERCHANT_ID'] = os.environ.get('MERCHANT_ID', '000000000000033')
app.config['UPLOAD_FOLDER'] = "static/data/upload"

app.config['TEST1_MID'] = "000000000000033"
app.config['TEST2_MID'] = "000000000000052"

app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 465))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'false').lower() in ('true', '1', 't')
app.config['MAIL_USE_SSL'] = os.environ.get('MAIL_USE_SSL', 'true').lower() in ('true', '1', 't')
app.config['MAIL_DEBUG'] = os.environ.get('MAIL_DEBUG', 'true').lower() in ('true', '1', 't')


app.config['EMAIL_SENDER'] = 'no_reply@paydee.co'
app.config['GOLIVE_TEAM_EMAIL'] = os.environ.get('GOLIVE_TEAM_EMAIL', 'yokesan@paydee.co')
app.config['LOGIN_LINK'] = os.environ.get('LOGIN_LINK', 'https://developers.paydee.co/login')
app.config['CZ_WEBSERVICE_URL'] = os.environ.get('CZ_WEBSERVICE_URL', 'https://devlink.paydee.co')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
czws = CZWebService(base_url=app.config['CZ_WEBSERVICE_URL'])

from project import routes, routes_mock, routes_test
