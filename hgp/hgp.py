#! -*- coding: utf8 -*-
import models
import os
import hashlib
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, send_from_directory, jsonify

from werkzeug import secure_filename
from functools import wraps

UPLOAD_FOLDER = '/var/www/hernanpepe.com.ar/web/hgp/hgp/uploads'
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


@app.route('/')
@app.route('/portfolio')
def portfolio():
    """Muestra el portfolio con las fotos"""
    return photos_by_tag(u'portfolio')

@app.route('/condor')
def condor():
    """Muestra las fotos con el tag condor"""
    return photos_by_tag(u'condor')

@app.route('/vintage')
def vintage():
    """Muestra las fotos con el tag vintage"""
    return photos_by_tag(u'vintage')

@app.route('/press')
def press():
    """Muestra las fotos con el tag prensa"""
    return photos_by_tag(u'prensa')

@app.route('/contact')
def contact():
    """Muestra la información de contacto"""
    return photos_by_tag(u'contacto')


@app.route('/photo/get')
def get_json_photo():
    """Devuelve un diccionario json con el nombre, la descripcion, 
        la url y el id de una foto"""
    
    action = request.args.get('action', None, type=str)
    tag = request.args.get('tag', None, type=str)
    index = request.args.get('index', None, type=int)
    actions = ['prev', 'next'] 

    if action in actions and tag is not None and index is not None:
        tag = models.Tag.get_by(name=unicode(tag))
        max_index = len(tag.photos) - 1   
        if action == 'prev' and index > 0:
            index -= 1
        elif action == 'next' and index < max_index:
            index += 1
        
        if  index < 0:
            index = 0
        elif index > max_index:
            index = max_index

        return_dict = {}
        photo = tag.photos[index]
        return_dict['title'] = photo.title
        return_dict['description'] = photo.description
        return_dict['url'] = url_for('uploaded_file', filename=photo.filehash )
        return_dict['index'] = index
        return_dict['borrar'] = url_for('erase_photo', photo_id=photo.id)
        return_dict['editar'] = url_for('edit_photo', photo_id=photo.id)
        return jsonify(return_dict)
    abort(404)

@app.route('/photo/tag/<string:tag_name>')
def photos_by_tag(tag_name):
    """Lleva a la vista de fotos con ese tag"""
    tag = models.Tag.get_by(name=tag_name)
    if tag and len(tag.photos):
        pic = tag.photos[0]
        max_index = len(tag.photos) - 1  
        return render_template('photo.html', tag = tag, pic=pic, max_index=max_index )
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
    photo = models.Photo.query.filter_by(id=photo_id).one()
    return render_template('edit.html', pic=photo)

@app.route('/admin/update/<int:photo_id>', methods=['POST'])
@logged
def actualizar_foto(photo_id):
    photo = models.Photo.query.filter_by(id=photo_id).one()
    photo.title=request.form['title']
    photo.description=request.form['description']
    photo.tags=procesar_tags(request.form['tags'])
    models.commit()
    flash(u"La fotografía %s fue actualizada correctamente" % photo.title)
    return redirect( url_for('admin') )

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
# Gestion de Fotos
###################################################
def delete_uploaded(name):
    os.unlink(os.path.join(UPLOAD_FOLDER, name))

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1]

def allowed_file(filename):
    return '.' in filename and \
               get_file_extension(filename).lower() in ALLOWED_EXTENSIONS


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

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run()
