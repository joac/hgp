from elixir import *
import datetime
#metadata.bind = "sqlite:///db.sqlite"
#metadata.bind.echo = True
metadata.bind = "mysql://c0hgp_client:test@localhost/c0sitio_hgp_db"
session.autocommit = True
class Photo(Entity):

    title = Field(Unicode(60))
    description = Field(UnicodeText)
    filehash = Field(Unicode(40))
    peso  = Field(Integer)
    timestamp = Field(DateTime, default=datetime.datetime.now)
    tags = ManyToMany('Tag')

    def __repr__(self):
        return '<Foto "%s" subida el %s>' % (self.title, self.timestamp)

    def get_tag_string(self):
        return ', '.join([t.name for t in self.tags])

class Video(Entity):

    title = Field(Unicode(60))
    description = Field(UnicodeText)
    peso  = Field(Integer)
    url = Field(Unicode(255))
    timestamp = Field(DateTime, default=datetime.datetime.now)
    tags = ManyToMany('Tag')

    def __repr__(self):
        return '<Video "%s" subida el %s>' % (self.title, self.timestamp)

    def get_tag_string(self):
        return ', '.join([t.name for t in self.tags])


class Tag(Entity):
    name = Field(Unicode(60))
    photos = ManyToMany('Photo')

    def count(self):
        return len(self.photos)

    def __repr__(self):
        return '<Tag "%s">' % self.name

def setupDb():
    setup_all()

def commit():
    session.commit()
