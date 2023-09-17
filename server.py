from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
import numpy as np
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)
model = load_model("FalseSignalDetectionModel.h5")
scaler = joblib.load("scaler.gz")

SEQ_LENGTH = 12  # your sequence length here

def init_db():
    with sqlite3.connect('forex_data.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS forex_data
                     (datetime text, open real, high real, low real, close real, volume real)'''
        )

@app.route('/store_data', methods=['POST'])
def store_data():
    data = request.json
    with sqlite3.connect('forex_data.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO forex_data (datetime, open, high, low, close, volume) VALUES (?, ?, ?, ?, ?, ?)",
                  (data['datetime'], data['open'], data['high'], data['low'], data['close'], data['volume']))
    return "success"

@app.route('/get_data', methods=['GET'])
def get_data():
    with sqlite3.connect('forex_data.db') as conn:
        df = pd.read_sql_query('SELECT * FROM forex_data', conn)
    return df.to_json(orient='records')

def create_sequences(data, seq_length):
    X = []
    for i in range(len(data) - seq_length):
        seq = data[i: (i + seq_length)]
        X.append(seq[:-1]) 
    return np.array(X)

@app.route('/predict', methods=['GET'])
def predict():
    with sqlite3.connect('forex_data.db') as conn:
        df = pd.read_sql_query('SELECT * FROM forex_data', conn)
        
    # Set the datetime column as the index
    df.set_index('datetime', inplace=True)
    
    # Handle NaN values by forward filling
    df.fillna(method='ffill', inplace=True)
    
    # Resample to 15-minute timeframes
    df = df.resample('15T').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    
    # Scale the features
    scaled_data = scaler.transform(df.values)
    
    # Create sequences
    X = create_sequences(scaled_data, SEQ_LENGTH)
    
    # Make predictions
    y_pred_probs = model.predict(X)
    y_pred = y_pred_probs.round()
    
    # Convert prediction to list for JSON response
    y_pred = y_pred.tolist()

    return jsonify(y_pred)

@app.route('/')
def hello():
    return "Hello, Your server is running"

port = 5178

if __name__ == '__main__':
    init_db()
    app.run(port=port)
    print("The server is running at port:", port)
