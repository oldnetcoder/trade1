import time
import sqlite3
from binance import Client, ThreadedWebsocketManager

db_name = 'td.db'
table_name = 'trades'

# create connection and cursor
conn = sqlite3.connect(db_name)
c = conn.cursor()

# create trades table if not exists
c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} \
           (id INTEGER PRIMARY KEY, symbol TEXT, buy_price REAL, sell_price REAL, \
           buy_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, sell_time TIMESTAMP, profit_rate REAL)")

# create binance client and start websocket manager
client = Client()
twm = ThreadedWebsocketManager()
twm.start()

# monitor funding rate every 5 seconds
while True:
    try:
        funding_rates = client.futures_funding_rate()
        for fr in funding_rates:
            symbol = fr['symbol']
            rate = float(fr['fundingRate'])
            # check if funding rate is less than -0.4% and there's no existing trade for this symbol
            c.execute(f"SELECT * FROM {table_name} WHERE symbol='{symbol}' AND sell_price IS NULL")
            existing_trade = c.fetchone()
            if rate < -0.004 and existing_trade is None:
                # get current spot price for symbol
                ticker = client.get_symbol_ticker(symbol=symbol.replace('PERP', 'USDT'))
                price = float(ticker['price'])
                # insert new trade record
                c.execute(f"INSERT INTO {table_name} (symbol, buy_price) VALUES (?, ?)", (symbol, price))
                conn.commit()
            # check if funding rate is greater than -0.1% and there's an existing trade for this symbol
            elif rate > -0.001 and existing_trade is not None:
                sell_price = float(client.get_symbol_ticker(symbol=symbol.replace('PERP', 'USDT'))['price'])
                # update existing trade record with sell price, sell time, and profit rate
                profit_rate = (sell_price - existing_trade[2]) / existing_trade[2] * 100
                c.execute(f"UPDATE {table_name} SET sell_price=?, sell_time=CURRENT_TIMESTAMP, profit_rate=? \
                           WHERE id=?", (sell_price, profit_rate, existing_trade[0]))
                conn.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
    time.sleep(5)
