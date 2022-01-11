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

from os.path import dirname, join
current_dir = dirname(__file__)


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    ref_file = join(current_dir, "data/referendum.csv")
    reg_file = join(current_dir, "data/regions.csv")
    dep_file = join(current_dir, "data/departments.csv")
    referendum = pd.read_csv(ref_file, sep=';').dropna()
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    regions = pd.read_csv(reg_file, sep=',').dropna()
    departments = pd.read_csv(dep_file, sep=',').dropna()
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    tmp = pd.merge(
        regions, departments, left_on="code",
        right_on='region_code', suffixes=('_reg', '_dep'))
    tmp = tmp[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    tmp = tmp.dropna()
    return tmp


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    tmp = pd.merge(
        regions_and_departments, referendum,
        right_on="Department code", left_on='code_dep')
    return tmp


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    tmp = referendum_and_areas.groupby(
        ['name_reg', 'code_reg'], as_index=False).sum()
    tmp = tmp.set_index('code_reg')
    tmp = tmp.drop('Town code', axis=1)
    return tmp


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    file_ = join(current_dir, "data/regions.geojson")

    map_ = gpd.read_file(file_)
    tmp2 = pd.merge(referendum_result_by_regions, map_,
                    left_on='code_reg',
                    right_on='code')

    tmp2 = gpd.GeoDataFrame(tmp2)

    tmp2['ratio'] = (tmp2['Choice A'])/(tmp2['Choice A']+tmp2['Choice B'])
    print(tmp2)
    tmp2.plot(column='ratio', legend=True)
    tmp2.filter(['ratio', 'geometry'])
    return tmp2


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
