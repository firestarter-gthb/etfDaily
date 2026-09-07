import pandas as pd
import numpy as np

def run_analysis():
    df = pd.read_csv('data/indices/SPX.csv', skiprows=[1, 2], index_col=0, parse_dates=True)
    df = df.sort_index()
    df = df[df.index <= '2025-12-31'] # Only completed years
    
    # Filter for September
    sep_df = df[df.index.month == 9].copy()
    
    years = sorted(sep_df.index.year.unique())
    print(f"Total September months analyzed: {len(years)} ({years[0]} - {years[-1]})")
    
    records = []
    
    for y in years:
        ydf = sep_df[sep_df.index.year == y].copy()
        if len(ydf) == 0:
            continue
        
        # Add trading day index (1-based)
        ydf['trading_day'] = range(1, len(ydf) + 1)
        ydf['cal_day'] = ydf.index.day
        ydf['day_of_week'] = ydf.index.day_name()
        
        # Week of month (1-7 = W1, 8-14 = W2, 15-21 = W3, 22-28 = W4, 29-30 = W5)
        def get_cal_week(day):
            if day <= 7:
                return "Week 1 (1-7)"
            elif day <= 14:
                return "Week 2 (8-14)"
            elif day <= 21:
                return "Week 3 (15-21)"
            elif day <= 28:
                return "Week 4 (22-28)"
            else:
                return "Week 5 (29-30)"
        ydf['cal_week'] = ydf['cal_day'].apply(get_cal_week)
        
        # Find 3rd Friday of September (OpEx)
        fridays = ydf[ydf.index.dayofweek == 4]
        opex_date = fridays.index[2] if len(fridays) >= 3 else None
        
        # Find monthly High
        high_idx = ydf['High'].idxmax()
        high_val = ydf.loc[high_idx, 'High']
        high_td = ydf.loc[high_idx, 'trading_day']
        high_cal_day = high_idx.day
        high_dow = high_idx.day_name()
        high_cal_week = ydf.loc[high_idx, 'cal_week']
        
        # High relative to OpEx
        if opex_date is not None:
            if high_idx < opex_date:
                opex_rel = "Before OpEx"
            elif high_idx == opex_date:
                opex_rel = "On OpEx"
            else:
                opex_rel = "After OpEx"
        else:
            opex_rel = "Unknown"
            
        # Find monthly Close max
        close_idx = ydf['Close'].idxmax()
        close_td = ydf.loc[close_idx, 'trading_day']
        close_cal_day = close_idx.day
        close_dow = close_idx.day_name()
        
        records.append({
            'year': y,
            'high_date': high_idx,
            'high_cal_day': high_cal_day,
            'high_trading_day': high_td,
            'total_trading_days': len(ydf),
            'high_dow': high_dow,
            'high_cal_week': high_cal_week,
            'opex_rel': opex_rel,
            'close_date': close_idx,
            'close_cal_day': close_cal_day,
            'close_td': close_td,
            'close_dow': close_dow,
            'sep_return': (ydf['Close'].iloc[-1] / ydf['Open'].iloc[0] - 1) * 100
        })
        
    res_df = pd.DataFrame(records)
    
    # Periods to evaluate
    periods = {
        'All Time (1928-2025)': res_df,
        'Post-WWII (1950-2025)': res_df[res_df['year'] >= 1950],
        'Modern Era (1975-2025)': res_df[res_df['year'] >= 1975],
        'Past 30 Years (1996-2025)': res_df[res_df['year'] >= 1996],
        'Past 20 Years (2006-2025)': res_df[res_df['year'] >= 2006]
    }
    
    for pname, pdf in periods.items():
        n = len(pdf)
        print("=" * 60)
        print(f"PERIOD: {pname} (N = {n} years)")
        print("=" * 60)
        
        print("\n--- 1. DISTRIBUTION BY CALENDAR WEEK OF SEPTEMBER ---")
        week_counts = pdf['high_cal_week'].value_counts()
        for w in ["Week 1 (1-7)", "Week 2 (8-14)", "Week 3 (15-21)", "Week 4 (22-28)", "Week 5 (29-30)"]:
            cnt = week_counts.get(w, 0)
            pct = cnt / n * 100
            print(f"  {w:18s}: {cnt:2d} keer ({pct:5.1f}%)")
            
        print("\n--- 2. DISTRIBUTION BY TRADING DAY OF MONTH (TOP 5) ---")
        td_counts = pdf['high_trading_day'].value_counts().head(7)
        for td, cnt in td_counts.items():
            pct = cnt / n * 100
            print(f"  Handelsdag {td:2d}          : {cnt:2d} keer ({pct:5.1f}%)")
            
        print("\n--- 3. DISTRIBUTION BY EXACT CALENDAR DAY (TOP 7) ---")
        cd_counts = pdf['high_cal_day'].value_counts().head(7)
        for cd, cnt in cd_counts.items():
            pct = cnt / n * 100
            print(f"  {cd:2d} september           : {cnt:2d} keer ({pct:5.1f}%)")
            
        print("\n--- 4. DISTRIBUTION BY DAY OF THE WEEK (DOW) ---")
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        dow_counts = pdf['high_dow'].value_counts()
        for dow in dow_order:
            cnt = dow_counts.get(dow, 0)
            pct = cnt / n * 100
            print(f"  {dow:12s}           : {cnt:2d} keer ({pct:5.1f}%)")
            
        print("\n--- 5. TIMING RELATIVE TO OPEX (3RD FRIDAY) ---")
        opex_counts = pdf['opex_rel'].value_counts()
        for k, cnt in opex_counts.items():
            pct = cnt / n * 100
            print(f"  {k:15s}        : {cnt:2d} keer ({pct:5.1f}%)")
            
        # First half vs Second half
        first_half = (pdf['high_cal_day'] <= 15).sum()
        second_half = (pdf['high_cal_day'] > 15).sum()
        print(f"\n--- 6. EERSTE HELFT (1-15 Sep) VS TWEEDE HELFT (16-30 Sep) ---")
        print(f"  1 t/m 15 september : {first_half:2d} keer ({first_half/n*100:5.1f}%)")
        print(f"  16 t/m 30 september: {second_half:2d} keer ({second_half/n*100:5.1f}%)")

if __name__ == '__main__':
    run_analysis()
