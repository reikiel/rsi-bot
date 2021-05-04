import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/uniusdt@kline_1m"
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'UNIUSDT'
TRADE_ASSET = 'UNI' # rmb change to uni
BASE_ASSET = 'USDT'
TRADE_BASE_AMOUNT = 1000

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

# check how much holdings
def check_qty(asset):
  balance = client.get_asset_balance(asset=asset)
  return float(balance['free'])
  

# On start, check if in position in case program closes
def check_in_position():
  global in_position
  if check_qty(TRADE_ASSET) > 2:
    in_position = True
  else:
    in_position = False

check_in_position()

# send order to binance
# Change all to create_order when done
def order(side, qty, symbol, order_type=ORDER_TYPE_MARKET):
  # if sell, sell all qty # of coins => use quantity
  if side == SIDE_SELL:
    try:
      order = client.create_test_order(
      symbol=symbol,
      side=side,
      type=ORDER_TYPE_MARKET,
      quantity=qty)
      return order
    except Exception as e:
      # TODO: log error
      return False

  # if buy, buy qty WORTH (USDT) of coin => use quoteOrderQty
  elif side == SIDE_BUY:
    try: 
      order = client.create_test_order(
      symbol=symbol,
      side=side,
      type=ORDER_TYPE_MARKET,
      quoteOrderQty=qty)
      return order
    except Exception as e:
      # TODO: log error
      return False


# check profit before selling - estimated profit
def check_profit_before():
  return

# see profit after selling - real profit accounting for fees
# can try to get trade history and see how much i buy at, and compare with the current sell order
# might need to get full response? use newOrderRespType
# calculate fill orders
# then minus TRADE_USDT_AMOUNT
def check_profit_after(order):
  return

########################## WebSocket Functions ##########################
def on_open(ws):
  print('connection opened')
  # print(in_position)
  
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
          # TODO: Check profit after fees (before selling)
          sell_quantity = check_qty(TRADE_ASSET)
          # Sell order logic - check if minimum profit is met
          print("RSI is overbought and your current balance is profiting. Selling...")
          order_success = order(SIDE_SELL, sell_quantity, TRADE_SYMBOL)
          if order_success != False:
            in_position = False
            print("SELL order for {} UNI success!".format(sell_quantity))
            # TODO: Check real profit from order response (after selling)
          else:
            print("SELL order not successful, please check what is the problem")
    
      elif current_rsi < RSI_OVERSOLD:
        if in_position:
          print("You are already in a position, can't buy")
        else:
          print("RSI is oversold and you are not in position. Buying...")         
          # Buy Order logic
          base_amt = check_qty(BASE_ASSET)
          buy_amt = min(base_amt, TRADE_BASE_AMOUNT)
          order_success = order(SIDE_BUY, buy_amt, TRADE_SYMBOL)
          if order_success != False:
            in_position = True
            # TODO: Check quantity from order for logging? or just use check_qty?
            buy_quantity = check_qty(TRADE_ASSET)
            print("BUY order for {} UNI success!".format(buy_quantity))
          else:
            print("BUY order not successful, please check what is the problem")


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
