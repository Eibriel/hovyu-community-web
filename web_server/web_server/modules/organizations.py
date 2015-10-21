import json
import random
import logging

from bson import ObjectId

from web_server import app

from flask import request
from flask import redirect
from flask import render_template

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch
from web_server.modules.server_requests import delete


def check_human_data(check_id, option):
    return True
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
        'process_description': request.form['process_description'],
        'address': request.form['address'],
        #'place': None,
        'score': {
            'count': 0,
            'sum': 0
        },
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

    #products_json = json.loads(request.form['products_json'])
    #products = []
    #if products_json:
    #    for product in products_json:
    #        products.append(product['_id'])
    #store['products'] = products

    if request.form['latitude'] != '' and request.form['longitude'] != '':
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
    else:
        latitude = 0.0
        longitude = 0.0

    store['location'] = {"type":"Point","coordinates":[longitude, latitude]}

    if 'exact_location' in request.form:
        store['exact_location'] = True

    # Place
    """place_json = json.loads(request.form['place_json'])
    if place_json:
        latitude = float(place_json['latitude'])
        longitude = float(place_json['longitude'])
        place = {'place_id': place_json['place_id'],
                 'osm_id': place_json['osm_id'],
                 'full_name': place_json['full_name'],
                 'location': {"type":"Point","coordinates":[longitude, latitude]}
                 }
        store['place'] = place"""

    # Highlight
    #if edit:
    #    'highlight': False,

    # Products
    products_json = json.loads(request.form['products_json'])
    products_documents = []
    products = []
    products_properties = []
    for product in products_json:
        product_store = {
            'product': product['product'],
            'properties': [],
            'brand': product['brand'],
            'price': product['price']
        }
        for product_property in product['properties']:
            products_properties.append(product_property['_id'])
            product_store['properties'].append(product_property['_id'])
        #print (product['properties'])
        products_documents.append(product_store)
        products.append(product['product'])
        #products_properties = products_properties + product['properties']

    store['products_documents'] = products_documents
    store['products'] = list(set(products))
    store['products_properties'] = list(set(products_properties))

    # IID WID, VIEWS
    if not edit:
        store['iid']=0
        store['wid']=""
        store['views'] = 0

    # LOGO PICTURE
    logo_picture_delete = False
    if 'logo_picture_delete' in request.form:
        logo_picture_delete = True
    if not logo_picture_delete and 'logo_picture' in request.files:
        storage = request.files['logo_picture']
        filename = storage.name
        filefile = storage
        filecontenttype = storage.content_type
        if filecontenttype in ['image/png', 'image/jpeg']:
            files = {'picture_binary': (filename, filefile, filecontenttype)}
            form = {}
            r = post('logo_pictures', form, files=files)
            logging.error( r.text )
            picture_id = r.json()['_id']
            store['logo_picture'] = picture_id
    if logo_picture_delete:
        store['logo_picture'] = None

    return store


@app.route("/organization_add_edit")
def store_add():
    editing = False
    edit_item = {}
    products = get('products')

    if 'e' in request.args:
        editing = True
        edit_item = get('stores/{0}'.format(request.args['e']))
        edit_item = edit_item[0]
        websites = []
        for website in edit_item['website']:
            websites.append(website)
        edit_item['websites_json'] = json.dumps(websites)

        edit_item['tels_json'] = json.dumps(edit_item['tel'])

        products_json = []
        for product in edit_item['products_documents']:
            product_json = {
                'brand': product['brand'],
                'price': product['price'],
                'product': product['product']
            }

            while True:
                product_json['tmp_id'] = random.randint(1, 99999)
                repeat = False
                for product_2 in products_json:
                    if product_2['tmp_id'] == product_json['tmp_id']:
                        repeat = True
                if not repeat:
                    break

            properties = []
            for prod_prop in product['properties']:
                prop = get('products_properties/{0}'.format(prod_prop))
                property_ = {
                    '_id': prod_prop,
                    'name': prop['name']
                }
                properties.append(property_)
            product_json['properties'] = properties
            prod = get('products/{0}'.format(product['product']))
            product_json['name'] = prod['name']
            products_json.append(product_json)
        edit_item['products_json'] = json.dumps(products_json)

        """place_json = None
        if edit_item.get('place'):
            place_json = {'place_id': edit_item['place']['place_id'],
                          'osm_id': edit_item['place']['osm_id'],
                          'full_name': edit_item['place']['full_name'],
                          'longitude': edit_item['place']['location']['coordinates'][0],
                          'latitude': edit_item['place']['location']['coordinates'][1]
                         }
        edit_item['place_json'] = json.dumps(place_json)"""

    if 'location' not in edit_item:
        edit_item['location'] = None

    """if 'place_json' not in edit_item:
        edit_item['place_json'] = json.dumps(None)"""

    if 'products_json' not in edit_item:
        edit_item['products_json'] = json.dumps([])

    return render_template('add_edit_store.html',
                           #products = products,
                           subtitle = "",
                           edit_item = edit_item,
                           editing = editing,
                           noindex = True)

@app.route('/new_store', methods=['POST'])
def new_store():
    if not check_human_data(request.form['human_check_id'], request.form['human_check_selected']):
        return '', 403
    store = get_form()
    r = post('stores', store)
    r_json = r.json()
    if r_json['_status']=='ERR':
        print (r.text)
        return '', 403
    _id = r_json['_id']
    return redirect('/?store={0}'.format(_id))


@app.route('/edit_store', methods=['POST'])
def edit_store():
    if not check_human_data(request.form['human_check_id'], request.form['human_check_selected']):
        return '', 403
    store = get_form(edit=True)
    _etag = request.form['_etag']
    _id = request.form['_id']
    r = patch('stores/{0}'.format(_id), store, _etag)
    print (r.text)
    return redirect('/?store={0}'.format(_id))
