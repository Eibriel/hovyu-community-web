import random
import logging

from flask.ext.babel import gettext

from web_server import app
from web_server import babel

from flask import g
from flask import request
from flask import redirect
from flask import render_template
from flask import make_response

from datetime import datetime

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch
from web_server.modules.server_requests import get_pictures_info
from web_server.modules.localization import domain_selector
from web_server.modules.localization import get_current_domain
from web_server.modules.localization import get_localized_domains


# ROBOTS
@app.route("/robots.txt")
def robots():
    response = make_response(render_template('robots.txt'))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


# CONTACT LIST
@app.route("/contacts.txt")
def contacts():
    current_domain = get_current_domain()
    stores = get('stores')
    response = make_response(render_template('contacts.txt',
                             stores = stores,
                             current_domain = current_domain))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


# ATOM
@app.route("/atom.xml")
def atom():
    canonical_domain = app.config['CANONICAL_DOMAIN']
    stores = get('stores')

    for store in stores:
        date = datetime.strptime(store['_updated'], '%a, %d %b %Y %H:%M:%S %Z')
        store['_formated_updated'] = date.strftime("%Y-%m-%dT%H:%M:%SZ")
        # 2002-10-02T15:00:00Z
        store['pictures_info'] = get_pictures_info( store )

    response = make_response(render_template('atom.xml',
                             stores = stores,
                             canonical_domain = canonical_domain))
    response.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return response


# SITEMAP
@app.route("/sitemap.xml")
def sitemap():
    canonical_domain = app.config['CANONICAL_DOMAIN']
    stores = get('stores')
    products = get('products')
    activities = get('activities')

    for store in stores:
        date = datetime.strptime(store['_updated'], '%a, %d %b %Y %H:%M:%S %Z')
        store['_formated_updated'] = date.strftime("%Y-%m-%d")
        store['pictures_info'] = get_pictures_info( store )

    response = make_response(render_template('sitemap.xml',
                             stores = stores,
                             products = products,
                             activities = activities,
                             canonical_domain = canonical_domain,
                             localizations = get_localized_domains()))
    response.headers['Content-Type'] = 'text/xml; charset=utf-8'
    return response


# CONTACT LIST
@app.route("/access_log.txt")
def access_log():
    current_domain = get_current_domain()
    logs = get('access_log?sort=-_updated')
    response = make_response(render_template('access_log.txt',
                             logs = logs,
                             current_domain = current_domain))
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response


# HOME
@app.route("/")
def home():
    located_urls, redirect_response = domain_selector()
    if redirect_response:
        return redirect_response

    import hashlib
    ip = '{1}{0}'.format(app.config['IP_LOG_SALT'], request.environ['REMOTE_ADDR'])
    ip = ip.encode('utf-8')
    ip_md5 = hashlib.sha224( ip ).hexdigest()
    access_log = {
        'page': request.url,
        'ip_md5': ip_md5,
        'useragent': request.user_agent.string,
        'useragent_platform': request.user_agent.platform,
        'useragent_browser': request.user_agent.browser,
        'useragent_version': request.user_agent.version,
        'useragent_language': request.user_agent.language,
        'acceptlanguage': request.accept_languages.to_header(),
        'referrer': request.referrer
    }

    #logging.error( access_log )
    r = post('access_log', access_log)
    #logging.error( r.text )

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
    store_profile = False

    if 'store' in request.args:
        items = get('stores/{0}?inc_views=1'.format(request.args['store']))
        if len(items) > 0:
            product_name = items[0]['name']
            page_description = items[0]['description']
            store_profile = True

    elif 'product' in request.args:
        if request.args['product']!='':
            product = request.args['product']
            product_db = get('products/{0}?inc_count=1'.format(product))
            if product_db:
                product_name = product_db['name']
            query = request.args['product']
            #current_use_count = 0
            #if 'use_count' in product_db:
            #    current_use_count = product_db['use_count']
            #use_count = {
            #    'use_count': current_use_count + 1
            #}
            #r = patch('products/{0}'.format(product), use_count, product_db['_etag'])
            #logging.error( r.text )
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
    elif not 'store' in request.args:
        items = get('stores?max_results=5&sort=-_updated')

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
    #tiptrick = []

    organizations_stats = get('store_stats')
    if organizations_stats:
        organizations_stats = organizations_stats[0]

    # PICTURES
    if items:
        for item in items:
            pictures_info = get_pictures_info( item )
            item['client_pictures'] = []
            item['process_pictures'] = []
            #item['pictures_info'] = pictures_info
            for picture in pictures_info:
                if picture['album'] == 'client':
                    item['client_pictures'].append( picture )
                elif picture['album'] == 'process':
                    item['process_pictures'].append( picture )

    current_domain = get_current_domain()

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
                           current_domain = current_domain,
                           located_urls = located_urls,
                           locale = g.get('locale'),
                           #place_full_name = place_full_name,
                           #place_id = place_id,
                           organizations_stats = organizations_stats,
                           tiptrick = tiptrick,
                           store_profile = store_profile)
