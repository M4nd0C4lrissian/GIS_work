import pandas as pd
from util.constants import COI
from util.pathing import path_exists

# this function pulls the full census for a province, and filters for the characteristics of interest (COI) at the Dissemination Area (DA) level
# NOTE: we remove any entries with certain Data quality conditions (you can read these in the meta txt file that is downloaded with the DA census data)
# NOTE: loading the first csv file will take a few minutes - change chunksize if RAM is an issue
def filter_for_coi(pr : str):

    chunk_iter = pd.read_csv(f'GIS_work\data\DA Data\{pr}\98-401-X2021006_English_CSV_data_{pr}.csv', encoding='latin-1', low_memory=False,
                     usecols=['ALT_GEO_CODE','GEO_LEVEL','GEO_NAME','DATA_QUALITY_FLAG','CHARACTERISTIC_ID','CHARACTERISTIC_NAME','CHARACTERISTIC_NOTE','C1_COUNT_TOTAL'],
                     chunksize=50_000) #change this if RAM availability is an issue
    
    matching_chunks = []

    for chunk in chunk_iter:
        # our characteristics of interest (COI) at the Dissemination Area (DA) level
        filtered = chunk[
            (chunk['GEO_LEVEL'] == 'Dissemination area') &
            (chunk['CHARACTERISTIC_ID'].isin(COI))
        ]
        if not filtered.empty:
            matching_chunks.append(filtered)

    da_coi = pd.concat(matching_chunks, ignore_index=True)
    del matching_chunks
    
    print(f'Loaded full census data of {pr}.')

    # Pad to 5 digits to handle integer-stored flags (e.g. 0 -> "00000")
    da_coi["DATA_QUALITY_FLAG"] = da_coi["DATA_QUALITY_FLAG"].fillna("0").astype(str).str.zfill(5)

    # Flag is problematic if the 2nd digit (short-form quality) is 3, 4, or 5
    bad_mask = da_coi["DATA_QUALITY_FLAG"].str[1].isin(["3", "4", "5"])

    print(f"Rows with poor data quality (short-form non-response ≥ 30%): {bad_mask.sum()}")
    print(da_coi[bad_mask][["ALT_GEO_CODE", "GEO_NAME", "DATA_QUALITY_FLAG"]])
    da_coi = da_coi[~bad_mask]
    da_coi.to_csv(f'GIS_work/data/DA Data/{pr}/{pr}_DA_filtered.csv', index=False)
    
    print(f'Filtered for COIs in census data of {pr}.')
    
    # NOTE: this needs to be modified to work with chunking, but for now it is ignorable as I have already generated this file, just need to remember to push it
    # GIS_work\data\DA Data\queryable_characteristics.csv

    # # makes a catalogue of what characteristics are available and their IDs, so the COI can be changed in constants.py
    # if not path_exists('GIS_work\data\queryable_characteristics.csv'):
    #     result_df = df.drop_duplicates(subset='CHARACTERISTIC_NAME', keep='first')[['CHARACTERISTIC_NAME', 'CHARACTERISTIC_ID']].reset_index(drop=True)
    #     result_df.to_csv('GIS_work\data\queryable_characteristics.csv')
 
# After previously filtering for characteristics of interest, this functions pivots DA-level census data
# to have a single row for each DA, with all of the COI values as the columns
# NOTE: it removes any DAs with NaNs (there are so many DAs that we can reasonably spare these)
def pivot_census(pr: str) -> None:
    df = pd.read_csv(f'GIS_work/data/DA Data/{pr}/{pr}_DA_filtered.csv', dtype=str)
 
    # Normalize column names
    df.columns = df.columns.str.strip()
 
    # Keep only what we need
    df = df[["ALT_GEO_CODE", "GEO_NAME", "CHARACTERISTIC_NAME", "C1_COUNT_TOTAL"]]
 
    # Convert count to numeric (keep NaN for missing/suppressed values)
    df["C1_COUNT_TOTAL"] = pd.to_numeric(df["C1_COUNT_TOTAL"], errors="coerce")
 
    # Pivot characteristics into columns
    pivoted = df.pivot_table(
        index=["ALT_GEO_CODE", "GEO_NAME"],
        columns="CHARACTERISTIC_NAME",
        values="C1_COUNT_TOTAL",
        aggfunc="first",
    )
 
    pivoted.columns.name = None
    pivoted = pivoted.reset_index()
 
    # Validate expected row count
    unique_codes = df["ALT_GEO_CODE"].nunique()
    if len(pivoted) != unique_codes:
        print(f"Warning: expected {unique_codes} rows but got {len(pivoted)}. "
              "Check for duplicate ALT_GEO_CODE + CHARACTERISTIC_NAME combinations.")
 
    unique_chars = df["CHARACTERISTIC_NAME"].nunique()
    if unique_chars != len(COI):
        print(f"Note: found {unique_chars} unique CHARACTERISTIC_NAME values (expected {len(COI)}).")
 
    print('NaN values per column.')
    print(pivoted.isnull().sum())
 
    pivoted.dropna(inplace=True)
    pivoted.to_csv(f'GIS_work\data\DA Data\{pr}\{pr}_DA_pivoted.csv', index=False)
    print(f"Done. Output: 'GIS_work\data\DA Data\{pr}\{pr}_DA_pivoted.csv'  ({len(pivoted)} rows + {len(pivoted.columns)} columns)")