import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import calendar
import warnings
warnings.filterwarnings("ignore")

symbols = ["^GSPC", "QQQ", "SMH"]
shifts = [-7, 0, 7]
shift_names = {-7: "-7 Dagen", 0: "Origineel", 7: "+7 Dagen"}

def get_som(year, month):
    return pd.Timestamp(year, month, 1)

def get_15th(year, month):
    return pd.Timestamp(year, month, 15)

def get_3rd_friday(year, month):
    d = datetime(year, month, 1)
    while d.weekday() != 4:
        d += timedelta(days=1)
    d += timedelta(days=14)
    return pd.Timestamp(d)

comparisons = []

for symbol in symbols:
    df = yf.download(symbol, period="max", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.index = pd.to_datetime(df.index)
    close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    df = df[df.index >= '2005-12-01']
    
    if df.empty:
        continue
        
    min_year = df.index.min().year
    max_year = df.index.max().year
    max_date = df.index.max()

    for shift in shifts:
        som_dates = []
        mid_dates = []
        opex_dates = []
        
        for y in range(min_year, max_year + 1):
            for m in range(1, 13):
                target_som = get_som(y, m) + timedelta(days=shift)
                if target_som <= max_date:
                    valid_som = df.index[df.index <= target_som]
                    if len(valid_som) > 0 and valid_som[-1] >= df.index[0]:
                        som_dates.append({'Year': y, 'Month': m, 'Price': df.loc[valid_som[-1], close_col]})
                    
                target_mid = get_15th(y, m) + timedelta(days=shift)
                if target_mid <= max_date:
                    valid_mid = df.index[df.index <= target_mid]
                    if len(valid_mid) > 0 and valid_mid[-1] >= df.index[0]:
                        mid_dates.append({'Year': y, 'Month': m, 'Price': df.loc[valid_mid[-1], close_col]})
                    
                target_opex = get_3rd_friday(y, m) + timedelta(days=shift)
                if target_opex <= max_date:
                    valid_opex = df.index[df.index <= target_opex]
                    if len(valid_opex) > 0 and valid_opex[-1] >= df.index[0]:
                        opex_dates.append({'Year': y, 'Month': m, 'Price': df.loc[valid_opex[-1], close_col]})
                    
        def calc_returns(dates_list):
            df_dates = pd.DataFrame(dates_list)
            if df_dates.empty:
                return pd.DataFrame()
            df_dates['Return'] = df_dates['Price'].pct_change().shift(-1)
            df_dates = df_dates.dropna()
            df_dates = df_dates[df_dates['Year'] % 4 == 2] # Midterm years
            return df_dates
            
        som_rets = calc_returns(som_dates)
        mid_rets = calc_returns(mid_dates)
        opex_rets = calc_returns(opex_dates)
        
        for name, rets in [('1e-tot-1e', som_rets), ('15e-tot-15e', mid_rets), ('OpEx-tot-OpEx', opex_rets)]:
            if not rets.empty:
                win_rate = (rets['Return'] > 0).mean() * 100
                avg_ret = rets['Return'].mean() * 100
                comparisons.append({
                    'Symbool': symbol,
                    'Periode': name,
                    'Situatie': shift_names[shift],
                    'Gem. Winstkans (%)': round(win_rate, 1),
                    'Gem. Rendement (%)': round(avg_ret, 2)
                })

df_comp = pd.DataFrame(comparisons)

print("\n\n=========================================================================")
print(" OVERALL PERFORMANCE VERGELIJKING (Gemiddelde over alle 12 maanden)")
print("=========================================================================\n")

pivot_win = df_comp.pivot_table(index=['Symbool', 'Periode'], columns='Situatie', values='Gem. Winstkans (%)')
pivot_win = pivot_win[['-7 Dagen', 'Origineel', '+7 Dagen']] 

pivot_rend = df_comp.pivot_table(index=['Symbool', 'Periode'], columns='Situatie', values='Gem. Rendement (%)')
pivot_rend = pivot_rend[['-7 Dagen', 'Origineel', '+7 Dagen']] 

print("--- GEMIDDELDE WINSTKANS (%) ---")
print(pivot_win.to_string())

print("\n--- GEMIDDELD RENDEMENT PER MAAND (%) ---")
print(pivot_rend.to_string())

print("\n\n=========================================================================")
print(" OVERALL AGGREGATIE (Alle periodes gecombineerd per symbool)")
print("=========================================================================\n")
agg = df_comp.groupby(['Symbool', 'Situatie'])[['Gem. Winstkans (%)', 'Gem. Rendement (%)']].mean()
agg = agg.unstack('Situatie')
agg = agg.swaplevel(0, 1, axis=1).sort_index(axis=1)

ordered_cols = []
for sit in ['-7 Dagen', 'Origineel', '+7 Dagen']:
    ordered_cols.append((sit, 'Gem. Winstkans (%)'))
    ordered_cols.append((sit, 'Gem. Rendement (%)'))
agg = agg[ordered_cols]

print(agg.to_string())
