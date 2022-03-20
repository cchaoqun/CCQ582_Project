#!/usr/bin/python3

from algosdk.v2client import algod
from algosdk import mnemonic
from algosdk import transaction
from algosdk import account, encoding

#Connect to Algorand node maintained by PureStake
algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "B3SU4KcVKi94Jap2VXkK83xx38bsv95K5UZm2lab"
#algod_token = 'IwMysN3FSZ8zGVaQnoUIJ9RXolbQ5nRY62JRqF2H'
headers = {
   "X-API-Key": algod_token,
}

acl = algod.AlgodClient(algod_token, algod_address, headers)
min_balance = 100000 #https://developer.algorand.org/docs/features/accounts/#minimum-balance
def generate_acc():
    # generate an account
    private_key, address = account.generate_account()
    print("Private key:", private_key)
    print("Address:", address)
    return private_key, address
generate_acc()
sender_sk = 'DznBELttxeOCBkyen1r5I38G62gnO+f9hTOJJ94oSQ/SBHfP4VWr6yHYx4X6RZT5tk5IIm0i6wvyMwKoIFwXSw=='
sender_pk = '2ICHPT7BKWV6WIOYY6C7URMU7G3E4SBCNUROWC7SGMBKQIC4C5FQQB33PM'
def send_tokens( receiver_pk, tx_amount ):
    params = acl.suggested_params()
    gen_hash = params.gh
    first_valid_round = params.first
    tx_fee = params.min_fee
    last_valid_round = params.last

    #Your code here

    txn = transaction.PaymentTxn(sender_pk, tx_fee, first_valid_round, last_valid_round, gen_hash, receiver_pk,
                                 tx_amount, flat_fee=True)

    signed_txn = txn.sign(sender_sk)
    txid = acl.send_transaction(signed_txn)
    # txinfo = wait_for_confirmation(acl, txid=txid)

    return sender_pk, txid

# Function from Algorand Inc.
def wait_for_confirmation(client, txid):
    """
    Utility function to wait until the transaction is
    confirmed before proceeding.
    """
    last_round = client.status().get('last-round')
    txinfo = client.pending_transaction_info(txid)
    while not (txinfo.get('confirmed-round') and txinfo.get('confirmed-round') > 0):
        print("Waiting for confirmation")
        last_round += 1
        client.status_after_block(last_round)
        txinfo = client.pending_transaction_info(txid)
    print("Transaction {} confirmed in round {}.".format(txid, txinfo.get('confirmed-round')))
    return txinfo



