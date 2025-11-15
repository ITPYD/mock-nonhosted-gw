'''
Fix (9/7/2021) : pip install pymsql

Cheat Sheet:

Go to terminal:
>> from project import db
>> from project.models import User
>> db.create_all()
>> User.query.all()


Delete db
>> db.drop_all()

Check a user
>> user = User.query.first()
>> user.id
>> user.password
>> user.email

Filter user
>> user = User.query.filter_by(id=1).first()

Add new user
>> user = User(username='YokeSan', email = 'yokesan@email.com', password='password')
>> db.session.add(user)
>> db.session.commit()
>> User.query.all()
'''

from datetime import datetime
from flask import url_for, redirect
from flask_login import UserMixin
from project import db, login_manager

# ---------------------
# Login Implementation
# ---------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    # do stuff
    #return f'Unauthorized Access. Please register to access this page'
    return redirect(url_for('register'))

class Audit(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, nullable=False)
    date_create  = db.Column(db.DateTime, default = datetime.utcnow())  
    activity = db.Column(db.String(2048), nullable = False)

    def __repr__(self):
        return f'{self.user_id}: {self.date_create.strftime("%d/%m/%Y, %H:%M:%S")  : {self.activity} }'    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False)
    email  = db.Column(db.String(120), unique = True, nullable = False)
    image_file  = db.Column(db.String(20), nullable = False, default = 'default.jpg')
    password = db.Column(db.String(60), nullable = False)
    date_create  = db.Column(db.DateTime, default = datetime.utcnow())
    is_admin = db.Column(db.String(4), nullable = False, default = 'N')
    organization = db.Column(db.String(256), unique = False, default = '')
    is_reset = db.Column(db.Integer, default = "0")

    def __repr__(self):
        return f'{self.username} : {self.email} : {self.is_admin} : {self.date_create.strftime("%d/%m/%Y, %H:%M:%S")} : {self.organization}'

# ---------------------
# Redirect Proxy Implementation
# ---------------------

class RedirectUrlProxy(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user = db.Column(db.Integer, primary_key = True)
    key = db.Column(db.String(32), nullable = False)
    mid = db.Column(db.String(48), primary_key = True)
    url = db.Column(db.String(256), nullable = False) 
    status_url = db.Column(db.String(256), nullable = False) 
    enable = db.Column(db.String(4), nullable = False, default = 'F')

    def __repr__(self):
        return f'{self.user} : {self.key} : {self.mid} : {self.url} : {self.enable}'  

# ---------------------
# MAC Key Implementation
# ---------------------

class MacKey(db.Model):
    mid = db.Column(db.String, primary_key = True)
    tid = db.Column(db.String(124), primary_key = True)
    private = db.Column(db.String(4256), nullable = False)
    public = db.Column(db.String(4256), nullable = False) 

    def __repr__(self):
        return f'{self.mid} : {self.tid} '  

# ---------------------
# Go Live
# ---------------------

class LiveEnv(db.Model):
    user = db.Column(db.Integer, primary_key = True)
    #user = db.Column(db.Integer)
    mid = db.Column(db.String(48))
    url = db.Column(db.String(256)) 
    status_url = db.Column(db.String(256)) 
    public = db.Column(db.String(4256)) 
    enable = db.Column(db.String(4), nullable = False, default = 'F')
    organization = db.Column(db.String(256), default='')

    def __repr__(self):
        return f' USER:{self.user} : PUBLIC:{self.public} : MID:{self.mid} : URL:{self.url} : STATUS:{self.status_url} : ORGANIZATION:{self.organization} : ENABLE:{self.enable}'     

class MacValidateModel(db.Model):
    user = db.Column(db.Integer, primary_key = True)
    public_rsa = db.Column(db.String(4256), nullable = True) 
    private_rsa = db.Column(db.String(4256), nullable = True) 
    data = db.Column(db.String(2048), nullable = True) 
    mac = db.Column(db.String(4256), nullable = True) 

    def __repr__(self):
        return f' USER:{self.user} PUBLIC:{self.public_rsa} PRIVATE:{self.private_rsa}'
