# Import Libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time

class TradeApp(EWrapper, EClient):
    def __init__(self, total_requests):
        EClient.__init__(self, self)
        self.data = {}
        # How many distinct historical‐data requests we expect to finish:
        self.total_requests = total_requests
        # When each reqId is done, we'll add it to this set:
        self.finished_req_ids = set()

    def historicalData(self, reqId, bar):
        # Append each bar to a pandas DataFrame keyed by reqId
        if reqId not in self.data:
            self.data[reqId] = pd.DataFrame([{
                "Date": bar.date,
                "Open": bar.open,
                "High": bar.high,
                "Low": bar.low,
                "Close": bar.close,
                "Volume": bar.volume
            }])
        else:
            new_row = pd.DataFrame([{
                "Date": bar.date,
                "Open": bar.open,
                "High": bar.high,
                "Low": bar.low,
                "Close": bar.close,
                "Volume": bar.volume
            }])
            self.data[reqId] = pd.concat([self.data[reqId], new_row], ignore_index=True)

        print(
            f"reqID:{reqId}, date:{bar.date}, "
            f"open:{bar.open}, high:{bar.high}, "
            f"low:{bar.low}, close:{bar.close}, "
            f"volume:{bar.volume}"
        )

    def historicalDataEnd(self, reqId, start: str, end: str):
        """
        This callback fires once per reqId when all bars have been sent.
        As soon as we've seen every reqId, we can safely call disconnect().
        """
        print(f"--> historicalDataEnd for reqId {reqId} (from {start} to {end})")
        self.finished_req_ids.add(reqId)

        if len(self.finished_req_ids) == self.total_requests:
            print("All historical-data requests are done. Disconnecting...")
            # This causes app.run() to exit
            self.disconnect()

def websocket_con():
    app.run()

def generalStk(symbol, currency, exchange, sec_type="STK"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract

def histData(req_num, contract, duration, candle_size):
    app.reqHistoricalData(
        reqId=req_num,
        contract=contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting=candle_size,
        whatToShow="ADJUSTED_LAST",
        useRTH=1,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[]
    )

def dataDataframe(ticker_data, TradeApp_obj):
    """Returns extracted historical data in dataframe format"""
    df_data = {}
    for symbol, info in ticker_data.items():
        idx = info["index"]
        try:
            df = pd.DataFrame(TradeApp_obj.data[idx])
            df.set_index("Date", inplace=True)
            df_data[symbol] = df
        except KeyError:
            print(f"Warning: no data found for {symbol} (reqId={idx})")
    return df_data

###########################################
# Main script
###########################################

# 1. Define which tickers + reqId‐metadata
tickers_data = {
    "INTC": {"index": 0, "currency": "USD", "exchange": "ISLAND"},
    "BARC": {"index": 1, "currency": "GBP", "exchange": "LSE"},
    "INFY": {"index": 2, "currency": "INR", "exchange": "NSE"},
}

# 2. Instantiate TradeApp with total_requests = number of tickers
app = TradeApp(total_requests=len(tickers_data))

# 3. Connect and start the API loop in a non‐daemon thread
app.connect("127.0.0.1", 7497, clientId=1)
con_thread = threading.Thread(target=websocket_con)
con_thread.start()

# 4. Give it a moment to establish the socket
time.sleep(1)

# 5. Send out historical‐data requests (each with its own reqId)
for symbol, info in tickers_data.items():
    histData(
        info["index"],
        generalStk(symbol, info["currency"], info["exchange"]),
        duration="1 M",
        candle_size="5 mins"
    )
    # A brief delay so IB has time to register each request
    time.sleep(5)

# 6. Now wait for all historicalDataEnd callbacks to arrive
#    Once all reqIds finish, app.disconnect() gets called.
con_thread.join()  # This will unblock only after .disconnect() is triggered

# 7. Convert whatever has been collected into DataFrames
historicalData = dataDataframe(tickers_data, app)

print("\n------------------")
for symbol, df in historicalData.items():
    print(f"\n=== {symbol} ===")
    print(df)

# At this point the script will exit cleanly.
