import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '73218d6a-6586-420c-870e-46ee72b67634'
    SECRET_API_KEY = os.environ.get('SECRET_API_KEY') or '0a37511d-be7d-4fdd-ab17-28b6c659d763'
    AUTH_API_RANGE = 20
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASKY_MAIL_SUBJECT_PREFIX = '[AuthSystem]'
    FLASKY_MAIL_SENDER = 'AuthSystem Admin <admin>'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI ='sqlite:///' + os.path.join(basedir,'devdata.sqlite')

    AUTHSYSTEM_MAIL_SUBJECT_PREFIX = '[DevAuthSystem]'
    FLASKY_ADMIN = 'liukaiqiang@miaozhen.com'
    AUTHSYSTEM_MAIL_SENDER = 'AuthSystem Admin <liukaiqiang@miaozhen.com>'
    AUTHSYSTEM_MESSAGE_PAGE = 20
    MAIL_SERVER = 'smtp.miaozhen.com'
    MAIL_PORT = 25
    MAIL_USER_TLS = False
    MAIL_USERNAME = '***'
    MAIL_PASSWORD = '***'

config = {
    'development':DevelopmentConfig,
    'default':DevelopmentConfig
}
