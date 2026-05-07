import pandas as pd
import numpy as np

def project(df):

    for c in df.columns[1:]:
        df[c] = df[c].str.replace(',', '', regex=False)
        df[c] = df[c].astype(int)
        df = df.rename(columns={c: int(c.replace(',', ''))})

    year_cols = [c for c in df.columns if c != df.columns[0]]
    label_col = df.columns[0]

    last_year = int(year_cols[-1])
    future_years = [last_year + i for i in range(1, 6)]

    df_extended = df.copy()

    for yr in future_years:
        if yr in df_extended.columns:  # skip if data already exists
            continue
        prev_years = [y for y in list(year_cols) + future_years if y < yr]
        last_3 = prev_years[-3:]
        growth_rates = df_extended[last_3].pct_change(axis=1).iloc[:, 1:]
        avg_growth = growth_rates.mean(axis=1)
        df_extended[yr] = (df_extended[prev_years[-1]] * (1 + avg_growth)).round(0).astype(int)

    return df_extended