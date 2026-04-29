from fetch_sd_polygon import and_over_or

import geopandas as gpd
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

#cities in Ontario
gdf = and_over_or('.\GIS_work\data\lcsd000a25p_e.gpkg', feature_dict={'PRNAME' : ['Ontario'],
                                    'CDNAME' : ['Toronto']})

#single for now
polygon = gdf['geometry'].iloc[0]
polygon = gpd.GeoDataFrame(geometry=[polygon], crs=gdf.crs).to_crs("EPSG:4326")


#https://wiki.openstreetmap.org/wiki/Map_features#Transportation
map_feature_dict = {'railway' : ['subway']}

#returns a bunch of LineStrings
features = ox.features.features_from_polygon(polygon=polygon.iloc[0]['geometry'], tags=map_feature_dict)

# looks like you need to make the fig and ax separately
fig, ax = plt.subplots(figsize=(10, 10))

#can normalize polygon coloring according to some characteristic of 
# the csd population (% immigrant, % rental, whatever - for now dummy values)
norm = mcolors.Normalize(vmin=0, vmax=100)
cmap = plt.cm.Reds

polygon.plot(
    ax=ax,
    cmap=cmap,
    linewidth=0.5,
    edgecolor='black',
)

features.plot(ax=ax, color='blue', linewidth=0.5)
plt.show()


# osmnx.graph.graph_from_polygon for main csd data, but what about the linestrings? 

pass