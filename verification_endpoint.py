from flask import Flask, request, jsonify
from flask_restful import Api
import json
import eth_account
import algosdk
'''
Assignment
In order to create a working exchange server, your server will need to accept buy/sell bids from users. These bids should be signed by their creator, so that users cannot submit bids on behalf of others. Thus your exchange server must be able to validate signatures corresponding to public keys on the platforms supported by the exchange.
In this assignment, you will use Python-Flask to create a REST endpoint that takes a (JSON) object that includes both a payload and a signature, and verifies that the signature is a valid signature on the payload. Your endpoint should accept both signatures generated from Ethereum and Algorand keys.
'''
app = Flask(__name__)
api = Api(app)
app.url_map.strict_slashes = False
emptyContent = "Get empty json object"
Ethereum = 'Ethereum'
Algorand = 'Algorand'
@app.route('/verify', methods=['GET','POST'])
def verify():
    # get json object
    content = request.get_json(silent=True)
    # check empty content
    if content == None:
        return jsonify(emptyContent)
    # 1. get 2 field
    signature = content.get('sig', '')
    payload = content.get('payload', {})
    message = payload.get('message', '')
    pk = payload.get('pk', '')
    platform = payload.get('platform', '')
    # Check if signature is valid
    result = True  # Should only be true if signature validates
    # 2. decide platform
    if platform == Ethereum:
        result = valid_Ethereum(payload, signature, pk)
    elif platform == Algorand:
        result = valid_Algorand(payload, signature, pk)
    return jsonify(result)

def valid_Ethereum(payload, signature, pk):
    eth_encoded_msg = eth_account.messages.encode_defunct(text=payload)
    if eth_account.Account.recover_message(eth_encoded_msg,signature=signature) == pk:
        return True
    return False

def valid_Algorand(payload, signature, pk):
    return algosdk.util.verify_bytes(payload.encode('utf-8'), signature, pk)

if __name__ == '__main__':
    app.run(port='5002')
