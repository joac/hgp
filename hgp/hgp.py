#! -*- coding: utf8 -*-
import models
import os
import hashlib
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, send_from_directory

from werkzeug import secure_filename
from functools import wraps

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'psd'])
DEBUG = True
SECRET_KEY = 'development key1'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

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

@app.route('/portfolio')
def portfolio():
    """Muestra el portfolio con las fotos"""
    tag = models.Tag.get_by(name='portfolio')
    return render_template('show_gallery.html', tag = tag )

@app.route('/condor')
def condor():
    """Muestra las fotos con el tag condor"""
    pass

@app.route('/press')
def press():
    """Muestra las fotos con el tag prensa"""
    pass

@app.route('/contact')
def contact():
    """Muestra la información de contacto"""
    pass

@app.route('/photo/<int:photo_id>')
def devolver_json_foto():
    """Devuelve un diccionario json con el nombre, la descripcion, 
        la url y el id de una foto"""
    pass

@app.route('/photo/tag/<string:tag_name>')
def photos_by_tag(tag_name):
    """Lleva a la vista de fotos con ese tag"""
    pass

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
    return render_template('all.html', photos = photos) 

@app.route('/admin/add', methods=['POST'])
@logged
def agregar_foto():
    """Agrega una foto nueva"""
    archive = request.files['file']
    if allowed_file(archive.filename):
        hashname =  hashlib.sha1(archive.read()).hexdigest()
        archive.seek(0)
        hashname += '.' + get_file_extension(archive.filename)
        filename = os.path.join(UPLOAD_FOLDER, hashname)
        archive.save(filename)
        tags =  procesar_tags(request.form['tags'])
        photo = models.Photo(title=request.form['title'], 
                            description=request.form['description'],
                            filehash=hashname,
                            tags=tags
                            ) 
        models.commit()
        flash(u'Se subió el archivo: %s y se renombro: "%s"' % (archive.filename, filename))
    else:
        flash(u'Error al subir el archivo %s' % archive.filename)
    return redirect( url_for('admin') )


def procesar_tags(tag_string):
    
    tag_names = [b.strip() for b in tag_string.split(',') if b != '' ]
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
    pass

@app.route('/admin/remove/<int:photo_id>')
@logged
def erase_photo(photo_id):
   """Hace Borrado fisico de una foto""" 
   photo = models.Photo.query.filter_by(id=photo_id).one()
   photo.delete()
   models.commit()
   delete_uploaded(photo.filehash)
   flash(u"Se elimino la foto '%s' y el archivo %s" % (photo.title, photo.filehash))
   return redirect(url_for('ver_todas_las_fotos'))












###################################################
#Gestion de galerias
###################################################

#ver lista
@app.route('/gallery/all')
def show_galleries():
    galleries = [dict(id=gal.id, title=gal.title, description=gal.description ) for gal in models.Gallery.query.all()]
    return render_template('show_galleries.html', galleries=galleries)

#agregar una galeria

@app.route('/gallery/add', methods=['POST'])
def add_gallery():
    if not session.get('logged_in'):
        abort(401)
    models.Gallery(title=request.form['title'], description=request.form['description'])
    models.commit()
    flash('Nueva Galeria Creada')
    return redirect(url_for('show_galleries'))

#ver una sola galeria

@app.route('/gallery/show/<int:gallery_id>')
def show_gallery(gallery_id):
    gallery = models.Gallery.query.filter_by(id=gallery_id).one()
    return render_template('show_gallery.html', gallery = gallery )

#borrar una galeria

@app.route('/gallery/remove/<int:gallery_id>')
def remove_gallery(gallery_id):
    if not session.get('logged_in'):
        abort(401)
    gallery = models.Gallery.query.filter_by(id=gallery_id).one()
    gallery.delete()
    models.commit()
    flash("Se elimino la galeria '%s'" % gallery.title)
    return redirect(url_for('show_galleries'))
    
@app.route('/gallery/edit/<int:gallery_id>')
def edit_gallery(gallery_id):
    abort(404)

###################################################
# Gestion de Fotos
###################################################
def delete_uploaded(name):
    os.unlink(os.path.join(UPLOAD_FOLDER, name))

    

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1]

def allowed_file(filename):
    return '.' in filename and \
               get_file_extension(filename).lower() in ALLOWED_EXTENSIONS

@app.route('/gallery/<int:gallery_id>/add/photo', methods=['POST'])
def add_photo(gallery_id):
    if not session.get('logged_in'):
        abort(401)
    archive = request.files['file']
    if allowed_file(archive.filename):
        hashname =  hashlib.sha1(archive.read()).hexdigest()
        archive.seek(0)
        hashname += '.' + get_file_extension(archive.filename)
        filename = os.path.join(UPLOAD_FOLDER, hashname)
        archive.save(filename)
        
        gallery = models.Gallery.query.filter_by(id=gallery_id).one()
        photo = models.Photo(title=request.form['title'], 
                            description=request.form['description'],
                            filehash=hashname,
                            gallery=gallery
                            ) 
        models.commit()
        flash('Se subio el archivo: %s y se renombro: "%s"' % (archive.filename, filename))
    else:
        flash('Error al subir el archivo %s' % archive.filename)
    return redirect( url_for('show_gallery', gallery_id=gallery_id) )
    
def remove_photo():
    if not session.get('logged_in'):
        abort(401)
    pass

def show_photo():
    pass

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
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

if __name__ == '__main__':
    app.run()
