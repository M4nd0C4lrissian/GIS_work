import duckdb
import pandas as pd

# Load database
con = duckdb.connect("data/migration_datasets.duckdb")
print(con.query("SHOW TABLES")) # Print all tables in the database

# Load unpivoted data
df = con.query("SELECT * FROM csd_housing").df()

# Calculate new columns
avg_housing_cost = df['avg_income'] * df['avg_stir'] / 100 
print(avg_housing_cost)

avg_remaining_after_housing = df['avg_income'] - avg_housing_cost
print(avg_remaining_after_housing)

# Verify consistency
print(avg_housing_cost + avg_remaining_after_housing)
print(df['avg_income'])

# Create view with new columns
con.query("CREATE VIEW csd_housing_rich AS " \
"SELECT *, avg_income * avg_stir / 100 AS avg_housing, " \
"avg_income - avg_housing AS avg_remaining " \
"FROM csd_housing")

# Export to .csv
con.query("SELECT * FROM csd_housing_rich ").df().to_csv("data/csd_unpivoted_rich.csv")
con.close() 
