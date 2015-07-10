import json
import random

from flask import jsonify

from web_server import app

from web_server.modules.wid import wid_chars
from web_server.modules.server_requests import get
from web_server.modules.server_requests import post


# HUMAN CHECK
@app.route('/human_check_add')
def human_check_add():
    emoji = random.choice(wid_chars)
    options = []
    for ch in wid_chars:
        options.append("{0:x}".format(ch))
    human_check = {
        'image': 'twemoji/36x36/{0:x}.png'.format(emoji),
        'options': options,
        'right_option': '{0:x}'.format(emoji),
        'type': 'emoji'
    }
    r = post('human_checks', human_check)

    return jsonify({'_id': r.json()['_id'],
                    'options': human_check['options'],
                    'type': 'emoji'})


@app.route('/human_check_image/<check_id>')
def human_check_image(check_id):
    check = get('human_checks/{0}'.format(check_id))
    return app.send_static_file(check['image'])
