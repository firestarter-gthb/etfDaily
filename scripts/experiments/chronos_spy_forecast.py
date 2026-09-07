import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import torch
from chronos import ChronosPipeline

def main():
    # Setup paths
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_path = base_dir / 'data' / 'daily' / 'SPY_1d.csv'
    reports_dir = base_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    report_path = reports_dir / 'chronos_spy_forecast.png'

    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path, parse_dates=['time'])
    df = df.sort_values('time').reset_index(drop=True)
    
    # We will forecast the 'close' price
    close_prices = df['close'].values
    dates = df['time'].values
    
    prediction_length = 60
    
    # Train / test split
    train_prices = close_prices[:-prediction_length]
    test_prices = close_prices[-prediction_length:]
    train_dates = dates[:-prediction_length]
    test_dates = dates[-prediction_length:]
    
    # Calculate historical seasonality projection
    train_df = pd.DataFrame({'time': train_dates, 'close': train_prices})
    train_df['ret'] = train_df['close'].pct_change()
    train_df['day_of_year'] = pd.to_datetime(train_df['time']).dt.dayofyear
    
    # Seasonality profile (median daily return per day of year for robustness)
    seasonality_profile = train_df.groupby('day_of_year')['ret'].median()
    
    test_doy = pd.to_datetime(test_dates).dayofyear
    seasonality_returns = [seasonality_profile.get(d, 0.0) for d in test_doy]
    
    seasonality_path = [train_prices[-1]]
    for ret in seasonality_returns:
        seasonality_path.append(seasonality_path[-1] * (1 + ret))
    seasonality_path = seasonality_path[1:] # discard the starting point
    
    context = torch.tensor(train_prices)
    
    print("Loading Chronos model (amazon/chronos-t5-small)...")
    # Determine device and dtype
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

    print(f"Forecasting {prediction_length} steps...")
    # forecast shape: [num_series, num_samples, prediction_length]
    torch.manual_seed(42)
    forecast = pipeline.predict(
        context,
        prediction_length=prediction_length,
        num_samples=20,
        temperature=1.0,
        top_k=50,
        top_p=1.0
    )

    # Calculate percentiles (median, 80% CI, 90% CI)
    forecast_samples = forecast[0].numpy()
    low_90, low_80, median, high_80, high_90 = np.percentile(
        forecast_samples, [5, 10, 50, 90, 95], axis=0
    )

    print("Calculating metrics...")
    mae = np.mean(np.abs(test_prices - median))
    rmse = np.sqrt(np.mean((test_prices - median)**2))
    
    # Directional accuracy
    actual_direction = np.sign(test_prices[-1] - test_prices[0])
    predicted_direction = np.sign(median[-1] - median[0])
    direction_correct = (actual_direction == predicted_direction)

    print(f"Metrics over {prediction_length} days:")
    print(f"  MAE: {mae:.2f}")
    print(f"  RMSE: {rmse:.2f}")
    print(f"  Actual Return: {test_prices[-1] - test_prices[0]:.2f} ({(test_prices[-1]/test_prices[0]-1)*100:.2f}%)")
    print(f"  Predicted Return: {median[-1] - median[0]:.2f} ({(median[-1]/median[0]-1)*100:.2f}%)")
    print(f"  Direction Correct: {direction_correct}")

    print("\n" + "="*50)
    print("AlphaGBM Trader's Report")
    print("="*50)
    
    try:
        from alphagbm_client import AlphaGBMClient
        client = AlphaGBMClient()
        
        # 1. Map Forecast to Market View
        pred_return = (median[-1] / median[0]) - 1
        if pred_return > 0.01:
            market_view = "bullish"
        elif pred_return < -0.01:
            market_view = "bearish"
        else:
            market_view = "neutral"
            
        print(f"Chronos Forecast View: {market_view.upper()} ({pred_return*100:.2f}% expected return)")
        
        # 2. Get Market Context
        vix_data = client.get_vix_status()
        sentiment_data = client.get_market_sentiment()
        macro_data = client.get_macro_view()
        
        print("\n[Market Regime]")
        print(f"- Sentiment: {sentiment_data['regime'].upper()} (Fear & Greed: {sentiment_data['fear_greed_index']})")
        print(f"- VIX Status: {vix_data['vix']} - {vix_data['label']} ({vix_data['strategy_hint']})")
        print(f"- Macro: {macro_data['macro_regime'].replace('_', ' ').title()}, {macro_data['fed_stance'].replace('_', ' ').title()}")
        
        # 3. Get Options Strategy Recommendation
        strat_data = client.get_options_strategy("SPY", market_view, vix_data['level'])
        if strat_data['recommendations']:
            top_rec = strat_data['recommendations'][0]
            print(f"\n[Options Strategy Recommendation: {top_rec['strategy']}]")
            print(f"Rationale: {top_rec['rationale']}")
            print("Legs:")
            for leg in top_rec['legs']:
                print(f"  - {leg['action'].upper()} {leg['strike']} {leg['type'].upper()}")
                
    except ImportError:
        print("AlphaGBMClient not found. Skipping Trader's Report.")
    except Exception as e:
        print(f"Error generating Trader's Report: {e}")
        
    print("="*50 + "\n")

    print("Generating plot...")
    plt.figure(figsize=(12, 6))
    
    # Plot last 100 days of train data for context
    plot_context = 100
    plt.plot(train_dates[-plot_context:], train_prices[-plot_context:], label='Historical (Train)')
    plt.plot(test_dates, test_prices, label='Actual (Test)', color='green')
    
    plt.plot(test_dates, median, label='Chronos Median Forecast', color='blue')
    plt.plot(test_dates, seasonality_path, label='Historical Seasonality Path', color='orange', linestyle='--')
    plt.fill_between(test_dates, low_80, high_80, color='blue', alpha=0.3, label='80% Prediction Interval')
    plt.fill_between(test_dates, low_90, high_90, color='blue', alpha=0.1, label='90% Prediction Interval')

    plt.title(f'SPY Price Forecast using Chronos (amazon/chronos-t5-small)')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(report_path)
    print(f"Plot saved to {report_path}")

if __name__ == "__main__":
    main()
