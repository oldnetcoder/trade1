from flask import Flask, render_template
import sqlite3

app = Flask(__name__, template_folder='./')

@app.route('/')
def index():
    conn = sqlite3.connect('td.db')
    c = conn.cursor()
    c.execute('SELECT * FROM trades order by id desc')
    trades = c.fetchall()
    conn.close()
    trades_with_profit = []
    for trade in trades:
        if trade[3] is not None:
            profit_rate = round((trade[3] - trade[2]) / trade[2] * 100, 2)
        else:
            profit_rate = 'N/A'
        trades_with_profit.append((trade[0], trade[1], trade[2], trade[3], trade[4], trade[5], profit_rate))

    return render_template('index.html', rows=trades_with_profit)