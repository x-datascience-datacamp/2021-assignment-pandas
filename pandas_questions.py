"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv('./data/referendum.csv', sep=';')
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merge_regions_departments = pd.merge(regions, departments,
                                         left_on='code',
                                         right_on='region_code')
    # merge_regions_departments = merge_regions_departments
    # [['code_x','name_x','code_y','name_y']].columns
    # (['code_reg', 'name_reg', 'code_dep', 'name_dep'])
    merge_regions_departments = merge_regions_departments[['code_x', 'name_x',
                                                           'code_y', 'name_y']]
    merge_regions_departments.columns = ['code_reg', 'name_reg',
                                         'code_dep', 'name_dep']
    return merge_regions_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    merge_referendum_areas = pd.merge(referendum, regions_and_departments,
                                      left_on='Department code',
                                      right_on='code_dep')
    # merge_referendum_areas = merge_referendum_areas
    # [merge_referendum_areas['Department code']>=10]
    return merge_referendum_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    set_columns = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
                   'Null', 'Choice A', 'Choice B']
    referendum_and_areas = referendum_and_areas[set_columns]
    referendum_result_by_regions = referendum_and_areas.groupby(['code_reg',
                                                                 'name_reg'])\
                                                       .sum()
    referendum_result_by_regions.reset_index(inplace=True)
    referendum_result_by_regions.set_index('code_reg', inplace=True)
    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geo = gpd.read_file('./data/regions.geojson')
    # department_geo = gpd.read_file('./data/departements.geojson')
    referendum_copy = referendum_result_by_regions.copy()
    show_up_vote = (referendum_copy['Registered']
                    - referendum_copy['Abstentions']
                    - referendum_copy['Null'])
    referendum_copy['ratio'] = referendum_copy['Choice A'] / show_up_vote
    geo_referendum_result_by_regions = pd.merge(regions_geo,
                                                referendum_copy,
                                                left_on='code',
                                                right_index=True)
    # geo_referendum_result_by_regions.plot('ratio', cmap='Blues')
    return geo_referendum_result_by_regions


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
