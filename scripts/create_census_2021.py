import duckdb
import pandas as pd

print(duckdb.query("SELECT * FROM read_csv('data/statcan census 2021/98-401-X2021006_English_CSV_data_Ontario.csv', encoding='latin-1')"))

con = duckdb.connect("data/migration_datasets.duckdb")

con.query("CREATE TABLE census_2021 AS " \
"SELECT * FROM read_csv('data/statcan census 2021/98-401-X2021006_English_CSV_data_Ontario.csv', encoding='latin-1')")

con.close()