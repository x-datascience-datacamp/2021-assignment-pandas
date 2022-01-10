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

    return pd.merge(regions[['code', 'name']].rename(
                        columns={'code': 'code_reg', 'name': 'name_reg'}),
                    departments[['code', 'name', 'region_code']].rename(
                        columns={'code': 'code_dep', 'name': 'name_dep',
                                 'region_code': 'code_reg'}),
                    on='code_reg')


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    # there is no need to explicitly remove non-metropolitan France and
    # Frenchs abroad, because the input dataframes have different codes
    # for these regions and we use how='inner'
    referendum['code_dep'] = referendum['Department code'].\
        apply(lambda s: '0'+s if len(s) == 1 else s)
    # the lambda function above is to put 1-digits dep codes in 2-digits
    # notation '1' => '01'
    df = pd.merge(referendum, regions_and_departments, on='code_dep')

    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    df = referendum_and_areas.drop(
            ['code_dep', 'Department name', 'Town code',
             'Town name', 'name_dep'],
            axis=1
        )
    df = df.groupby(['code_reg']).aggregate(
        {'name_reg': 'min', 'Registered': 'sum', 'Abstentions': 'sum',
         'Null': 'sum', 'Choice A': 'sum', 'Choice B': 'sum'})

    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    file = open('data/regions.geojson')
    df = gpd.read_file(file)
    df = df.rename(columns={'code': 'code_reg'}).set_index('code_reg')

    # "the stand-alone pandas.merge() function will work if the GeoDataFrame is
    # in the left argument; if a DataFrame is in the left argument and a
    # GeoDataFrame is in the right position, the result will no longer be
    # a GeoDataFrame."
    # -- https://geopandas.org/en/stable/docs/user_guide/mergingdata.html
    df = pd.merge(df, referendum_result_by_regions, on='code_reg')
    df['ratio'] = df['Choice A'] / (df['Choice A'] + df['Choice B'])
    df.plot('ratio', legend=True)

    return df


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
