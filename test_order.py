import config, json, pprint
from binance.client import Client
from binance.enums import *

client = Client(config.API_KEY, config.API_SECRET)

# TRADE_SYMBOL = 'UNIUSDT'

# if True:
#   order = client.create_test_order(
#     symbol=TRADE_SYMBOL,
#     side=SIDE_BUY,
#     type=ORDER_TYPE_MARKET,
#     quoteOrderQty = 5000)
#   print(order)

# print(1)

# # testing function scope
# def testing():
#   global test
#   test = 2

# test = 1
# testing()
# print(test)

# test get historical trades
trades = client.get_my_trades(symbol="THETAUSDT")

# for trade in trades:
#   pprint.pprint(trade)

print(client.get_asset_balance(asset="USDT")['free'])