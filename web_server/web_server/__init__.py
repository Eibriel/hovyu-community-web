import os
import json
import requests

from flask import Flask
from flask import url_for
from flask import jsonify
from flask import request
from flask import redirect
from flask import render_template

from requests.exceptions import MissingSchema
from requests.exceptions import ConnectionError

app = Flask(__name__)


def getserverip():
    ip = None
    try:
        ip = os.environ['COMUNIDAD_MAIN_1_PORT_80_TCP_ADDR']
    except KeyError:
        ip = '127.0.0.1:5000'
        pass
    return ip


def get(resource):
    items = []
    try:
        r = requests.get('http://{0}/{1}'.format(getserverip(), resource))
        json = r.json()
        if '_items' in json:
            items = json['_items']
        else:
            items = json
    except MissingSchema:
        msg = "MissingSchema"
    except ConnectionError:
        msg = "ConnectionError"
        
    return items


def post(resource, data):
    serverip = getserverip()
    headers = {'Content-Type': 'application/json'}
    
    try:
        r = requests.post('http://{0}/{1}/'.format(serverip, resource),
                          data=json.dumps(data),
                          headers=headers)
    except MissingSchema:
        msg = "MissingSchema"
    except ConnectionError:
        msg = "ConnectionError"


def patch(resource, data, eTag):
    serverip = getserverip()
    headers = {'Content-Type': 'application/json', 'If-Match': eTag}
    
    try:
        r = requests.patch('http://{0}/{1}'.format(serverip, resource),
                          data=json.dumps(data),
                          headers=headers)
        print (r.text)
    except MissingSchema:
        msg = "MissingSchema"
    except ConnectionError:
        msg = "ConnectionError"


@app.route("/store_add")
def store_add():
    return "Add Store"
    

@app.route("/store_edit")
def store_edit():
    return "Edit Store"


@app.route("/")
def home():
    msg = ""
    query = ""
    product = ""
    product_name = "todo"
    latitude = ""
    longitude = ""
    location_name = "cualquier lado"
    edit_item = {}
    items = []
    editing = False
    
    products = get('products')
    
    if 'e' in request.args:
        editing = True
        edit_item = get('stores/{0}'.format(request.args['e']))
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
            for product in edit_item['products']:
                for product_ in products:
                    if product_['_id'] == product:
                        products_json.append(product_)
            edit_item['products_json'] = json.dumps(products_json)
        else:
            edit_item['products_json'] = []

    if 'location' not in edit_item:
        edit_item['location'] = None

    if 'product' in request.args:
        product = request.args['product']
        if 'product_name' in request.args:
            product_name = request.args['product_name']
        if 'location_name' in request.args:
            location_name = request.args['location_name']
        if 'latitude' in request.args and 'longitude' in request.args:
            latitude = request.args['latitude']
            longitude = request.args['longitude']
            items = get('stores?products={0}&latitude={1}&longitude={2}'.format(request.args['product'], request.args['latitude'], request.args['longitude']))
        else:
            items = get('stores?products={0}'.format(request.args['product']))
        query = request.args['product']
        
    return render_template('home.html',
                           msg = msg,
                           products = products,
                           edit_item=edit_item,
                           editing=editing,
                           items = items,
                           latitude = latitude,
                           longitude = longitude,
                           location_name = location_name,
                           product = product,
                           product_name = product_name)


def get_form():
    store = {
        'name': request.form['name'],
        'description': request.form['description'],
        'address': request.form['address'],
        'country': '554ce34116a24e0fe8197493',
        'highlight': False,
        'score': {
            'count': 0,
            'sum': 0
        },
        'views': 0,
        'email': request.form['email'],
        'website': [],
        'tel': [],
    }
    
    websites_json = json.loads(request.form['websites_json'])
    store['website'] = websites_json
    
    tels_json = json.loads(request.form['tels_json'])
    store['tel'] = tels_json
    
    products_json = json.loads(request.form['products_json'])
    products = []
    for product in products_json:
        products.append(product['_id'])
    store['products'] = products
    
    if request.form['latitude'] != '' and request.form['longitude'] != '':
        latitude = float(request.form['latitude'])
        longitude = float(request.form['longitude'])
        store['location'] = {"type":"Point","coordinates":[latitude, longitude]}
    else:
        store['location'] = None
    
    return store

@app.route('/build_query', methods=['POST'])
def build_query():
    items = get('products?find_products={0}'.format(request.form['q']))
    products_items = []
    for item in items:
        products_items.append({'_id': item['_id'], 'name': item['name']})
    
    items = get('points_of_interest?find_places={0}'.format(request.form['q']))
    places_items = ['aquí', 'cualquier lado']
    for item in items:
        places_items.append(item['name'])
    
    r = {'products': products_items, 'places': places_items}
    return jsonify(r)

@app.route('/new_store', methods=['POST'])
def new_store():
    store = get_form()
    post('stores', store)
    return redirect('/?store={0}'.format('123'))


@app.route('/edit_store', methods=['POST'])
def edit_store():
    store = get_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    patch('stores/{0}'.format(_id), store, _etag)
    return redirect('/?store={0}'.format(_id))



