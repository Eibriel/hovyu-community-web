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


# nl2br ###########################
import re

from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result 
###################################


def getserverip():
    ip = None
    try:
        ip = os.environ['WIDU_MAIN_1_PORT_80_TCP_ADDR']
    except KeyError:
        ip = '127.0.0.1:5000'
    #print ("IP: {0}".format(ip))
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
    except MissingSchema:
        msg = "MissingSchema"
    except ConnectionError:
        msg = "ConnectionError"
    
    return r


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
    place_id = ""
    place_full_name = ""
    location_name = "cualquier lado"
    items = []
    
    products = get('products')

    if 'store' in request.args:
        items = get('stores/{0}'.format(request.args['store']))
    elif 'product' in request.args:
        product = request.args['product']
        if 'product_name' in request.args:
            product_name = request.args['product_name']
        if 'location_name' in request.args:
            location_name = request.args['location_name']
        if 'latitude' in request.args:
            latitude = request.args['latitude']
        if 'longitude' in request.args:
            longitude = request.args['longitude']
        if 'place_id' in request.args:
            place_id = request.args['place_id']
        if 'place_full_name' in request.args:
            place_full_name = request.args['place_full_name']
        
        if latitude!='' and longitude!='':
            items = get('stores?products={0}&latitude={1}&longitude={2}'.format(product, request.args['latitude'], request.args['longitude']))
        elif place_id!='':
            items = get('stores?products={0}&place_id={1}'.format(product, place_id))
        else:
            items = get('stores?products={0}'.format(product))
        query = request.args['product']
        
    return render_template('home.html',
                           msg = msg,
                           products = products,
                           items = items,
                           latitude = latitude,
                           longitude = longitude,
                           location_name = location_name,
                           product = product,
                           product_name = product_name,
                           place_full_name = place_full_name,
                           place_id = place_id)


def get_form():
    store = {
        'name': request.form['name'],
        'description': request.form['description'],
        'address': request.form['address'],
        'country': '554ce34116a24e0fe8197493',
        'place': None,
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
    return store

@app.route('/build_query', methods=['POST'])
def build_query():
    items = get('products?find_products={0}'.format(request.form['q']))
    products_items = []
    for item in items:
        products_items.append({'_id': item['_id'], 'name': item['name']})
    
    items = get('points_of_interest?find_points={0}'.format(request.form['q']))
    point_items = ['aquí', 'cualquier lado']
    for item in items:
        point_items.append(item['name'])
        
    items = get('places?find_places={0}'.format(request.form['q']))
    place_items = []
    for item in items:
        full_name = item['name']
        city = item['is_in']['city']
        state = item['is_in']['state']
        country = item['is_in']['country']
        if city:
            full_name = "{0}, {1}".format(full_name, city)
        if state:
            full_name = "{0}, {1}".format(full_name, state)
        if country:
            full_name = "{0}, {1}".format(full_name, country)
        
        if not city and not state and not country:
            near_name = item['near_place']['name']
            near_city = item['near_place']['city']
            near_state = item['near_place']['state']
            near_country = item['near_place']['country']
            full_name = "{0} ({1}".format(full_name, near_name)
            if near_city:
                full_name = "{0}, {1}".format(full_name, near_city)
            if near_state:
                full_name = "{0}, {1}".format(full_name, near_state)
            if near_country:
                full_name = "{0}, {1}".format(full_name, near_country)
            full_name = "{0})".format(full_name)
            
        osm_id = item['osm_id']
        latitude = item['location']['coordinates'][0]
        longitude = item['location']['coordinates'][1]
        
        place_items.append({'_id': item['_id'],
                            'name': item['name'],
                            'full_name': full_name,
                            'osm_id': osm_id,
                            'latitude': latitude,
                            'longitude': longitude})
    
    r = {'products': products_items, 'points': point_items, 'places': place_items}
    return jsonify(r)

@app.route('/new_store', methods=['POST'])
def new_store(): 
    store = get_form()
    r = post('stores', store)
    _id = r.json()['_id']
    return redirect('/?store={0}'.format(_id))


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

# PRODUCTS

@app.route('/products')
def products():
    items = get('products')
    return render_template('products.html', items=items)


@app.route('/product_add_edit')
def product_add_edit():
    editing = False
    edit_item = {}
    
    if 'e' in request.args:
        editing = True
        edit_item = get('products/{0}'.format(request.args['e']))
    return render_template('add_edit_product.html',
                            editing = editing,
                            edit_item = edit_item)


def get_product_form():
    product = {
        'name': request.form['name'],
        'description': request.form['description'],
        'wiktionary': request.form['wiktionary']
    }
        
    return product


@app.route('/new_product', methods=['POST'])
def add_product():
    product = get_product_form()
    r = post('products', product)
    print (r.text)
    return redirect('/products')


@app.route('/edit_product', methods=['POST'])
def edit_product():
    product = get_product_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    r = patch('products/{0}'.format(_id), product, _etag)
    print (r.text)
    return redirect('/products')
