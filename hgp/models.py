from elixir import *
import datetime
metadata.bind = "sqlite:///db.sqlite"
metadata.bind.echo = True

class Photo(Entity):
    
    title = Field(Unicode(60))
    timestamp = Field(Integer)
    description = Field(UnicodeText)
    filehash = Field(Unicode(40))
    timestamp = Field(DateTime, default=datetime.datetime.now) 
    gallery = ManyToOne('Gallery')
    tags = ManyToMany('Tag')
    
    def __repr__(self):
        return '<Foto "%s" de  galeria "%s" subida el %s>' % (self.title, self.gallery, self.timestamp)

class Gallery(Entity):
    
    title = Field(Unicode(60))
    timestamp = Field(Integer)
    description = Field(UnicodeText)
    photos = OneToMany('Photo')
    
    def __repr__(self):
        return '<Galeria "%s">' % (self.title) 

class Tag(Entity):
    name = Field(Unicode(60))
    galleries = ManyToMany('Gallery')
    photos = ManyToMany('Photo')

    def __repr__(self):
        return '<Tag "%s">' % self.name
