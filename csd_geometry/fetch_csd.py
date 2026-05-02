import geopandas as gpd
import numpy as np

# INPUT:
#   filepath - path to locally-saved Census Sub-Division Data (CSD) (expected as a .gpkg file (GeoPackage))
#   feature_dict - a dict of key, value_range, we are looking for CSDs that satisfy at least one value in value range over all keys present in feature dict
#   NOTE - this is an AND over ORs
# returns a GeoDataFrame (I think) including all of the features outlined in README.md

def reformat_csd(gdf):
    assert gdf.crs is not None
    return gpd.GeoDataFrame(gdf, crs=gdf.crs).to_crs("EPSG:4326")

def and_over_or(filepath, feature_dict):
    
    gdf = gpd.read_file(filepath)
    
    per_key_masks = []
    
    for key, value_range in feature_dict.items():
        assert type(value_range) == list
        value_masks = [gdf[key] == val for val in value_range]
        per_key_masks.append(np.logical_or.reduce(value_masks))

    final_mask = np.logical_and.reduce(per_key_masks)
    return reformat_csd(gdf.loc[final_mask])

#NOTE - untested
#same as above, except only one out of any of the listed conditions need to be true
def logical_or(filepath, feature_dict):
    
    gdf = gpd.read_file(filepath)
    
    per_key_masks = []
    
    for key, value_range in feature_dict.items():
        assert type(value_range) == list
        value_masks = [gdf[key] == val for val in value_range]
        per_key_masks.append(np.logical_or.reduce(value_masks))

    final_mask = np.logical_or.reduce(per_key_masks)
    return reformat_csd(gdf.loc[final_mask])

if __name__ == '__main__':
    #translation: a city OR a town that is in either Ontario or Quebec
    gdf = and_over_or(filepath='.\GIS_work\data\lcsd000a25p_e.gpkg', 
                     feature_dict={'PRNAME' : ['Ontario'],
                                   'CSDTYPE' : ['CTY', 'T']})
    #translation: a sub-division that satisfies being a city OR a town OR is in Quebec OR is in Ontario
    gdf2 = logical_or(filepath='.\GIS_work\data\lcsd000a25p_e.gpkg', 
                     feature_dict={'PRNAME' : ['Ontario', 'Quebec / Québec'],
                                   'CSDTYPE' : ['CTY', 'T']})
    pass
