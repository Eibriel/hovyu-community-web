

# CALLBAKS
from bson import ObjectId
@app.route('/bitcoin_callback/<payment_id>/<secret>')
def bitcoin_callback(payment_id, secret):
    return_text = ""
    if not ObjectId.is_valid(payment_id):
        return 'Invalid ObjectID', 400
    input_address = request.args['input_address']
    destination_address = request.args['destination_address']
    transaction_hash = request.args['transaction_hash']
    input_transaction_hash = request.args['input_transaction_hash']
    confirmations = int(request.args['confirmations'])
    value = int(request.args['value'])

    item = get('payments/{0}?callback=bitcoin\
&input_address={1}\
&destination_address={2}\
&transaction_hash={3}\
&input_transaction_hash={4}\
&confirmations={5}\
&value={6}\
&secret={7}'.format(payment_id, input_address, destination_address, transaction_hash, input_transaction_hash, confirmations, value, secret))

    #print (item)
    #print (item['_status'])
    #print (r.status_code)
    if '_status' in item and item['_status']=='ERR':
        return '', 400
    else:
        resp = make_response('*ok*', 200)
        resp.mimetype = 'text/plain'
        return resp


@app.route('/mercadopago_callback/<payment_id>/<secret>', methods=['POST'])
def mercadopago_callback(payment_id, secret):
    print (request.args)
    topic = request.args['topic']
    notification_id = request.args['id']
    item = get('payments/{0}?callback=mercadopago&topic={1}&notification_id={2}'.format(payment_id, topic, notification_id))
    #print (item)
    if '_status' in item and item['_status']=='ERR':
        return '', 400
    else:
        return '', 200
