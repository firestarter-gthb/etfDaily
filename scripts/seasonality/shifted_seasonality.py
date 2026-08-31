import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import calendar
import warnings
warnings.filterwarnings("ignore")

symbols = ["^GSPC", "QQQ", "SMH"]  # ^GSPC is SPX
shifts = [-7, 7]
shift_names = {-7: "Een week eerder (-7 dagen)", 7: "Een week later (+7 dagen)"}

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

for symbol in symbols:
    print(f"\n===========================================================")
    print(f"               RESULTATEN VOOR {symbol}")
    print(f"===========================================================\n")
    
    df = yf.download(symbol, period="max", progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.index = pd.to_datetime(df.index)
    close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    df = df[df.index >= '2005-12-01']
    
    if df.empty:
        print(f"Geen data voor {symbol}")
        continue
        
    min_year = df.index.min().year
    max_year = df.index.max().year

    for shift in shifts:
        print(f"\n--- {shift_names[shift].upper()} ---")
        
        som_dates = []
        mid_dates = []
        opex_dates = []
        
        for y in range(min_year, max_year + 1):
            for m in range(1, 13):
                # SOM + shift
                target_som = get_som(y, m) + timedelta(days=shift)
                valid_som = df.index[df.index <= target_som]
                if len(valid_som) > 0 and valid_som[-1] >= df.index[0]:
                    som_dates.append({'Year': y, 'Month': m, 'Price': df.loc[valid_som[-1], close_col]})
                    
                # 15th + shift
                target_mid = get_15th(y, m) + timedelta(days=shift)
                valid_mid = df.index[df.index <= target_mid]
                if len(valid_mid) > 0 and valid_mid[-1] >= df.index[0]:
                    mid_dates.append({'Year': y, 'Month': m, 'Price': df.loc[valid_mid[-1], close_col]})
                    
                # OpEx + shift
                target_opex = get_3rd_friday(y, m) + timedelta(days=shift)
                valid_opex = df.index[df.index <= target_opex]
                if len(valid_opex) > 0 and valid_opex[-1] >= df.index[0]:
                    opex_dates.append({'Year': y, 'Month': m, 'Price': df.loc[valid_opex[-1], close_col]})
                    
        def calc_returns(dates_list, name):
            df_dates = pd.DataFrame(dates_list)
            if df_dates.empty:
                return pd.DataFrame()
            df_dates['Return'] = df_dates['Price'].pct_change().shift(-1)
            df_dates = df_dates.dropna()
            df_dates = df_dates[df_dates['Year'] % 4 == 2] # Midterm years
            
            res = []
            for m in range(1, 13):
                m_data = df_dates[df_dates['Month'] == m]
                if len(m_data) > 0:
                    win = (m_data['Return'] > 0).mean() * 100
                    avg = m_data['Return'].mean() * 100
                    res.append({
                        'Maand': calendar.month_abbr[m],
                        f'{name} Winstkans': f"{win:.0f}%",
                        f'{name} Gem. Rend': f"{avg:.2f}%"
                    })
            return pd.DataFrame(res).set_index('Maand')
            
        som_df = calc_returns(som_dates, '1e-tot-1e')
        mid_df = calc_returns(mid_dates, '15e-tot-15e')
        opex_df = calc_returns(opex_dates, 'OpEx-tot-OpEx')
        
        if not som_df.empty and not mid_df.empty and not opex_df.empty:
            final_df = som_df.join(mid_df).join(opex_df)
            print(final_df.to_string())
        else:
            print("Onvoldoende data voor berekening.")
