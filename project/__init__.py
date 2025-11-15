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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisfirstflaskapp'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://devusr:hello123@127.0.0.1:3306/devboxdb'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://epiz_32034111:YN8OIc798ESVt@sql308.epizy.com/epiz_32034111_User'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://yOknKizheA:oTZYWPHT1I@remotemysql.com/yOknKizheA'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ba35104d7b3d3f:b52ef3e2@us-cdbr-east-04.cleardb.com/heroku_13b52dd7911dfd6'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE']=90

app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['KEY_PATH'] = "./project/static/data/key"
#app.config['KEY_PATH'] = "D:\dev\paydee.devop\mpidevbox\project\static\data\key"
#app.config['MPI_URL'] = "https://mpijumpbox.herokuapp.com/mpi"
#app.config['MPI_URL'] = "https://mpidevbox.herokuapp.com/mpi"
app.config['MPI_URL'] = "https://devlink.paydee.co/mpi"
#app.config['MPI_URL'] = "https://link.paydee.co/mpi"

app.config['MERCHANT_ID'] = "000000000000033"
#app.config['MERCHANT_ID'] = "000009600000001"
#app.config['UPLOAD_FOLDER'] = "static\\data\\upload"
app.config['UPLOAD_FOLDER'] = "static/data/upload"

app.config['TEST1_MID'] = "000000000000033"
app.config['TEST2_MID'] = "000000000000052"

#app.config['MAIL_SERVER']='smtp.cloudmta.net'
#app.config['MAIL_PORT'] = 587
#app.config['MAIL_USERNAME'] = '1a62f948c506dea7'
#app.config['MAIL_PASSWORD'] = 'zYccWnJxzy91iebARqqRz1X3'
#app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = False
#app.config['MAIL_DEBUG'] = True

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'roam.chat.email'
app.config['MAIL_PASSWORD'] = 'gpsdzuxokokqvftd'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEBUG'] = True


app.config['EMAIL_SENDER'] = 'no_reply@paydee.co'
app.config['GOLIVE_TEAM_EMAIL'] = 'yokesan@paydee.co'
#app.config['LOGIN_LINK'] = 'http://localhost:5000/login'
#app.config['LOGIN_LINK'] = 'http://mpidevbox.herokuapp.com/login'
#app.config['LOGIN_LINK'] = 'https://mpidevbox-do7t.onrender.com/login'
#app.config['LOGIN_LINK'] = 'https://mpibox.onrender.com/login'
app.config['LOGIN_LINK'] = 'https://developers.paydee.co/login'
app.config['CZ_WEBSERVICE_URL'] = 'https://devlink.paydee.co'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
mail = Mail(app)
czws = CZWebService(base_url=app.config['CZ_WEBSERVICE_URL'])

from project import routes
