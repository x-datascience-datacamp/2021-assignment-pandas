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
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    res1 = pd.merge(
        regions, departments, left_on='code', how='left',
        right_on='region_code', suffixes=('_reg', '_dep')
        )[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return (res1)


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    dd_cleaned = regions_and_departments.loc[(regions_and_departments['code_reg'] != 'COM') 
        & (regions_and_departments['name_dep'] != "FRANCAIS DE L'ETRANGER")]
    dd_cleaned["code_dep"] = dd_cleaned["code_dep"].apply(lambda x: x.zfill(3))
    referendum["Department code"] = referendum["Department code"].apply(
        lambda x: x.zfill(3))
    res2 = pd.merge(dd_cleaned, referendum, left_on='code_dep', how="left",
         right_on='Department code')
    res2.dropna(inplace=True)
    res2.reset_index(drop=True, inplace=True)
    return pd.DataFrame(res2)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    res3 = referendum_and_areas.groupby(['code_reg', 'name_reg']).sum().reset_index().set_index('code_reg')[['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]

    return pd.DataFrame(res3)


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file('C:/assignment/pandas/2021-assignment-pandas/data/departements.geojson')
    df = pd.merge(geo_df, referendum_result_by_regions, left_on='code', right_on='code_reg')
    df['ratio'] = df['Choice A'] / (df['Choice A'] + df['Choice B'])
    df.plot("ratio")
    plt.show()
    return gpd.GeoDataFrame(df)


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
    
