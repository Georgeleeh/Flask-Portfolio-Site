from app import app
from app.models import Entry

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Entry': Entry}