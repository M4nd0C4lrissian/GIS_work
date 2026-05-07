import geopandas as gpd
import pandas as pd
from pathlib import Path
import os
import itertools

from process_geometry.fetch_geometry import and_over_or
from util.constants import PR_TO_ID_MAP
from plotting.plotting_overpass_features import plot_features_over_geometry, plot_polygons, simple_plot_polygons
from process_geometry.fetch_geometry import reformat_crs

from plotting.plotting_overpass_features import truncate_cmap

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

def get_csd_immigrant_renters(contest_data_path, pr):
    df = pd.read_csv(os.path.join(contest_data_path, 'Edited_csd_unpivoted_rich.csv'))
    
    ##filter first two CSD digits to map up to current 
    df = df[df['PRUID'] == PR_TO_ID_MAP[pr]]
    
    ## extract only rows where we have immigrant renters
    imm_renters = df[(df['immigrant_status'] == 'Immigrant') & (df['tenure'] == 'Renter')]
    # imm_owners = df[(df['immigrant_status'] == 'Immigrant') & (df['tenure'] == 'Owner')]
    # imm_total = 
    
    total_renters = df[(df['immigrant_status'] == 'Both') & (df['tenure'] == 'Renter')]
    
    merged = imm_renters[['CSD_UID', 'population']].merge(
        total_renters[['CSD_UID', 'population']],
        on='CSD_UID',
        suffixes=('_renters', '_total')
    )
    
    merged['imm_renter_percent'] = merged['population_renters'] / (merged['population_total'])
    return merged
    
    
#what do we wanna show - 

# 1 percent population of immigrants renters in each CSD (specifically where immigrant renters take up > X% of the immigrant population)
# 2 leftover income differences of all people
    # and then perhaps solely for all 4 combinations of immigrants, non-immigrants, renters, owners

# 
# immigrant_status type - Immigrant, Non-immigrant, Both
# tenure_type - Owner, Renter, Both
def get_csd_avg_remaining_income(contest_data_path, pr, immigrant_status_type, tenure_status):
    # income data at CSD level - remove flat grocery cost, match with DAs
    # at DA level, extract percent drivers and percent transiters, remove according to average transit and driving costs
    # visualize this for all peoples, then for immigrants, then for non-immigrants

    df = pd.read_csv(os.path.join(contest_data_path, 'Edited_csd_unpivoted_rich.csv'))
    
    ##filter first two CSD digits to map up to current 
    df = df[df['PRUID'] == PR_TO_ID_MAP[pr]]

    sub_pop = df[(df['immigrant_status'] == immigrant_status_type) & (df['tenure'] == tenure_status)]
    
    # # we need to merge this with total populations
    
    # populations = df
    
    return sub_pop

# def merge_da_csd(csd_data, da_data, )

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
    
    # color = result['  Renter'] / result["Total - Private households by tenure - 25% sample data"]
    # fig, ax = plot_polygons(result, color, title='Percent Apartments', continue_plot=True)
    # simple_plot_polygons(to_plot['geometry'], fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_apartments.png')
    
    contest_data_path='GIS_work\data\Contest Data'
    
    percent_imm_renter = get_csd_immigrant_renters(contest_data_path, pr)
    
    #this is at CSD-level
    percent_imm_renter['condition'] = (percent_imm_renter['imm_renter_percent'] > 0.75)
    # have to extend it to match 
    
    result = result.merge(
        percent_imm_renter[['condition', 'CSD_UID', 'imm_renter_percent']],
        on='CSD_UID',
        how='left'
    )
    
    color = result['  Immigrants'].values / (result['  Non-immigrants'].values + result['  Immigrants'].values)
    fig, ax = plot_polygons(result, color, title='Percent Immigrant Residents (Green is where >75% of renting population are immigrants)', continue_plot=True, alt_color_condition = 'condition')
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_immigrants_with_threshold.png')
    
    color = result['  Immigrants'].values / (result['  Non-immigrants'].values + result['  Immigrants'].values)
    fig, ax = plot_polygons(result, color, title='Percent Immigrant Residents', continue_plot=True)
    simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_immigrants.png')
    
    status_set = ['Immigrant', 'Non-immigrant']
    tenure_type = ['Owner', 'Renter', 'Both']
    
    
    GROCERY_COST = 8_065
    PRIVATE_TRANS = 11_258
    PUBLIC_TRANS = 1_479
    
    #NOTE: cmap and norm need to be arguments
    
    #crazy shit that needs to be moved
