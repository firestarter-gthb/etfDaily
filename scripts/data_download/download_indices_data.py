from pathlib import Path
import yfinance as yf
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Target directory
output_dir = str(BASE_DIR / "data" / "indices")
os.makedirs(output_dir, exist_ok=True)

# Tickers mapping
# Using standard Yahoo Finance tickers
tickers = {
    "SPX": "^GSPC",
    "QQQ": "QQQ",
    "VIX": "^VIX",
    "Russell_3000": "^RUA", # Russell 3000 Index
    "MSCI_World": "URTH",   # iShares MSCI World ETF as proxy
    "Russell_2000": "^RUT",
    "Dow_Jones": "^DJI",
    "Nasdaq": "^IXIC",
    "VVIX": "^VVIX",
    "SKEW": "^SKEW",
    "Treasury_Yield_10Y": "^TNX",
    "Treasury_Bond_20Y_Plus": "TLT",
    "US_Dollar_Index": "DX-Y.NYB",
    "Gold": "GC=F",
    "Crude_Oil": "CL=F",
    "Euro_Stoxx_50": "^STOXX50E",
    "Nikkei_225": "^N225",
    "Bitcoin": "BTC-USD"
}

for name, ticker in tickers.items():
    print(f"Downloading data for {name} ({ticker})...")
    # Download all available historical data (period="max")
    data = yf.download(ticker, period="max", progress=False)
    
    if data.empty:
        print(f"Warning: No data found for {name} ({ticker})")
        continue
        
    output_path = os.path.join(output_dir, f"{name}.csv")
    data.to_csv(output_path)
    print(f"Saved {len(data)} rows for {name} data to {output_path}")

print("All downloads completed successfully!")
