import logging
import time

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s')
logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')

sell_qty = 1000
profit = 1000
logging.info("Selling {} UNI for an estimated of ${} profit".format(sell_qty, profit))

# logging exceptions to capture stack trace
a = 5
b = 0

try:
  c = a / b
except Exception as e:
  logging.info('you profited')
  logging.error("Exception occurred", exc_info=True)
  logging.exception("Exception occurred") # will show a log at the level of ERROR, always dumps exception info, so should only be called from exception