#!/usr/bin/python
# -*- coding: utf-8 -*-

import models
import os
import hashlib
from PIL import Image
from flask import request, session, redirect, url_for, \
    abort, render_template, flash, send_from_directory, jsonify

from functools import wraps
from settings import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, DEBUG, \
     USERNAME, PASSWORD, SECRET_KEY, TEMPLATE_VARIABLES

from sqlalchemy import desc

# Handle session in the filesystem instead with cookies
from session import FlaskSess


# http://mail.python.org/pipermail/image-sig/2009-January/005369.html
# http://mail.python.org/pipermail/image-sig/2009-January/005370.html
# http://mail.python.org/pipermail/image-sig/1999-August/000816.html
from PIL import ImageFile
ImageFile.MAXBLOCK = 1000000  # default is 64k

app = FlaskSess(__name__)
app.config.from_object(__name__)


@app.context_processor
def template_vars():
    return TEMPLATE_VARIABLES


@app.before_request
def before_request():
    models.setupDb()


def logged(f):
    @wraps(f)
    def inner(*args, **kwargs):
        if not session.get('logged_in'):
            abort(401)
        else:
            return f(*args, **kwargs)

    return inner


@app.route('/')
def home():
    """Muestra todas las fotos en orden cronologico descendente"""
    photos = models.Photo.query.order_by(desc(models.Photo.timestamp))
    if photos and len(photos.all()):
        session['photos'] = photos.all()
        pic = photos[0]
        max_index = len(photos.all()) - 1
        return render_template('photo_list.html',
                               pic=pic, max_index=max_index)
    else:
        return render_template('error.html')


@app.route('/portfolio')
def portfolio():
    """Muestra el portfolio con las fotos"""
    return photos_by_tag(u'portfolio')


@app.route('/photo/get')
def get_json_photo():
    """Devuelve un diccionario json con el nombre, la descripcion,
        la url y el id de una foto"""

    action = request.args.get('action', None, type=str)
    index = request.args.get('index', None, type=int)
    actions = ['prev', 'next']

    if action in actions and index is not None:
        photos = session['photos']
        max_index = len(photos) - 1
        if action == 'prev' and index > 0:
            index -= 1
        elif action == 'next' and index < max_index:
            index += 1

        if  index < 0:
            index = 0
        elif index > max_index:
            index = max_index

        return_dict = {}
        photo = photos[index]
        return_dict['title'] = photo.title
        return_dict['description'] = photo.description
        return_dict['url'] = url_for('uploaded_file_thumb',
                                     filename=photo.filehash)
        return_dict['url_original'] = url_for('uploaded_file_original',
                                     filename=photo.filehash)
        return_dict['index'] = index
        return_dict['borrar'] = url_for('erase_photo', photo_id=photo.id)
        return_dict['editar'] = url_for('edit_photo', photo_id=photo.id)
        return_dict['permalink'] = photo.get_absolute_url()
        return_dict['id_photo'] = photo.id
        return jsonify(return_dict)
    abort(404)


@app.route('/photo/<int:pk>')
def photo_by_pk(pk):
    """Show a specific Photography"""
    pic = models.Photo.get_by(id=pk)
    if pic:
        return render_template('photo.html', pic=pic)
    else:
        return render_template('error.html')


@app.route('/photo/tag/<string:tag_name>')
@app.route('/<string:tag_name>')
def photos_by_tag(tag_name):
    """Lleva a la vista de fotos con ese tag"""
    tag = models.Tag.get_by(name=tag_name)
    photos = models.Photo.query.filter(models.Photo.tags.any(name=tag_name)) \
                               .order_by(desc(models.Photo.timestamp)).all()
    if tag and len(photos):
        session['photos'] = list(photos)
        pic = photos[0]
        max_index = len(tag.photos) - 1
        return render_template('photo_list.html', tag=tag,
                               pic=pic, max_index=max_index)
    else:
        return render_template('error.html')


@app.route('/tag/delete/<string:tag_name>')
@logged
def delete_tag(tag_name):
    models.Tag.get_by(name=tag_name).delete()
    models.commit()
    flash(u'Se eliminó el tag "%s"' % tag_name)

    return redirect(url_for('admin'))


