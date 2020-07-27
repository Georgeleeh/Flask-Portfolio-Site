import os

class Config(object):
    # The secret key is used internally by Flask to encrypt session data stored in cookies
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'wouldnt-you-like-to-know-weatherboy'

    APP_DIR = os.path.dirname(os.path.realpath(__file__))

    # The playhouse.flask_utils.FlaskDB object accepts database URL configuration.
    DATABASE = 'sqliteext:///%s' % os.path.join(APP_DIR, 'blog.db')

    DEBUG = True

    # This is used by micawber, which will attempt to generate rich media
    # embedded objects with maxwidth=800.
    SITE_WIDTH = 800