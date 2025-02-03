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

# Example usage
def main():
    # Set the symbol
    symbol = "WDOH25"  
    
    # Get intraday data with 1-minute intervals for current session
    intraday_df = get_stock_data(symbol, period="1d", interval="1m", trading_session_only=True)
    
    if intraday_df is not None and not intraday_df.empty:
        # Calculate both rolling and full session volatility
        intraday_vol = calculate_volatility_intraday(intraday_df, window=60)  # 60-min rolling
        session_vol = calculate_volatility_intraday(intraday_df, full_session=True)  # full available session
        
        # Print results with better formatting
        print("\nIntraday Rolling Volatility (60-min window):")
        print(intraday_vol[['time_str', 'Close', 'volatility', 'volatility_points']].tail(10))
        
        # Print current volatilities
        current_vol = intraday_vol['volatility'].iloc[-1]
        current_vol_points = intraday_vol['volatility_points'].iloc[-1]
        session_vol_current = session_vol['volatility'].iloc[-1]
        session_vol_points = session_vol['volatility_points'].iloc[-1]
        
        print(f"\nCurrent 60-min Volatility: {current_vol:.4%}")  # Removido "annualized"
        print(f"Current 60-min Volatility in points: {current_vol_points:.2f}")
        print(f"Current Session Volatility: {session_vol_current:.4%}")  # Removido "annualized"
        print(f"Current Session Volatility in points: {session_vol_points:.2f}")
    else:
        print("No data available for analysis")

    return
    # Get daily data for weekly and monthly calculations
    daily_df = get_stock_data(symbol, period="1y", interval="1d")
    daily_vol = calculate_volatility(daily_df, windows=[5, 21, 63])  # Week, Month, Quarter

    print("\nDaily/Weekly/Monthly Volatility:")
    print(daily_vol[['Close', 'volatility_5', 'volatility_21', 'volatility_63']].tail())
    
    # Using pandas-ta's volatility indicators
    # Calculate Average True Range (ATR)
    daily_df.ta.atr(length=14, append=True)
    
    # Calculate Bollinger Bands
    daily_df.ta.bbands(length=20, append=True)
    
    print("\nAdvanced Volatility Indicators:")
    print(daily_df[['Close', 'ATRr_14', 'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0']].tail())

if __name__ == "__main__":
    main()