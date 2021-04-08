import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY ='1to1anyherzt'
    SQLALCHEMY_DATABASE_URI = 'mysql://uolcg8z6xjblwsuq:DlBzAEijVaY886OcOjjZ@b5ick1tqoytd9ldsooyn-mysql.services.clever-cloud.com:3306/b5ick1tqoytd9ldsooyn'
    
    #SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
