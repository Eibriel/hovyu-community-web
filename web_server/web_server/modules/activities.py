import json

from flask import request
from flask import redirect
from flask import render_template

from web_server import app

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch

# ACTIVITIES
def get_activity_form():
    activity = {
        'name': request.form['name'],
        'products': []
    }
    products_json = json.loads(request.form['products_json'])
    products = []
    if products_json:
        for product in products_json:
            products.append(product['_id'])
        activity['products'] = products
    return activity


@app.route('/activities')
def activities():
    items = get('activities')
    #print (items)
    return render_template('activities.html', items=items, noindex = True)


@app.route('/new_activity', methods=['POST'])
def add_activity():
    activity = get_activity_form()
    #print (activity)
    r = post('activities', activity)
    #print (r.text)
    return redirect('/activities')


@app.route('/edit_activity', methods=['POST'])
def edit_activity():
    activity = get_activity_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    r = patch('activities/{0}'.format(_id), activity, _etag)
    #print (r.text)
    return redirect('/activities')


@app.route('/activity_add_edit')
def activity_add_edit():
    editing = False
    edit_item = {}

    if 'e' in request.args:
        editing = True
        edit_item = get('activities/{0}'.format(request.args['e']))
        if 'products' in edit_item:
            products_json = []
            for product in edit_item['products']:
                product_ = get('products/{0}'.format(product))
                products_json.append(product_)
            edit_item['products_json'] = json.dumps(products_json)
    return render_template('add_edit_activities.html',
                            editing = editing,
                            edit_item = edit_item)
