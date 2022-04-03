from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only
from datetime import datetime
import sys

from models import Base, Order, Log

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)


@app.before_request
def create_session():
    g.session = scoped_session(DBSession)


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    sys.stdout.flush()
    g.session.commit()
    g.session.remove()


""" Suggested helper methods """


def check_sig(payload, sig):
    sender_pk = payload.get('pk')
    platform = payload.get('platform')
    if platform == 'Algorand':
        return algosdk.util.verify_bytes(json.dumps(payload).encode('utf-8'), sig, sender_pk)
    elif platform == 'Ethereum':
        msg = eth_account.messages.encode_defunct(text=json.dumps(payload))
        return eth_account.Account.recover_message(msg, signature=sig) == sender_pk


def fill_order(order, txes=[]):
    cur_order = Order(sender_pk=order['sender_pk'],
                      receiver_pk=order['receiver_pk'],
                      buy_currency=order['buy_currency'],
                      sell_currency=order['sell_currency'],
                      buy_amount=order['buy_amount'],
                      sell_amount=order['sell_amount'],)
    g.session.add(cur_order)
    g.session.commit()
    matched = g.session.query(Order).filter(Order.filled == None,
                                            Order.buy_currency == cur_order.sell_currency,
                                            Order.sell_currency == cur_order.buy_currency,
                                            Order.sell_amount / Order.buy_amount >= cur_order.buy_amount / cur_order.sell_amount).first()
    if matched != None:
        matched.filled = datetime.now()
        cur_order.filled = matched.filled
        matched.counterparty_d = cur_order.id
        cur_order.counterparty_d = matched.id

        if cur_order.buy_amount > matched.sell_amount:
            new_order = Order(sender_pk=cur_order.sender_pk,
                              receiver_pk=cur_order.receiver_pk,
                              buy_currency=cur_order.buy_currency,
                              sell_currency=cur_order.sell_currency,
                              buy_amount=cur_order.buy_amount - matched.sell_amount,
                              sell_amount=(cur_order.buy_amount - matched.sell_amount) * cur_order.sell_amount / cur_order.buy_amount,
                              creator_id=cur_order.id)

            g.session.add(new_order)
            g.session.commit()
        if matched.buy_amount > cur_order.sell_amount:
            new_order = Order(sender_pk=matched.sender_pk,
                              receiver_pk=matched.receiver_pk,
                              buy_currency=matched.buy_currency,
                              sell_currency=matched.sell_currency,
                              buy_amount=matched.buy_amount - cur_order.sell_amount,
                              sell_amount=(matched.buy_amount - cur_order.sell_amount) * matched.sell_amount / matched.buy_amount,
                              creator_id=matched.id)
            g.session.add(new_order)
            g.session.commit()

def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    # Hint: use json.dumps or str() to get it in a nice string form
    log = Log(message=json.dumps(d))
    g.session.add(log)
    g.session.commit()


""" End of helper methods """


@app.route('/trade', methods=['POST'])
def trade():
    print("In trade endpoint")
    if request.method == "POST":
        content = request.get_json(silent=True)
        print(f"content = {json.dumps(content)}")
        columns = ["sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform"]
        fields = ["sig", "payload"]

        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                print(json.dumps(content))
                log_message(content)
                return jsonify(False)

        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                print(json.dumps(content))
                log_message(content)
                return jsonify(False)

        # Your code here
        # Note that you can access the database session using g.session
        '''
        {'sig': signature,
        'payload': { 'sender_pk': public_key,
                     'receiver_pk': public_key,
                    'buy_currency': "Ethereum",
                    'sell_currency': "Algorand",
                    'buy_amount': 51,
                    'sell_amount': 257}
        '''
        # TODO: Check the signature
        sig = content.get('sig')
        payload = content.get('payload')
        if check_sig(payload, sig):
            # TODO: Add the order to the database
            order = {}
            order['sender_pk'] = payload['sender_pk']
            order['receiver_pk'] = payload['receiver_pk']
            order['buy_currency'] = payload['buy_currency']
            order['sell_currency'] = payload['sell_currency']
            order['buy_amount'] = payload['buy_amount']
            order['sell_amount'] = payload['sell_amount']
            order['signature'] = sig
            fill_order(order, txes=[])

        else:
            log_message(payload)
            return jsonify(False)
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        return jsonify(True)

@app.route('/order_book')
def order_book():
    # Your code here
    # Note that you can access the database session using g.session
    all_orders = g.session.query(Order).all()
    res = []
    for order in all_orders:
        cur = {}
        cur['sender_pk'] = order.sender_pk
        cur['receiver_pk'] = order.receiver_pk
        cur['buy_currency'] = order.buy_currency
        cur['sell_currency'] = order.sell_currency
        cur['buy_amount'] = order.buy_amount
        cur['sell_amount'] = order.sell_amount
        cur['signature'] = order.signature
        # cur['tx_id'] = order.tx_id
        res.append(cur)
    res_dict = {'data': res}
    return json.dumps(res_dict)


if __name__ == '__main__':
    app.run(port='5002')

