import json
import logging
#import random

from web_server import app

from flask import request
from flask import redirect
from flask import render_template

from datetime import datetime

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch


# PRODUCTS
def get_badge_store_form():
    badge_store = {
        'store': request.form['store'],
        'badge': request.form['badge'],
        'start_date': request.form['start_date'],
        'end_date': request.form['end_date'],
        'paused': False
    }
    if 'paused' in request.form:
        badge_store['paused'] = True


    badge_store['start_date'] = datetime.strptime(badge_store['start_date'], '%d/%m/%Y')
    badge_store['end_date'] = datetime.strptime(badge_store['end_date'], '%d/%m/%Y')

    badge_store['start_date'] = badge_store['start_date'].strftime("%a, %d %b %Y %H:%M:%S GMT")
    badge_store['end_date'] = badge_store['end_date'].strftime("%a, %d %b %Y %H:%M:%S GMT")

    return badge_store


@app.route('/badge_stores')
def badge_stores():
    items = get('badge_store?sort=-_updated')
    #logging.error(items)
    return render_template('badge_stores.html', items=items, noindex = True, subtitle='Badges & Stores')


@app.route('/badge_store_add_edit')
def badge_store_add_edit():
    editing = False
    edit_item = {}

    if 'e' in request.args:
        editing = True
        edit_item = get('badge_store/{0}'.format(request.args['e']))
    return render_template('add_edit_badge_store.html',
                            editing = editing,
                            edit_item = edit_item,
                            subtitle='Add or Edit Badge Store relation')


@app.route('/new_badge_store', methods=['POST'])
def add_badge_store():
    badge = get_badge_store_form()
    print ( badge )
    password = request.form['admin_password']
    r = post('badge_store', badge, password)
    print (r.text)
    return redirect('/badge_stores')


@app.route('/edit_badge_store', methods=['POST'])
def edit_badge_store():
    badge = get_badge_store_form()
    password = request.form['admin_password']
    _etag = request.form['_etag']
    _id = request.form['_id']
    r = patch('badge_store/{0}'.format(_id), product, _etag, password)
    #print (r.text)
    return redirect('/badge_stores')
