import sqlite3

conn = sqlite3.connect('td.db')

c = conn.cursor()

# 创建trades数据表
c.execute('''CREATE TABLE IF NOT EXISTS trades
             (id INTEGER PRIMARY KEY, symbol TEXT, buy_price REAL, sell_price REAL, buy_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, sell_time TIMESTAMP, profit_rate REAL)''')

conn.commit()
