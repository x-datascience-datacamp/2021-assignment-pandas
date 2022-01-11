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
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    reg = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    dep = departments.rename(columns={'code': 'code_dep', 'name': 'name_dep',
                                      'region_code': 'code_reg'})
    return pd.merge(dep[['code_dep', 'name_dep', 'code_reg']],
                    reg[['code_reg', 'name_reg']], on='code_reg', how='left')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    def code_dep_normalization(code_dep):
        if code_dep.startswith('0'):
            return code_dep[1:]
        else:
            return code_dep
    regions_and_departments["code_dep"] = regions_and_departments["code_dep"]\
        .apply(code_dep_normalization)
    return pd.merge(referendum, regions_and_departments,
                    left_on='Department code', right_on='code_dep',
                    how='left').dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    temp = referendum_and_areas[['name_reg', 'Registered', 'Abstentions',
                                 'Null', 'Choice A',
                                 'Choice B']].groupby('name_reg').sum()

    return temp.reset_index()


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_regions = gpd.read_file('data/regions.geojson')\
        .rename(columns={'nom': 'name_reg'})
    temp = pd.merge(referendum_result_by_regions, geo_regions,
                    on='name_reg', how='left')
    temp['ratio'] = \
        temp['Choice A']/(temp['Registered']-temp['Abstentions']-temp['Null'])
    temp = gpd.GeoDataFrame(temp)
    return temp


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
