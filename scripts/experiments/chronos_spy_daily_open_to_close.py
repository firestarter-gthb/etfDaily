import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import torch
from chronos import ChronosPipeline
from tqdm import tqdm

def main():
    # Setup paths
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / 'data' / 'daily' / 'SPY_1d.csv'
    reports_dir = base_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / 'chronos_spy_intraday_forecast.png'

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path, parse_dates=['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    # Create interleaved Open-Close sequence
    # For each day, we append (open, close)
    # The index of open for day i is 2*i, close is 2*i + 1
    
    opens = df['open'].values
    closes = df['close'].values
    dates = df['time'].values
    
    test_days = 60
    total_days = len(df)
    
    # We want to test on the last `test_days`
    # For day `i`, context includes everything up to `opens[i]`
    # Target is `closes[i]`
    
    contexts = []
    actual_opens = []
    actual_closes = []
    test_dates_list = []
    
    # To avoid building massive sequences if not needed, we will limit context to 512 steps 
    # (which is 256 days) as Chronos T5 models typically use 512 token context windows.
    context_limit = 512
    
    for i in range(total_days - test_days, total_days):
        # Flatten all prices up to day i's open
        # We take history from max(0, i - 300) to ensure we have enough points to fill the 512 context limit
        start_idx = max(0, i - 300)
        
        seq = []
        for j in range(start_idx, i):
            seq.extend([opens[j], closes[j]])
        
        # Add today's open
        seq.append(opens[i])
        
        # Keep only the last `context_limit` points
        seq = seq[-context_limit:]
        
        contexts.append(torch.tensor(seq, dtype=torch.float32))
        actual_opens.append(opens[i])
        actual_closes.append(closes[i])
        test_dates_list.append(dates[i])
        
    print("Loading Chronos model (amazon/chronos-t5-small)...")
    if torch.cuda.is_available():
        device_map = "cuda"
        torch_dtype = torch.bfloat16
    else:
        device_map = "cpu"
        torch_dtype = torch.float32
        
    pipeline = ChronosPipeline.from_pretrained(
        "amazon/chronos-t5-small",
        device_map=device_map,
        torch_dtype=torch_dtype,
    )

    print(f"Forecasting 1 step ahead for {test_days} days (Batch mode)...")
    torch.manual_seed(42)
    # Batch predict
    forecast = pipeline.predict(
        contexts,
        prediction_length=1,
        num_samples=20,
        temperature=1.0,
        top_k=50,
        top_p=1.0
    )

    # forecast shape: [batch_size, num_samples, prediction_length]
    # We take the median across samples
    forecast_samples = forecast.numpy() # [60, 20, 1]
    
    predicted_closes = []
    for b in range(test_days):
        median_val = np.median(forecast_samples[b, :, 0])
        predicted_closes.append(median_val)
        
    actual_opens = np.array(actual_opens)
    actual_closes = np.array(actual_closes)
    predicted_closes = np.array(predicted_closes)
    
    # Calculate directional accuracy
    actual_dir = np.sign(actual_closes - actual_opens)
    pred_dir = np.sign(predicted_closes - actual_opens)
    
    # Handle exact zero differences
    actual_dir[actual_dir == 0] = 1
    pred_dir[pred_dir == 0] = 1
    
    correct = (actual_dir == pred_dir)
    win_rate = np.mean(correct) * 100
    
    # VIX (Historical Volatility) Calculation
    # We use 20-day standard deviation of daily returns as a proxy for VIX
    # to filter out "Extreme Fear" days.
    df['ret'] = df['close'].pct_change()
    df['hv20'] = df['ret'].rolling(20).std() * np.sqrt(252) * 100
    
    hv20_test = df['hv20'].values[-test_days:]
    
    strategy_returns = []
    bps_returns = []
    
    for i in range(test_days):
        # 1. VIX Filter (from alphagbm-vix-status)
        is_extreme_fear = hv20_test[i] > 35
        
        # Original L/S Strategy
        if is_extreme_fear:
            # Cash on extreme fear days
            strategy_returns.append(0.0)
        else:
            strat_ret = pred_dir[i] * ((actual_closes[i] - actual_opens[i]) / actual_opens[i])
            strategy_returns.append(strat_ret)
            
        # 2. Bull Put Spread (BPS) Simulation (from alphagbm-bps-backtest)
        # If prediction is bullish and market is not in extreme fear, sell a put spread.
        if pred_dir[i] > 0 and not is_extreme_fear:
            if actual_closes[i] >= actual_opens[i]:
                bps_returns.append(0.005) # Max profit (e.g. 0.5% return on margin)
            else:
                bps_returns.append(-0.015) # Max loss (e.g. -1.5% return on margin)
        else:
            bps_returns.append(0.0)

    strategy_returns = np.array(strategy_returns)
    bps_returns = np.array(bps_returns)
    
    cumulative_strategy = np.cumprod(1 + strategy_returns)
    cumulative_bps = np.cumprod(1 + bps_returns)
    
    buy_hold_returns = (actual_closes - actual_opens) / actual_opens
    cumulative_buy_hold = np.cumprod(1 + buy_hold_returns)

    print("\n--- INTRADAY RESULTS (Open to Close) ---")
    print(f"Total test days: {test_days}")
    print(f"Directional Accuracy (Win Rate): {win_rate:.2f}%")
    print(f"L/S Strategy (VIX Filtered) Cumulative Return: {(cumulative_strategy[-1] - 1)*100:.2f}%")
    print(f"BPS Strategy (VIX Filtered) Cumulative Return: {(cumulative_bps[-1] - 1)*100:.2f}%")
    print(f"Buy & Hold Intraday Cumulative Return: {(cumulative_buy_hold[-1] - 1)*100:.2f}%")

    print("Generating plot...")
    plt.figure(figsize=(14, 7))
    
    plt.subplot(1, 2, 1)
    # Scatter plot of actual vs predicted return % from open
    actual_pct = (actual_closes - actual_opens) / actual_opens * 100
    pred_pct = (predicted_closes - actual_opens) / actual_opens * 100
    
    colors = ['green' if c else 'red' for c in correct]
    plt.scatter(pred_pct, actual_pct, c=colors, alpha=0.7)
    plt.axhline(0, color='black', linestyle='--', alpha=0.5)
    plt.axvline(0, color='black', linestyle='--', alpha=0.5)
    plt.xlabel('Predicted Intraday Return (%)')
    plt.ylabel('Actual Intraday Return (%)')
    plt.title(f'Prediction vs Actual\nWin Rate: {win_rate:.1f}%')
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    # Equity curve of the strategy
    plt.plot(test_dates_list, cumulative_strategy * 100, label='Filtered L/S Strategy', color='blue', linewidth=2)
    plt.plot(test_dates_list, cumulative_bps * 100, label='BPS Strategy', color='purple', linewidth=2)
    plt.plot(test_dates_list, cumulative_buy_hold * 100, label='Buy & Hold (Intraday)', color='gray', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Growth (100 = Base)')
    plt.title('Strategy Performance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(report_path)
    print(f"Plot saved to {report_path}")

if __name__ == "__main__":
    main()
