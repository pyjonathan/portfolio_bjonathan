#EX_Liniks/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from settings import DB_PASSWORD

app = Flask(__name__)

app.config['SECRET_KEY'] = 'my_secret'  #Use a real key in production

#############################
### DATABASE SETUP ##########
#############################
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/"
app.config['SQLALCHEMY_BINDS'] = {'portfolio_mtg': f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/portfolio_mtg",
                                  'portfolio_rmet': f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/portfolio_rmet",
                                  'portfolio_users': f"postgresql://postgres:{DB_PASSWORD}@localhost:5432/portfolio_users"}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

db = SQLAlchemy(app)
Migrate(app,db)

#############################
### LOGIN CONFIGS ###########
#############################

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "user_management_portfolio.login"

###########################
### BLUEPRINT CONFIGS #####
###########################

from portfolio_bjonathan.user_management.views import user_management_portfolio
from portfolio_bjonathan.app_management.views import app_management
from portfolio_bjonathan.remodel_et.views import remodel_et
from portfolio_bjonathan.mtg.views import mtg

app.register_blueprint(user_management_portfolio)
app.register_blueprint(app_management)
app.register_blueprint(remodel_et)
app.register_blueprint(mtg)


