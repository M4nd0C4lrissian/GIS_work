import duckdb
import pandas as pd

# Create VIEW with only selected features (see util/constants.py)
with duckdb.connect("data/migration_datasets.duckdb") as con:
    print(con.query("SHOW TABLES"))
    print(con.query("DESCRIBE census_2021"))

    # Print characteristic IDs and description
    print(con.query("SELECT DISTINCT characteristic_id, characteristic_name, characteristic_note " \
        "FROM census_2021 ORDER BY characteristic_id").df())

    # Print all rows with characteristic note in [1, 4, 5, 6, 45, 46, 47, 1528, 1529, 1666, 1667, 1668, 2224, 2225, 2226, 2227, 2228, 2229, 2230, 2594, 2595, 2596, 2597, 2604, 2607, 2608, 2609, 2612, 2613, 2614, 2615, 2616]
    print(con.query("CREATE OR REPLACE VIEW census_2021_selected_coi AS " \
        "SELECT * FROM census_2021 WHERE characteristic_note IN "
        "(1, 4, 5, 6, 45, 46, 47, 1528, 1529, 1666, 1667, 1668, 2224, 2225, 2226, " \
        "2227, 2228, 2229, 2230, 2594, 2595, 2596, 2597, 2604, 2607, 2608, 2609, 2612, " \
        "2613, 2614, 2615, 2616)"))

