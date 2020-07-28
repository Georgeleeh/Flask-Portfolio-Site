import re
from datetime import datetime

from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import parse_html

from flask import Markup

from app import app, db, oembed_providers

from sqlalchemy import UniqueConstraint


class Entry(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    content=db.Column(db.Text,nullable=False)
    feature_image=db.Column(db.String,nullable=False)
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(50),nullable=False,unique=True)
    published = db.Column(db.Boolean,nullable=False)

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
            'slug': re.sub(r'[^\w]+', '-', self.title.lower()).strip('-'),
            'published': self.published
        }
