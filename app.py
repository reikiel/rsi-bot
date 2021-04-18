import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/uniusdt@kline_1m"
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'UNIUSDT'
TRADE_USDT_AMOUNT = 1000
IN_POSITION_THRESHOLD = 2

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

# Check from binance if in position - this is in case the code gets interrupted


def on_open(ws):
  print('connection opened')

def on_close(ws):
  print('closed connection')

# whenever websocket gets data
def on_message(ws, message):
  global closes

  json_message = json.loads(message)
  
  candle = json_message['k']
  is_candle_closed = candle['x']

  if is_candle_closed:
    close = candle['c']
    closes.append(float(close))
    print(closes)

    # make sure have 15 closes
    if len(closes) > RSI_PERIOD:
      np_closes = numpy.array(closes)
      rsi = talib.RSI(np_closes, RSI_PERIOD)
      print("All rsi calculated so far: {}".format(rsi))
      current_rsi = rsi[-1]
      print("The current RSI is {}".format(current_rsi))

      if current_rsi > RSI_OVERBOUGHT:
        if not in_position:
          print("You are not in position, can't sell")
        else:
          # TODO: Check profit after fees
          # TODO: Check quantity
          sell_quantity = check_qty()
          # Sell order logic - check if minimum profit is met
          print("RSI is overbought and your current balance is profiting. Selling...")
          order_success = order(SIDE_SELL, sell_quantity, TRADE_SYMBOL)
          if order_success:
            in_position = False
            print("SELL order for {} UNI success!".format(sell_quantity))
          else:
            print("SELL order not successful, please check what is the problem")
    
      elif current_rsi < RSI_OVERSOLD:
        if in_position:
          print("You are already in a position, can't buy")
        else:
          print("RSI is oversold and you are not in position. Buying...")         
          # Buy Order logic
          order_success = order(SIDE_BUY, TRADE_USDT_AMOUNT, TRADE_SYMBOL)
          if order_success:
            in_position = True
            # TODO: Check quantity from order for logging? or just use check_qty?
            buy_quantity = check_qty()
            print("BUY order for {} UNI success!".format(buy_quantity))
          else:
            print("BUY order not successful, please check what is the problem")


# send order to binance
def order(side, qty, symbol, order_type=ORDER_TYPE_MARKET):
  # if sell, sell all qty => use quantity
  # if buy, buy qty WORTH (USDT) of coin => use quoteOrderQty
  return True

# check profit before selling
def check_profit_before():
  return

# see profit after selling
# might need to get full response? use newOrderRespType
# calculate fill orders
# then minus TRADE_USDT_AMOUNT
def check_profit_after():
  return

# check how much holdings
def check_qty():
  account = client.get_account()
  print(account)
  return 1

check_qty()

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
