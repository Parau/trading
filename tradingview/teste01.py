import pandas as pd
from lightweight_charts import Chart
import MetaTrader5 as mt5
import time


if __name__ == '__main__':
  
  # Initialize MT5 connection
  if not mt5.initialize():
    print("Initialize failed, error code =", mt5.last_error())
    quit()

  # Choose the symbol
  symbol = "WSPZ24"

  # Check if the symbol is available
  selected = mt5.symbol_select(symbol, True)
  if not selected:
      print(f"Failed to select {symbol}, error code =", mt5.last_error())
      mt5.shutdown()
      quit()

  # Get data (last 1000 bars)
  rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 500)

  # Convert to DataFrame for easier manipulation
  df = pd.DataFrame(rates)
  df['time'] = pd.to_datetime(df['time'], unit='s')
  # ajusta para o nome no tradinview
  df.rename(columns={'real_volume': 'volume'}, inplace=True)
  #print(df.head())

  chart = Chart()
    
  # Columns: time | open | high | low | close | volume 
  chart.set(df)
    
  chart.show()
  print('depois do chart.show')
  try:
    while True:
      tick = mt5.symbol_info_tick(symbol)
      print(tick)
      #chart.update_from_tick(tick)    
      time.sleep(1)
  except KeyboardInterrupt:
    print("Interrompendo captura de dados... (teclado)")
  finally:
    print('Liberando MT5')
    mt5.shutdown()
    print('Encerrado!')