"""
Verification of Presidential Cycle Zones.

For each cycle year (1-4) and each OpEx month (Jan-Dec), calculate:
- The actual average OpEx-to-OpEx return
- Win rate
- Number of observations

This lets us verify whether the Golden/Danger/Neutral zone assignments
in the infographic and sniper_trade_analyzer.py are justified by the data.

Cycle years (using year % 4):
  Year 1 (Post-Election): 2001, 2005, 2009, 2013, 2017, 2021, 2025 => year%4 == 1
  Year 2 (Midterm):       2002, 2006, 2010, 2014, 2018, 2022, 2026 => year%4 == 2
  Year 3 (Pre-Election):  2003, 2007, 2011, 2015, 2019, 2023       => year%4 == 3
  Year 4 (Election):      2004, 2008, 2012, 2016, 2020, 2024       => year%4 == 0
"""
import pandas as pd
import yfinance as yf
import numpy as np
import datetime
import calendar
import warnings
warnings.filterwarnings('ignore')

tickers = ["SPY", "QQQ", "SMH"]
data = yf.download(tickers, start="2001-01-01", progress=False)['Close'].dropna()
max_data_date = data.index.max()
print(f"Data range: {data.index.min().date()} to {max_data_date.date()}")

def get_3rd_friday(year, month):
    d = datetime.date(year, month, 1)
    while d.weekday() != 4:
        d += datetime.timedelta(days=1)
    d += datetime.timedelta(days=14)
    return pd.Timestamp(d)

# Build OpEx price table for each ticker
def build_opex_returns(ticker):
    price_series = data[ticker]
    min_year = price_series.index.min().year
    max_year = price_series.index.max().year
    
    opex_prices = []
    for y in range(min_year, max_year + 1):
        for m in range(1, 13):
            target_opex = get_3rd_friday(y, m)
            if target_opex > max_data_date:
                continue
            valid = price_series.index[price_series.index <= target_opex]
            if len(valid) > 0:
                opex_prices.append({
                    'Year': y,
                    'Month': m,
                    'OpExDate': valid[-1].date(),
                    'Price': price_series.loc[valid[-1]]
                })
    
    df = pd.DataFrame(opex_prices)
    # Return for month M = from OpEx(M-1) to OpEx(M)
    df['Return'] = df['Price'].pct_change() * 100
    df = df.dropna(subset=['Return'])
    
    # Cycle year: the year of the OpEx month determines the cycle
    df['CycleYear'] = df['Year'] % 4  # 0=Election, 1=Post-Election, 2=Midterm, 3=Pre-Election
    
    return df

cycle_names = {
    1: "Year 1: Post-Election",
    2: "Year 2: Midterm",
    3: "Year 3: Pre-Election",
    0: "Year 4: Election"
}

# Current zone definitions from sniper_trade_analyzer.py
zones = {
    1: {  # Post-Election (year%4==1)
        'danger':  [2],
        'golden':  [4, 5, 7, 11, 12],
    },
    2: {  # Midterm (year%4==2)
        'danger':  [6, 8, 9, 12],
        'golden':  [11],
    },
    3: {  # Pre-Election (year%4==3)
        'danger':  [8, 9],
        'golden':  [4, 10, 11, 12],
    },
    0: {  # Election (year%4==0)
        'danger':  [10],
        'golden':  [8, 11, 12],
    },
}

def get_zone_label(cycle_year, month):
    z = zones[cycle_year]
    if month in z['danger']:
        return 'DANGER'
    elif month in z['golden']:
        return 'GOLDEN'
    else:
        return 'NEUTRAL'

# Analyze for SPY (primary), then show QQQ and SMH for reference
for ticker in tickers:
    df = build_opex_returns(ticker)
    
    print(f"\n{'='*90}")
    print(f"  PRESIDENTIAL CYCLE ZONES VERIFICATION: {ticker} (OpEx-to-OpEx)")
    print(f"{'='*90}")
    
    for cy in [1, 2, 3, 0]:
        print(f"\n  --- {cycle_names[cy]} ---")
        print(f"  {'Month':<6} {'Zone':<14} {'N':>4} {'WinRate':>8} {'AvgRet':>8} {'MedianRet':>10} {'AllReturns'}")
        
        cy_data = df[df['CycleYear'] == cy]
        
        for m in range(1, 13):
            m_data = cy_data[cy_data['Month'] == m]['Return']
            zone = get_zone_label(cy, m)
            n = len(m_data)
            
            if n > 0:
                wr = (m_data > 0).mean() * 100
                ar = m_data.mean()
                med = m_data.median()
                returns_str = ', '.join([f"{r:+.1f}" for r in m_data.values])
                
                # Flag potential misclassifications
                flag = ""
                if 'GOLDEN' in zone and ar < 0:
                    flag = " ** GOLDEN but negative avg!"
                elif 'DANGER' in zone and ar > 1.5:
                    flag = " ** DANGER but strongly positive!"
                elif 'NEUTRAL' in zone and ar > 2.5:
                    flag = " >> Consider GOLDEN?"
                elif 'NEUTRAL' in zone and ar < -1.0:
                    flag = " >> Consider DANGER?"
                    
                print(f"  {calendar.month_abbr[m]:<6} {zone:<14} {n:>4} {wr:>7.1f}% {ar:>+7.2f}% {med:>+9.2f}%  [{returns_str}]{flag}")
            else:
                print(f"  {calendar.month_abbr[m]:<6} {zone:<14}    -        -        -")

# Summary of potential issues
print(f"\n\n{'='*90}")
print("SUMMARY: Potential Zone Misclassifications")
print(f"{'='*90}")

ticker = 'SPY'  # Use SPY as the primary classifier
df = build_opex_returns(ticker)

issues = []
for cy in [1, 2, 3, 0]:
    cy_data = df[df['CycleYear'] == cy]
    for m in range(1, 13):
        m_data = cy_data[cy_data['Month'] == m]['Return']
        zone = get_zone_label(cy, m)
        n = len(m_data)
        if n > 0:
            ar = m_data.mean()
            wr = (m_data > 0).mean() * 100
            
            if 'GOLDEN' in zone and (ar < 0 or wr < 50):
                issues.append(f"  !! {cycle_names[cy]} | {calendar.month_abbr[m]:>3} | {zone} | AvgRet={ar:+.2f}% WR={wr:.0f}% => Possibly wrong! Avg is negative or WR<50%")
            elif 'DANGER' in zone and (ar > 1.0 and wr > 60):
                issues.append(f"  !! {cycle_names[cy]} | {calendar.month_abbr[m]:>3} | {zone} | AvgRet={ar:+.2f}% WR={wr:.0f}% => Possibly wrong! Positive with good WR")
            elif 'NEUTRAL' in zone and (ar > 3.0 and wr > 70):
                issues.append(f"  >> {cycle_names[cy]} | {calendar.month_abbr[m]:>3} | {zone} | AvgRet={ar:+.2f}% WR={wr:.0f}% => Consider upgrading to GOLDEN")
            elif 'NEUTRAL' in zone and (ar < -2.0 and wr < 40):
                issues.append(f"  >> {cycle_names[cy]} | {calendar.month_abbr[m]:>3} | {zone} | AvgRet={ar:+.2f}% WR={wr:.0f}% => Consider downgrading to DANGER")

if issues:
    for issue in issues:
        print(issue)
else:
    print("  OK: No obvious misclassifications found.")
