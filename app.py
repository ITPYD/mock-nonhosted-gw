'''
Deploy to heroku
git init
git add .
heroku git:remote -a mpidevbox
git commit -m "heroku deploy"
pip freeze > requirement
echo "web: gunicorn wsgi:app" > Profile
git push heroku master

Username:	ba35104d7b3d3f
Password:	b52ef3e2 (Reset)
mysql://ba35104d7b3d3f:b52ef3e2@us-cdbr-east-04.cleardb.com/heroku_13b52dd7911dfd6?reconnect=true

Troubleshoot heroku issue
https://realpython.com/flask-by-example-part-1-project-setup/

Note:
$ heroku buildpacks
$ heroku buildpacks:add heroku/python 
'''

from project import app
from project.models import User
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

if __name__ == '__main__':
    app.run(debug=True)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)    

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

