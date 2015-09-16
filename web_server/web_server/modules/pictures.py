import json
import logging
#import random

from web_server import app

from flask import request
from flask import redirect
from flask import render_template

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch


# PRODUCTS
def get_client_picture_form():
    client_picture = {
        'name': '',
        'approved': 'false',
        'admin_comments': '',
        'score': 0
#        'admin_password': request.form['admin_password']
    }
    return client_picture


@app.route('/add_client_picture', methods=['POST'])
def add_client_picture():
    #logging.error (request.files['client_picture'])
    storage = request.files['client_picture']
    filename = storage.name
    #filepath = '/tmp/filetmp'
    #storage.save(filepath)
    #filefile = open(filepath, 'rb')
    filefile = storage
    filecontenttype = storage.content_type
    files = {'picture_binary': (filename, filefile, filecontenttype)}
    #logging.error (files)
    #product = get_client_picture_form()
    #password = request.form['admin_password']
    form = get_client_picture_form() 
    #form = {}
    #files=None
    r = post('client_pictures', {}, files=files)
    logging.error (r.text)
    picture_id = r.json()['_id']
    
    store_id = request.form['store_id']
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
    logging.error (r.text)
    #import requests
    #url = 'http://httpbin.org/post'
    #r = requests.post(url, data=form, files=files)
    #logging.error(r.text)
    #r = requests.post(url, json=form)
    #logging.error(r.text)
    return redirect('/?store={0}'.format(store_id))
