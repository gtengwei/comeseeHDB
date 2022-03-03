## To create the app and database

from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
db = SQLAlchemy()
DB_NAME = "database.db"

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


#def create_app():
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

# To send reset password email to user
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lattadcane@gmail.com'
app.config['MAIL_PASSWORD'] = 'Lattadcane123'

mail=Mail(app)

db.init_app(app)

# Insert Blueprint here
from .views import views
from .auth import auth
from .user import user
from .HDBFlatUI import flat

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(user, url_prefix='/')
app.register_blueprint(flat, url_prefix='/')

from .models import User, Review, HDBFlat

create_database(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    ## Looks for primary key in database
    return User.query.get(int(id))

    #return app



