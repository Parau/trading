from flask import Flask, send_from_directory, jsonify
import MetaTrader5 as mt5
import pandas as pd
import random
import time

# Initialize MT5 connection
if not mt5.initialize():
  print("Initialize failed, error code =", mt5.last_error())
  quit()
else: 
  print("MT5 inicializado")

# Choose the symbol
symbol = "WSPZ24"
# Check if the symbol is available
selected = mt5.symbol_select(symbol, True)
if not selected:
    print(f"Failed to select {symbol}, error code =", mt5.last_error())
    mt5.shutdown()
    quit()
else:
   print('Carregado valores iniciais de ', symbol)

# Get data
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 500)

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')
# ajusta para o nome no tradinview
df.rename(columns={'real_volume': 'volume'}, inplace=True)



######################################
# Roteamento
app = Flask(__name__)

######################################
# homepage
@app.route("/")
def pagina_inicial():
  print('get_initial_data')
  return send_from_directory('./', 'index.html')


######################################
# initial-data

# Sample function to generate candlestick data
def generate_candlestick_data():
    return {
        'time': int(time.time()),
        'open': random.uniform(20, 25),
        'high': random.uniform(25, 30),
        'low': random.uniform(15, 20),
        'close': random.uniform(20, 25)
    }

# API endpoint for initial data
@app.route('/api/initial-data', methods=['GET'])
def get_initial_data():
  print('get_initial_data')
  initial_data = [generate_candlestick_data() for _ in range(2500)]
  return jsonify(initial_data)


######################################
# updated-data

# API endpoint for real-time updated data
@app.route('/api/updated-data', methods=['GET'])
def get_updated_data():
    updated_data = generate_candlestick_data()
    return jsonify(updated_data)