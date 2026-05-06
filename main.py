import geopandas as gpd
import pandas as pd
from pathlib import Path

from process_geometry.fetch_geometry import and_over_or
from util.constants import PR_TO_ID_MAP
from plotting.plotting_overpass_features import plot_features_over_geometry, plot_polygons, simple_plot_polygons
from process_geometry.fetch_geometry import reformat_crs

def plot_da_data(pr):

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

    Path(f'GIS_work\graphs\{pr}').mkdir(parents=True, exist_ok=True)
    
    csd_geo = reformat_crs(gpd.read_file('GIS_work\data\CSD Geometry Data\lcsd000a25p_e.gpkg'))
    to_plot = csd_geo[csd_geo['CSDUID'].isin(result['CSD_UID'].astype(str).values)]
    to_plot = gpd.GeoDataFrame(to_plot, geometry='geometry', crs=csd_geo.crs)
    #IMMIGRANTS AND HOUSING
    
    color = result['  Renter'] / result["Total - Private households by tenure - 25% sample data"]
    fig, ax = plot_polygons(result, color, title='Percent Apartments', continue_plot=True)
    simple_plot_polygons(to_plot['geometry'], fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_apartments.png')
    
    color = result['  Immigrants'].values / (result['  Non-immigrants'].values + result['  Immigrants'].values)
    fig, ax = plot_polygons(result, color, title='Percent Immigrant Residents', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_immigrants.png')

    color = result['Private dwellings occupied by usual residents'] / result['Total private dwellings']
    fig, ax = plot_polygons(result, color, title='Percent Dwellings Occupied', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_occupied.png')
    
    #NOTE: this one should not show up as a percent
    color = result['  Median monthly shelter costs for owned dwellings ($)']
    fig, ax = plot_polygons(result, color, title='Median monthly shelter costs', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_median_shelter_costs.png')
    
    color = result['  Major repairs needed'] / (result['  Only regular maintenance and minor repairs needed'] + result['  Major repairs needed'])
    fig, ax = plot_polygons(result, color, title='Percent Dwellings in Need of Major Repairs', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_repair.png')
    
    #UNEMPLOYMENT

    color = result['Unemployment rate'] / 100
    fig, ax = plot_polygons(result, color, title='Unemployment Rate', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_unemployment.png')
    #COMMUTE - NOTE: all these totals are different - :TODO - switch to using indices instead

    total_commute_dest = result['Total - Commuting destination for the employed labour force aged 15 years and over with a usual place of work - 25% sample data']
    commute_out_of_csd = result['  Commute to a different census subdivision (CSD) within census division (CD) of residence'] \
                        + result['  Commute to a different census subdivision (CSD) and census division (CD) within province or territory of residence']
                        
    color = commute_out_of_csd / total_commute_dest
    fig, ax = plot_polygons(result, color, title='Percent Commute out of CSD', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_commute_out_of_csd.png')
    
    color =  (result['Total - Place of work status for the employed labour force aged 15 years and over - 25% sample data'] - result['  Worked at home']) / result['Total - Place of work status for the employed labour force aged 15 years and over - 25% sample data']
    fig, ax = plot_polygons(result, color, title='Percent of Employed who Commute', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_commuters.png')
    
    color = result['  Car, truck or van'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    fig, ax = plot_polygons(result, color, title='Percent of Commuters who Drive',continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_drivers.png')
    
    color = result['  Public transit'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    fig, ax = plot_polygons(result, color, title='Percent of Commuters who take Public Transit', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_transiters.png')
    
    color = (result['  60 minutes and over']) / result['Total - Commuting duration for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    fig, ax = plot_polygons(result, color, title='Percent of Commuters who commute > 60 minutes', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_commute_times.png')
#TODO: check if I'm pre-pruning rows based on a single NaN (I think I am)
#tomorrow - overlay CSD data (with lines) over this - have a series of plot functions that pass around
# figs and axes to continuously overlay stuff

if __name__ == '__main__':
    
    plot_da_data('Ontario')
    # for pr in ['BritishColumbia', 'Quebec', 'Ontario', 'Alberta']:
    #     plot_da_data(pr)