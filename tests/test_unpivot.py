import pandas as pd
import duckdb as ddb
import math

RAW_CSV = "data/Mtl_Tor_Edm_Van_CSDs_Natasha.csv"
DB_FILE = "data/csd_unpivoted.duckdb"

def get_raw_csv_df():
    tenures = ['Total', 'Owner', 'Renter']
    metrics = ['population', 'income', 'stir']
    col_names = ['geography', 'immigrant_status'] + [
        f"{t}_{m}" for t in tenures for m in metrics
    ]
    df = pd.read_csv(RAW_CSV, encoding='latin-1', skiprows=6, names=col_names)
    return df

def test_data_points(duckdb_con, raw_df):
    print("Running test_data_points...")
    # Test Westmount
    westmount_raw = raw_df[
        (raw_df['geography'].str.contains("Westmount", na=False)) & 
        (raw_df['immigrant_status'].str.strip() == "Non-immigrants")
    ].iloc[0]
    
    raw_pop = pd.to_numeric(westmount_raw['Owner_population'], errors='coerce')
    res = duckdb_con.execute("""
        SELECT population FROM csd_housing_data 
        WHERE subdivision = 'Westmount' 
        AND immigrant_status = 'Non-immigrant' 
        AND tenure = 'Owner'
    """).fetchone()
    
    if pd.isna(raw_pop):
        assert math.isnan(res[0]), f"Expected NaN, got {res[0]}"
    else:
        assert raw_pop == res[0], f"Expected {raw_pop}, got {res[0]}"

    # Test Toronto
    toronto_raw = raw_df[
        (raw_df['geography'].str.contains("Toronto (3520005)", na=False, regex=False)) & 
        (raw_df['immigrant_status'].str.strip() == "Total Immigrant Status")
    ].iloc[0]

    raw_inc = pd.to_numeric(toronto_raw['Renter_income'], errors='coerce')
    res2 = duckdb_con.execute("""
        SELECT income FROM csd_housing_data 
        WHERE subdivision = 'Toronto' 
        AND immigrant_status = 'Both' 
        AND tenure = 'Renter'
    """).fetchone()

    if pd.isna(raw_inc):
        assert math.isnan(res2[0]), f"Expected NaN, got {res2[0]}"
    else:
        assert raw_inc == res2[0], f"Expected {raw_inc}, got {res2[0]}"

    # Test Burnaby
    burnaby_raw = raw_df[
        (raw_df['geography'].str.contains("Burnaby", na=False)) & 
        (raw_df['immigrant_status'].str.strip() == "Immigrant")
    ].iloc[0]

    raw_stir = pd.to_numeric(burnaby_raw['Total_stir'], errors='coerce')
    res3 = duckdb_con.execute("""
        SELECT stir FROM csd_housing_data 
        WHERE subdivision = 'Burnaby' 
        AND immigrant_status = 'Immigrant' 
        AND tenure = 'Total'
    """).fetchone()

    if pd.isna(raw_stir):
        assert math.isnan(res3[0]), f"Expected NaN, got {res3[0]}"
    else:
        assert raw_stir == res3[0], f"Expected {raw_stir}, got {res3[0]}"

    print("test_data_points passed.")

def test_hierarchy(duckdb_con):
    print("Running test_hierarchy...")
    res = duckdb_con.execute("""
        SELECT city FROM csd_housing_data 
        WHERE subdivision = 'Westmount' 
        LIMIT 1
    """).fetchone()
    assert res is not None
    assert res[0] == 'Montréal', f"Expected 'Montréal', got {res[0]}"
    print("test_hierarchy passed.")

def test_totals_match(duckdb_con, raw_df):
    print("Running test_totals_match...")
    res = duckdb_con.execute("""
        SELECT population FROM csd_housing_data 
        WHERE subdivision = 'Westmount' 
        AND immigrant_status = 'Non-immigrant' 
        AND tenure = 'Total'
    """).fetchone()
    
    duck_pop_total = res[0]
    
    westmount_raw = raw_df[
        (raw_df['geography'].str.contains("Westmount", na=False)) & 
        (raw_df['immigrant_status'].str.strip() == "Non-immigrants")
    ].iloc[0]
    
    raw_pop_total = pd.to_numeric(westmount_raw['Total_population'], errors='coerce')
    
    if pd.isna(raw_pop_total):
        assert math.isnan(duck_pop_total), f"Expected NaN, got {duck_pop_total}"
    else:
        assert raw_pop_total == duck_pop_total, f"Expected {raw_pop_total}, got {duck_pop_total}"
    print("test_totals_match passed.")

if __name__ == "__main__":
    duckdb_con = ddb.connect(DB_FILE, read_only=True)
    raw_df = get_raw_csv_df()
    
    try:
        test_data_points(duckdb_con, raw_df)
        test_hierarchy(duckdb_con)
        test_totals_match(duckdb_con, raw_df)
        print("All tests passed successfully!")
    finally:
        duckdb_con.close()
