#! -*- coding: utf8 -*-
import models
import os
import hashlib
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, send_from_directory

from werkzeug import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)

@app.before_request
def before_request():
    models.setupDb()

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
def get_file_extension(filename):
    return filename.rsplit('.', 1)[1]

def allowed_file(filename):
    return '.' in filename and \
               get_file_extension(filename) in ALLOWED_EXTENSIONS

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
            error = 'Contraseña Incorrecta'
        else:
            session['logged_in'] = True
            return redirect(url_for('show_galleries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Se desconectó del sistema')
    return redirect(url_for('show_galleries'))

if __name__ == '__main__':
    app.run()
