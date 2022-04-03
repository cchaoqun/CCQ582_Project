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
    pass


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
            sender_pk = payload['sender_pk']
            receiver_pk = payload['receiver_pk']
            buy_currency = payload['buy_currency']
            sell_currency = payload['sell_currency']
            buy_amount = payload['buy_amount']
            sell_amount = payload['sell_amount']
            tx_id = payload['tx_id']
            # TODO: Fill the order
            order = Order(sender_pk=sender_pk, receiver_pk=receiver_pk, buy_currency=buy_currency, sell_currency=sell_currency, buy_amount=buy_amount, sell_amount=sell_amount, tx_id=tx_id)
            # TODO: commit
            g.session.add(order)
            g.session.commit()
        else:
            log_message(payload)
            return jsonify(False)
        # TODO: Be sure to return jsonify(True) or jsonify(False) depending on if the method was successful
        return jsonify(True)

@app.route('/order_book')
def order_book():
    # Your code here
    # Note that you can access the database session using g.session
    all_orders = g.session.query(Order)
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
        cur['tx_id'] = order.tx_id
        res.append(cur)
    return json.dumps(res)


if __name__ == '__main__':
    app.run(port='5002')