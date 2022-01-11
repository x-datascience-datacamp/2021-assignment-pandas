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
    referendum = pd.read_csv("./data/referendum.csv", sep=";")
    regions = pd.read_csv("./data/regions.csv")
    departments = pd.read_csv("./data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    columns = ['code_reg',
               'name_reg',
               'code_dep',
               'name_dep']
    merge_regions_and_departments = departments.merge(regions,
                                                      how="left",
                                                      left_on=["region_code"],
                                                      right_on=["code"],
                                                      suffixes=["_dep", "_reg"])
    return merge_regions_and_departments[columns]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    abroad = ["DOM", "TOM", "COM"]
    r_d_cdep = regions_and_departments["code_dep"]
    referendum["Department code"] = pd.Series(referendum["Department code"],
                                              dtype="string").str.zfill(2)
    filter_abroad_regions = ~regions_and_departments["code_reg"].isin(abroad)
    regions_and_departments = regions_and_departments[filter_abroad_regions]
    r_d_cdep = pd.Series(r_d_cdep, dtype="string")
    merge_referendum_and_areas = referendum.merge(regions_and_departments,
                                                  how="left",
                                                  left_on=["Department code"],
                                                  right_on=['code_dep'])
    merge_referendum_and_areas = merge_referendum_and_areas.dropna()

    return merge_referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    columns = ['name_reg',
               'Registered',
               'Abstentions',
               'Null',
               'Choice A',
               'Choice B']
    cols = columns + ["code_reg"]
    gby = ["code_reg", "name_reg"]
    referendum_result_by_regions = referendum_and_areas[cols].groupby(gby).sum()
    referendum_result_by_regions = referendum_result_by_regions.reset_index()

    return referendum_result_by_regions[columns]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geographic_regions = gpd.read_file('./data/regions.geojson')
    referendum_map = referendum_result_by_regions.merge(geographic_regions,
                                                        how="left",
                                                        left_on=["name_reg"],
                                                        right_on=['nom']
                                                        )
    A = referendum_map['Choice A'].astype(int)
    B = referendum_map["Choice B"].astype(int)
    tot_ref = A + B
    referendum_map["ratio"] = referendum_map["Choice A"].astype(int) / tot_ref
    referendum_map_geodataframe = gpd.GeoDataFrame(referendum_map)
    referendum_map_geodataframe.plot("ratio")

    return referendum_map_geodataframe


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
