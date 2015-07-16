import os
import json
import requests

from requests.exceptions import MissingSchema
from requests.exceptions import ConnectionError

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
