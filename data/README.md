The following files are expected for DuckDB-related scripts:

| Filename | Purpose | Description | Comments |
| -------- | ------- | ----------- | -------- |
| `migration_datasets.duckdb` | Database file | Contains SQL tables for efficient querying. | Can be generated using `scripts/unpivot_csd_data.py` with `data/Mtl_Tor_Edm_Van_CSDs_Natasha.csv` |
| `Mtl_Tor_Edm_Van_CSDs_Natasha.csv` | Source of truth | The raw .csv file provided by MDC organizers. | Required to generate the `csd_housing` table in `migration_datasets.duckdb`. |

The database file contains multiple SQL tables optimized for efficient querying:

| Tables | Description |
| ------ | ----------- | 
| csd_housing | Contains the population, average household income, average shelter-cost-to-income ratio ("STIR") for various 2021 census subdivisions in Canada, provided by the Migration Data Challenge hosts. |
