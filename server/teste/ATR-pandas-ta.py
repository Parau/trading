import pandas as pd
import pandas_ta as ta
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import numpy as np

# Function to fetch and prepare data
def get_stock_data(symbol, period="1y", interval="1h", trading_session_only=False):
    """
    Fetch stock data using MetaTrader 5
    
    Parameters:
    symbol (str): Stock symbol
    period (str): Data period to download ('1mo', '1y', etc)
    interval (str): Data interval ('1h', '1d', etc)
    trading_session_only (bool): If True, gets only trading session data
    """
    if not mt5.initialize():
        print("MetaTrader5 initialization failed")
        return None

    # Convert period string to number of candles
    period_map = {
        "1d": 1,
        "1mo": 30,
        "1y": 365,
        "3mo": 90,
        "6mo": 180
    }
    days = period_map.get(period, 30)  # default to 30 days

    # Convert interval string to MT5 timeframe
    timeframe_map = {
        "1m": mt5.TIMEFRAME_M1,
        "1h": mt5.TIMEFRAME_H1,
        "1d": mt5.TIMEFRAME_D1,
        "4h": mt5.TIMEFRAME_H4,
        "1w": mt5.TIMEFRAME_W1,
    }
    timeframe = timeframe_map.get(interval, mt5.TIMEFRAME_H1)

    # Calculate number of bars based on period and interval
    if interval == "1h":
        bars = days * 24
    else:
        bars = days

    # Get current time
    utc_now = datetime.now()
    
    if trading_session_only:
        # Define trading session hours (adjust according to your market)
        # Example for B3 (Brazil): 10:00 to 17:00
        today = utc_now.replace(hour=9, minute=0, second=0, microsecond=0)
        session_end = utc_now.replace(hour=18, minute=30, second=0, microsecond=0)
        
        # Get data only for trading session
        rates = mt5.copy_rates_range(symbol, timeframe, today, session_end)
    else:
        rates = mt5.copy_rates_from(symbol, timeframe, utc_now, bars)
    
    if rates is None:
        print(f"Failed to get data for {symbol}")
        return None

    # Convert to pandas DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('time', inplace=True)
    
    # Rename columns to match yfinance format
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'tick_volume': 'Volume'
    })

    mt5.shutdown()
    return df

# Function to calculate volatility for different timeframes
def calculate_volatility(df, windows=[20, 5*20, 20*20]):
    """
    Calculate volatility for different timeframes
    
    Parameters:
    df (DataFrame): Price data
    windows (list): List of periods for volatility calculation
    """
    # Calculate returns
    df['returns'] = df['Close'].pct_change()
    
    # Calculate volatility for different windows
    for window in windows:
        df[f'volatility_{window}'] = df['returns'].rolling(window=window).std() * (252 ** 0.5)  # Annualized
        
    return df

def calculate_volatility_intraday(df, window=60, full_session=False):
    """
    Calculate rolling intraday volatility using both percentage and points
    
    Parameters:
    df (DataFrame): Price data with minute timeframe
    window (int): Window size in minutes for volatility calculation
    full_session (bool): If True, uses all available minutes of the session
    """
    # Calculate simple returns for easier interpretation
    df['returns'] = df['Close'].pct_change()
    
    # If full_session is True, use all available minutes
    if full_session:
        window = len(df)
    
    # Calculate rolling volatility in percentage (não anualizada)
    df['volatility'] = df['returns'].rolling(window=window, min_periods=2).std()
    
    # Calculate volatility in points
    df['price_diff'] = df['Close'] - df['Close'].shift(1)
    df['volatility_points'] = df['price_diff'].rolling(window=window, min_periods=2).std()
    
    # Add timestamp for easier reading
    df['time_str'] = df.index.strftime('%H:%M')
    
    return df

def calculate_atr_intraday(df, window=60, full_session=False):
    """
    Calculate ATR for intraday data
    
    Parameters:
    df (DataFrame): Price data with minute timeframe
    window (int): Window size in minutes for ATR calculation
    full_session (bool): If True, calculates ATR for entire session
    """
    if full_session:
        window = min(14, len(df))  # Use default ATR period if session is short
    
    # Garantir pelo menos 2 períodos de dados
    if len(df) < 2:
        return df
    
    # Calculate ATR using pandas_ta with minimal periods
    df.ta.atr(length=window, append=True, col_names=(f'ATR_{window}',), mamode='ema')
    
    # Add timestamp for easier reading
    df['time_str'] = df.index.strftime('%H:%M')
    
    return df

# Example usage
def main():
    # Set the symbol
    symbol = "WDOH25"  
    
    # Get intraday data with 1-minute intervals for current session
    intraday_df = get_stock_data(symbol, period="1d", interval="1m", trading_session_only=True)
    
    if intraday_df is not None and not intraday_df.empty:
        # Calculate ATR for last 60 minutes and full session
        df_atr = calculate_atr_intraday(intraday_df.copy(), window=60)
        df_session_atr = calculate_atr_intraday(intraday_df.copy(), full_session=True)
        
        # Print results with validation
        print("\nIntraday ATR (60-min window):")
        print(df_atr[['time_str', 'Close', f'ATR_60']].tail(10))
        
        # Print current ATR values with validation
        current_atr = df_atr['ATR_60'].iloc[-1] if 'ATR_60' in df_atr else float('nan')
        session_atr = df_session_atr[f'ATR_14'].iloc[-1] if 'ATR_14' in df_session_atr else float('nan')
        
        print(f"\nCurrent 60-min ATR: {current_atr:.2f} points")
        print(f"Current Session ATR: {session_atr:.2f} points")
    else:
        print("No data available for analysis")

if __name__ == "__main__":
    main()