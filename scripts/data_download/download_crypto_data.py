from pathlib import Path
import yfinance as yf
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Target directory for Crypto data
output_dir = str(BASE_DIR / "data" / "crypto")
os.makedirs(output_dir, exist_ok=True)

# Tickers mapping for Crypto
tickers = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Solana": "SOL-USD"
}

print(f"Starting download of crypto data to {output_dir}...\n")

for name, ticker in tickers.items():
    print(f"Downloading data for {name} ({ticker})...")
    # Download all available historical daily data
    data = yf.download(ticker, period="max", progress=False)
    
    if data.empty:
        print(f"  --> Warning: No data found for {name} ({ticker})")
        continue
        
    output_path = os.path.join(output_dir, f"{name}.csv")
    data.to_csv(output_path)
    print(f"  --> Saved {len(data)} rows ({data.index.min().strftime('%Y-%m-%d')} tot {data.index.max().strftime('%Y-%m-%d')}) to {output_path}")

print("\nCrypto downloads completed successfully!")
