from pathlib import Path
import os
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent

data_dir = str(BASE_DIR / "data" / "countries")
results = []

for file in os.listdir(data_dir):
    if not file.endswith(".csv"):
        continue
    country = file.replace(".csv", "")
    filepath = os.path.join(data_dir, file)
    
    try:
        # Yahoo Finance CSVs might have a 3-row header
        try:
            df = pd.read_csv(filepath, skiprows=[1, 2], index_col=0, parse_dates=True)
            if 'Adj Close' not in df.columns:
                df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        except:
            df = pd.read_csv(filepath, index_col=0, parse_dates=True)
        
        # Flatten columns if multi-index
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        price_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
        if price_col not in df.columns:
            continue
            
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce')
        df.dropna(subset=[price_col], inplace=True)
        
        if len(df) < 20: # Need at least 1 month
            continue
            
        current_price = df[price_col].iloc[-1]
        
        # Calculate returns based on trading days (21=1M, 63=3M, 126=6M, 252=12M)
        ret_1m = (current_price / df[price_col].iloc[-21] - 1) * 100 if len(df) >= 21 else np.nan
        ret_3m = (current_price / df[price_col].iloc[-63] - 1) * 100 if len(df) >= 63 else np.nan
        ret_6m = (current_price / df[price_col].iloc[-126] - 1) * 100 if len(df) >= 126 else np.nan
        ret_12m = (current_price / df[price_col].iloc[-252] - 1) * 100 if len(df) >= 252 else np.nan
        
        # Composite Momentum Score (Average of 3M, 6M, and 12M)
        score = np.nanmean([ret_3m, ret_6m, ret_12m])
        
        results.append({
            "Land": country,
            "1M (%)": ret_1m,
            "3M (%)": ret_3m,
            "6M (%)": ret_6m,
            "12M (%)": ret_12m,
            "Momentum Score": score
        })
    except Exception as e:
        pass

df_res = pd.DataFrame(results)
df_res.sort_values(by="Momentum Score", ascending=False, inplace=True)
df_res.set_index("Land", inplace=True)

# Format for printing
for col in df_res.columns:
    df_res[col] = df_res[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")

print("--- HUIDIGE MOMENTUM RANKING ---")
print(df_res.to_string())
