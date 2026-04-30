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

#Input
#   gdf : the polygons to plot
#   features : features to plot (expecting geometry such as LineStrings) - will test with other feature types
#   save_filepath : optional path where to save the graph, if not present, plot displayed and deleted
#   color_norm_value : optional string representing the gdf column values to normalize polygon coloring according to some condition of the CSDs (i.e. %rental properties)
# NOTE: the gdf we plot does not need to be the gdf we searched features over - this is helpful, as we could pass in much more granular CSDs, while querying over the larger Toronto CSD for the API call
def plot_features_over_geometry(gdf, features, feature_keys, save_filepath=None, color_norm_value=None, label_names=True):
            
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

    if label_names:

        for _, row in gdf.iterrows():
            centroid = row['geometry'].centroid
            ax.annotate(
                text=row['CDNAME'],
                xy=(centroid.x, centroid.y),
                ha='center',
                va='center',
                fontsize=8,
                color='black'
            )

    #need each feature to have its own color and legend should reflect that
    feature_gdf_list = []
    labels = []

    for tup in feature_keys:
        # filter for only the high-level feature type
        temp_f = features.dropna(subset=[tup[0]])
        # then filter for low-level feature type
        feature_gdf_list.append(temp_f[temp_f[tup[0]] == tup[1]])
        labels.append(tup[1])

    # generate N distinct colors, excluding reds
    colors = plt.cm.tab10.colors  # 10 distinct colors, none are red

    legend_handles = []

    for i, (feature_gdf, label) in enumerate(zip(feature_gdf_list, labels)):
        color = colors[i % len(colors)]
        feature_gdf.plot(ax=ax, color=color, linewidth=0.5)
        legend_handles.append(mpatches.Patch(color=color, label=label))

    ax.legend(handles=legend_handles, loc='upper right')

    # features.plot(ax=ax, color='blue', linewidth=0.5)

    if save_filepath:
        plt.savefig(save_filepath)
    else:
        plt.show()

if __name__ == '__main__':
    #cities in Ontario
    # gdf = and_over_or('.\GIS_work\data\lcsd000a25p_e.gpkg', feature_dict={'PRNAME' : ['Ontario'], 'CSDTYPE' : ['CTY', 'T']})
    gdf = and_over_or('.\GIS_work\data\lcsd000a25p_e.gpkg', feature_dict={'PRNAME' : ['Ontario'],
                                    'CDNAME' : ['Toronto']})

    # features we want to find
    map_feature_dict = {'railway' : ['subway'], 'highway' : ['motorway', 'trunk', 'primary', 'bus_stop'], 'amenity' : ['bus_station'], 'cycleway' : ['lane'], 'public_transport' : ['stop_position'], 'route' : ['bus']}
    # map_feature_dict = {'railway' : ['subway']}

    features, multi_polygon, feature_keys = fetch_features(gdf, map_feature_dict)

    plot_features_over_geometry(gdf, features, feature_keys, save_filepath='.\GIS_work\graphs\\better_graph_with_bus.png')

