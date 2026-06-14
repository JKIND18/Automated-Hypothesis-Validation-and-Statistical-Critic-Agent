import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats


COMMON_TICKERS = {
    'microsoft': 'MSFT',
    'apple': 'AAPL',
    'google': 'GOOGL',
    'nvidia': 'NVDA',
    'amazon': 'AMZN',
    'tesla': 'TSLA',
    'meta': 'META',
}


def resolve_ticker(stock_input: str) -> str:
    """Resolve a user-provided stock name or ticker symbol to a Yahoo Finance ticker."""
    query = stock_input.strip()
    if not query:
        return 'AAPL'

    normalized_query = query.lower()
    if normalized_query in COMMON_TICKERS:
        return COMMON_TICKERS[normalized_query]

    candidate = query.split()[0].upper()
    if candidate.isalpha() and len(candidate) <= 5:
        return candidate

    try:
        # Simple fallback search using yfinance
        ticker_obj = yf.Ticker(query)
        if ticker_obj.info and 'symbol' in ticker_obj.info:
            return ticker_obj.info['symbol'].upper()
    except Exception:
        pass

    return candidate

def download_history(ticker: str) -> pd.DataFrame:
    """Download the last 2 years of daily data for the requested ticker and handle multi-index."""
    end_date = pd.Timestamp.today().normalize()
    start_date = end_date - pd.DateOffset(years=2)

    data = yf.download(
        ticker,
        start=start_date,
        end=end_date + pd.Timedelta(days=1),
        progress=False,
        group_by='ticker' # Keeps data predictable
    )

    if data.empty:
        raise ValueError(f"No data found for {ticker}.")

    # Handle yfinance multi-index column structures safely
    if isinstance(data.columns, pd.MultiIndex):
        if ticker in data.columns.levels[0]:
            df_ticker = data[ticker]
        else:
            df_ticker = data.iloc[:, data.columns.get_level_values(0) == ticker]
    else:
        df_ticker = data

    # Clean column names to lowercase
    df_ticker.columns = [col.lower() for col in df_ticker.columns]
    
    if 'close' not in df_ticker.columns:
        raise ValueError(f"Could not extract 'Close' price for {ticker}")

    return df_ticker[['close']]

def calculate_moving_average_strategy(data: pd.DataFrame) -> dict:
    """Calculate a simple 20-day moving average strategy and summary metrics."""
    df = data.copy().dropna()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['signal'] = np.where(df['close'] > df['sma_20'], 1.0, 0.0)

    # Shifting the signal by 1 day explicitly prevents look-ahead bias
    df['strategy_return'] = df['close'].pct_change() * df['signal'].shift(1).fillna(0.0)
    
    strategy_returns = df['strategy_return'].dropna()
    if strategy_returns.empty:
        raise ValueError("Not enough data to compute strategy returns.")

    # Calculate performance metrics
    total_return = (np.prod(1.0 + strategy_returns) - 1.0) * 100.0
    daily_mean = strategy_returns.mean()
    daily_std = strategy_returns.std()
    sharpe_ratio = (daily_mean / daily_std) * np.sqrt(252) if daily_std != 0 else 0.0

    # Execute a 1-sample t-test to check if returns are significantly different from zero
    t_stat, p_value = stats.ttest_1samp(strategy_returns, popmean=0)

    return {
        'total_return_pct': float(total_return),
        'annualized_sharpe_ratio': float(sharpe_ratio),
        'p_value': float(p_value),
        'trade_count': int(df['signal'].diff().abs().sum() / 2) # Counts unique buy/sell cycles
    }

def run_pipeline(stock_input: str) -> str:
    """Main execution function designed to be called directly by the Microsoft Foundry Agent Tool."""
    try:
        ticker = resolve_ticker(stock_input)
        data = download_history(ticker)
        metrics = calculate_moving_average_strategy(data)
        
        # Format a clean, structured text output that the Critic Agent can easily read and parse
        output = (
            f"BACKTEST RESULTS FOR TICKER: {ticker}\n"
            f"Strategy Tested: 20-Day Simple Moving Average (SMA) Trend Following\n"
            f"Total Strategy Return: {metrics['total_return_pct']:.2f}%\n"
            f"Annualized Sharpe Ratio: {metrics['annualized_sharpe_ratio']:.4f}\n"
            f"Statistical Significance (p-value): {metrics['p_value']:.6f}\n"
            f"Total Trade Count: {metrics['trade_count']}\n"
            f"Data Horizon: Past 24 months (Daily intervals)\n"
        )
        return output
    except Exception as e:
        return f"Error executing backtest: {str(e)}"

if __name__ == "__main__":
    # Allows you to still test it locally in your VS Code terminal
    test_input = input("Enter a stock ticker or company name to test (e.g. TSLA): ")
    print("\nRunning local pipeline test...\n")
    print(run_pipeline(test_input))