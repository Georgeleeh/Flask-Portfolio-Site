import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # The secret key is used internally by Flask to encrypt session data stored in cookies
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'wouldnt-you-like-to-know-weatherboy'

    APP_DIR = os.path.dirname(os.path.realpath(__file__))

    # DB
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = True

    # This is used by micawber, which will attempt to generate rich media
    # embedded objects with maxwidth=800.
    SITE_WIDTH = 800

    # File Upload
    UPLOAD_FOLDER = 'app/static/images/uploads/'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif', 'gif'}

    # site map
    SITEMAP_INCLUDE_RULES_WITHOUT_PARAMS=True