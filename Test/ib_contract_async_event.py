from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import threading
import time


class TradingApp(EWrapper, EClient):
    def __init__(self):
        super().__init__(self)

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

def websocket_con(app):
    app.run()

def main():
    app = TradingApp()
    app.connect("127.0.0.1", 7497, clientId=1)

    # Start the socket connection in a thread
    con_thread = threading.Thread(target=websocket_con, args=(app,), daemon=True)
    con_thread.start()
    time.sleep(1)

    contract = Contract()
    contract.symbol = "AAPL"
    contract.secType = "STK"
    contract.currency = "USD"
    contract.exchange = "SMART"

    app.reqContractDetails(100, contract)
    time.sleep(5)

    # Disconnect the app cleanly
    app.disconnect()

if __name__ == "__main__":
    main()
