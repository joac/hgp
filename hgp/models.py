# -*- coding: utf-8 -*-

import os
import datetime

from settings import UPLOAD_FOLDER

from elixir import Field, ManyToMany, Entity, metadata, session, Unicode, \
     Integer, UnicodeText, DateTime, setup_all

metadata.bind = 'sqlite://' + os.path.join(UPLOAD_FOLDER, 'db.sqlite')
metadata.bind.echo = True
# metadata.bind = "mysql://c0hgp_client:test@localhost/c0sitio_hgp_db"
# session.autocommit = True


class Photo(Entity):
    title = Field(Unicode(60))
    timestamp = Field(Integer)
    description = Field(UnicodeText)
    filehash = Field(Unicode(40))
    timestamp = Field(DateTime, default=datetime.datetime.now)
    tags = ManyToMany('Tag')

    def __repr__(self):
        return '<Foto "%s" de  galeria "%s" subida el %s>' % \
               (self.title, self.gallery, self.timestamp)

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
