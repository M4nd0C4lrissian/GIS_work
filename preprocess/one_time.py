
import pandas as pd
import os
from util.pathing import path_exists

# simple one-time reformat that makes CSD ids more easily queries from contest data
def one_time(contest_data_path):
    
    if not path_exists(os.path.join(contest_data_path, 'Edited_Data.csv')):

        df = pd.read_csv(os.path.join(contest_data_path, 'Cleaned_Mtl_Data.csv'), encoding='latin-1')

        df[['name', 'CSD_UID', 'CSD_type']] = df['geography_name'].str.extract(r'^(.+?)\s*\((\d+)\)\s*([A-Z]+)')
        df = df.drop(columns=['geography_name'])

        df['PRUID'] = df['CSD_UID'].astype(str).str[:2]

        df.to_csv(os.path.join(contest_data_path, 'Edited_Data.csv'), encoding='latin-1')
        
    if not path_exists(os.path.join(contest_data_path, 'Edited_csd_unpivoted_rich.csv')):
        
        df = pd.read_csv(os.path.join(contest_data_path, 'csd_unpivoted_rich.csv'), encoding='latin-1')
        
        df[['name', 'CSD_UID', 'CSD_type']] = df['geography'].str.extract(r'^(.+?)\s*\((\d+)\)\s*([A-Z]+)')
        df['PRUID'] = df['CSD_UID'].str[:2]
        df.to_csv(os.path.join(contest_data_path, 'Edited_csd_unpivoted_rich.csv'), encoding='latin-1')
        
if __name__ == '__main__':
    one_time('GIS_work\data\Contest Data')