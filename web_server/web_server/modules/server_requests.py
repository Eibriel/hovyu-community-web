import os
import json
import requests

from requests.exceptions import MissingSchema
from requests.exceptions import ConnectionError
from requests.auth import HTTPBasicAuth

def get_pictures_info(item):
    pictures_info = []
    for picture_id in item['client_pictures']:
        picture = get('client_pictures/{0}?projection=%7B%22picture_binary%22%3A0%7D'.format(picture_id))
        # TODO move to server
        if not picture['approved']:
            continue
        if not 'name' in picture:
            picture['name'] = ''
        if not 'album' in picture:
            picture['album'] = 'client'
        picture_info = {
            'name': picture['name'],
            'album': picture['album'],
            'approved': picture['approved'],
            'admin_comments': picture['admin_comments'],
            'score': picture['score'],
            'id': picture_id,
            'etag': picture['_etag']
        }
        pictures_info.append( picture_info )
    return pictures_info


def getserverip():
    ip = None
    try:
        ip = os.environ['WIDU_MAIN_1_PORT_80_TCP_ADDR']
    except KeyError:
        pass
    try:
        ip = os.environ['WIDUDEV_DEVMAIN_1_PORT_80_TCP_ADDR']
    except KeyError:
        pass
    if ip == None:
        ip = '127.0.0.1:5000'
    #print ("IP: {0}".format(ip))
    return ip


#def credentials(username, password):
#   return b64encode(b"{0}:{1}".format(username, password)).decode("ascii")


def get(resource, params = None):
    items = []
    try:
        r = requests.get('http://{0}/{1}'.format(getserverip(), resource), params = params)
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


def post(resource, data, password = None, files = None):
    serverip = getserverip()
    headers = {'Content-Type': 'application/json'}
    if password != None:
        auth = ('a', password)
    else:
        auth = None
    if files:
        data = data
        json = None
        headers = {} 
    else:
        json = data
        data = None

    try:
        r = requests.post('http://{0}/{1}/'.format(serverip, resource),
                          data=data,
                          json=json,
                          files=files,
                          headers=headers,
                          auth = auth)
    except MissingSchema:
        msg = "MissingSchema"
    except ConnectionError:
        msg = "ConnectionError"

    return r


def patch(resource, data, eTag, password = None):
    serverip = getserverip()
    headers = {'Content-Type': 'application/json', 'If-Match': eTag}
    if password != None:
        auth = ('a', password)
    else:
        auth = None

    try:
        r = requests.patch('http://{0}/{1}'.format(serverip, resource),
                          json=data,
                          headers=headers,
                          auth = auth)
    except MissingSchema:
        msg = "MissingSchema"
    except ConnectionError:
        msg = "ConnectionError"

    return r

def delete(resource, eTag):
    serverip = getserverip()
    headers = {'Content-Type': 'application/json', 'If-Match': eTag}

    try:
        r = requests.delete('http://{0}/{1}'.format(serverip, resource),
                          headers=headers)
    except MissingSchema:
        msg = "MissingSchema"
    except ConnectionError:
        msg = "ConnectionError"

    return r
