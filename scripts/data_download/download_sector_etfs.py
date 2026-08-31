from pathlib import Path
import yfinance as yf
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Target directory for Sector ETFs
output_dir = str(BASE_DIR / "data" / "sectors")
os.makedirs(output_dir, exist_ok=True)

# 11 Official S&P 500 SPDR Select Sector ETFs + Key Industry Proxies
tickers = {
    # 11 Official S&P 500 GICS Sector ETFs
    "XLK_Technology": "XLK",
    "XLF_Financials": "XLF",
    "XLV_Healthcare": "XLV",
    "XLE_Energy": "XLE",
    "XLI_Industrials": "XLI",
    "XLY_Consumer_Discretionary": "XLY",
    "XLP_Consumer_Staples": "XLP",
    "XLU_Utilities": "XLU",
    "XLB_Materials": "XLB",
    "XLRE_Real_Estate": "XLRE",
    "XLC_Communication_Services": "XLC",
    
    # Key Sub-Sectors & Industry ETFs
    "SMH_Semiconductors": "SMH",
    "XBI_Biotech": "XBI",
    "XHB_Homebuilders": "XHB",
    "XRT_Retail": "XRT",
    "XME_Metals_Mining": "XME",
    "XOP_Oil_Gas_Exploration": "XOP",
    "KRE_Regional_Banking": "KRE",
    "IYT_Transportation": "IYT"
}

print(f"Starting download of {len(tickers)} S&P sector and industry ETFs to {output_dir}...\n")

for name, ticker in tickers.items():
    print(f"Downloading data for {name} ({ticker})...")
    # Download all available historical daily data
    data = yf.download(ticker, period="max", progress=False)
    
    if data.empty:
        print(f"  --> Warning: No data found for {name} ({ticker})")
        continue
        
    output_path = os.path.join(output_dir, f"{name}.csv")
    data.to_csv(output_path)
    print(f"  --> Saved {len(data)} rows to {output_path}")

print("\nAll SPX sector ETF downloads completed successfully!")
