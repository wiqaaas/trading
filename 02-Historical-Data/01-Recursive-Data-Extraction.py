# Import Libraries
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd
import threading
import time

class TradeApp(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}

    def historicalData(self, reqId, bar):
        print(f"Time: {bar.date}, Open: {bar.open}, Close: {bar.close}")
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
            self.data[reqId] = pd.concat([
                self.data[reqId],
                pd.DataFrame([{
                    "Date": bar.date,
                    "Open": bar.open,
                    "High": bar.high,
                    "Low": bar.low,
                    "Close": bar.close,
                    "Volume": bar.volume
                }])
            ])

def usTechStk(symbol, sec_type="STK", currency="USD", exchange="ISLAND"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract

def histData(req_num, contract, duration, candle_size):
    """Extracts historical data"""
    app.reqHistoricalData(
        reqId=req_num,
        contract=contract,
        endDateTime='',
        durationStr=duration,
        barSizeSetting=candle_size,
        whatToShow='ADJUSTED_LAST',
        useRTH=1,
        formatDate=1,
        keepUpToDate=False,
        chartOptions=[]
    )

def websocket_con():
    app.run()  # This will block until app.disconnect() is called

app = TradeApp()
app.connect("127.0.0.1", port=7497, clientId=23)

# Start the API loop in a daemon thread
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()

############################################
# Storing trade app object in dataframe
############################################
def dataDataFrame(TradeApp_obj, symbols):
    """Returns extracted historical data in dataframe format"""
    df_data = {}
    for symbol in symbols:
        df_data[symbol] = pd.DataFrame(TradeApp_obj.data[symbols.index(symbol)])
        df_data[symbol].set_index("Date", inplace=True)
    TradeApp_obj.data = {}
    return df_data

############################################
# Extract and store historical data in dataframe repetitively
############################################
tickers = ["AAPL", "MSFT", "INTC"]
starttime = time.time()

while time.time() < starttime + 60 * 2:
    for ticker in tickers:
        histData(tickers.index(ticker), usTechStk(ticker), '3600 S', '30 secs')
        time.sleep(4)

    data = dataDataFrame(app, tickers)
    print('-----------------------')
    print(data)
    print('-----------------------')
    # Ensure each 30-second cycle aligns with the start time
    time.sleep(30 - ((time.time() - starttime) % 30.0))

# Once the 2-minute window is up, disconnect and join the thread
app.disconnect()
con_thread.join()
