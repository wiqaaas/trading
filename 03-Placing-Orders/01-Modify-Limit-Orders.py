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
        """Fired by IB as soon as connection is ready for placing orders."""
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

# Wait until IB sends us the first valid orderId
while app.nextValidOrderId is None:
    time.sleep(0.1)

def usTechStk(symbol, sec_type="STK", currency="USD", exchange="SMART"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract

def limitOrder(direction, quantity, lmt_price):
    order = Order()
    order.action = direction
    order.orderType = "LMT"
    order.totalQuantity = quantity
    order.lmtPrice = lmt_price

    # --- Explicitly clear unsupported TWS/Gateway-only flags ---
    order.tif = "DAY"
    order.eTradeOnly = False
    order.firmQuoteOnly = False
    # If you still see issues, you can also explicitly disable these:
    # order.optOutSmartRouting = False
    # order.allowPastTime = False

    return order

# === Place first limit order ===
first_id = app.nextValidOrderId
print(f"Placing order {first_id} @ $200")
app.placeOrder(first_id, usTechStk("META"), limitOrder("BUY", 1, 200))

# Wait a few seconds to let IB register the order
time.sleep(5)

# === Cancel that first order ===
print(f"Cancelling order {first_id}")
app.cancelOrder(first_id)

# Wait for cancel to go through
time.sleep(2)

# Manually bump our local nextValidOrderId so we don’t reuse the same ID
app.nextValidOrderId += 1
second_id = app.nextValidOrderId

# === Place a second limit order with the new ID ===
print(f"Placing order {second_id} @ $190")
app.placeOrder(second_id, usTechStk("META"), limitOrder("BUY", 1, 190))
time.sleep(5)

# Finally disconnect and join the thread cleanly
app.disconnect()
con_thread.join()
print("Finished.")
