import geopandas as gpd
import pandas as pd
import numpy as np

from process_geometry.fetch_geometry import and_over_or
from util.constants import PR_TO_ID_MAP
from plotting.plotting_overpass_features import plot_features_over_geometry, plot_polygons

pr = 'Quebec'

da_geometry = gpd.read_file(f'GIS_work\data\DA Data\{pr}\{pr}_DA_per_CSD.shp')

da_census_info = pd.read_csv(f'GIS_work\data\DA Data\{pr}\{pr}_DA_pivoted.csv')
da_census_info = gpd.GeoDataFrame(da_census_info)

result = da_geometry.merge(
    da_census_info,
    right_on='ALT_GEO_CODE',
    left_on='DAUID',
    how='left'
)

result = gpd.GeoDataFrame(result, geometry='geometry', crs=da_geometry.crs)
nan_rows = result[result.isna().any(axis=1)]
print(f'{nan_rows.shape[0]} of the DA shapes did not have any associated information.')

# color = result['  Immigrants'].values / (result['  Non-immigrants'].values + result['  Immigrants'].values)
color = result['Private dwellings occupied by usual residents'] / result['Total private dwellings']

plot_polygons(result, color, title='% Occupied Dwellings', save_filepath='GIS_work\graphs\\montreal_percent_occupied.png')


#tomorrow - overlay CSD data (with lines) over this - have a series of plot functions that pass around
# figs and axes to continuously overlay stuff

