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


# ---------------------
# Login Implementation
# ---------------------



# ---------------------
# Redirect Proxy Implementation
# ---------------------



# ---------------------
# MAC Key Implementation
# ---------------------



# ---------------------
# Go Live
# ---------------------

 
