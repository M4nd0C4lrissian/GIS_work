import pandas as pd
import duckdb as ddb
import numpy as np

df = pd.read_csv(
    "data/Mtl_Tor_Edm_Van_CSDs_Natasha.csv",
    encoding='latin-1',
    header=[4, 5],
    skiprows=[0, 1, 2, 3]
)

new_columns = []
for col in df.columns:
    if isinstance(col, tuple):
        level0, level1 = col
        if level1 and level1 != '':
            new_columns.append(level1)
        else:
            new_columns.append(level0)
    else:
        new_columns.append(col)

df.columns = new_columns

df_raw = pd.read_csv(
    "data/Mtl_Tor_Edm_Van_CSDs_Natasha.csv",
    encoding='latin-1',
    skiprows=4,
    header=0
)

df_data = pd.read_csv(
    "data/Mtl_Tor_Edm_Van_CSDs_Natasha.csv",
    encoding='latin-1',
    skiprows=5,
    header=0
)

base_cols = ['geography', 'immigrant_status']
tenure_metrics = ['population', 'income', 'stir']

column_names = base_cols.copy()
tenure_list = ['Total', 'Owner', 'Renter']
for tenure in tenure_list:
    for metric in tenure_metrics:
        column_names.append(f"{tenure}_{metric}")

df_data.columns = column_names

df_data['geography'] = df_data['geography'].str.strip()

# --- NEW: Extract city and subdivision ---
is_cma = df_data['geography'].str.contains('(CMA)', regex=False)

df_data['city'] = np.where(is_cma, df_data['geography'], np.nan)
df_data['city'] = df_data['city'].ffill()
df_data['city'] = df_data['city'].str.extract(r'^\s*([^\(]+)').squeeze().str.strip()

df_data['subdivision'] = df_data['geography'].str.extract(r'^\s*([^\(]+)').squeeze().str.strip()

# Filter out CMA aggregates and Canada rows to keep only subdivisions
df_data = df_data[~is_cma & ~df_data['geography'].str.contains('Canada', regex=False)]
# -----------------------------------------

dfs_long = []
for tenure in tenure_list:
    pop_col = f"{tenure}_population"
    inc_col = f"{tenure}_income"
    stir_col = f"{tenure}_stir"
    
    # Include new columns in the subset
    df_subset = df_data[['city', 'subdivision', 'geography', 'immigrant_status', pop_col, inc_col, stir_col]].copy()
    df_subset = df_subset.rename(columns={
        pop_col: 'population',
        inc_col: 'income',
        stir_col: 'stir'
    })
    df_subset['tenure'] = tenure
    dfs_long.append(df_subset)

df_unpivoted = pd.concat(dfs_long, ignore_index=True)

# Reorder columns with city and subdivision
df_unpivoted = df_unpivoted[['city', 'subdivision', 'geography', 'immigrant_status', 'tenure', 'population', 'income', 'stir']]

df_unpivoted = df_unpivoted.sort_values(['city', 'subdivision', 'immigrant_status', 'tenure']).reset_index(drop=True)

# Clean up immigrant_status labels
df_unpivoted['immigrant_status'] = df_unpivoted['immigrant_status'].str.strip()
df_unpivoted['immigrant_status'] = df_unpivoted['immigrant_status'].replace({
    'Non-immigrants': 'Non-immigrant',
    'Total Immigrant Status': 'Both'
})

# Replace non-numeric values with NaN for metrics
for col in ['population', 'income', 'stir']:
    df_unpivoted[col] = pd.to_numeric(df_unpivoted[col], errors='coerce')

print(f"Unpivoted shape: {df_unpivoted.shape}")
print(f"\nFirst 10 rows:")
print(df_unpivoted.head(10).to_string())
print(f"\nUnique cities: {df_unpivoted['city'].nunique()}")
print(f"Unique subdivisions: {df_unpivoted['subdivision'].nunique()}")
print(f"Unique tenures: {df_unpivoted['tenure'].unique()}")

con = ddb.connect("data/csd_unpivoted.duckdb")
con.execute("DROP TABLE IF EXISTS csd_housing_data")
con.execute("CREATE TABLE csd_housing_data AS SELECT * FROM df_unpivoted")

result = con.execute("SELECT COUNT(*) as row_count FROM csd_housing_data").fetchone()
print(f"\nSaved to DuckDB: {result[0]} rows in csd_housing_data table")

print(f"\nSample by tenure:")
sample = con.execute("""
    SELECT tenure, COUNT(*) as count
    FROM csd_housing_data 
    GROUP BY tenure
    ORDER BY tenure
""").fetchdf()
print(sample.to_string(index=False))

con.close()
print("\nDone! File saved to: data/csd_unpivoted.duckdb")