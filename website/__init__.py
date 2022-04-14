## To create the app and database

from venv import create
from flask import Flask, Blueprint
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
import mysql.connector
import pymysql
from .models import *

DB_NAME = "database.db"
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()

def create_database(app):

    if not path.exists('website/' + DB_NAME):
        create_Flat_table()
        db.create_all(app=app)
        print('Created Database!')

    '''
    create_mysql_database()
    conn = pymysql.connect(
        host="localhost",
        user="root",
        passwd="Clutch123!",
        database = "mysql_database"
    )
    cursor = conn.cursor()
    cursor.execute("SET GLOBAL FOREIGN_KEY_CHECKS = 0")

    ## MUST CREATE FLAT TABLE FIRST BEFORE OTHER TABLES
    ## IF NOT WILL RESULT IN ERRORS
    if not cursor.execute("SHOW TABLES LIKE 'review'"):
        db.create_all(app=app)
        print('Created Database!')
    '''
    return




def create_app():
    app = Flask(__name__)
    

    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Clutch123!@localhost/mysql_database?charset=utf8'
    create_database(app)
    # To send reset password email to user
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'cz2006.clutch@gmail.com'
    app.config['MAIL_PASSWORD'] = 'Clutch123!'

    moment = Moment(app)
    login_manager.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    
    # Insert Blueprint here
    from .views import views
    from .auth import auth
    from .user import user

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(user, url_prefix='/')

    return app

    


@login_manager.user_loader
def load_user(id):
    ## Looks for primary key in database
    return User.query.get(int(id))

    #return app



