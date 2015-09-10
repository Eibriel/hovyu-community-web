# PAYMENTS
def get_payment_form():
    payment = {
        'payment_method': request.form['payment_method'],
        'description': request.form['description'],
        'email': request.form['email'],
        'store_id': request.form['store_id'],
        'currency': request.form['currency'],
        'amount': float(request.form['amount']),
        'day_cost': float(request.form['day_cost']),
        'completed': False,
        'refunded': False,
        'refund_description': request.form['refund_description'],
    }
    if 'completed' in request.form:
        payment['completed'] = True
    if 'refunded' in request.form:
        payment['refunded'] = True
    return payment


@app.route('/payments')
def payments():
    items = get('payments')
    stats = get('payment_stats')[0]
    return render_template('payments.html', items=items, stats=stats, noindex = True)


@app.route('/payment_add_edit')
def payment_add_edit():
    editing = False
    edit_item = {}

    if 'e' in request.args:
        editing = True
        edit_item = get('payments/{0}'.format(request.args['e']))
        #print (edit_item)
        #edit_item = edit_item[0]
    return render_template('add_edit_payment.html',
                            editing = editing,
                            edit_item = edit_item)


@app.route('/new_payment', methods=['POST'])
def add_payment():
    payment = get_payment_form()
    r = post('payments', payment)
    #print (r.text)
    return redirect('/payments')


@app.route('/edit_payment', methods=['POST'])
def edit_payment():
    payment = get_payment_form()
    _etag = request.form['_etag']
    _id = request.form['_id']
    patch('payments/{0}'.format(_id), payment, _etag)
    return redirect('/payments')


@app.route('/send_payment_instructions')
def send_payment_instructions():
    email = request.args.get('email')
    product = request.args.get('product')
    country = request.args.get('country')
    method = request.args.get('method')
    name = request.args.get('name')
    _id = request.args.get('id')
    iid = request.args.get('iid')

    if not email or email == '':
        return '', 403
    if method not in ['pagomiscuentas', 'mercadopago', 'local_bank', 'bitcoin']:
        return '', 403
    if not name:
        return '', 403
    if not _id:
        return '', 403
    if not iid:
        return '', 403

    if product not in ['highlight_one_year', 'highlight_one_month']:
        return '', 403

    payment = {
        'payment_method': method,
        'description': '',
        'email': email,
        'product': product,
        'country': country,
        'store_id': _id,
        'completed': False,
        'refunded': False,
        'refund_description': '',
    }
    r = post('payments', payment)
    print (r.text)
    return ''
