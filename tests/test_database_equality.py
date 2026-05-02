import duckdb

def assert_databases_identical(db_path1, db_path2):
    # Connect to the first database
    con = duckdb.connect(db_path1)
    
    # Attach the second database as 'other'
    con.execute(f"ATTACH '{db_path2}' AS other")
    
    try:
        # 1. Check if both have the same tables
        tables_main = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        tables_other = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        
        assert tables_main == tables_other, f"Table lists differ: {tables_main} vs {tables_other}"
        
        # 2. Compare content table by table
        for (table_name,) in tables_main:
            # Check row counts first (fast)
            count1 = con.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            count2 = con.execute(f"SELECT COUNT(*) FROM other.{table_name}").fetchone()[0]
            assert count1 == count2, f"Row count mismatch in table {table_name}"
            
            # Check for data differences using EXCEPT
            # This finds rows in A that aren't in B, and rows in B that aren't in A
            diff_query = f"""
                (SELECT * FROM {table_name} EXCEPT SELECT * FROM other.{table_name})
                UNION ALL
                (SELECT * FROM other.{table_name} EXCEPT SELECT * FROM {table_name})
            """
            diff_count = con.execute(f"SELECT COUNT(*) FROM ({diff_query})").fetchone()[0]
            
            assert diff_count == 0, f"Data mismatch found in table {table_name}"
            
        print("✅ Databases are identical in schema and content.")
        
    finally:
        con.execute("DETACH other")
        con.close()

# Usage
assert_databases_identical('data/csd_housing_new.duckdb', 'data/csd_housing_old.duckdb')