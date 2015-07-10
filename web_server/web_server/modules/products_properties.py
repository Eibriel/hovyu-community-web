import json
import random

from web_server import app

from flask import request
from flask import redirect
from flask import render_template

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch


# PRODUCTS PROPERTIES
def get_product_property_form():
    product = {
        'name': request.form['name'],
    }
    return product


@app.route('/products_properties')
def products_properties():
    items = get('products_properties')
    return render_template('products_properties.html', items=items)


@app.route('/product_property_add_edit')
def product_property_add_edit():
    editing = False
    edit_item = {}

    if 'e' in request.args:
        editing = True
        edit_item = get('products_properties/{0}'.format(request.args['e']))
    return render_template('add_edit_product_property.html',
                            editing = editing,
                            edit_item = edit_item)


@app.route('/new_product_property', methods=['POST'])
def add_product_property():
    product = get_product_property_form()
    r = post('products_properties', product)
    #print (r.text)
    return redirect('/products_properties')


@app.route('/edit_product_property', methods=['POST'])
def edit_product_property():
    product = get_product_property_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    r = patch('products_properties/{0}'.format(_id), product, _etag)
    #print (r.text)
    return redirect('/products_properties')
