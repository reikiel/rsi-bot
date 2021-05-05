import websocket, json, pprint, talib, numpy, logging
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
BINANCE_FEE = 0.1/100 # 0.1% of the TRADE_ASSET

closes = []
buy_amt = 1000
total_session_profit = 0
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

# Logging
logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# check how much holdings
def check_qty(asset):
  balance = client.get_asset_balance(asset=asset)
  return float(balance['free'])
  

# On start, check if in position and the buy_amt in case program closes
def check_in_position():
  global in_position, buy_amt
  if check_qty(TRADE_ASSET) > 5:
    in_position = True
    # TODO: Check whats the estimated buy amt from previous trades if < TRADE_BASE_AMOUNT
  else:
    in_position = False
  

check_in_position()

# send order to binance
# TODO: Change all to create_order when done
def order(side, qty, symbol, order_type=ORDER_TYPE_MARKET):
  # if sell, sell all qty # of coins => use quantity
  if side == SIDE_SELL:
    try:
      order = client.create_test_order(
      symbol=symbol,
      side=side,
      type=ORDER_TYPE_MARKET,
      newOrderRespType=ORDER_RESP_TYPE_FULL,
      quantity=qty)
      return order
    except Exception as e:
      logging.exception("SELL error occurred")
      return False

  # if buy, buy qty WORTH (USDT) of coin => use quoteOrderQty
  elif side == SIDE_BUY:
    try: 
      order = client.create_test_order(
      symbol=symbol,
      side=side,
      type=ORDER_TYPE_MARKET,
      newOrderRespType=ORDER_RESP_TYPE_FULL,
      quoteOrderQty=qty)
      return order
    except Exception as e:
      logging.exception("BUY error occurred")
      return False


# check profit before selling - estimated profit
# fee is 0.1% of what you use to buy and what you going to receive
# check how much you going to receive (must current price * holdings)
def check_profit_before(price, sell_qty):
  total_from_sale = price * sell_qty
  est_fee_buy = buy_amt * BINANCE_FEE
  est_fee_sell = total_from_sale * BINANCE_FEE
  profit = total_from_sale - est_fee_sell - est_fee_buy
  logging.info("Checking to sell {} UNI for an estimated of ${} profit".format(sell_qty, profit))
  return profit

# see profit after selling - real profit accounting for fees
# can try to get trade history and see how much i buy at, and compare with the current sell order
# might need to get full response? use newOrderRespType
# calculate fill orders
# then minus TRADE_USDT_AMOUNT
def check_profit_after(order):
  global total_session_profit
  fills = order['fills']
  total_money = 0
  total_qty = 0
  for fill in fills:
    total_qty += float(fill['qty'])
    temp = float(fill['price']) * float(fill['qty']) - float(fill['commission'])
    total_money += temp
  profit = total_money - buy_amt 
  logging.info("Sold {} UNI for a ${} profit".format(total_qty, profit))
  total_session_profit += profit
  print("Total profit from this session is ${}!".format(total_session_profit))
  return profit

########################## WebSocket Functions ##########################
def on_open(ws):
  print('connection opened')
  # print(in_position)
  
def on_close(ws):
  print('closed connection')

# whenever websocket gets data
def on_message(ws, message):
  global closes, buy_amt

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
      # print("All rsi calculated so far: {}".format(rsi))
      current_rsi = rsi[-1]
      # print("The current RSI is {}".format(current_rsi))

      if current_rsi > RSI_OVERBOUGHT:
        logging.info("Current RSI is {}, overbought.".format(current_rsi))
        print("Current RSI is {}, overbought.")
        if not in_position:
          logging.info("You are not in position, can't sell")
          print("You are not in position, can't sell")
        else:
          # Check estimated profit after fees, before selling
          sell_quantity = check_qty(TRADE_ASSET)
          est_profit = check_profit_before(float(close), sell_quantity)
          # Sell order logic - check if minimum profit is met
          if est_profit > 15:
            print("RSI is overbought and your current balance is profiting. Selling...")
            order_success = order(SIDE_SELL, sell_quantity, TRADE_SYMBOL)
            if order_success != False:
              in_position = False
              print("SELL order for {} UNI success!".format(sell_quantity))
              # Check real profit from order response (after selling)
              act_profit = check_profit_after(order_success)
            else:
              print("SELL order not successful, please check what is the problem")
          else:
            logging.info("Current profit is not minimum, not selling.")
            print("RSI is overbought BUT your current balance is not profiting. Hold.")
    
      elif current_rsi < RSI_OVERSOLD:
        logging.info("Current RSI is {}, oversold.".format(current_rsi))
        if in_position:
          logging.info("You are already in a position, can't buy")
          print("You are already in a position, can't buy")
        else:
          print("RSI is oversold and you are not in position. Buying...")         
          # Buy Order logic
          base_amt = check_qty(BASE_ASSET)
          buy_amt = min(base_amt, TRADE_BASE_AMOUNT)
          order_success = order(SIDE_BUY, buy_amt, TRADE_SYMBOL)
          if order_success != False:
            in_position = True
            buy_quantity = check_qty(TRADE_ASSET)
            logging.info("Bought {} UNI for ${}".format(buy_quantity, buy_amt))
            print("BUY order for {} UNI success!".format(buy_quantity))
          else:
            print("BUY order not successful, please check what is the problem")


ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
