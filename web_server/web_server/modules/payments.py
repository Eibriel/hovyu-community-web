from web_server import app

from flask import request
from flask import redirect
from flask import render_template

from datetime import datetime

from web_server.modules.server_requests import get
from web_server.modules.server_requests import post
from web_server.modules.server_requests import patch

# PAYMENTS
def get_payment_form():
    payment = {
        'payment_method': request.form['payment_method'],
        'description': request.form['description'],
        'email': request.form['email'],
        'badge': request.form['badge'],
        'months': int(request.form['months']),
        'store_id': request.form['store_id'],
        'currency': request.form['currency'],
        'amount': float(request.form['amount']),
        'real_amount': float(request.form['real_amount']),
        'completed': False,
        'completion_date': None,
        'refunded': False,
        'refund_description': request.form['refund_description'],
    }
    if 'completed' in request.form:
        payment['completed'] = True
    if 'refunded' in request.form:
        payment['refunded'] = True

    if request.form['completion_date'] != '':
        payment['completion_date'] = datetime.strptime(payment['completion_date'], '%d/%m/%Y')
        payment['completion_date'] = payment['completion_date'].strftime("%a, %d %b %Y %H:%M:%S GMT")

    return payment


@app.route('/payments')
def payments():
    items = get('payments?sort=-_updated')
    stats = get('payment_stats')[0]
    return render_template('payments.html',
                            items=items,
                            stats=stats,
                            noindex = True,
                            subtitle = 'Payments')


@app.route('/payment_add_edit')
def payment_add_edit():
    editing = False
    edit_item = {}

    if 'e' in request.args:
        editing = True
        edit_item = get('payments/{0}'.format(request.args['e']))
    return render_template('add_edit_payment.html',
                            editing = editing,
                            edit_item = edit_item,
                            subtitle = 'Payment add edit')


@app.route('/new_payment', methods=['POST'])
def add_payment():
    payment = get_payment_form()

    # Security Averride
    payment['real_amount'] = 0
    payment['completed'] = False
    payment['refunded'] = False

    r = post('payments', payment)

    return redirect('/payments')


@app.route('/edit_payment', methods=['POST'])
def edit_payment():
    payment = get_payment_form()
    password = request.form['admin_password']
    _etag = request.form['_etag']
    _id = request.form['_id']
    r = patch('payments/{0}'.format(_id), payment, _etag, password)
    print (r.text)
    return redirect('/payments')


@app.route('/send_payment_instructions')
def send_payment_instructions():
    email = request.args.get('email')
    method = request.args.get('method')
    #product = request.args.get('product')
    country = request.args.get('country')
    badge = request.args.get('badge')
    months = request.args.get('months')
    _id = request.args.get('id')
    iid = request.args.get('iid')
    name = request.args.get('name')

    if not email or email == '':
        return '', 403
    if method not in ['pagomiscuentas', 'mercadopago', 'local_bank', 'bitcoin']:
        return '', 403
    if not name:
        return '', 403
    if not badge:
        return '', 403
    if not months:
        return '', 403
    if not _id:
        return '', 403
    if not iid:
        return '', 403

    try:
        months = int(months)
    except:
        return '', 403

    #if product not in ['highlight_one_year', 'highlight_one_month']:
    #    return '', 403

    payment = {
        'payment_method': method,
        'description': '',
        'email': email,
        #'product': product,
        'country': country,
        'badge': badge,
        'months': months,
        'store_id': _id,
        'completed': False,
        'refunded': False,
        'refund_description': '',
    }
    r = post('payments', payment)
    #print (r.text)
    return ''
