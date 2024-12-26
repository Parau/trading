import MetaTrader5 as mt5

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

######################################
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
# Inicializa o MT5

# MT5 connection
if not mt5.initialize():
  print("Initialize failed, error code =", mt5.last_error())
  quit()
else: 
  print("MT5 inicializado")

"""
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
"""