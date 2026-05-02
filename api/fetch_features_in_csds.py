from fetch_csd import and_over_or

import geopandas as gpd
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from shapely.ops import unary_union

#Input
#   gdf - a GeoDataFrame containing the polygons within which we search, with coordinates in a recognized CRS standard, which we conver to ESPG:4326 to work with OSMNX
#   map_feature_dict - a set of key-value pairs that can be queried for using OverPass API (through OSMNX), a comprehensive list can be found here #https://wiki.openstreetmap.org/wiki/Map_features
#Returns: all the features found in each polygon present in gdf (still need to test if this works for multiple polygons)
def fetch_features(gdf, map_feature_dict):

    #TODO - make it work for multi-polygon
    multi = unary_union(gdf['geometry'])
    polygons = gpd.GeoDataFrame(geometry=[multi], crs=gdf.crs)

    #API call to extract features from our multipolygon - can timeout
    features = ox.features.features_from_polygon(polygon=polygons['geometry'].iloc[0], tags=map_feature_dict)

    found_keys = []
    #will not necessarily find all feature types
    for key, vals in map_feature_dict.items():

        if key in features.columns:
            for val in vals:
                if val in features[key].unique():
                    print(f'Found at least one {key}:{val}')
                    found_keys.append((key, val))

    return features, polygons, found_keys

if __name__ == '__main__':
    #cities in Ontario
    # gdf = and_over_or('.\GIS_work\data\lcsd000a25p_e.gpkg', feature_dict={'PRNAME' : ['Ontario'], 'CSDTYPE' : ['CTY', 'T']})
    gdf = and_over_or('.\GIS_work\data\lcsd000a25p_e.gpkg', feature_dict={'PRNAME' : ['Ontario'],
                                    'CDNAME' : ['Toronto']})

    # features we want to find
    # map_feature_dict = {'railway' : ['subway'], 'highway' : ['motorway', 'trunk', 'primary', 'bus_stop'], 'amenity' : ['bus_station'], 'cycleway' : ['lane'], 'public_transport' : ['stop_position'], 'route' : ['bus']}
    # map_feature_dict = {'railway' : ['subway']}
    map_feature_dict = {'railway' : ['subway'], 'highway' : ['motorway', 'trunk', 'primary']}

    features, multi_polygon, feature_keys = fetch_features(gdf, map_feature_dict)

    plot_features_over_geometry(gdf, features, feature_keys, save_filepath='.\GIS_work\graphs\\better_graph_example.png')

