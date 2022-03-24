## To create the app and database

from io import open_code
from venv import create
from db import open_connection
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
import pymysql

from website.test import create_mysql_database

app = Flask(__name__)
db = SQLAlchemy()
DB_NAME = "database.db"

def create_database(app):

    #if not path.exists('website/' + DB_NAME):
    #    create_Flat_table()
    #    db.create_all(app=app)
    #    print('Created Database!')

    # create_mysql_database()
    conn = open_connection()
    # conn = pymysql.connect(
    #     host="localhost",
    #     user="root",
    #     passwd="Clutch123!",
    #     database = "mysql_database"
    # )
    cursor = conn.cursor()
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    ## MUST CREATE FLAT TABLE FIRST BEFORE OTHER TABLES
    ## IF NOT WILL RESULT IN ERRORS
    if not cursor.execute("SHOW TABLES LIKE 'review'"):
        db.create_all(app=app)
        print('Created Database!')
#def create_app():
app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
#app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Clutch123!@/mysql_database?unix_socket=/cloudsql/comesee-hdb:asia-southeast1:comeseehdb-database'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Clutch123!@localhost/mysql_database?charset=utf8'

# To send reset password email to user
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'cz2006.clutch@gmail.com'
app.config['MAIL_PASSWORD'] = 'Clutch123!'

mail=Mail(app)
moment = Moment(app)

db.init_app(app)
from .views import views
from .auth import auth
from .user import user

app.register_blueprint(views, url_prefix='/')
app.register_blueprint(auth, url_prefix='/')
app.register_blueprint(user, url_prefix='/')

from .models import *


create_database(app)
#os.chdir("website")
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    ## Looks for primary key in database
    return User.query.get(int(id))

    #return app



