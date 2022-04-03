# from flask import Flask, request, g
# from flask_restful import Resource, Api
# from sqlalchemy import create_engine, select, MetaData, Table
# from flask import jsonify
# import json
# import eth_account
# import algosdk
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import scoped_session
# from sqlalchemy.orm import load_only
#
# from models import Base, Order, Log
#
# engine = create_engine('sqlite:///orders.db')
# Base.metadata.bind = engine
# DBSession = sessionmaker(bind=engine)
#
# app = Flask(__name__)
#
#
# # These decorators allow you to use g.session to access the database inside the request code
# @app.before_request
# def create_session():
#     g.session = scoped_session(
#         DBSession)  # g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals
#
#
# @app.teardown_appcontext
# def shutdown_session(response_or_exc):
#     g.session.commit()
#     g.session.remove()
#
#
# """
# -------- Helper methods (feel free to add your own!) -------
# """
#
#
# def log_message(d):
#     # Takes input dictionary d and writes it to the Log table
#     msg = json.dumps(d)
#     log = Log(message=msg)
#     g.session.add(log)
#     g.session.commit()
#
#
# """
# ---------------- Endpoints ----------------
# """
#
#
# @app.route('/trade', methods=['POST'])
# def trade():
#     if request.method == "POST":
#         content = request.get_json(silent=True)
#         print(f"content = {json.dumps(content)}")
#         columns = ["sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform"]
#         fields = ["sig", "payload"]
#         error = False
#         for field in fields:
#             if not field in content.keys():
#                 print(f"{field} not received by Trade")
#                 print(json.dumps(content))
#                 log_message(content)
#                 return jsonify(False)
#
#         error = False
#         for column in columns:
#             if not column in content['payload'].keys():
#                 print(f"{column} not received by Trade")
#                 error = True
#         if error:
#             print(json.dumps(content))
#             log_message(content)
#             return jsonify(False)
#
#         # Your code here
#         # Note that you can access the database session using g.session
#         '''
#         {'sig': signature,
#         'payload': { 'sender_pk': public_key,
#                      'receiver_pk': public_key,
#                     'buy_currency': "Ethereum",
#                     'sell_currency': "Algorand",
#                     'buy_amount': 51,
#                     'sell_amount': 257,
#                     'platform': 'Algorand'
#                     }
#         '''
#         # get fields
#         sig = content['sig']
#         payload = content['payload']
#         sender_pk = payload['sender_pk']
#         buy_currency = payload['buy_currency']
#         sell_currency = payload['sell_currency']
#         buy_amount = payload['buy_amount']
#         sell_amount = payload['sell_amount']
#         platform = payload['platform']
#
#         # verify sig for each platform
#         shouldOrder = False
#         if platform == 'Algorand':
#             shouldOrder = algosdk.util.verify_bytes(json.dumps(payload).encode('utf-8'), sig, sender_pk)
#         elif platform == 'Ethereum':
#             shouldOrder = eth_account.Account.recover_message(eth_account.messages.encode_defunct(text=json.dumps(payload)), signature=sig) == sender_pk
#
#         if shouldOrder:
#             order = Order(signature=sig, sender_pk=sender_pk, buy_currency=buy_currency, sell_currency=sell_currency, buy_amount=buy_amount, sell_amount=sell_amount)
#             g.session.add(order)
#             g.session.commit()
#         return jsonify(shouldOrder)
#     else:
#         return jsonify(True)
#
#
#
# @app.route('/order_book')
# def order_book():
#     # Your code here
#     # Note that you can access the database session using g.session
#     '''
#     {'data': [
#   {'sender_pk':'...',
#    'receiver_pk':'...',
#    'buy_currency':'...',
#    'sell_currency':'...',
#    'buy_amount':'...',
#    'sell_amount':'...',
#    'signature': '...'},
#     '''
#     all_orders = g.session.query(Order)
#     res = {'data': []}
#     for order in all_orders:
#         cur = {}
#         cur['sender_pk'] = order.sender_pk
#         cur['receiver_pk'] = order.receiver_pk
#         cur['buy_currency'] = order.buy_currency
#         cur['sell_currency'] = order.sell_currency
#         cur['buy_amount'] = order.buy_amount
#         cur['sell_amount'] = order.sell_amount
#         cur['signature'] = order.signature
#         res['data'].append(cur)
#     return res
#
# if __name__ == '__main__':
#     app.run(port='5002')


