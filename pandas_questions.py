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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions_and_departments = pd.merge(regions,
                                       departments,
                                       how='inner',
                                       left_on='code', right_on='region_code',
                                       suffixes=('_reg', '_dep'))[['code_reg',
                                                                   'name_reg',
                                                                   'code_dep',
                                                                   'name_dep']]
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    def normalize(code):
        if len(code) == 1:
            return '0' + code
        else:
            return code
    # To have the same code size between both DF
    referendum['Department code'] = referendum['Department code']\
        .apply(normalize)
    Delete_Dep = ['ZA', 'ZB',
                  'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']
    referendum = referendum[~referendum['Department code'].isin(Delete_Dep)]
    Final = pd.merge(left=referendum, right=regions_and_departments,
                     left_on='Department code', right_on='code_dep')

    return Final


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    a = referendum_and_areas.groupby(by=['code_reg', 'name_reg']).sum()
    a = a.reset_index(level='name_reg')[['name_reg',
                                         'Registered', 'Abstentions',
                                         'Null', 'Choice A', 'Choice B']]
    return a


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    region_geojson = gpd.read_file("./data/regions.geojson")
    referendum_map = pd.merge(left=referendum_result_by_regions,
                              right=region_geojson,
                              left_on='code_reg', right_on='code')
    referendum_map.drop(columns=['nom'], inplace=True)
    referendum_map['ratio'] = (referendum_map['Choice A'])/(
        referendum_map['Choice A'] + referendum_map['Choice B'])

    referendum_map = gpd.GeoDataFrame(referendum_map, geometry='geometry')

    return referendum_map


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
