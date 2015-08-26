from web_server import app

from flask import request
from flask import jsonify

from web_server.modules.server_requests import get


#BUILD QUERY
@app.route('/build_query', methods=['POST'])
def build_query():
    items = get('activities?find_activities={0}'.format(request.form['q']))
    activities_items = []
    for item in items:
        activities_items.append({'_id': item['_id'], 'name': item['name']})

    items = get('stores?find_stores={0}'.format(request.form['q']))
    stores_items = []
    for item in items:
        full_name = "{0}({1})".format(item['name'], item.get('address', ''))
        stores_items.append({'_id': item['_id'], 'full_name': full_name})

    items = get('products?find_products={0}'.format(request.form['q']))
    products_items = []
    for item in items:
        products_items.append({'_id': item['_id'], 'name': item['name']})

    items = get('products_properties?find_products_properties={0}'.format(request.form['q']))
    products_properties_items = []
    for item in items:
        products_properties_items.append({'_id': item['_id'], 'name': item['name']})

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
        longitude = item['location']['coordinates'][0]
        latitude = item['location']['coordinates'][1]

        place_items.append({'_id': item['_id'],
                            'name': item['name'],
                            'full_name': full_name,
                            'osm_id': osm_id,
                            'latitude': latitude,
                            'longitude': longitude})

    r = {'products': products_items,
        'products_properties': products_properties_items,
        'places': place_items,
        'stores': stores_items,
        'activities': activities_items}
    return jsonify(r)
