import pandas as pd
import numpy as np

def calculate_sma(df: pd.DataFrame, window: int = 20, column: str = 'Close') -> pd.Series:
    """Calculate Simple Moving Average."""
    if df.empty or len(df) < window:
        return pd.Series(dtype=float)
    return df[column].rolling(window=window).mean()

def calculate_ema(df: pd.DataFrame, window: int = 20, column: str = 'Close') -> pd.Series:
    """Calculate Exponential Moving Average."""
    if df.empty or len(df) < window:
        return pd.Series(dtype=float)
    return df[column].ewm(span=window, adjust=False).mean()

def calculate_rsi(df: pd.DataFrame, window: int = 14, column: str = 'Close') -> pd.Series:
    """Calculate Relative Strength Index."""
    if df.empty or len(df) < window:
        return pd.Series(dtype=float)
    
    delta = df[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, column: str = 'Close') -> pd.DataFrame:
    """Calculate MACD Line, Signal Line, and Histogram."""
    if df.empty or len(df) < slow:
        return pd.DataFrame(columns=['MACD_Line', 'MACD_Signal', 'MACD_Hist'])
    
    ema_fast = df[column].ewm(span=fast, adjust=False).mean()
    ema_slow = df[column].ewm(span=slow, adjust=False).mean()
    
    macd_line = ema_fast - ema_slow
    macd_signal = macd_line.ewm(span=signal, adjust=False).mean()
    macd_hist = macd_line - macd_signal
    
    return pd.DataFrame({
        'MACD_Line': macd_line,
        'MACD_Signal': macd_signal,
        'MACD_Hist': macd_hist
    })

def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience function to add major indicators to the dataframe."""
    df = df.copy()
    if not df.empty and len(df) > 26:
        df['SMA_20'] = calculate_sma(df, 20)
        df['SMA_50'] = calculate_sma(df, 50)
        df['EMA_20'] = calculate_ema(df, 20)
        df['RSI_14'] = calculate_rsi(df, 14)
        
        macd_df = calculate_macd(df)
        if not macd_df.empty:
            df = pd.concat([df, macd_df], axis=1)
            
    return df