@app.route('/admin')
@logged
def admin():
    """Muestra un panel para agregar fotos"""
    tags = models.Tag.query.all()
    return render_template('admin.html', tags=tags)


@app.route('/admin/all')
@logged
def ver_todas_las_fotos():
    """muestra un listado con todas las fotos"""
    photos = models.Photo.query.all()
    return render_template('all.html', photos=photos)


@app.route('/admin/add', methods=['POST'])
@logged
def agregar_foto():
    """Agrega una foto nueva"""
    archive = request.files['file']
    landscape = 'landscape' in request.form.keys()
    if allowed_file(archive.filename):
        hashname = hashlib.sha1(archive.read()).hexdigest()
        archive.seek(0)
        hashname += '.' + get_file_extension(archive.filename)
        photo = Image.open(archive)
        if not landscape:
            width = photo.size[0] * 800 / photo.size[1]
            size = (width, 800)
        else:
            height = photo.size[1] * 800 / photo.size[0]
            size = (800, height)
        photo_thumb = photo.resize(size, Image.ANTIALIAS)
        filename = os.path.join(UPLOAD_FOLDER, hashname)
        photo_thumb.save(filename, quality=95, optimize=True)
        photo.save(os.path.join(UPLOAD_FOLDER, 'originals', hashname),
                   quality=95, optimize=True)
        tags = procesar_tags(request.form['tags'])
        models.Photo(title=request.form['title'],
                     description=request.form['description'],
                     filehash=hashname,
                     tags=tags)
        models.commit()
        flash(u'Se subió el archivo: %s y se renombro: "%s"' % \
              (archive.filename, filename))
    else:
        flash(u'Error al subir el archivo %s' % archive.filename)
    return redirect(url_for('admin'))


def procesar_tags(tag_string):
    tag_names = [b.strip() for b in tag_string.split(',') if b != '']
    tags = [tag for tag in models.Tag.query.all() if tag.name in tag_names]
    existent_tag_names = [tag.name for tag in tags]
    new_tags = set(tag_names) - set(existent_tag_names)
    for tag in new_tags:
        tags.append(models.Tag(name=tag))
        flash(u'Se creó el tag "%s"' % tag)
    models.commit()
    return tags


@app.route('/admin/edit/<int:photo_id>')
@logged
def edit_photo(photo_id):
    """Edita los datos para una foto especifica"""
    photo = models.Photo.query.filter_by(id=photo_id).one()
    return render_template('edit.html', pic=photo)


@app.route('/admin/update/<int:photo_id>', methods=['POST'])
@logged
def actualizar_foto(photo_id):
    photo = models.Photo.query.filter_by(id=photo_id).one()
    photo.title = request.form['title']
    photo.description = request.form['description']
    photo.tags = procesar_tags(request.form['tags'])
    models.commit()
    flash(u"La fotografía %s fue actualizada correctamente" % photo.title)
    return redirect(url_for('admin'))


@app.route('/admin/remove/<int:photo_id>')
@logged
def erase_photo(photo_id):
    """Hace Borrado fisico de una foto"""

    photo = models.Photo.query.filter_by(id=photo_id).one()
    photo.delete()
    models.commit()
    delete_uploaded(photo.filehash)
    flash(u"Se elimino la foto '%s' y el archivo %s" % \
          (photo.title, photo.filehash))
    return redirect(url_for('ver_todas_las_fotos'))


###################################################
# Gestion de Fotos
###################################################
def delete_uploaded(name):
    os.unlink(os.path.join(UPLOAD_FOLDER, name))
    os.unlink(os.path.join(UPLOAD_FOLDER, 'originals', name))


def get_file_extension(filename):
    return filename.rsplit('.', 1)[1]


def allowed_file(filename):
    return '.' in filename and \
               get_file_extension(filename).lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file_thumb(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)


@app.route('/uploads/originals/<filename>')
def uploaded_file_original(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'originals')
    return send_from_directory(path,
                               filename)


###################################################
# Gestion de Usuarios
###################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Usuario Invalido'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Contrasena Incorrecta'
        else:
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'Se desconecto del sistema')
    return redirect(url_for('login'))


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.debug = DEBUG
    app.run()
