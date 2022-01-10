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
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv", sep=',')
    departments = pd.read_csv("data/departments.csv", sep=',')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.
    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    columns = {'code': 'code_dep',
               'name': 'name_dep',
               'region_code': 'code_reg'}
    departments = departments.rename(columns=columns)
    regions_df = regions[['code_reg', 'name_reg']]
    dep_df = departments[['code_reg', 'code_dep', 'name_dep']]
    merged_df = regions_df.merge(dep_df, on='code_reg')

    return merged_df


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # print(referendum.shape)
    # print(referendum[~referendum['Department code'].
    # isin(['ZA', 'ZB', 'ZC', 'ZD', 'ZM', 'ZN', 'ZP', 'ZZ'])].shape)
    cond = referendum['Department code'].str.len() == 1
    col = 'Department code'
    value = '0' + referendum['Department code']
    referendum.loc[cond, col] = value
    l_df = referendum
    r_df = regions_and_departments
    merged_df = l_df.merge(r_df, right_on='code_dep', left_on=col)
    return merged_df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    cols = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
            'Null', 'Choice A', 'Choice B']
    df = referendum_and_areas[cols]
    df = df.groupby(['code_reg', 'name_reg']).sum()
    df = df.reset_index()
    df = df.set_index('code_reg')
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_df = gpd.read_file('data/regions.geojson')
    merged_df = pd.merge(referendum_result_by_regions, geo_df,
                         left_on='name_reg', right_on='nom')
    merged_df.index = referendum_result_by_regions.index
    denom = (merged_df['Choice A'] + merged_df['Choice B'])
    merged_df['ratio'] = merged_df['Choice A'] / denom
    res = gpd.GeoDataFrame(merged_df, geometry='geometry')
    res.plot(column='ratio', legend=True)
    return res


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
