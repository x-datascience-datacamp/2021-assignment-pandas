import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    regs = regions.rename(columns={"code": "code_reg", "name": "name_reg"})
    deps = departments.rename(
        columns={"region_code": "code_reg", "name": "name_dep",
                 "code": "code_dep"})
    deps['code_dep'] = deps['code_dep'].str.lstrip("0")
    df_res = pd.merge(regs, deps, on='code_reg', how='left')
    return df_res[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """
    Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    wanted_zones = np.arange(1, 96).astype(str)
    wanted_zones = np.append(wanted_zones, ['2A', '2B'])

    refs = referendum[referendum["Department code"].isin(wanted_zones)]
    df_res = pd.merge(refs, regions_and_departments, how='left',
                      left_on='Department code', right_on='code_dep')
    return df_res


def compute_referendum_result_by_regions(referendum_and_areas):
    """
    Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    result = referendum_and_areas[['code_reg', 'name_reg', 'Registered',
                                   'Abstentions', 'Null', 'Choice A',
                                   'Choice B']]
    result = result.groupby(['code_reg', 'name_reg'], as_index=False).sum()
    return result.set_index(['code_reg'])


def plot_referendum_map(referendum_result_by_regions):
    """
    Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    regions_geo = gpd.read_file('data/regions.geojson')
    result = pd.merge(regions_geo, referendum_result_by_regions,
                      left_on='code', right_on='code_reg', how='left')
    result['ratio'] = result['Choice A'] / \
        (result['Registered'] - result['Abstentions'] - result['Null'])
    result.plot('ratio')
    return result


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
