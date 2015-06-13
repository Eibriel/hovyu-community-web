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
    
    return r


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


@app.route("/store_add_edit")
def store_add():
    editing = False
    edit_item = {}
    
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
            products = get('products')
            for product in edit_item['products']:
                for product_ in products:
                    if product_['_id'] == product:
                        products_json.append(product_)
            edit_item['products_json'] = json.dumps(products_json)
        else:
            edit_item['products_json'] = []
    
    if 'location' not in edit_item:
        edit_item['location'] = None
        
    return render_template('add_edit_store.html',
                           edit_item = edit_item,
                           editing = editing)


@app.route("/")
def home():
    msg = ""
    query = ""
    product = ""
    product_name = "todo"
    latitude = ""
    longitude = ""
    location_name = "cualquier lado"
    items = []
    
    products = get('products')

    if 'store' in request.args:
        items = get('stores/{0}'.format(request.args['store']))
        print (items)
    elif 'product' in request.args:
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
        'exact_location': False
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
    else:
        latitude = 0.0
        longitude = 0.0
        
    store['location'] = {"type":"Point","coordinates":[latitude, longitude]}
    
    if 'exact_location' in request.form:
        store['exact_location'] = True
    
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
    r = post('stores', store)
    _store = r.json()['_id']
    return redirect('/?store={0}'.format(_store))


@app.route('/edit_store', methods=['POST'])
def edit_store():
    store = get_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    patch('stores/{0}'.format(_id), store, _etag)
    return redirect('/?store={0}'.format(_id))


@app.route('/payments')
def payments():
    items = get('payments')
    stats = get('payment_stats')[0]
    return render_template('payments.html', items=items, stats=stats)


@app.route('/payment_add_edit')
def payment_add_edit():
    editing = False
    edit_item = {}
    
    if 'e' in request.args:
        editing = True
        edit_item = get('payments/{0}'.format(request.args['e']))
        #print (edit_item)
        #edit_item = edit_item[0]
    return render_template('add_edit_payment.html',
                            editing = editing,
                            edit_item = edit_item)

def get_payment_form():
    payment = {
        'payment_method': request.form['payment_method'],
        'description': request.form['description'],
        'store_id': '554ce34116a24e0fe8197493',
        'currency': request.form['currency'],
        'amount': float(request.form['amount']),
        'day_cost': float(request.form['day_cost']),
        'completed': False,
        'refunded': False,
        'refund_description': request.form['refund_description'],
    }
    if 'completed' in request.form:
        payment['completed'] = True
    if 'refunded' in request.form:
        payment['refunded'] = True
        
    return payment


@app.route('/new_payment', methods=['POST'])
def add_payment():
    payment = get_payment_form()
    r = post('payments', payment)
    print (r.text)
    return redirect('/payments')
    
@app.route('/edit_payment', methods=['POST'])
def edit_payment():
    payment = get_payment_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    patch('payments/{0}'.format(_id), payment, _etag)
    return redirect('/payments')

