import os
import re
import functools

from app import app, db
from app.models import Entry

from werkzeug.utils import secure_filename
from flask import Flask, flash, Markup, redirect, render_template, request, Response, session, url_for


def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

@app.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        # TODO: If using a one-way hash, you would also hash the user-submitted
        # password and do the comparison on the hashed versions.
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')

@app.route('/')
def index():
    query = Entry.query.filter(Entry.published.is_(True)).order_by(Entry.timestamp.desc())
    return render_template('index.html', object_list=query)

def _create_or_edit(entry, template):
    if request.method == 'POST':
        entry.title = request.form.get('title') or ''
        entry.content = request.form.get('content') or ''
        entry.published = True if request.form.get('published') == 'y' else False
        entry.slug = re.sub(r'[^\w]+', '-', entry.title.lower()).strip('-')
        if not (entry.title and entry.content):
            flash('Title and Content are required.', 'danger')
        else:

            db.session.add(entry)

            db.session.commit()

            flash('Entry saved successfully.', 'success')
            if entry.published:
                return redirect(url_for('detail', slug=entry.slug))
            else:
                return redirect(url_for('edit', slug=entry.slug))

    return render_template(template, entry=entry)

@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return _create_or_edit(Entry(title='', content=''), 'create.html')

@app.route('/drafts/')
@login_required
def drafts():
    query = Entry.query.filter(Entry.published.is_(False)).order_by(Entry.timestamp.desc())
    return render_template('index.html', object_list=query)

@app.route('/<slug>/')
def detail(slug):
    entry = Entry.query.filter(Entry.slug.is_(slug)).first()
    return render_template('detail.html', entry=entry)

@app.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = Entry.query.filter(Entry.slug.is_(slug)).first()
    return _create_or_edit(entry, 'edit.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload-image/', methods=['GET', 'POST'])
@login_required
def upload_image():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part.', 'danger')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file,', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Image uploaded successfully.', 'success')
            return redirect(url_for('index'))
    return render_template('upload_image.html')


@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404