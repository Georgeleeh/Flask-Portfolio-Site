import os
import re
import functools
from datetime import datetime
from pathlib import Path

from app import app, db
from app.models import Entry, Tag

from werkzeug.utils import secure_filename
from flask import Flask, flash, Markup, redirect, render_template, request, Response, session, url_for, send_from_directory


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
    featured_entries = Entry.query.filter(Entry.featured.is_(True)).order_by(Entry.timestamp.desc()).all()[:3]

    if len(featured_entries) > 0:
        return render_template('index.html', featured=featured_entries, len=len(featured_entries))
    else:
        return render_template('index.html')

@app.route('/blog/')
def blog():
    search_query = request.args.get('q')
    if search_query:
        found_tag = Tag.query.filter(Tag.name.like(search_query)).first()
        if found_tag is None:
            return render_template('blog.html')
        found_entries = found_tag.entries_associated.all()
        if session.get('logged_in'):
            return render_template('blog.html', entry_list=found_entries)
        else:
            found_published_entries = [entry for entry in found_entries if entry.published]
            return render_template('blog.html', entry_list=found_published_entries)

    query = Entry.query.filter(Entry.published.is_(True)).order_by(Entry.timestamp.desc())
    return render_template('blog.html', entry_list=query)

@app.route('/blog/tags/<tag>')
def tags(tag):
    found_tag = Tag.query.filter(Tag.name.like(tag)).first()

    if found_tag is None:
        return render_template('blog.html')

    found_entries = found_tag.entries_associated.all()

    if session.get('logged_in'):
        return render_template('blog.html', entry_list=found_entries)
    else:
        found_published_entries = [entry for entry in found_entries if entry.published]
        return render_template('blog.html', entry_list=found_published_entries)


def _create_or_edit(entry, template):
    if request.method == 'POST':
        button_value = request.form.get('button')
        if button_value == 'save':
            entry.title = request.form.get('title') or ''
            entry.one_liner = request.form.get('one_liner') or ''
            entry.feature_image = request.form.get('feature_image') or ''
            entry.content = request.form.get('content') or ''
            entry.published = True if request.form.get('published') == 'y' else False
            entry.featured = True if request.form.get('featured') == 'y' else False
            entry.slug = re.sub(r'[^\w]+', '-', entry.title.lower()).strip('-')

            if request.form.get('created') != "":
                entry.timestamp = datetime.strptime(request.form.get('created'), '%d/%m/%Y at %H:%M')

            for tag in entry.tags:
                if entry in tag.entries_associated.all():
                    tag.entries_associated.remove(entry)

            for tag in request.form.get('tags').split(','):
                # clean string to avoid accidental duplication
                tag = tag.strip()
                if tag == '':
                    pass
                else:
                    # check if tag exists
                    present_tag=Tag.query.filter_by(name=tag).first()
                    if(present_tag):
                        if entry not in present_tag.entries_associated.all():
                            present_tag.entries_associated.append(entry)
                    else:
                        new_tag=Tag(name=tag)
                        new_tag.entries_associated.append(entry)
                        db.session.add(new_tag)

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

        elif button_value == 'delete':
            for tag in entry.tags:
                if entry in tag.entries_associated.all():
                    tag.entries_associated.remove(entry)
            
            db.session.delete(entry)
            db.session.commit()
            flash('Entry deleted.', 'danger')
            return redirect(url_for('index'))


    return render_template(template, entry=entry, tags=[tag.name for tag in entry.tags], images=os.listdir(app.config['UPLOAD_FOLDER']))

@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return _create_or_edit(Entry(title='', content=''), 'create.html')

@app.route('/drafts/')
@login_required
def drafts():
    query = Entry.query.filter(Entry.published.is_(False)).order_by(Entry.timestamp.desc())
    return render_template('blog.html', entry_list=query)

@app.route('/<slug>/')
def detail(slug):
    entry = Entry.query.filter(Entry.slug.is_(slug)).first()
    return render_template('detail.html', entry=entry, tags=[tag.name for tag in entry.tags])

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
            # check if file exists
            if file.filename in [name.name for name in Path(app.config['UPLOAD_FOLDER']).iterdir()]:
                flash('Filename exists,', 'danger')
                return redirect(request.url)
            else:
                
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Image uploaded successfully.', 'success')
                return redirect(url_for('index'))
    return render_template('upload_image.html')

@app.route('/image-gallery/')
@login_required
def image_gallery():
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('image_gallery.html', images=images)


@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])