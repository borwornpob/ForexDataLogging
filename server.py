from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    with sqlite3.connect('forex_data.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS forex_data
                     (datetime text, open real, high real, low real, close real, volume real)''')


@app.route('/store_data', methods=['POST'])
def store_data():
    data = request.json
    with sqlite3.connect('forex_data.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO forex_data (datetime, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)",
                  (data['datetime'], data['open'], data['high'], data['low'], data['close'], data['volume']))
    return jsonify(success=True)

@app.route('/predict', methods=['GET'])
def predict():
    pass

@app.route('/')
def hello():
    return "Hello, Your server is running"

if __name__ == '__main__':
    init_db()
    app.run(port=5000)