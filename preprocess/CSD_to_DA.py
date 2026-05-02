import pandas as pd
from util.constants import PR_TO_ID_MAP

#Input:
#   pr - the string representation of the Province in question
#Operation:
#   Pulls all of the CSDs in the input province, as found in the Contest Data
#   Finds all DAs present, creates a table that stores DA geographic info, and maps it to the associated CSD
#   the intention is for the created file to facilitate connection of DA-level information to larger CSDs

def map_das_to_csds(pr : str) -> None:

    pr_id = PR_TO_ID_MAP[pr]

    contest_data = pd.read_csv(f'GIS_work\data\Contest Data\Edited_Data.csv', encoding='latin-1')

    #hopefully the id is saved as an int
    pr_contest_data = contest_data[contest_data['PRUID'] == pr_id]

    #geographic_attribute_file
    gaf = pd.read_csv('GIS_work\data\\2021_geographic_attribute_file.csv', encoding='latin-1', low_memory=False)

    # we want all of the DAs present in the CSDs in our 
    pr_csd_ids = pr_contest_data['CSD_UID'].unique()
    filtered_gaf = gaf[gaf['CSDUID_SDRIDU'].isin(pr_csd_ids)]

    # For each unique DA, keep the relevant columns
    # DA is not unique per row (there are smaller dissemination blocks)
    da_table = (
        filtered_gaf[['CSDUID_SDRIDU', 'DAUID_ADIDU', 
                    'DARPLAMX_ADLAMX', 'DARPLAMY_ADLAMY', 
                    'DARPLAT_ADLAT', 'DARPLONG_ADLONG']]
        .drop_duplicates(subset='DAUID_ADIDU')
        .set_index('DAUID_ADIDU')
    )
    # rename so we're not flipping between standards
    da_table = da_table.reset_index().rename(columns={
        'CSDUID_SDRIDU': 'CSD_UID',
        'DAUID_ADIDU': 'DA_UID'
    }).set_index('DA_UID')

    da_table.to_csv(f'GIS_work\data\DA Data\{pr}\{pr}_DA_per_CSD.csv')