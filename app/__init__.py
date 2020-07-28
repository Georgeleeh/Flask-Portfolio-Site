from flask import Flask
from config import Config

from micawber import bootstrap_basic
from micawber.cache import Cache as OEmbedCache

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)

# DB
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

# Configure micawber with the default OEmbed providers (YouTube, Flickr, etc).
# We'll use a simple in-memory cache so that multiple requests for the same
# video don't require multiple network requests.
oembed_providers = bootstrap_basic(OEmbedCache())

from app import routes