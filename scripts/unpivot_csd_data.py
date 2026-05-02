import pandas as pd
import duckdb as ddb
import numpy as np

file_path = "data/Mtl_Tor_Edm_Van_CSDs_Natasha.csv"

# ---------------------------------------------------------
# 1. READ ONCE & ENFORCE SCHEMA
# ---------------------------------------------------------
tenures = ['Both', 'Owner', 'Renter']
metrics = ['population', 'income', 'stir']

# Generates: ['geography', 'immigrant_status', 'Total_population', 'Total_income', ...]
col_names = ['geography', 'immigrant_status'] + [
    f"{t}_{m}" for t in tenures for m in metrics
]

df = pd.read_csv(file_path, encoding='latin-1', skiprows=6, names=col_names)

# ---------------------------------------------------------
# 2. EXTRACT CITY & SUBDIVISION
# ---------------------------------------------------------
df['geography'] = df['geography'].str.strip()
is_cma = df['geography'].str.contains('(CMA)', regex=False)

df['city'] = np.where(is_cma, df['geography'], np.nan)
df['city'] = df['city'].ffill().str.extract(r'^\s*([^\(]+)').squeeze().str.strip()
df['subdivision'] = df['geography'].str.extract(r'^\s*([^\(]+)').squeeze().str.strip()

# Filter out aggregates
df = df[~is_cma & ~df['geography'].str.contains('Canada', regex=False)]

# ---------------------------------------------------------
# 3. THE MAGIC UNPIVOT (Replacing the For-Loop)
# ---------------------------------------------------------
# Isolate the columns that identify the row
index_cols = ['city', 'subdivision', 'geography', 'immigrant_status']
df = df.set_index(index_cols)

# We turn the 9 flat metric columns into a MultiIndex (Level 1: Tenure, Level 2: Metric)
df.columns = pd.MultiIndex.from_product([tenures, metrics], names=['tenure', 'metric'])

# .stack() pushes the 'tenure' level from the columns down into the rows.
# It automatically leaves population, income, and stir as columns!
df_unpivoted = df.stack(level='tenure').reset_index()

# ---------------------------------------------------------
# 4. CLEAN UP & TYPE CONVERSION
# ---------------------------------------------------------
df_unpivoted['immigrant_status'] = df_unpivoted['immigrant_status'].str.strip().replace({
    'Non-immigrants': 'Non-immigrant',
    'Total Immigrant Status': 'Both'
})

for col in metrics:
    df_unpivoted[col] = pd.to_numeric(df_unpivoted[col], errors='coerce')

df_unpivoted = df_unpivoted.sort_values(
    ['city', 'subdivision', 'immigrant_status', 'tenure']
).reset_index(drop=True)

# ---------------------------------------------------------
# 5. DATABASE EXPORT
# ---------------------------------------------------------
print(f"Unpivoted shape: {df_unpivoted.shape}")
print(f"\nFirst 5 rows:\n{df_unpivoted.head(5).to_string()}")
print(f"\nUnique cities: {df_unpivoted['city'].nunique()}")
print(f"Unique subdivisions: {df_unpivoted['subdivision'].nunique()}")

# Use a context manager (with) to ensure the database connection closes safely
with ddb.connect("data/csd_unpivoted.duckdb") as con:
    con.execute("DROP TABLE IF EXISTS csd_housing_data")
    con.execute("CREATE TABLE csd_housing_data AS SELECT * FROM df_unpivoted")
    
    row_count = con.execute("SELECT COUNT(*) FROM csd_housing_data").fetchone()[0]
    print(f"\nSaved to DuckDB: {row_count} rows in csd_housing_data table")
    
    print(f"\nSample by tenure:")
    sample = con.execute("""
        SELECT tenure, COUNT(*) as count
        FROM csd_housing_data 
        GROUP BY tenure
        ORDER BY tenure
    """).fetchdf()
    print(sample.to_string(index=False))

print("\nDone! File saved to: data/csd_unpivoted.duckdb")