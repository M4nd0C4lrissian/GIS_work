import duckdb
import pandas as pd

with duckdb.connect("data/csd_housing.duckdb") as con:
    df = con.query("FROM csd_housing_data SELECT DISTINCT geography").df()

print(df.head(100))
