from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import threading
import time

class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.nextValidOrderId = None

    def error(self, reqId, errorCode, errorString):
        print(f"Error {reqId} {errorCode} {errorString}")

    def nextValidId(self, orderId):
        super().nextValidId(orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)

def websocket_con():
    app.run()

app = TradingApp()
app.connect("127.0.0.1", 7497, clientId=1)

# Start the socket thread
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()

# Wait until IB Gateway/TWS sends us the first nextValidOrderId
while app.nextValidOrderId is None:
    time.sleep(0.1)

# ---------- Contract Builder ----------
def usTechStk(symbol, sec_type="STK", currency="USD",
              exchange="SMART", primaryExchange="NASDAQ"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    contract.primaryExchange = primaryExchange
    return contract

# ---------- Common Order Settings ----------
def _apply_common_order_settings(order: Order):
    order.tif = "DAY"
    order.eTradeOnly = False
    order.firmQuoteOnly = False
    return order

# ---------- Order Types ----------
def limitOrder(direction, quantity, lmt_price):
    order = Order()
    order.action = direction
    order.orderType = "LMT"
    order.totalQuantity = quantity
    order.lmtPrice = lmt_price
    return _apply_common_order_settings(order)

def marketOrder(direction, quantity):
    order = Order()
    order.action = direction
    order.orderType = "MKT"
    order.totalQuantity = quantity
    return _apply_common_order_settings(order)

def stopOrder(direction, quantity, st_price):
    order = Order()
    order.action = direction
    order.orderType = "STP"
    order.totalQuantity = quantity
    order.auxPrice = st_price
    return _apply_common_order_settings(order)

def trailStopOrder(direction, quantity, st_price, tr_step=1):
    order = Order()
    order.action = direction
    order.orderType = "TRAIL"
    order.totalQuantity = quantity
    order.trailStopPrice = st_price
    order.auxPrice = tr_step
    return _apply_common_order_settings(order)

# === Execute Sample Orders ===

# 1) Market Order (META)
order_id = app.nextValidOrderId
print(f"Placing Market Order #{order_id}")
app.placeOrder(order_id, usTechStk("META"), marketOrder("BUY", 1))
time.sleep(5)

app.nextValidOrderId += 1

# 2) Stop Order (META)
order_id = app.nextValidOrderId
print(f"Placing Stop Order #{order_id}")
app.placeOrder(order_id, usTechStk("META"), stopOrder("SELL", 1, 200))
time.sleep(5)

app.nextValidOrderId += 1

# 3) Trailing Stop Order (TSLA)
order_id = app.nextValidOrderId
print(f"Placing Trailing Stop Order #{order_id}")
app.placeOrder(order_id, usTechStk("TSLA"), trailStopOrder("BUY", 1, 1400, 2))
time.sleep(5)

# Disconnect cleanly
app.disconnect()
con_thread.join()
print("Finished.")
