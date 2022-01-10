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
    """
    Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    d = departments.merge(regions,
                          how="left",
                          left_on=["region_code"],
                          right_on=["code"],
                          suffixes=["_dep", "_reg"])

    return d[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    #  to_drop = ["COM", "TOM"]
    #  r_d = regions_and_departments.query("code_reg not in @to_drop")

    to_drop = ~regions_and_departments["code_reg"].\
        isin(["COM", "TOM", "DOM"])
    r_d = regions_and_departments[to_drop]

    r_d["code_dep"] = pd.Series(r_d["code_dep"],
                                dtype="string")
    referendum["Department code"] = pd.Series(referendum["Department code"],
                                              dtype="string")
    referendum["Department code"] = referendum["Department code"].str.zfill(2)

    d = referendum.merge(r_d,
                         how="left",
                         left_on=["Department code"],
                         right_on=['code_dep']
                         )

    return d.dropna()


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    cols = ['name_reg', 'Registered',
            'Abstentions', 'Null',
            'Choice A', 'Choice B']
    d = referendum_and_areas[
        cols + ["code_reg"]].groupby(["name_reg", "code_reg"]).sum()

    d = d.reset_index()

    return d[cols]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_region = gpd.read_file('./data/regions.geojson')
    print(geo_region.columns)
    geo_region["nom"] = geo_region["nom"].str.title()

    referendum_result_by_regions["name_reg"] = \
        referendum_result_by_regions["name_reg"]\
        .str.title()

    d = referendum_result_by_regions.merge(geo_region,
                                           how="left",
                                           left_on=["name_reg"],
                                           right_on=['nom']
                                           )

    d["ratio"] = d["Choice A"].astype(int) / (
            d["Choice A"].astype(int) +
            d['Choice B'].astype(int)
    )
    d = gpd.GeoDataFrame(d)
    d.plot("ratio", legend=True)

    return d


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

    h = plot_referendum_map(referendum_results)
    plt.show()
