import json
import logging
#import random

from web_server import app

from flask import request
from flask import make_response
from flask import redirect
from flask import render_template

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch
from web_server.modules.server_requests import get_pictures_info


# PRODUCTS
def get_client_picture_form():
    client_picture = {
        'name': ' ',
        #'approved': 'false',
        'admin_comments': ' ',
        'score': 0
#        'admin_password': request.form['admin_password']
    }
    return client_picture


@app.route('/client_picture/<picture_id>')
def client_picture(picture_id):
    picture = get('client_pictures/{0}'.format(picture_id))
    if 'if-modified-since' in request.headers:
        content_type = picture['picture_binary']['content_type']
        response = make_response('', 304)
        response.headers['content-type'] = content_type
        response.headers['last-modified'] = picture['_updated']
        response.headers['cache-control'] = 'max-age=2628000, public'
        return response 
    import base64
    picture_binary = base64.b64decode(picture['picture_binary']['file'])
    content_type = picture['picture_binary']['content_type']
    response = make_response(picture_binary)
    response.headers['content-type'] = content_type
    response.headers['last-modified'] = picture['_updated']
    response.headers['cache-control'] = 'max-age=2628000, public'
    return response


@app.route('/client_pictures/')
def client_pictures():
    pictures = get('client_pictures?projection=%7B%22picture_binary%22%3A0%7D')
    return render_template('client_pictures.html', items=pictures, noindex = True, subtitle='Fotografías de los clientes')


@app.route('/client_picture_approving', methods=['POST'])
def client_picture_approve():
    picture_id = request.form['picture_id']
    picture_etag = request.form['picture_etag']
    picture_approved = request.form['picture_approved']
    if picture_approved == "True":
        picture_approved = True
    else:
        picture_approved = False
    picture_set = {
        'approved': picture_approved 
    }
    password = request.form['admin_password']
    r = patch('client_pictures/{0}'.format(picture_id), picture_set, picture_etag, password)
    return redirect('/client_pictures')


@app.route('/add_client_picture', methods=['POST'])
def add_client_picture():
    storage = request.files['client_picture']
    filename = storage.name
    filefile = storage
    filecontenttype = storage.content_type
    files = {'picture_binary': (filename, filefile, filecontenttype)}
    store_id = request.form['store_id']
    form = get_client_picture_form() 
    form['store_id'] = store_id 
    form['name'] = request.form['name'] 
    r = post('client_pictures', form, files=files)
    picture_id = r.json()['_id']
    
    store = get('stores/{0}'.format(store_id))
    store = store[0]
    store_etag = store['_etag']
    store_patch = {}
    if 'client_pictures' not in store:
        store_patch['client_pictures'] = []
    else:
        store_patch['client_pictures'] = store['client_pictures']
    store_patch['client_pictures'].append(picture_id)
    r = patch('stores/{0}'.format(store_id), store_patch, store_etag)
    return redirect('/?store={0}'.format(store_id))


@app.route('/logo_picture/<picture_id>')
def logo_picture(picture_id):
    picture = get('logo_pictures/{0}'.format(picture_id))
    if 'if-modified-since' in request.headers:
        content_type = picture['picture_binary']['content_type']
        response = make_response('', 304)
        response.headers['content-type'] = content_type
        response.headers['last-modified'] = picture['_updated']
        response.headers['cache-control'] = 'max-age=2628000, public'
        return response 
    import base64
    picture_binary = base64.b64decode(picture['picture_binary']['file'])
    content_type = picture['picture_binary']['content_type']
    response = make_response(picture_binary)
    response.headers['content-type'] = content_type
    response.headers['last-modified'] = picture['_updated']
    response.headers['cache-control'] = 'max-age=2628000, public'
    return response


@app.route('/edit_process_album/<store_id>')
def edit_process_album(store_id):
    store = get('stores/{0}'.format(store_id))
    store = store[0]
    #logging.error( store )

    if store:
        pictures_info = get_pictures_info( store )

    return render_template('edit_process_album.html',
                            pictures = pictures_info,
                            store_id = store_id,
                            noindex = True,
                            subtitle = 'Editar album de proceso')

@app.route('/set_album', methods=['POST'])
def set_album():
    picture_id = request.form['picture_id']
    picture_etag = request.form['picture_etag']
    album_form = request.form['album']
    store_id = request.form['store_id']

    if album_form == 'process':
        album = 'process'
    else:
        album = 'client'

    password = request.form['admin_password']
    r = patch('client_pictures/{0}'.format(picture_id), {'album': album}, picture_etag, password)
    #logging.error( r.text )
    return redirect('/?store={0}'.format(store_id))
