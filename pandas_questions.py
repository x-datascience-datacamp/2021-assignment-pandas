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
    reg_df = pd.DataFrame({'code_reg': regions['code'],
                           'name_reg': regions['name']})

    depart_df = pd.DataFrame({'code_dep': departments['code'],
                              'name_dep': departments['name'],
                              'code_reg': departments['region_code']
                              })
    return pd.merge(reg_df, depart_df, on='code_reg', how='left')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    mask = regions_and_departments['code_dep'].str.len() < 3
    regs_and_departs_df = regions_and_departments[mask]
    regs_and_departs_df.loc[:, 'code_dep'] = \
        regs_and_departs_df.loc[:, 'code_dep'].str.lstrip('0')

    refs_df = referendum[~referendum['Department code']
                         .str.startswith('Z')]
    refs_df.rename(columns={'Department code': 'code_dep'})

    refs_df.loc[:, 'code_dep'] = refs_df['Department code']

    return pd.merge(refs_df, regs_and_departs_df, on='code_dep', how='left')


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    name_cols = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
                 'Null', 'Choice A', 'Choice B']
    refs_and_areas_df = referendum_and_areas.loc[:, name_cols]
    refs_and_areas_df = refs_and_areas_df.groupby(
        ['name_reg', 'code_reg']).sum()
    refs_and_areas_df = refs_and_areas_df.reset_index('name_reg')

    return refs_and_areas_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.
    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geog_df = gpd.read_file('./data/regions.geojson')
    referendum_result_by_regions =\
        referendum_result_by_regions.rename(columns={
            'name_reg': 'nom'})
    geog_and_refs = pd.merge(referendum_result_by_regions, geog_df,
                             how='left')
    gpd.GeoDataFrame(geog_and_refs).plot(column='Choice A')

    ratio_df = gpd.GeoDataFrame()
    ratio_df['name_reg'] = geog_and_refs['nom']
    ratio_df['ratio'] = geog_and_refs['Choice A'] / \
        (geog_and_refs['Choice A'] + geog_and_refs['Choice B'])
    ratio_df['Choice_B_ratio'] = geog_and_refs['Choice B'] / \
        (geog_and_refs['Choice A'] + geog_and_refs['Choice B'])

    return ratio_df


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
