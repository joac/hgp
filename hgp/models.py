from elixir import *
import datetime
metadata.bind = "sqlite:///db.sqlite"
#metadata.bind.echo = True

class Photo(Entity):
    
    title = Field(Unicode(60))
    timestamp = Field(Integer)
    description = Field(UnicodeText)
    filehash = Field(Unicode(40))
    timestamp = Field(DateTime, default=datetime.datetime.now) 
    tags = ManyToMany('Tag')
    
    def __repr__(self):
        return '<Foto "%s" de  galeria "%s" subida el %s>' % (self.title, self.gallery, self.timestamp)


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
