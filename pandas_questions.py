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
import os


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.read_csv(os.path.join("data", "referendum.csv"), sep=";")
    regions = pd.read_csv(os.path.join("data", "regions.csv"))
    departments = pd.read_csv(os.path.join("data", "departments.csv"))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    return pd.merge(
        regions[["code", "name"]].rename(columns=({"code": "code_reg"})),
        departments[["region_code", "code", "name"]].rename(
            columns=({"region_code": "code_reg", "code": "code_dep"})
        ),
        on="code_reg",
        how="right",
        suffixes=("_reg", "_dep"),
    )


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum_ = referendum.loc[
        ~referendum["Department code"].str.startswith("Z"), :
    ].copy() # drop domtom and French living abroad
    # adapt dep numbers to oher table
    referendum_["code_dep"] = referendum_["Department code"].apply(
        lambda x: "0" + x if len(x) == 1 else x
    )
    # merge
    merged = pd.merge(referendum_,
                      regions_and_departments,
                      on="code_dep",
                      how="left")
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    return referendum_and_areas.groupby("code_reg").agg(
        {
            "name_reg": "first",
            "Registered": "sum",
            "Abstentions": "sum",
            "Null": "sum",
            "Choice A": "sum",
            "Choice B": "sum",
        }
    )


def plot_referendum_map(referendum_results):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    print(referendum_results)
    referendum_results["expressed"] = (
        referendum_results["Registered"]
        - referendum_results["Abstentions"]
        - referendum_results["Null"]
    )
    referendum_results["ratio"] = (
        referendum_results["Choice A"] / referendum_results["expressed"]
    )

    gdf = gpd.read_file(os.path.join("data", "regions.geojson"))
    gdfm = gdf.rename(columns={"code": "code_reg"}).merge(
        referendum_results[["ratio", 'name_reg']], on="code_reg"
    )
    gdfm.plot(column="ratio", legend=True)
    return gdfm


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
