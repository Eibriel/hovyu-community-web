import json
import random

from web_server import app

from flask import request
from flask import redirect
from flask import render_template

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch


def check_human_data(check_id, option):
    check = get('human_checks/{0}'.format(check_id))
    #print (check)
    if check and check['right_option'] == option:
        return True
    else:
        return False

# STORE
def get_form(edit = False):
    store = {
        'name': request.form['name'],
        'description': request.form['description'],
        'address': request.form['address'],
        'place': None,
        'score': {
            'count': 0,
            'sum': 0
        },
        'views': 0,
        'email': request.form['email'],
        'website': [],
        'tel': [],
        'exact_location': False,
        'edit_reason': request.form['edit_reason'],
    }

    websites_json = json.loads(request.form['websites_json'])
    store['website'] = websites_json

    tels_json = json.loads(request.form['tels_json'])
    store['tel'] = tels_json

    products_json = json.loads(request.form['products_json'])
    products = []
    #print (request.form['products_json'])
    #print (products_json)
    if products_json:
        for product in products_json:
            #print(ObjectId.is_valid(product['_id']))
            products.append(product['_id'])
    store['products'] = products

    if request.form['latitude'] != '' and request.form['longitude'] != '':
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
    else:
        latitude = 0.0
        longitude = 0.0

    store['location'] = {"type":"Point","coordinates":[latitude, longitude]}

    if 'exact_location' in request.form:
        store['exact_location'] = True

    # Place
    place_json = json.loads(request.form['place_json'])
    if place_json:
        latitude = float(place_json['latitude'])
        longitude = float(place_json['longitude'])
        place = {'place_id': place_json['place_id'],
                 'osm_id': place_json['osm_id'],
                 'full_name': place_json['full_name'],
                 'location': {"type":"Point","coordinates":[latitude, longitude]}
                 }
        store['place'] = place

    # Highlight
    #if edit:
    #    'highlight': False,

    if not edit:
        store['iid']=0
        store['wid']=""
    return store


@app.route("/store_add_edit")
def store_add():
    editing = False
    edit_item = {}

    products = get('products')

    if 'e' in request.args:
        editing = True
        edit_item = get('stores/{0}'.format(request.args['e']))
        edit_item = edit_item[0]
        websites = []
        if type(edit_item['website']) == list:
            for website in edit_item['website']:
                websites.append(website)
            edit_item['websites_json'] = json.dumps(websites)
        else:
            edit_item['websites_json'] = json.dumps([edit_item['website']])
            edit_item['website'] = [edit_item['website']]

        edit_item['tels_json'] = json.dumps(edit_item['tel'])
        if 'products' in edit_item:
            products_json = []
            #products = get('products')
            for product in edit_item['products']:
                product_ = get('products/{0}'.format(product))
                products_json.append(product_)
                #for product_ in products:
                #    if product_['_id'] == product:
                #        products_json.append(product_)
            edit_item['products_json'] = json.dumps(products_json)
        place_json = None
        if edit_item.get('place'):
            place_json = {'place_id': edit_item['place']['place_id'],
                          'osm_id': edit_item['place']['osm_id'],
                          'full_name': edit_item['place']['full_name'],
                          'latitude': edit_item['place']['location']['coordinates'][0],
                          'longitude': edit_item['place']['location']['coordinates'][1]
                         }
        edit_item['place_json'] = json.dumps(place_json)

    if 'location' not in edit_item:
        edit_item['location'] = None

    if 'place_json' not in edit_item:
        edit_item['place_json'] = json.dumps(None)

    if 'products_json' not in edit_item:
        edit_item['products_json'] = json.dumps([])

    return render_template('add_edit_store.html',
                           #products = products,
                           edit_item = edit_item,
                           editing = editing)

@app.route('/new_store', methods=['POST'])
def new_store():
    if not check_human_data(request.form['human_check_id'], request.form['human_check_selected']):
        return '', 403
    store = get_form()
    print (store['products'])
    r = post('stores', store)
    #print (r.text)
    _id = r.json()['_id']
    return redirect('/?store={0}'.format(_id))


@app.route('/edit_store', methods=['POST'])
def edit_store():
    if not check_human_data(request.form['human_check_id'], request.form['human_check_selected']):
        return '', 403
    store = get_form(edit=True)
    _etag = request.form['_etag']
    _id = request.form['_id']
    print (store)
    r = patch('stores/{0}'.format(_id), store, _etag)
    #print (r.text)
    return redirect('/?store={0}'.format(_id))
