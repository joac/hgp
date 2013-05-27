from flask import Flask
from flaskext import uploads
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_peewee.admin import Admin

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

auth = Auth(app, db)
admin = Admin(app, auth)

photos = uploads.UploadSet('photos', uploads.IMAGES)
uploads.configure_uploads(app, photos)
uploads.patch_request_class(app, 3 * 1024 * 1024) #Max size of photo 3mb

import models

@app.route('/')
def index():
    return "Hello world"




if __name__ == '__main__':
    auth.register_admin(admin)
    admin.register(models.Video)
    admin.register(models.Photo)
    admin.register(models.Tag)
    admin.register(models.PhotoTag)
    admin.register(models.VideoTag)
    admin.setup()
    app.run()
