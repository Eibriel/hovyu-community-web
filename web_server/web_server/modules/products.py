import json
import random

from web_server import app

from flask import request
from flask import redirect
from flask import render_template

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch


# PRODUCTS
def get_product_form():
    product = {
        'name': request.form['name'],
    }
    return product


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


@app.route('/new_product', methods=['POST'])
def add_product():
    product = get_product_form()
    r = post('products', product)
    #print (r.text)
    return redirect('/products')


@app.route('/edit_product', methods=['POST'])
def edit_product():
    product = get_product_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    r = patch('products/{0}'.format(_id), product, _etag)
    #print (r.text)
    return redirect('/products')
