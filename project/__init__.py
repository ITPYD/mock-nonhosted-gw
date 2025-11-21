'''
Fix:
# python -m pip install --upgrade pip
# python -m pip install --no-use-pep517 flask-bcrypt
'''
from flask import Flask
from flask_mail import Mail

import os

app = Flask(__name__)

# Load configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'a-default-secret-key-for-development')


app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['KEY_PATH'] = "./project/static/data/key"
#app.config['KEY_PATH'] = "D:\dev\paydee.devop\mpidevbox\project\static\data\key"

app.config['MPIGW_URL'] = os.environ.get('MPI_URL', 'https://devlinkv2.paydee.co/mpigw')
app.config['MPI_URL'] = os.environ.get('MPI_URL', 'https://devlinkv2.paydee.co/mpi')
app.config['MPI_URL2'] = os.environ.get('MPI_UR2L', 'https://devlinkv2.paydee.co/')
#app.config['MPI_URL'] = 'https://pag-v3.onrender.com/'

app.config['REMOTE_MPI_DOMAIN'] = "https://devlink.paydee.co/mpi"
app.config["EXTERNAL_INIT_URL"] = 'https://devlinkv2.paydee.co/mpigw'

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



mail = Mail(app)

from project import routes, routes_mock, routes_test, models