from flask import Flask, request, g
from flask_restful import Resource, Api
from sqlalchemy import create_engine, select, MetaData, Table
from flask import jsonify
import json
import eth_account
import algosdk
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import load_only

from models import Base, Order, Log

engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

app = Flask(__name__)


# These decorators allow you to use g.session to access the database inside the request code
@app.before_request
def create_session():
    g.session = scoped_session(
        DBSession)  # g is an "application global" https://flask.palletsprojects.com/en/1.1.x/api/#application-globals


@app.teardown_appcontext
def shutdown_session(response_or_exc):
    g.session.commit()
    g.session.remove()


"""
-------- Helper methods (feel free to add your own!) -------
"""


def log_message(d):
    # Takes input dictionary d and writes it to the Log table
    new_log = Log(message=json.dumps(d))
    g.session.add(new_log)
    g.session.commit()


"""
---------------- Endpoints ----------------
"""


@app.route('/trade', methods=['POST'])
def trade():
    if request.method == "POST":
        content = request.get_json(silent=True)
        print(f"content = {json.dumps(content)}")
        columns = ["sender_pk", "receiver_pk", "buy_currency", "sell_currency", "buy_amount", "sell_amount", "platform"]
        fields = ["sig", "payload"]
        error = False
        for field in fields:
            if not field in content.keys():
                print(f"{field} not received by Trade")
                print(json.dumps(content))
                log_message(content)
                return jsonify(False)

        error = False
        for column in columns:
            if not column in content['payload'].keys():
                print(f"{column} not received by Trade")
                error = True
        if error:
            print(json.dumps(content))
            log_message(content)
            return jsonify(False)

        # Your code here
        # Note that you can access the database session using g.session
        sig = content['sig']
        payload = content['payload']

        sender_pk = payload['sender_pk']
        receiver_pk = payload['receiver_pk']
        buy_ccy = payload['buy_currency']
        sell_ccy = payload['sell_currency']
        buy_amt = payload['buy_amount']
        sell_amt = payload['sell_amount']
        platform = payload['platform']

        if platform == 'Algorand':
            if algosdk.util.verify_bytes(json.dumps(payload).encode('utf-8'), sig, sender_pk):
                result = True
            else:
                result = False
        elif platform == 'Ethereum':
            encoded_msg = eth_account.messages.encode_defunct(text=json.dumps(payload))
            if eth_account.Account.recover_message(encoded_msg, signature=sig) == sender_pk:
                result = True
            else:
                result = False

        if result:
            new_order = Order(sender_pk=sender_pk, receiver_pk=receiver_pk, buy_currency=buy_ccy,
                              sell_currency=sell_ccy, buy_amount=buy_amt, sell_amount=sell_amt, signature=sig)
            g.session.add(new_order)
            g.session.commit()
        return jsonify(result)
    else:
        return jsonify(True)


@app.route('/order_book')
def order_book():
    # Your code here
    # Note that you can access the database session using g.session
    orders = g.session.query(Order)
    result = {'data': []}

    for order in orders:
        data = dict()
        data['sender_pk'] = order.sender_pk
        data['receiver_pk'] = order.receiver_pk
        data['buy_currency'] = order.buy_currency
        data['sell_currency'] = order.sell_currency
        data['buy_amount'] = order.buy_amount
        data['sell_amount'] = order.sell_amount
        data['signature'] = order.signature
        result['data'].append(data)
    return result


if __name__ == '__main__':
    app.run(port='5002')
