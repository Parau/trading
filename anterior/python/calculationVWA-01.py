import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
import mplfinance as mpf
from datetime import datetime
import time

# Function to connect to MetaTrader 5
def connect_mt5():
    if not mt5.initialize():
        print("Failed to connect to MetaTrader 5")
        return False
    print("Connected to MetaTrader 5")
    return True

# Function to get data from the asset
def get_data(symbol, timeframe, n_candles):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n_candles)
    if rates is None or len(rates) == 0:
        print(f"Error fetching data for {symbol}")
        return None

    # Convert to DataFrame and process
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')  # Convert timestamp to datetime
    df.set_index('time', inplace=True)  # Set index to time

    # Handle 'real_volume' or 'tick_volume' if 'real_volume' doesn't exist
    if 'real_volume' in df.columns:
        df.rename(columns={'real_volume': 'volume'}, inplace=True)
    elif 'tick_volume' in df.columns:
        df.rename(columns={'tick_volume': 'volume'}, inplace=True)
    else:
        print(f"No volume data available for {symbol}")
        return None
    
    return df

# Function to calculate VWAP using pandas-ta
def calculate_vwap(df):
    df['vwap'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])
    return df

# Function to plot candlestick chart with VWAP
def plot_candlestick_with_vwap(df):
    # Create VWAP plot
    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)

    # Prepare VWAP line to overlay on candlestick chart
    add_vwap = [mpf.make_addplot(df['vwap'], color='blue')]

    # Plot the candlestick chart with VWAP
    mpf.plot(df, type='candle', style=s, addplot=add_vwap, volume=False, title="Candlestick Chart with VWAP")

# Main function
def main():
    symbol = "WSPZ24"
    timeframe = mt5.TIMEFRAME_M1  # 1-minute timeframe
    n_candles = 500  # Number of candles to display

    # Connect to MetaTrader 5
    if not connect_mt5():
        return

    try:
        while True:
            # Fetch data
            df = get_data(symbol, timeframe, n_candles)
            if df is not None and not df.empty:
                # Calculate VWAP
                df = calculate_vwap(df)
                
                # Plot candlestick chart with VWAP
                plot_candlestick_with_vwap(df)

            # Wait 1 minute before updating the data
            time.sleep(60)

    except KeyboardInterrupt:
        print("Stopping execution...")

    finally:
        mt5.shutdown()

if __name__ == "__main__":
    main()
