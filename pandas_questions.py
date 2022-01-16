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
    referendum = pd.DataFrame(pd.read_csv("data/referendum.csv", sep=';'))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv"))

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    departments1 = departments.rename(columns={'name': 'name_dep',
                                               'code': 'code_dep',
                                               'region_code': 'code_reg'})
    regions1 = regions.rename(columns={'name': 'name_reg', 'code': 'code_reg'})
    merged = pd.merge(regions1[['code_reg', 'name_reg']],
                      departments1[['code_reg', 'code_dep', 'name_dep']],
                      on='code_reg', how='left')
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    Rg = regions_and_departments
    Rg1 = Rg.drop(Rg.loc[(Rg['code_reg'] == 'TOM') |
                         (Rg['code_reg'] == 'COM') |
                         (Rg['code_reg'] == 'DOM')].index)
    Rg1['code_dep'] = Rg1['code_dep'].str.zfill(2)
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    referendum1 = referendum.drop(
        referendum[referendum['Department code'] == 'ZZ'].index)
    referendum1['code_dep'] = referendum1['Department code']
    merged = pd.merge(referendum1,
                      Rg1[['code_dep', 'code_reg',
                           'name_reg', 'name_dep']],
                      on='code_dep', how='left').dropna()

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    gb = referendum_and_areas[['code_reg', 'name_reg',
                               'Registered', 'Abstentions',
                               'Null', 'Choice A',
                               'Choice B']].set_index('code_reg')
    gb = gb.groupby('code_reg').agg({'name_reg': 'first',
                                     'Registered': sum,
                                     'Abstentions': sum,
                                     'Null': sum,
                                     'Choice A': sum,
                                     'Choice B': sum})
    return gb


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    df = gpd.read_file('data/regions.geojson')
    df = df.rename(columns={'nom': 'name_reg', 'code': 'code_reg'})

    mrg = pd.merge(referendum_result_by_regions,
                   df[['code_reg', 'geometry']],
                   on='code_reg', how='left').dropna()
    mrg = pd.merge(df[['code_reg', 'geometry']],
                   referendum_result_by_regions,
                   on='code_reg', how='left').dropna()
    mrg['ratio'] = mrg['Choice A'] / (mrg['Choice A'] + mrg['Choice B'])
    mrg.plot('ratio', legend=True)
    return mrg


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
