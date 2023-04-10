import time
from datetime import datetime
import sqlite3
from binance import Client

db_name = 'td.db'
table_name = 'trades'

# create connection and cursor
conn = sqlite3.connect(db_name)
c = conn.cursor()

# create binance client
client = Client()

# monitor funding rate every 5 seconds
while True:
    try:
        funding_rates = client.futures_mark_price()
        for fr in funding_rates:
            # print(fr)
            symbol = fr['symbol']
            rate = float(fr['lastFundingRate'])
            
            # check if funding rate is less than -0.4% and there's no existing trade for this symbol
            c.execute(f"SELECT * FROM {table_name} WHERE symbol='{symbol}' AND sell_price IS NULL")
            existing_trade = c.fetchone()
            if rate < -0.004 and existing_trade is None:
                print(f"Symbol {symbol}: funding rate = {rate}")
                buy_price = float(fr['markPrice'])
                c.execute(f"INSERT INTO {table_name} (symbol, buy_price) VALUES (?, ?)", (symbol, buy_price))
                conn.commit()
            # check if funding rate is greater than -0.1% and there's an existing trade for this symbol
            elif rate > -0.001 and existing_trade is not None:
                sell_price = float(fr['markPrice']) 
                profit_rate = (sell_price - existing_trade[2]) / existing_trade[2] * 100
                start_time = datetime.strptime(existing_trade[4], '%Y-%m-%d %H:%M:%S')
                start_timestamp = int(start_time.timestamp())
                end_timestamp = int(time.time())
                funding_rates2 = client.futures_funding_rate(symbol=symbol, start_time=start_timestamp, end_time=end_timestamp)
                # calculate total funding rate for the time period 
                multiplier = 1
                for rate2 in funding_rates2:
                    multiplier *= (1 + abs(float(rate2['fundingRate'])))
                multiplier-=1
                multiplier*=100

                c.execute(f"UPDATE {table_name} SET sell_price=?, sell_time=CURRENT_TIMESTAMP, profit_rate=? , funding_rate=?\
                           WHERE id=?", (sell_price, profit_rate,multiplier, existing_trade[0]))
                conn.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
    time.sleep(15)
