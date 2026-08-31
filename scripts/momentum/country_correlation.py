import pandas as pd
import numpy as np
import yfinance as yf

tickers = {
    "Zuid-Korea": "EWY", "Taiwan": "EWT", "Colombia": "GXG", "Griekenland": "GREK", "Polen": "EPOL",
    "Singapore": "EWS", "Zweden": "EWD", "Noorwegen": "ENOR", "Canada": "EWC", "Italië": "EWI",
    "Thailand": "THD", "Zuid-Afrika": "EZA", "Spanje": "EWP", "Denemarken": "EDEN", "Zwitserland": "EWL",
    "USA": "SPY", "Japan": "EWJ", "Wereld Benchmark": "URTH", "Europa 600": "EZU", "Israël": "EIS",
    "Mexico": "EWW", "VK": "EWU", "Australië": "EWA", "Brazilië": "EWZ", "Turkije": "TUR",
    "Argentinië": "ARGT", "Maleisië": "EWM", "Duitsland": "EWG", "Frankrijk": "EWQ", "Saudi-Arabië": "KSA",
    "Verenigde Arabische Emiraten": "UAE", "India": "INDA", "Vietnam": "VNM", "China": "MCHI", "Indonesië": "EIDO"
}

print("Downloading fresh data from yfinance...")
data = yf.download(list(tickers.values()), period="max", progress=False)
adj_close = data['Adj Close'] if 'Adj Close' in data.columns else data['Close']

usa_returns = adj_close["SPY"].pct_change().dropna()

results = []
for country, ticker in tickers.items():
    if ticker == "SPY":
        continue
    
    country_series = adj_close[ticker].dropna()
    country_returns = country_series.pct_change().dropna()
    
    aligned = pd.concat([usa_returns, country_returns], axis=1, join='inner')
    aligned.columns = ['USA', country]
    
    if len(aligned) < 252:
        continue
        
    corr = aligned['USA'].corr(aligned[country])
    
    monthly = country_series.resample('ME').last().pct_change().dropna()
    
    sept_returns = monthly[monthly.index.month == 9]
    sept_avg = sept_returns.mean() * 100 if len(sept_returns) > 0 else np.nan
    
    q4_returns = monthly[monthly.index.month.isin([10, 11, 12])]
    q4_avg = q4_returns.mean() * 100 if len(q4_returns) > 0 else np.nan
    
    results.append({
        "Land": country,
        "Correlatie vs US": corr,
        "Sept Gem. (%)": sept_avg,
        "Q4 Gem. (%)": q4_avg
    })

df_res = pd.DataFrame(results)
df_res.sort_values(by="Correlatie vs US", ascending=False, inplace=True)
df_res.set_index("Land", inplace=True)

for col in ["Sept Gem. (%)", "Q4 Gem. (%)"]:
    df_res[col] = df_res[col].apply(lambda x: f"{x:.2f}%" if pd.notnull(x) else "N/A")
df_res["Correlatie vs US"] = df_res["Correlatie vs US"].apply(lambda x: f"{x:.2f}")

print("\n--- CORRELATIE & SEIZOENSINVLOED ---")
print(df_res.to_string())
