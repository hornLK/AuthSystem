from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import config

mail = Mail()
moment = Moment()
db = SQLAlchemy()
api = Api()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    CORS(app,resources=r'/*')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    api.init_app(app)

    from .api_1_0 import api as api_blueprint
    app.register_blueprint(api_blueprint,
                          url_prefix='/apiv1')

    return app
