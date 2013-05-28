# -*- coding: utf8 -*-
import datetime

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
    timestamp = DateTimeField(default=datetime.datetime.now)

    def save_tags(self, tags, weight=1):
        for tag in tags:
            rel = PhotoTag(tag=tag, photo=self, weight=weight)
            rel.save()

class Video(db.Model):
    """Represents a single video with metadata"""
    title = CharField(255)
    description = TextField()
    url = CharField(255)
    timestamp = DateTimeField(default=datetime.datetime.now)
    source = CharField(255) # youtube, vimeo, etc

    def save_tags(self, tags, weight=1):
        for tag in tags:
            rel = VideoTag(tag=tag, video=self, weight=weight)
            rel.save()

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
    weight = IntegerField()


class VideoTag(db.Model):
    """Represents a Many-to-Many relationship betwen Video and Tag """
    video = ForeignKeyField(Video, related_name='tags')
    tag = ForeignKeyField(Tag, related_name='videos')
    weight = IntegerField()