######################################################################    
    # fig, axes = plt.subplots(2, 3, figsize=(24, 18), constrained_layout=False)
    
    # for row_idx, immigrant_status_type in enumerate(status_set):
    #     for col_idx, tenure_status in enumerate(tenure_type):
    
    #         # immigrant_status_type = 'Immigrant'
    #         # tenure_status = 'Owner'
    #         sub_pop = get_csd_avg_remaining_income(contest_data_path, pr, immigrant_status_type, tenure_status)
    #         temp_result = result.merge(
    #             sub_pop[['CSD_UID', 'avg_remaining']],
    #             on = 'CSD_UID',
    #             how='left'
    #         )
            
    #         percent_drivers = result['  Car, truck or van'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    #         percent_transit = result['  Public transit'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    #         color = temp_result['avg_remaining'] - GROCERY_COST - percent_drivers * PRIVATE_TRANS - percent_transit * PUBLIC_TRANS
            
    #         axes[row_idx, col_idx].set_xticks([])
    #         axes[row_idx, col_idx].set_yticks([])
            
    #         plot_polygons(temp_result, color, fig=fig, ax=axes[row_idx, col_idx], continue_plot=True, percent_flag=False, c_bar=False, vmin=30_000, vmax=140_000)
    #         simple_plot_polygons(to_plot, fig=fig, ax=axes[row_idx, col_idx], continue_plot=True)
    
    
    # # Shrink the right margin to make room for the colorbar
    # fig.subplots_adjust(
    #     wspace=0.05,
    #     hspace=0.15,
    #     top=0.95,
    #     right=0.88   # leave space on the right for the colorbar
    # )

    # # Manually place the colorbar axes: [left, bottom, width, height]
    # cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
    #     # --- Shared colorbar ---
    # sm = plt.cm.ScalarMappable(
    #     cmap=truncate_cmap(plt.cm.Reds, minval=0.0, maxval=1),
    #     norm=mcolors.Normalize(vmin=30_000, vmax=140_000)
    # )
    # sm.set_array([])

    # cbar = fig.colorbar(sm, cax=cbar_ax, fraction=0.02, pad=0.5, shrink=0.6)
    # cbar.ax.yaxis.set_major_formatter(
    #     plt.FuncFormatter(lambda x, _: f"${x:,.0f}")
    # )
    # cbar.set_label('Leftover Income ($)', fontsize=13)

    # # --- Row labels (immigration status) on the left ---
    # for row_idx, status in enumerate(status_set):
    #     axes[row_idx, 0].set_ylabel(status, fontsize=18, fontweight='bold', labelpad=20)

    # # --- Column labels (tenure) on the top ---
    # for col_idx, tenure in enumerate(tenure_type):
    #     axes[0, col_idx].set_title(tenure, fontsize=18, fontweight='bold', pad=20)

    # # --- Overall title ---
    # fig.suptitle(
    #     f'{pr} — Leftover Income by Immigration Status & Tenure',
    #     fontsize=35, fontweight='bold', y=1.01
    # )
    
    # # fig.subplots_adjust(
    # #     wspace=0.05,   # horizontal space between columns (reduce to pack tighter)
    # #     hspace=0.15,   # vertical space between rows (increase for padding under titles)
    # #     top=0.95       # how close the subplots come to the suptitle
    # # )

    # # --- Save & show ---
    # fig.savefig(
    #     f'GIS_work/graphs/{pr}/{pr}_LI_grid.png',
    #     dpi=150,
    #     bbox_inches='tight'
    # )
    # plt.show()
    
    ##################################################### One more:
    
    # dollar difference in the above (Non-immigrant - immigrant)
    
    fig, axes = plt.subplots(1, 3, figsize=(24, 18), constrained_layout=False)
    row_idx = 0
    vmin=-100_000
    vmax=100_000
    
    percent_drivers = result['  Car, truck or van'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    percent_transit = result['  Public transit'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    
    for col_idx, tenure_status in enumerate(tenure_type):

        # immigrant_status_type = 'Immigrant'
        # tenure_status = 'Owner'
        immigrant_sub_pop = get_csd_avg_remaining_income(contest_data_path, pr, 'Immigrant', tenure_status)
        temp_result = result.merge(
            immigrant_sub_pop[['CSD_UID', 'avg_remaining']],
            on = 'CSD_UID',
            how='left'
        )
        imm_income = temp_result['avg_remaining'] - GROCERY_COST - percent_drivers * PRIVATE_TRANS - percent_transit * PUBLIC_TRANS
        
        
        non_immigrant_sub_pop = get_csd_avg_remaining_income(contest_data_path, pr, 'Non-immigrant', tenure_status)
        second_temp_result = result.merge(
            non_immigrant_sub_pop[['CSD_UID', 'avg_remaining']],
            on = 'CSD_UID',
            how='left'
        )
        
        non_imm_income = second_temp_result['avg_remaining'] - GROCERY_COST - percent_drivers * PRIVATE_TRANS - percent_transit * PUBLIC_TRANS
        
        color = non_imm_income - imm_income
        
        axes[col_idx].set_xticks([])
        axes[col_idx].set_yticks([])
        
        plot_polygons(temp_result, color, fig=fig, ax=axes[col_idx], continue_plot=True, percent_flag=False, c_bar=False, vmin=vmin, vmax=vmax, allow_neg=True)
        simple_plot_polygons(to_plot, fig=fig, ax=axes[col_idx], continue_plot=True)
    
    
    # Shrink the right margin to make room for the colorbar
    fig.subplots_adjust(
        wspace=0.05,
        hspace=0.15,
        top=0.95,
        right=0.88   # leave space on the right for the colorbar
    )

    # Manually place the colorbar axes: [left, bottom, width, height]
    cbar_ax = fig.add_axes([0.90, 0.15, 0.02, 0.7])
        # --- Shared colorbar ---
    norm = mcolors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

    sm = plt.cm.ScalarMappable(
        cmap=plt.cm.RdBu,   # red=negative, white=zero, blue=positive
        norm=norm
    )
    sm.set_array([])

    cbar = fig.colorbar(sm, cax=cbar_ax, fraction=0.02, pad=0.5, shrink=0.6)
    cbar.ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${x:,.0f}")
    )
    cbar.set_label('Leftover Income ($)', fontsize=13)

    # # --- Row labels (immigration status) on the left ---
    # for row_idx, status in enumerate(status_set):
    #     axes[row_idx, 0].set_ylabel(status, fontsize=18, fontweight='bold', labelpad=20)

    # --- Column labels (tenure) on the top ---
    for col_idx, tenure in enumerate(tenure_type):
        axes[col_idx].set_title(tenure, fontsize=18, fontweight='bold', pad=20)

    # --- Overall title ---
    fig.suptitle(
        f'{pr} — Difference in Leftover Income across Tenure status (Non-immigrant - Immigrant)',
        fontsize=35, fontweight='bold', y=1.01
    )
    
    # fig.subplots_adjust(
    #     wspace=0.05,   # horizontal space between columns (reduce to pack tighter)
    #     hspace=0.15,   # vertical space between rows (increase for padding under titles)
    #     top=0.95       # how close the subplots come to the suptitle
    # )

    # --- Save & show ---
    fig.savefig(
        f'GIS_work/graphs/{pr}/{pr}_LI_difference_grid.png',
        dpi=150,
        bbox_inches='tight'
    )
    
    ######################################################
    
    # Singular implementation:
    
#     status_set = ['Immigrant', 'Non-immigrant', 'Both']
    # tenure_type = ['Renter', 'Owner', 'Both']
    
    
    # GROCERY_COST = 8_065
    # PRIVATE_TRANS = 11_258
    # PUBLIC_TRANS = 1_479
    
    # for immigrant_status_type, tenure_status in itertools.product(status_set, tenure_type):
    
    #     # immigrant_status_type = 'Immigrant'
    #     # tenure_status = 'Owner'
    #     sub_pop = get_csd_avg_remaining_income(contest_data_path, pr, immigrant_status_type, tenure_status)
    #     temp_result = result.merge(
    #         sub_pop[['CSD_UID', 'avg_remaining']],
    #         on = 'CSD_UID',
    #         how='left'
    #     )
        
    #     percent_drivers = result['  Car, truck or van'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    #     percent_transit = result['  Public transit'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
        
    #     color = temp_result['avg_remaining'] - GROCERY_COST - percent_drivers * PRIVATE_TRANS - percent_transit * PUBLIC_TRANS
    #     fig, ax = plot_polygons(temp_result, color, title=f'Leftover Income of {immigrant_status_type} {tenure_status}', continue_plot=True, percent_flag=False, vmin=30_000, vmax=140_000)
    #     simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_LI_{immigrant_status_type}_{tenure_status}.png')


    ######################################################
    
    #would be good to set a fixed max for the grids in each of these


    # color = result['Private dwellings occupied by usual residents'] / result['Total private dwellings']
    # fig, ax = plot_polygons(result, color, title='Percent Dwellings Occupied', continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_occupied.png')
    
    # #NOTE: this one should not show up as a percent
    # color = result['  Median monthly shelter costs for owned dwellings ($)']
    # fig, ax = plot_polygons(result, color, title='Median monthly shelter costs', continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_median_shelter_costs.png')
    
    # color = result['  Major repairs needed'] / (result['  Only regular maintenance and minor repairs needed'] + result['  Major repairs needed'])
    # fig, ax = plot_polygons(result, color, title='Percent Dwellings in Need of Major Repairs', continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_repair.png')
    
    # #UNEMPLOYMENT

    # color = result['Unemployment rate'] / 100
    # fig, ax = plot_polygons(result, color, title='Unemployment Rate', continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_unemployment.png')
    # #COMMUTE - NOTE: all these totals are different - :TODO - switch to using indices instead

    # total_commute_dest = result['Total - Commuting destination for the employed labour force aged 15 years and over with a usual place of work - 25% sample data']
    # commute_out_of_csd = result['  Commute to a different census subdivision (CSD) within census division (CD) of residence'] \
    #                     + result['  Commute to a different census subdivision (CSD) and census division (CD) within province or territory of residence']
                        
    # color = commute_out_of_csd / total_commute_dest
    # fig, ax = plot_polygons(result, color, title='Percent Commute out of CSD', continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_percent_commute_out_of_csd.png')
    
    # color =  (result['Total - Place of work status for the employed labour force aged 15 years and over - 25% sample data'] - result['  Worked at home']) / result['Total - Place of work status for the employed labour force aged 15 years and over - 25% sample data']
    # fig, ax = plot_polygons(result, color, title='Percent of Employed who Commute', continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_commuters.png')
    
    # color = result['  Car, truck or van'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    # fig, ax = plot_polygons(result, color, title='Percent of Commuters who Drive',continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_drivers.png')
    
    # color = result['  Public transit'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    # fig, ax = plot_polygons(result, color, title='Percent of Commuters who take Public Transit', continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_transiters.png')
    
    # color = (result['  60 minutes and over']) / result['Total - Commuting duration for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    # fig, ax = plot_polygons(result, color, title='Percent of Commuters who commute > 60 minutes', continue_plot=True)
    # simple_plot_polygons(to_plot, fig=fig, ax=ax, save_filepath=f'GIS_work\graphs\\{pr}\\{pr}_commute_times.png')
#TODO: check if I'm pre-pruning rows based on a single NaN (I think I am)
#tomorrow - overlay CSD data (with lines) over this - have a series of plot functions that pass around
# figs and axes to continuously overlay stuff

if __name__ == '__main__':
    
    plot_da_data('Ontario')
    # for pr in ['BritishColumbia', 'Quebec', 'Ontario', 'Alberta']:
    #     plot_da_data(pr)