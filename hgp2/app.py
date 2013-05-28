#! -*- coding: utf8 -*-
from flask import Flask, flash, redirect, url_for, render_template, request
from flaskext import uploads
from flask.ext.bootstrap import Bootstrap
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_peewee.admin import Admin
from forms import PhotoForm, VideoForm

DATABASE = {
        'name': 'example.db',
        'engine': 'peewee.SqliteDatabase',
        }

DEBUG = True
SECRET_KEY = 'super super secret'
UPLOADS_DEFAULT_DEST = 'photos/'

app = Flask(__name__)

app.config.from_object(__name__)

db = Database(app)
Bootstrap(app)
auth = Auth(app, db)
admin = Admin(app, auth)

photos = uploads.UploadSet('photos', uploads.IMAGES)
uploads.configure_uploads(app, photos)
uploads.patch_request_class(app, 3 * 1024 * 1024) #Max size of photo 3mb

import models

@app.route('/')
def index():
    return "Hello world"

@app.route('/photo/new', methods=['GET', 'POST'])
def update_photo():
    form = PhotoForm()
    if form.validate_on_submit():
        filename = photos.save(request.files[form.image.name])
        photo = models.Photo(
                   title=form.name.data,
                   description=form.description.data,
                   filename=filename,
                )
        photo.save()
        photo.save_tags(
                process_tags(form.tags.data),
                form.weight.data,
                )



        return redirect(url_for('index'))
    else:

        return render_template('photo_form.html', form=form)


@app.route('/video/new', methods=['GET', 'POST'])
def update_video():
    form = VideoForm()
    if form.validate_on_submit():

        return redirect(url_for('index'))
    else:

        return render_template('video_form.html', form=form)


def process_tags(tag_string):
    """Process a string of comma separated tags, creating them in db"""
    tag_names = [b.strip() for b in tag_string.split(',') if b != '' ]
    tags = [tag for tag in models.Tag.select() if tag.name in tag_names]
    existent_tag_names = [tag.name for tag in tags]
    new_tags = set(tag_names) - set(existent_tag_names)
    for tag_name in new_tags:
        tag = models.Tag(name=tag_name)
        tag.save()
        flash(u'Se creó el tag "%s"' % tag)
    return tags




if __name__ == '__main__':
    auth.register_admin(admin)
    admin.register(models.Video)
    admin.register(models.Photo)
    admin.register(models.Tag)
    admin.register(models.PhotoTag)
    admin.register(models.VideoTag)
    admin.setup()
    app.run()
