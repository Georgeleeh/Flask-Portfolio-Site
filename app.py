from app import app
from app.models import Entry, Tag

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Entry': Entry, 'Tag': Tag}