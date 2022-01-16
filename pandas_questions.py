"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
from pandas.io.parsers import read_csv
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = read_csv('data/referendum.csv', sep=';')
    regions = read_csv('data/regions.csv', sep=',')
    departments = read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    import copy as cp
    R = cp.deepcopy(regions[['code', 'name']])
    D = cp.deepcopy(departments[['code', 'name', 'region_code']])
    merged_df = R.merge(D, left_on='code', right_on='region_code', suffixes=('_reg', '_dep'))
    del merged_df['region_code']
    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    import copy as cp
    RF = cp.deepcopy(referendum)
    deps_to_delete = ['ZZ', 'ZX', 'ZW', 'ZS', 'ZP', 'ZN']
    for elm in deps_to_delete:
        ind = np.where(RF['Department code'] == elm)[0]
        RF = RF.drop(ind)
    # Solve the problem of Department code of Mayotte, Reunion, Guadeloupe, Guyanne and Martinique
    problem = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM']
    solution = ['971', '972', '973', '974', '976']
    for i, elm in enumerate(problem):
        RF['Department code'] = RF['Department code'].replace([elm], solution[i])
    merged_df = RF.merge(regions_and_departments, right_on='code_dep', left_on='Department code')
    # We remove these two columns because they are duplicated in name_dep and code_dep
    merged_df.drop(columns=['Department code', 'Department name'])
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    import copy as cp
    to_return = cp.deepcopy(referendum_and_areas)
    to_be_removed = ['name_dep', 'Town name', 'code_dep', 'Town code']
    to_return = to_return.drop(columns=to_be_removed)
    to_return = to_return.set_index('code_reg')
    to_return = to_return.groupby('code_reg').sum()
    return to_return


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file("data/regions.geojson")
    regions_geo_results = regions_geo.merge(referendum_result_by_regions, right_on='code_reg', left_on='code')
    regions_geo_results['ratio'] = regions_geo_results['Choice A'] / (regions_geo_results['Choice A'] + regions_geo_results['Choice B'])
    regions_geo_results.plot('ratio', legend=True)
    return regions_geo_results


if __name__ == "__main__":

    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(
        df_reg, df_dep
    )
    referendum_and_areas = merge_referendum_and_areas(
        referendum, regions_and_departments
    )
    referendum_results = compute_referendum_result_by_regions(
        referendum_and_areas
    )
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()