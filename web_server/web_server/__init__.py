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

from web_server.mail_client import send_mail

app = Flask(__name__)

app.config.from_object('web_server.config.Config')


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
                           products = products,
                           edit_item = edit_item,
                           editing = editing)


@app.route("/")
def home():
    if 'interpolate_places' in request.args:
        get('places?interpolate_places')
        return ("Interpolation OK")
    elif 'rebuild_places' in request.args:
        get('places?rebuild_places')
        return ("Rebuild OK")

    msg = ""
    query = ""
    product = ""
    product_name = "todo"
    latitude = ""
    longitude = ""
    here = False
    place_id = ""
    place_full_name = ""
    location_name = "cualquier lado"
    items = []

    if 'store' in request.args:
        items = get('stores/{0}'.format(request.args['store']))
    elif 'product' in request.args:
        product = request.args['product']
        #if 'product_name' in request.args:
        #    product_name = request.args['product_name']
        if product != '':
            product_db = get('products/{0}'.format(product))
            if product_db:
                product_name = product_db['name']
        if 'location_name' in request.args:
            location_name = request.args['location_name']
        if 'latitude' in request.args:
            latitude = request.args['latitude']
        if 'longitude' in request.args:
            longitude = request.args['longitude']
        if 'place_id' in request.args:
            place_id = request.args['place_id']
            if place_id != '':
                place = get('places/{0}'.format(place_id))
                if place:
                    place_full_name = place['name']
        #if 'place_full_name' in request.args:
        #    place_full_name = request.args['place_full_name']
        
        if latitude!='' and longitude!='':
            here = True
            items = get('stores?products={0}&latitude={1}&longitude={2}'.format(product, request.args['latitude'], request.args['longitude']))
        elif place_id!='':
            items = get('stores?products={0}&place_id={1}'.format(product, place_id))
        else:
            items = get('stores?products={0}'.format(product))
        query = request.args['product']
        
    return render_template('home.html',
                           msg = msg,
                           items = items,
                           latitude = latitude,
                           longitude = longitude,
                           here = here,
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
    
    r = {'products': products_items, 'places': place_items}
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
    
@app.route('/send_payment_instructions')
def send_payment_instructions():
    smtp_server = app.config['PAYMENT_SMTP_SERVER']
    from_ = app.config['PAYMENT_MAIL_FROM']
    username = app.config['PAYMENT_MAIL_USERNAME']
    password = app.config['PAYMENT_MAIL_PASSWORD']

    to = request.args.get('email')
    amount = request.args.get('amount')
    method = request.args.get('method')
    name = request.args.get('name')
    _id = request.args.get('id')

    #print( request.args )

    if not to or to == '':
        return '', 403

    if method not in ['pagomiscuentas', 'transfer', 'bitcoin']:
        return '', 403
        
    if not name:
        return '', 403

    if amount == 'year':
        amount_text = 'Pago de 1 año: $2000'
        saving_text = '$400'
    elif amount == 'month':
        amount_text = 'Pago de 1 mes: $200'
        saving_text = '$0'
    else:
        return '', 403

    text="""\
¡Hola!
Para destacar el comercio "{0}" siga estas instrucciones.

{1} (descuento: {2})

Métodos de pago disponibles:

Transferencia Bancaria
----------------------
Realice la transferencia a la siguiente cuenta,
luego responda este correo con el comprobante de transferencia correspondiente.
(Es importante que no modifique el asunto del correo)
            
Cuenta Corriente en pesos
Banco: BBVA Frances
Número: 270-7129/2
CBU: 0170270720000000712925
Titular: Gabriel Caraballo
CUIT: 20311134451

PagoMisCuentas
--------------
(Próximamente)

Bitcoin
-------
(Próximamente)

Atte.
Gabriel Caraballo
WIDU Transmedia

    """.format(name, amount_text, saving_text)
    
    html="""\
    <html>
        <head></head>
        <body>
            <p>¡Hola!</p>
            <p>Para destacar el comercio "{0}" siga estas instrucciones.</p>
            <p>{1} (descuento: {2})</p>
            <p>Métodos de pago disponibles</p>
            <p>Transferencia Bancaria</p>
            <p>
            Realice la transferencia a la siguiente cuenta,<br>
            luego responda este correo con el comprobante de transferencia correspondiente.<br>
            (Es importante que no modifique el asunto del correo)
            </p>
            Cuenta Corriente en pesos<br>
            Banco: BBVA Frances<br>
            Número: 270-7129/2<br>
            CBU: 0170270720000000712925<br>
            Titular: Gabriel Caraballo<br>
            CUIT: 20311134451<br>
            </p>
            
            <p>PagoMisCuentas</p>
            <p>(Próximamente)</p>

            <p>Bitcoin</p>
            <p>(Próximamente)</p>
        </body>
    </html>
    """.format(name, amount_text, saving_text)

    subject="Instrucciones de pago ({0})".format(_id)
    
    send_mail(from_, to, subject, text, html, smtp_server, username, password)
    return ''
