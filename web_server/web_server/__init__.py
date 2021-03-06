from flask import g
from flask import Flask
from flask import url_for
from flask import request
from flask import make_response
#from flask.ext.qrcode import QRcode

from flask.ext.babel import Babel


app = Flask(__name__)
babel = Babel(app)
#QRcode(app)

app.config.from_object('web_server.config.Config')

# Set locale
@babel.localeselector
def get_locale():
    locale = g.get('locale_babel')
    return locale

from web_server.modules.jinja_filters import nl2br
from web_server.modules.jinja_filters import char2emoji
from web_server.modules.jinja_filters import money_scale_inverse

from web_server.modules.home import home
from web_server.modules.home import robots
from web_server.modules.home import sitemap
from web_server.modules.home import atom
from web_server.modules.home import contacts
# STORES
from web_server.modules.stores import store_add
from web_server.modules.stores import new_store
from web_server.modules.stores import edit_store
# ACTIVITIES
from web_server.modules.activities import activities
from web_server.modules.activities import add_activity
from web_server.modules.activities import edit_activity
from web_server.modules.activities import activity_add_edit
# PRODUCTS
from web_server.modules.products import products
from web_server.modules.products import add_product
from web_server.modules.products import edit_product
from web_server.modules.products import product_add_edit
# PRODUCTS PROPERTIES
from web_server.modules.products_properties import products_properties
from web_server.modules.products_properties import add_product_property
from web_server.modules.products_properties import edit_product_property
from web_server.modules.products_properties import product_property_add_edit
# TIPS & TRICKS
from web_server.modules.tipstricks import tipstricks
from web_server.modules.tipstricks import add_tiptrick
from web_server.modules.tipstricks import edit_tiptrick
from web_server.modules.tipstricks import tiptrick_add_edit
# HUMAN_CHECK
from web_server.modules.human_check import human_check_add
from web_server.modules.human_check import human_check_image
# ABOUT
from web_server.modules.about import about
# BUILD QUERY
from web_server.modules.build_query import build_query
# PICTURES
from web_server.modules.pictures import add_client_picture
from web_server.modules.pictures import client_picture
from web_server.modules.pictures import client_pictures
from web_server.modules.pictures import client_picture_approve
from web_server.modules.pictures import add_client_picture
from web_server.modules.pictures import logo_picture
# PAYMENTS
from web_server.modules.payments import payments
from web_server.modules.payments import payment_add_edit
from web_server.modules.payments import add_payment
from web_server.modules.payments import edit_payment
from web_server.modules.payments import send_payment_instructions
# CALLBACKS
from web_server.modules.callbacks import bitcoin_callback
from web_server.modules.callbacks import mercadopago_callback
from web_server.modules.callbacks import test_callback
# BADGES
from web_server.modules.badge_stores import badge_stores
from web_server.modules.badge_stores import add_badge_store
from web_server.modules.badge_stores import edit_badge_store
from web_server.modules.badge_stores import badge_store_add_edit
