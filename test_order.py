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
#     newOrderRespType=ORDER_RESP_TYPE_FULL,
#     quoteOrderQty = 5000)
#   print(order)

# print(1)

# testing function scope
test = 10
def testing():
  global test
  print(test)
  test=2

# test = 10
testing()
print(test)


# test get historical trades
# quoteQty is the amount u spent in total!
# need to figure out which ones is the same trade, to get the total buy price?
trades = client.get_my_trades(symbol="ANKRUSDT", fromId=17808115)

for trade in trades:
  pprint.pprint(trade)

# print(client.get_asset_balance(asset="USDT")['free'])

order = {
    "symbol": "BTCUSDT",
    "orderId": 28,
    "clientOrderId": "6gCrw2kRUAF9CvJDGP16IP",
    "transactTime": 1507725176595,
    "price": "0.00000000",
    "origQty": "10.00000000",
    "executedQty": "10.00000000",
    "status": "FILLED",
    "timeInForce": "GTC",
    "type": "MARKET",
    "side": "SELL",
    "fills": [
        {
            "price": "4000.00000000",
            "qty": "1.00000000",
            "commission": "4.00000000",
            "commissionAsset": "USDT"
        },
        {
            "price": "3999.00000000",
            "qty": "5.00000000",
            "commission": "19.99500000",
            "commissionAsset": "USDT"
        },
        {
            "price": "3998.00000000",
            "qty": "2.00000000",
            "commission": "7.99600000",
            "commissionAsset": "USDT"
        },
        {
            "price": "3997.00000000",
            "qty": "1.00000000",
            "commission": "3.99700000",
            "commissionAsset": "USDT"
        },
        {
            "price": "3995.00000000",
            "qty": "1.00000000",
            "commission": "3.99500000",
            "commissionAsset": "USDT"
        }
    ]
}

# fills = order['fills']
# profit = 0
# for fill in fills:
#   temp = float(fill['price']) * float(fill['qty']) - float(fill['commission'])
#   profit += temp

# print(profit)