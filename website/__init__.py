# To create the app and database
from venv import create
from flask import Flask, Blueprint
from os import path
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from .models import *

DB_NAME = "database.db"
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()


def create_database(app):

    if not path.exists('website/' + DB_NAME):
        create_Flat_table()
        db.create_all()
        print('Created Database!')
    return


# def create_app():
app = Flask(__name__)


app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
create_database(app)

# To send reset password email to user
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cz3002.clutch@gmail.com'
app.config['MAIL_PASSWORD'] = 'zmexsqegkpavaovi'

moment = Moment(app)
login_manager.init_app(app)
db.init_app(app)
mail.init_app(app)

# Insert Blueprint here
from .user import user
from .auth import auth
from .views import views
app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(user, url_prefix='/')

# return app


@login_manager.user_loader
def load_user(id):
    # Looks for primary key in database
    return User.query.get(int(id))

    # return app