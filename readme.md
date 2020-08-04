How to run a website instance

1. create a .env file with:

FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY = [STRING]
ADMIN_PASSWORD = [STRING]

2. run 'flask db init'

3. run 'flask db migrate -m "initialise database"'

2. run 'flask db upgrade'