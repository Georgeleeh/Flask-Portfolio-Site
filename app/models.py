from datetime import datetime

from micawber import parse_html
from sqlalchemy import UniqueConstraint
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension

from flask import Markup

from app import app, db, oembed_providers


tag_entry = db.Table('tag_entry',
    db.Column('tag_id',db.Integer,db.ForeignKey('tag.id'), primary_key=True),
    db.Column('entry_id', db.Integer,db.ForeignKey('entry.id'),primary_key=True)
)

class Tag(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)

    @property
    def serialize(self):
        return {
        'id': self.id,
        'name': self.name     
        }

class Entry(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    one_liner=db.Column(db.String(50),nullable=False)
    content=db.Column(db.Text,nullable=False)
    feature_image=db.Column(db.String,nullable=True)
    timestamp=db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(50),nullable=False,unique=True)
    published = db.Column(db.Boolean,nullable=False)
    featured = db.Column(db.Boolean,nullable=False)

    tags=db.relationship('Tag',secondary=tag_entry,backref=db.backref('entries_associated',lazy="dynamic"))

    def __repr__(self):
        return f'<Entry {self.title}>'

    @property
    def html_content(self):
        """
        Generate HTML representation of the markdown-formatted blog entry,
        and also convert any media URLs into rich media objects such as video
        players or images.
        """
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=app.config['SITE_WIDTH'])
        return Markup(oembed_content)
    
    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'feature_image': self.feature_image,
            'created_at': self.created_at,
            # Generate a URL-friendly representation of the entry's title.
            'slug': self.slug,
            'published': self.published
        }
