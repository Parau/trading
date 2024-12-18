import pandas as pd
from lightweight_charts import Chart
import MetaTrader5 as mt5
import time
from datetime import datetime


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
  print(df.head())

  chart = Chart()
    
  # Columns: time | open | high | low | close | volume 
  chart.set(df)
    
  chart.show()
  print('depois do chart.show')
  try:
    while True:
      tick = mt5.symbol_info_tick(symbol)
      print(tick)
      tickDateTime = pd.to_datetime(tick.time, unit='s')
      # Criando um DataFrame
      newTick = pd.DataFrame({
        'time': [tickDateTime],  # Usando uma lista para criar a coluna
        'price': [tick.last],
        'volume': [tick.volume]
      })
      for i, tick in newTick.iterrows():    #não consegui fazer isso acessando o primeiro item (erro no update_from_tick)
        chart.update_from_tick(tick)        #usei o código exemplo para fazer funcionar, mesmo que o dataframe tenha somente uma linha

      time.sleep(5)
  except KeyboardInterrupt:
    print("Interrompendo captura de dados... (teclado)")
  finally:
    print('Liberando MT5')
    mt5.shutdown()
    print('Encerrado!')