import random
import logging

from web_server import app

from flask import request
from flask import render_template
from flask import make_response

from web_server.modules.server_requests import get

# ROBOTS
@app.route("/robots.txt")
def robots():
    response = make_response(render_template('robots.txt'))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response

# SITEMAP
@app.route("/sitemap.xml")
def sitemap():
    canonical_domain = app.config['CANONICAL_DOMAIN']
    stores = get('stores')
    products = get('products')
    activities = get('activities')

    response = make_response(render_template('sitemap.xml',
                             stores = stores,
                             products = products,
                             activities = activities,
                             canonical_domain = canonical_domain))
    response.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return response

# HOME
@app.route("/")
def home():
    #if 'interpolate_places' in request.args:
    #    get('places?interpolate_places')
    #    return ("Interpolation OK")
    #elif 'rebuild_places' in request.args:
    #    get('places?rebuild_places')
    #    return ("Rebuild OK")

    msg = ""
    query = ""
    product = ""
    product_name = ""
    activity = ""
    activity_name = ""
    latitude = ""
    longitude = ""
    page = "1"
    here = False
    #place_id = ""
    #place_full_name = ""
    location_name = "cualquier lado"
    subtitle = ""
    page_description = "Alimentación Consciente, Vida Sustentable y Comercio Justo"
    items = None

    if 'store' in request.args:
        items = get('stores/{0}?inc_views=1'.format(request.args['store']))
        product_name = items[0]['name']
        page_description = items[0]['description']

    elif 'product' in request.args:
        if request.args['product']!='':
            product = request.args['product']
            product_db = get('products/{0}'.format(product))
            if product_db:
                product_name = product_db['name']
            query = request.args['product']
        else:
            product_name = "todo"
    if 'activity' in request.args and request.args['activity']!='':
        activity = request.args['activity']
        activity_db = get('activities/{0}'.format(activity))
        #print (activity_db)
        if activity_db:
            activity_name = activity_db['name']

    if 'location_name' in request.args:
        location_name = request.args['location_name']
    if 'latitude' in request.args:
        latitude = request.args['latitude']
    if 'longitude' in request.args:
        longitude = request.args['longitude']
    #if 'place_id' in request.args:
    #    place_id = request.args['place_id']
    #    if place_id != '':
    #        place = get('places/{0}'.format(place_id))
    #        if place:
    #            place_full_name = place['name']
    if 'page' in request.args:
        page = request.args['page']

    if latitude!='' and longitude!='':
        here = True
    if 'product' in request.args or 'activity' in request.args:
        items = get('stores?inc_views=1&product={0}&activity={1}&latitude={2}&longitude={3}&page={4}'.format(product, activity, latitude, longitude, page))
    
    if product_name != "":
        #subtitle = " - {0}".format(product_name)
        subtitle = product_name
    if activity_name != "":
        subtitle = activity_name

    #if place_id != '':
    #    subtitle = "{0} en {1}".format(subtitle, place_full_name)

    tiptrick = get('tipstricks')
    if len(tiptrick) > 0:
        tiptrick = random.choice(tiptrick)

    store_stats = get('store_stats')
    if store_stats:
        store_stats = store_stats[0]

    # PICTURES
    if items:
        for item in items:
            pictures_info = []
            for picture_id in item['client_pictures']:
                picture = get('client_pictures/{0}?projection=%7B%22picture_binary%22%3A0%7D'.format(picture_id))
                # TODO move to server
                if not picture['approved']:
                    continue
                if not 'name' in picture:
                    picture['name'] = ''
                picture_info = {
                    'name': picture['name'],
                    'approved': picture['approved'],
                    'admin_comments': picture['admin_comments'],
                    'score': picture['score'],
                    'id': picture_id
                }
                pictures_info.append( picture_info )
            item['pictures_info'] = pictures_info

    return render_template('home.html',
                           msg = msg,
                           items = items,
                           latitude = latitude,
                           longitude = longitude,
                           page = page,
                           here = here,
                           subtitle = subtitle,
                           page_description = page_description,
                           location_name = location_name,
                           product = product,
                           product_name = product_name,
                           activity = activity,
                           activity_name = activity_name,
                           canonical_domain = app.config['CANONICAL_DOMAIN'],
                           #place_full_name = place_full_name,
                           #place_id = place_id,
                           store_stats = store_stats,
                           tiptrick = tiptrick)
