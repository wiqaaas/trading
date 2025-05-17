from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time


class TradingApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)

    # def error(self, reqId, errorCode, errorString):
    #     print("Error {} {} {}".format(reqId, errorCode, errorString))

    def contractDetails(self, reqId, contractDetails):
        print()
        print("reqId: {}, contract:{}".format(reqId, contractDetails))
        print()
        summary = contractDetails.contract        
        print(f"Contract Details for reqId {reqId}:")
        print(f"  Symbol: {summary.symbol}")
        print(f"  SecType: {summary.secType}")
        print(f"  Currency: {summary.currency}")
        print(f"  Exchange: {summary.exchange}")
        print(f"  Primary Exchange: {summary.primaryExchange}")
        print(f"  Long Name: {contractDetails.longName}")
        print(f"  Market Name: {contractDetails.marketName}")
        print(f"  Time Zone: {contractDetails.timeZoneId}")
        print(f"  Min Tick: {contractDetails.minTick}")
        print(f"  Trading Class: {summary.tradingClass}")
        print()

def websocket_con():
    app.run()


app = TradingApp()
app.connect("127.0.0.1", 7497, clientId=1)

# starting a separate daemon thread to execute the websocket connection
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1)  # some latency added to ensure that the connection is established

# creating object of the Contract class - will be used as a parameter for other function calls
contract = Contract()
contract.symbol = "AAPL"
contract.secType = "STK"
contract.currency = "USD"
contract.exchange = "SMART"

app.reqContractDetails(100, contract)  # EClient function to request contract details
time.sleep(5)  # some latency added to ensure that the contract details request has been processed

app.disconnect()