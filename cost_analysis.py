import geopandas as gpd
import pandas as pd
from pathlib import Path
import os
import itertools

from process_geometry.fetch_geometry import and_over_or
from util.constants import PR_TO_ID_MAP
from process_geometry.fetch_geometry import reformat_crs

from plotting.plotting_overpass_features import truncate_cmap


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

def analysis(pr):
    
    da_geometry = gpd.read_file(f'GIS_work\data\DA Data\{pr}\{pr}_DA_per_CSD.shp')
    da_census_info = pd.read_csv(f'GIS_work\data\DA Data\{pr}\{pr}_DA_pivoted.csv')
    result = da_geometry.merge(
        da_census_info,
        right_on='ALT_GEO_CODE',
        left_on='DAUID',
        how='left'
    )
    
    GROCERY_COST = 8_065
    PRIVATE_TRANS = 16_476 #according to bloomberg
    PUBLIC_TRANS = 1_479
    
    #avg commute cost inside and outside of Toronto proper
    # immigrant_sub_pop = get_csd_avg_remaining_income(contest_data_path, pr, 'Both', 'Both')
    
    #what is CSDUID for Toronto proper? - 3520005
    
    
    #so, per unique CSD_UID (that is not Toronto), for each DA we look at percent 
    result['percent_drivers'] = result['  Car, truck or van'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    result['percent_transiters'] = result['  Public transit'] / result['Total - Main mode of commuting for the employed labour force aged 15 years and over with a usual place of work or no fixed workplace address - 25% sample data']
    result['percent_commuters'] = (result['Total - Place of work status for the employed labour force aged 15 years and over - 25% sample data'] - result['  Worked at home']) / result['Total - Place of work status for the employed labour force aged 15 years and over - 25% sample data']
    
    # we want to normalize by the commuting population so:
    
    result['commuting_population'] = result['percent_commuters'] * result["Population, 2021"]
    result['driving_population'] = result['percent_drivers'] * result['commuting_population']
    result['transit_population'] = result['percent_transiters'] * result['commuting_population']
    
    # so, each DA contributes 
    result['total_private_vehicle_costs'] = result['driving_population'] * PRIVATE_TRANS
    result['total_transit_costs'] = result['transit_population'] * PUBLIC_TRANS
    result['total_exp_travel_costs'] = result['total_private_vehicle_costs'] + result['total_transit_costs']
    
    csd_ids = result['CSD_UID'].unique()
    
    assert 3520005 in csd_ids
    
    # so we're asking - out of this total costs, what percentage are drivers, what percent are transiters, and how much do each of them spend in each scenario
    pops = ["commuting_population", 'commuting_population', 'commuting_population']
    costs = ["total_exp_travel_costs", 'total_private_vehicle_costs', 'total_transit_costs']
    other_pops = ['commuting_population', 'driving_population', 'transit_population']
    
    for i in range(len(pops)):
    
        population_type = pops[i]
        cost_type = costs[i]
        
        print('---------------')
    
        compare_transiters(csd_ids, result, cost_type, population_type)
        
        print('--------------')
        print(f'Percents: {other_pops[i]}')
        compare_transiters(csd_ids, result, other_pops[i] , pops[i])
    
def compare_transiters(ids, df, cost_type, population_type):
    csd_ids = ids[ids != 3520005]
    
    mask1 = df[cost_type].isna()
    mask2 = df[population_type].isna()
    
    result = df[(~mask1) & (~mask2)]
    
    aggregate_pop = 0
    inc_exp = 0
    for csd in csd_ids:
        slice = result[result['CSD_UID'] == csd]
        aggregate_pop += slice[population_type].sum()
        inc_exp += slice[cost_type].sum()
                
    print(f'The {cost_type} for {population_type} in Ontarian CSDs outside of Toronto is {inc_exp / aggregate_pop}')
    
    toronto_slice = result[result['CSD_UID'] == 3520005]
    toronto_agg_pop = toronto_slice[population_type].sum()
    toronto_exp = toronto_slice[cost_type].sum()
            
    print(f'The {cost_type} for {population_type}  inside of Toronto proper is {toronto_exp / toronto_agg_pop}')
    
    return inc_exp / aggregate_pop, toronto_exp / toronto_agg_pop
    
if __name__ == '__main__':
    analysis('Ontario')
    
    
#we can even heavily isolate particular 'downtown core DAs', if we wanted (as Scarborough, for example)
#would show very different transiter trends