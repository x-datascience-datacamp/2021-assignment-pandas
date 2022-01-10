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
import numpy as np


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    res = pd.merge(regions, departments, left_on='code',
                   right_on='region_code')
    res = res[['code_x', 'name_x', 'code_y', 'name_y']]
    res = res.rename(columns={'code_x': 'code_reg', 'name_x': 'name_reg',
                              'code_y': 'code_dep', 'name_y': 'name_dep'})

    return res


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    deps = np.arange(0, 96).astype(str)
    deps = np.append(deps, ['2A', '2B'])
    k = regions_and_departments['code_dep'].apply(lambda x: x.lstrip('0'))
    regions_and_departments['code_dep'] = k

    selected_refs = referendum[referendum['Department code'].isin(deps)]
    r = pd.merge(selected_refs, regions_and_departments,
                 left_on='Department code', right_on='code_dep', how='left')
    return r


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result = referendum_and_areas.copy()
    result = result[['Registered', 'Abstentions', 'Null',
                     'Choice A', 'Choice B', 'name_reg', 'code_reg']]
    result = result.groupby(['code_reg', 'name_reg'], as_index=False).sum()
    result = result.set_index('code_reg')
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodf = gpd.read_file('data/regions.geojson')
    resmap = pd.merge(geodf, referendum_result_by_regions,
                      left_on='code', right_on='code_reg', how='left')
    resmap['ratio'] = resmap['Choice A'] / \
        (resmap['Registered'] - resmap['Abstentions'] - resmap['Null'])
    resmap.plot('ratio')
    return resmap


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
