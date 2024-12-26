from flask import Flask, send_from_directory, jsonify, request
import MetaTrader5 as mt5
import pandas as pd
import random
import time
from datetime import datetime
import sys
sys.path.append('./lib')
import di as di

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
@app.route("/WSPFUT")
def wsp_fut():
  return send_from_directory('cli', 'graficoWSPFUT.html')
@app.route("/DI")
def di_fut():
  return send_from_directory('cli', 'DI.html')

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

# Get historical data from MT5
def get_historical_data():
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 500)
    df = pd.DataFrame(rates)
    #df['time'] = pd.to_datetime(df['time'], unit='s') não precisa transformar deve ficar em inteiro
    df.rename(columns={'real_volume': 'volume'}, inplace=True)
    print(df.head())
    return df.to_dict(orient='records')

######################################
# Get real-time tick data from MT5
def get_real_time_tick():
    tick = mt5.symbol_info_tick(symbol)
    if tick:
        return {
            'time': tick.time,
            'bid': tick.bid,
            'ask': tick.ask,
            'last': tick.last,
            'volume': tick.volume
        }
    return None

######################################
# Get real-time tick data from MT5 (este pode passar o tick como parâmetro)
def get_real_time_tick2(tickerName):
    tick = mt5.symbol_info_tick(tickerName)
    if tick:
        return {
            'time': tick.time,
            'bid': tick.bid,
            'ask': tick.ask,
            'last': tick.last,
            'volume': tick.volume
        }
    return None

def get_lastbar_data():
  rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 1)
  if rates is None or len(rates) == 0:
      return None
  latest_candle = rates[0]
  return {
    'time': int(latest_candle['time']),     # Unix timestamp
    'open': latest_candle['open'],
    'high': latest_candle['high'],
    'low': latest_candle['low'],
    'close': latest_candle['close'],
    'volume': int(latest_candle['real_volume'])  # Sem o int estava dando erro no jsonify
    }

######################################
# API
# API endpoint for initial data
@app.route('/api/initial-data', methods=['GET'])
def get_initial_data():
  print('get_initial_data')
  initial_data = get_historical_data()
  return jsonify(initial_data)
  #initial_data = [generate_candlestick_data() for _ in range(2500)]
  #return jsonify(initial_data)

# updated-data
# API endpoint for real-time updated data
@app.route('/api/updated-data', methods=['GET'])
def get_updated_data():
    #updated_data = get_real_time_tick()
    update = get_lastbar_data()
    #print(update)
    if update:
      return jsonify(update)
    return jsonify(None)

# last-ticker-data
# API endpoint for real-time updated data nesta versão passa de 1 a n símbolos como parâmetro
@app.route('/api/last-ticker-data', methods=['GET'])
def get_ticker_data():
  ticker_names = request.args.getlist('tickerName')
  updates = {}
  for ticker in ticker_names:
    # Como não tem um ticker específico para o CDI, foi criado um if para tratar este caso
    if ticker == "CDI":
      updates[ticker] = {
        'time': int(time.time()),
        'bid': 12.25,
        'ask': 12.25,
        'last': 12.25,
        'volume': 0
      }
    else:
      update = get_real_time_tick2(ticker)
      if update:
        updates[ticker] = update
  return jsonify(updates)

# estimate-cdi
# API endpoint for real-time updated data nesta versão passa de 1 a n símbolos como parâmetro
@app.route('/api/estimate-cdi', methods=['GET'])
def get_CDI_estimate():
  ticker = request.args.get('ticker')
  target_rate = request.args.get('target_rate', type=float)
  
  if not ticker or target_rate is None:
    return jsonify({'error': 'Ticker and target_rate are required'}), 400
  
  initial_date = datetime.now().date()
  
  ticker_dates = {
    "DI1N24": datetime(2024, 7, 1).date(),
    "DI1F25": datetime(2025, 1, 2).date(),
    "DI1N25": datetime(2025, 7, 1).date(),
    "DI1F26": datetime(2026, 1, 2).date(),
    "DI1N26": datetime(2026, 7, 1).date(),
    "DI1F27": datetime(2027, 1, 4).date(),
    "DI1F28": datetime(2028, 1, 3).date(),
    "DI1F29": datetime(2029, 1, 2).date(),
    "DI1F30": datetime(2030, 1, 2).date(),
    "DI1F31": datetime(2031, 1, 2).date()
  }

  final_date = ticker_dates.get(ticker)
  if not final_date:
    return jsonify({'error': 'Invalid ticker'}), 400

  # CDI atual  
  initial_rate = 12.25  

  # Chame a função EstimaCDI
  resultado = di.EstimaCDI(initial_rate, target_rate, initial_date, final_date)

  # Convert DataFrame to dictionary
  resultado_dict = resultado.to_dict(orient='records')

  print({'result': resultado_dict})

  return jsonify({'result': resultado_dict})