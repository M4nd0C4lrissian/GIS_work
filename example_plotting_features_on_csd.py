from csd_geometry.fetch_csd import and_over_or
from api.fetch_features_in_csds import fetch_features
from plotting.plotting_overpass_features import plot_features_over_geometry

from pathlib import Path
from util.pathing import is_empty_folder

if __name__ == '__main__':
    
    Path("GIS_work/data/CSD Geometry Data").mkdir(parents=True, exist_ok=True)
    
    if is_empty_folder("GIS_work/data/CSD Geometry Data"):
        raise RuntimeError("Need to download data files!")
    
    
    #load locally saved CSD info
    gdf_toronto = and_over_or('.\GIS_work\data\CSD Geometry Data\lcsd000a25p_e.gpkg', feature_dict={'PRNAME' : ['Ontario'],
                                    'CDNAME' : ['Toronto']})
    gdf_toronto_hamilton = and_over_or('.\GIS_work\data\CSD Geometry Data\lcsd000a25p_e.gpkg', feature_dict={'PRNAME' : ['Ontario'],
                                    'CDNAME' : ['Toronto', 'Hamilton']})
    #see https://wiki.openstreetmap.org/wiki/Map_features
    transit_features = {'railway' : ['subway'], 'highway' : ['motorway', 'trunk', 'primary']}
    amenity_features = {'amenity' : ['hospital', 'casino', 'arts_centre', 'cinema', 'nightclub']}
    #NOTE - we could just as easily search for all of these features in the query

    feat1, _, keys1 = fetch_features(gdf_toronto, transit_features)
    feat2, _, keys2 = fetch_features(gdf_toronto_hamilton, transit_features)
    feat3, _, keys3 = fetch_features(gdf_toronto, amenity_features)
    feat4, _, keys4 = fetch_features(gdf_toronto_hamilton, amenity_features)

    plot_features_over_geometry(gdf_toronto, feat1, keys1, save_filepath='.\GIS_work\graphs\\example_1.png')
    plot_features_over_geometry(gdf_toronto_hamilton, feat2, keys2, save_filepath='.\GIS_work\graphs\\example_2.png')

    plot_features_over_geometry(gdf_toronto, feat3, keys3, save_filepath='.\GIS_work\graphs\\example_3.png')
    plot_features_over_geometry(gdf_toronto_hamilton, feat4, keys4, save_filepath='.\GIS_work\graphs\\example_4.png')