# -*- coding: utf-8 -*-
import datetime

from flask import url_for

from elixir import Field, ManyToMany, Entity, metadata, session, Unicode, \
     Integer, UnicodeText, DateTime, setup_all

from settings import DATABASE

metadata.bind = DATABASE['path']
if DATABASE['name'] == 'sqlite3':
    metadata.bind.echo = True
elif DATABASE['name'] == 'mysql':
    session.autocommit = True


class Photo(Entity):
    title = Field(Unicode(60))
    timestamp = Field(Integer)
    description = Field(UnicodeText)
    filehash = Field(Unicode(50))
    timestamp = Field(DateTime, default=datetime.datetime.now)
    tags = ManyToMany('Tag')

    def __repr__(self):
        return '<Foto "%s" subida el %s>' % \
               (self.title, self.timestamp)

    def get_tag_string(self):
        return ', '.join([t.name for t in self.tags])

    def get_absolute_url(self):
        return url_for('photo_by_pk', pk=self.id)


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
