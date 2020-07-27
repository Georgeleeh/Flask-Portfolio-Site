from app import app, database
from app.models import Entry, FTSEntry

@app.shell_context_processor
def make_shell_context():
    return {'database': database, 'Entry': Entry, 'FTSEntry': FTSEntry}