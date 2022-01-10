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
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.set_index('id')
    departments = departments.set_index('id')
    left = regions.drop(columns=['slug'])
    right = departments.drop(columns=['slug'])
    merged = pd.merge(left, right, left_on='code',
                      right_on='region_code', suffixes=('_reg', '_dep'))
    merged.drop(columns=['region_code'], inplace=True)
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    to_drop_left = ['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN',
                    'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']
    left = referendum[~referendum['Department code'].isin(to_drop_left)].copy()

    def format_dep_num(x):
        if len(x) == 1:
            return '0' + x
        else:
            return x
    # Function defined to avoid next line exceeding 80 characters
    # And lambda functions are not recommanded
    replace_col = left.loc[:, 'Department code'].apply(format_dep_num)
    left.loc[:, 'Department code'] = replace_col
    to_drop_right = ['01', '02', '03', '04', '05', '06', 'COM']
    right = regions_and_departments.copy()
    # Copy created to avoid next line exceeding 80 characters
    right = right[~right['code_reg'].isin(to_drop_right)]
    merged = pd.merge(left, right,
                      left_on='Department code', right_on='code_dep')
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    to_keep = ['code_reg', 'name_reg',
               'Registered', 'Abstentions',
               'Null', 'Choice A', 'Choice B']
    count = referendum_and_areas[to_keep]
    count = count.groupby(by=['code_reg', 'name_reg']).sum()
    count = count.reset_index()
    count = count.set_index('code_reg')
    return count


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    df = gpd.read_file('data/regions.geojson')
    output = pd.merge(referendum_result_by_regions, df,
                      left_on='name_reg', right_on='nom')
    output.index = referendum_result_by_regions.index
    output['ratio'] = output['Choice A'] / (output['Registered'] -
                                            output['Abstentions'] -
                                            output['Null'])
    output = gpd.GeoDataFrame(output, geometry='geometry')
    title = 'Percentage of votes expressed for' +\
            'A in every metroplitan region in France'
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    output.plot(column='ratio', ax=ax, legend=True)
    ax.set_title(title)
    return output


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
