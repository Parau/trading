import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_ta as ta
import mplfinance as mpf

# Load historical data from a CSV file
csv_file_path = 'WSPZ24.csv'  # Defina o caminho do arquivo CSV
spi = pd.read_csv(csv_file_path)

# Convert 'time' column to datetime format
spi['time'] = pd.to_datetime(spi['time'])

# Set the 'time' column as the index
spi.set_index('time', inplace=True)

# Rename 'real_volume' to 'volume'
spi.rename(columns={'real_volume': 'volume'}, inplace=True)

# Ensure the data contains the necessary columns
spi = spi[['open', 'high', 'low', 'close', 'tick_volume', 'spread', 'volume']]

# Calculate VWAP using pandas_ta
spi['vwap'] = ta.vwap(spi['high'], spi['low'], spi['close'], spi['volume'])

# Print the first few rows of the DataFrame
print(spi.head())


# Plotting the candlestick chart with VWAP
# Create a new figure
plt.figure(figsize=(14, 7))

# Add candlestick chart
mpf.plot(spi, type='candle', volume=True, title='Candlestick Chart with VWAP', ylabel='Price',
         addplot=mpf.make_addplot(spi['vwap'], color='blue', panel=0))

# Show the plot
#plt.show()