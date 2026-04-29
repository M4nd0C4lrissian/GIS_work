import geopandas as gpd
import numpy as np

# feature_dict - a dict of key, value_range, we are looking for CSDs that satisfy at least one value in value range over all keys present in feature dict
# hence it is an AND over ORs
def and_over_or(filepath, feature_dict):
    
    gdf = gpd.read_file(filepath)
    
    assert gdf.crs is not None
    
    per_key_masks = []
    
    for key, value_range in feature_dict.items():
        assert type(value_range) == list
        value_masks = [gdf[key] == val for val in value_range]
        per_key_masks.append(np.logical_or.reduce(value_masks))

    final_mask = np.logical_and.reduce(per_key_masks)
    return gdf.loc[final_mask]

if __name__ == '__main__':
    #translation: a city OR a town that is in either Ontario or Quebec
    gdf = and_over_or(filepath='.\GIS_work\data\lcsd000a25p_e.gpkg', 
                     feature_dict={'PRNAME' : ['Ontario', 'Quebec / Québec'],
                                   'CSDTYPE' : ['CTY', 'T']})
    pass
