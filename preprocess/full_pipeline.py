from CSD_to_DA import map_das_to_csds
from one_time import one_time
from pivot_DA_census import filter_for_coi, pivot_census
from constants import COI, PR_TO_ID_MAP
from util.pathing import is_empty_folder

from pathlib import Path
import pandas as pd
import numpy as np

#USAGE notes - 

def preprocess(contest_data_path, provinces=['Quebec']):

    Path("GIS_work/data/Contest Data").mkdir(parents=True, exist_ok=True)
    Path("GIS_work/data/DA Data").mkdir(parents=True, exist_ok=True)
    
    if is_empty_folder("GIS_work/data/Contest Data") or is_empty_folder("GIS_work/data/DA Data"):
        raise RuntimeError("Need to download data files!")
    
    one_time(contest_data_path)
    
    characteristics = pd.read_csv('GIS_work\data\DA Data\queryable_characteristics.csv')
    coi_names = characteristics[characteristics['CHARACTERISTIC_ID'].isin(COI)]['CHARACTERISTIC_NAME']
    
    print('Characteristics of interest:')
    print('---------------------------------------------')
    print(coi_names)
    
    assert np.all([p in PR_TO_ID_MAP for p in provinces]), "Unsupported provinces - check constants.py"
    
    for pr in provinces:
        assert Path(f'GIS_work/data/DA Data/{pr}')
        
        
        filter_for_coi(pr)
        pivot_census(pr)
        map_das_to_csds(pr)
        
        
if __name__ == '__main__':
    preprocess('GIS_work\data\Contest Data\Cleaned_Mtl_Data.csv')
    
    
    
    