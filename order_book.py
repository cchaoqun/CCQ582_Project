from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, Order
engine = create_engine('sqlite:///orders.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def process_order(order):
    #Your code here
    buy_currency = order.get('buy_currency', '')
    sell_currency = order.get('sell_currency', '')
    buy_amount = order.get('buy_amount', '')
    sell_amount = order.get('sell_amount', '')
    sender_pk = order.get('sender_pk', '')
    receiver_pk = order.get('receiver_pk', '')
    creator_id = order.get('creator_id')

    # fill field for new order
    newOrder = None
    if creator_id == None:
        newOrder = Order(buy_currency=buy_currency, sell_currency=sell_currency, buy_amount=buy_amount, sell_amount=sell_amount, sender_pk=sender_pk, receiver_pk=receiver_pk)
    else:
        newOrder = Order(buy_currency=buy_currency, sell_currency=sell_currency, buy_amount=buy_amount, sell_amount=sell_amount, sender_pk=sender_pk, receiver_pk=receiver_pk, creator_id=creator_id)

    # 1. Insert the order into the database
    session.add(newOrder)
    session.commit()

    # 2.Check existing order match
    unfilledOrders = session.query(Order).filter(Order.filled == None).all()
    # iterate through all unfilled orders
    for oldOrder in unfilledOrders:
        if check_match(newOrder, oldOrder):
            # check exchange rate
            new_er = newOrder.sell_amount / newOrder.buy_amount
            old_er = oldOrder.buy_amount / oldOrder.sell_amount
            if new_er >= old_er:
                # 3. match found
                # set timestamp
                time = datetime.now()
                newOrder.filled = time
                oldOrder.filled = time
                # set counterparty_id
                newOrder.counterparty_id = oldOrder.id
                oldOrder.counterparty_id = newOrder.id
                session.commit()
                # check incomplete filled order
                if oldOrder.sell_amount > newOrder.buy_amount:
                    next = {}
                    next['buy_currency'] = oldOrder.buy_currency
                    next['sell_currency'] = oldOrder.sell_currency
                    next['sell_amount'] = oldOrder.sell_amount - newOrder.buy_amount
                    next['buy_amount'] = next['sell_amount'] * old_er
                    # next['buy_amount'] = next['sell_amount'] * 0.99 * old_er
                    next['sender_pk'] = oldOrder.sender_pk
                    next['receiver_pk'] = oldOrder.receiver_pk
                    next['creator_id'] = oldOrder.id
                    process_order(next)
                if newOrder.buy_amount > oldOrder.sell_amount:
                    next = {}
                    next['buy_currency'] = newOrder.buy_currency
                    next['sell_currency'] = newOrder.sell_currency
                    next['buy_amount'] = newOrder.buy_amount - oldOrder.sell_amount
                    next['sell_amount'] = next['buy_amount'] * new_er
                    # next['sell_amount'] = next['buy_amount'] * 1.01 * new_er
                    next['sender_pk'] = newOrder.sender_pk
                    next['receiver_pk'] = newOrder.receiver_pk
                    next['creator_id'] = newOrder.id
                    process_order(next)





def check_incomplete_filled_order(newOrder, oldOrder):
    li = [0 , 0]
    li[0] = (1, newOrder, oldOrder) if (newOrder.buy_amount > oldOrder.sell_amount) else (0)
    li[1] = (1, oldOrder, newOrder) if (oldOrder.sell_amount > newOrder.buy_amount) else (0)
    return li


def check_match(newOrder, oldOrder):
    return (newOrder.filled == None) and (newOrder.buy_currency == oldOrder.sell_currency) and (newOrder.sell_currency == oldOrder.buy_currency)


