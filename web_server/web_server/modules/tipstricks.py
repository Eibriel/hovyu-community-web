import json
#import random

from web_server import app

from flask import request
from flask import redirect
from flask import render_template

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch


# TIPS & TRICKS
@app.route('/tipstricks')
def tipstricks():
    items = get('tipstricks')
    #print (items)
    return render_template('tipstricks.html', items=items)


def get_tiptrick_form():
    tiptrick = {
        'text': request.form['text'],
        'image': request.form['image']
    }
    return tiptrick


@app.route('/new_tiptrick', methods=['POST'])
def add_tiptrick():
    tiptrick = get_tiptrick_form()
    r = post('tipstricks', tiptrick)
    #print (r.text)
    return redirect('/tipstricks')


@app.route('/edit_tiptrick', methods=['POST'])
def edit_tiptrick():
    tiptrick = get_tiptrick_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    r = patch('tipstricks/{0}'.format(_id), tiptrick, _etag)
    #print (r.text)
    return redirect('/tipstricks')


@app.route('/tiptrick_add_edit')
def tiptrick_add_edit():
    editing = False
    edit_item = {}

    if 'e' in request.args:
        editing = True
        edit_item = get('tipstricks/{0}'.format(request.args['e']))
    return render_template('add_edit_tipstricks.html',
                            editing = editing,
                            edit_item = edit_item)
