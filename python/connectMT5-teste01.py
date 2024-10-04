import MetaTrader5 as mt5
import pandas as pd

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
rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 1000)

# Convert to DataFrame for easier manipulation
df = pd.DataFrame(rates)
df['time'] = pd.to_datetime(df['time'], unit='s')

# Display the last 5 rows
print(df.tail())

# Shutdown connection
mt5.shutdown()
