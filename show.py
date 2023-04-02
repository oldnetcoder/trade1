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
    
    return render_template('index.html', rows=trades)
