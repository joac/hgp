# -*- coding: utf8 -*-

from peewee import (
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    TextField,
    )

from app import db

class Photo(db.Model):
    """Represents a single photo with metadata"""
    title = CharField(255)
    description = TextField()
    filename = CharField(255)
    timestamp = DateTimeField()


class Video(db.Model):
    """Represents a single video with metadata"""
    title = CharField(255)
    description = TextField()
    url = CharField(255)
    timestamp = DateTimeField()
    source = CharField(255) # youtube, vimeo, etc

class Text(db.Model):
    title = CharField(255)
    body = TextField()


class Tag(db.Model):
    """Represents a tag"""
    name = CharField(255)


class PhotoTag(db.Model):
    """Represents a relationship betwen a Photo and a Tag"""
    photo = ForeignKeyField(Photo, related_name='tags')
    tag = ForeignKeyField(Tag, related_name='photos')
    peso = IntegerField()


class VideoTag(db.Model):
    """Represents a Many-to-Many relationship betwen Video and Tag """
    video = ForeignKeyField(Video, related_name='tags')
    tag = ForeignKeyField(Tag, related_name='videos')
    peso = IntegerField()
