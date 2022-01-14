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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.rename(columns={"code": "region_code"}, inplace=True)
    merged = pd.merge(regions, departments, on='region_code', how='left')
    # keys = new names, values = old ones
    rename_cols = {"code_reg": "region_code",
                   "name_reg": "name_x",
                   "code_dep": "code",
                   "name_dep": "name_y"}
    merged = merged[rename_cols.values()]
    for new_name, old_name in rename_cols.items():
        merged.rename(columns={old_name: new_name}, inplace=True)
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    def adapt_nb(s):
        if s in [str(i) for i in range(1, 10)]:
            return "0{}".format(s)
        return s
    department_codes = referendum["Department code"]
    referendum["Department code"] = department_codes.apply(adapt_nb)
    referendum["code_dep"] = referendum["Department code"]
    merged = pd.merge(referendum, regions_and_departments,
                      on='code_dep', how='inner')
    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols_to_keep = ['Registered', 'Abstentions',
                    'Null', 'Choice A', 'Choice B', 'code_reg']
    referendum_and_areas = referendum_and_areas[cols_to_keep]
    df_compute = referendum_and_areas.groupby("code_reg").sum()
    regions = pd.read_csv("data/regions.csv")
    code_regions = regions["code"].isin(list(df_compute.index))
    df_compute["name_reg"] = list(regions[code_regions]["name"])
    return df_compute


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_geojson = gpd.read_file("data/regions.geojson")
    regions_geojson.rename(columns={"nom": "name_reg"}, inplace=True)
    merged = pd.merge(regions_geojson,
                      referendum_result_by_regions,
                      on="name_reg",
                      how="inner")
    totals = merged["Choice A"] + merged["Choice B"]
    merged["ratio"] = merged["Choice A"] / totals
    # uncomment the 2 lines below to plot the map
    # merged.plot(column="ratio", cmap='OrRd', legend=True)
    # plt.show()
    return merged


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
