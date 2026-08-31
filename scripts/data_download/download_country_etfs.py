from pathlib import Path
import yfinance as yf
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Target directory for country ETFs
output_dir = str(BASE_DIR / "data" / "countries")
os.makedirs(output_dir, exist_ok=True)

# Accumulating (Acc) UCITS ETFs for various well-performing countries/regions
# These are European-listed ETFs (e.g. Euronext Amsterdam .AS, Xetra .DE, London .L)
# because US-listed ETFs are legally required to distribute dividends (Dist).
tickers = {
    "USA": "CSPX.AS",          # iShares Core S&P 500 UCITS ETF (Acc)
    "World_Benchmark": "IWDA.AS", # iShares Core MSCI World UCITS ETF (Acc)
    "Japan": "IJPA.AS",        # iShares Core MSCI Japan IMI UCITS ETF (Acc)
    "India": "FLXI.DE",        # Franklin FTSE India UCITS ETF (Acc)
    "Germany": "EXS1.DE",      # iShares Core DAX UCITS ETF (Acc)
    "UK": "CUKX.L",            # iShares Core FTSE 100 UCITS ETF (Acc)
    "Europe_600": "MEUD.PA",   # Amundi STOXX Europe 600 UCITS ETF (Acc)
    "Switzerland": "CSSMI.SW", # iShares Core SMI UCITS ETF (Acc)
    "Taiwan": "FLXT.DE",       # Franklin FTSE Taiwan UCITS ETF (Acc)
    "France": "C40.PA",        # Amundi CAC 40 UCITS ETF (Acc)
    "Netherlands": "XAMS.AS",  # Xtrackers AEX UCITS ETF
    "Spain": "IQQA.DE",        # iShares MSCI Spain UCITS ETF (Acc)
    "Sweden": "XS7R.DE",       # Xtrackers MSCI Sweden UCITS ETF (Acc)
    "Denmark": "XDND.DE",      # Xtrackers MSCI Denmark UCITS ETF (Acc)
    "Italy": "EWI",            # iShares MSCI Italy ETF (US)
    "Poland": "EPOL",          # iShares MSCI Poland ETF (US)
    "Norway": "ENOR",          # iShares MSCI Norway ETF (US)
    "Greece": "GREK"           # Global X MSCI Greece ETF (US)
}

for name, ticker in tickers.items():
    print(f"Downloading data for {name} ({ticker})...")
    # Download all available historical data
    data = yf.download(ticker, period="max", progress=False)
    
    if data.empty:
        print(f"Warning: No data found for {name} ({ticker})")
        continue
        
    output_path = os.path.join(output_dir, f"{name}.csv")
    data.to_csv(output_path)
    print(f"Saved {len(data)} rows for {name} data to {output_path}")

print("All country ETF downloads completed successfully!")
