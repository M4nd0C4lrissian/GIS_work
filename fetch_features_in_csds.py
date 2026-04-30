from fetch_csd_polygon import and_over_or

import geopandas as gpd
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

#Input
#   gdf - a GeoDataFrame containing the polygons within which we search, with coordinates in a recognized CRS standard, which we conver to ESPG:4326 to work with OSMNX
#   map_feature_dict - a set of key-value pairs that can be queried for using OverPass API (through OSMNX), a comprehensive list can be found here #https://wiki.openstreetmap.org/wiki/Map_features
#Returns: all the features found in each polygon present in gdf (still need to test if this works for multiple polygons)
def fetch_features(gdf, map_feature_dict):

    assert gdf.crs is not None

    #TODO - make it work for multi-polygon
    #single for now
    polygon = gdf['geometry'].iloc[0]
    polygon = gpd.GeoDataFrame(geometry=[polygon], crs=gdf.crs).to_crs("EPSG:4326")

    #returns a bunch of LineStrings
    features = ox.features.features_from_polygon(polygon=polygon.iloc[0]['geometry'], tags=map_feature_dict)

    return features, polygon

#Input
#   gdf : the polygons to plot (need to test if this can be a gdf with multiple non-geometry columns, for now expects geometry)
#   features : features to plot (expecting geometry such as LineStrings) - will test with other feature types
#   save_filepath : optional path where to save the graph, if not present, plot displayed and deleted
#   color_norm_value : optional string representing the gdf column values to normalize polygon coloring according to some condition of the CSDs (i.e. %rental properties)
def plot_features_over_geometry(gdf, features, save_filepath=None, color_norm_value=None):
            
    # looks like you need to make the fig and ax separately
    fig, ax = plt.subplots(figsize=(10, 10))
        
    #can normalize polygon coloring according to some characteristic of the csd population
    vmin=0
    vmax=100
    if color_norm_value:
        vmin = gdf[color_norm_value].min()
        vmax = gdf[color_norm_value].max()

    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = plt.cm.Reds

    gdf.plot(
        ax=ax,
        cmap=cmap,
        linewidth=0.5,
        edgecolor='black',
        norm=norm
    )

    features.plot(ax=ax, color='blue', linewidth=0.5)
    if save_filepath:
        plt.savefig(save_filepath)
    else:
        plt.show()

if __name__ == '__main__':
    #cities in Ontario
    gdf = and_over_or('.\GIS_work\data\lcsd000a25p_e.gpkg', feature_dict={'PRNAME' : ['Ontario'],
                                    'CDNAME' : ['Toronto']})

    # features we want to find
    map_feature_dict = {'railway' : ['subway']}

    features, polygon = fetch_features(gdf, map_feature_dict)

    plot_features_over_geometry(polygon, features, save_filepath='.\GIS_work\graphs\graph.png')

