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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    merged_tables = pd.merge(regions.set_index('code'), departments,
                             left_index=True, right_on='region_code',
                             suffixes=('_reg', '_dep'))
    merged_tables.rename(columns={'region_code': 'code_reg',
                                  'code': 'code_dep'}, inplace=True)
    return merged_tables[['code_reg', 'name_reg', 'code_dep', 'name_dep']]


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    # Create a code_dep column in referendum, as the field 'Department
    # code' is inconsistent with it (01 becomes 1, etc.)
    referendum['code_dep'] = referendum['Department code']. \
        apply(lambda x: '0' + x if len(x) == 1 else x)

    # Merging the two will turn out to remove DOM-TOM-COM departments
    return pd.merge(referendum, regions_and_departments, on='code_dep')


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    retained_columns = ['code_reg', 'name_reg', 'Registered', 'Abstentions',
                        'Null', 'Choice A', 'Choice B']
    result = referendum_and_areas[retained_columns].groupby(['code_reg']). \
        aggregate({'name_reg': 'min', 'Registered': 'sum',
                   'Abstentions': 'sum', 'Null': 'sum', 'Choice A': 'sum',
                   'Choice B': 'sum'})
    return result


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    # First off, load the map and adjust merging column
    region_file = open('data/regions.geojson')
    map_parse = gpd.read_file(region_file).rename(columns={'code': 'code_reg'})
    map_parse = map_parse.set_index('code_reg')

    # Then, effectively apply the merge
    output = pd.merge(map_parse, referendum_result_by_regions, on='code_reg')

    # Afterwards, map the ratios, plot them, and output the resulting map
    output['ratio'] = output['Choice A']
    output['ratio'] /= output['Choice A'] + output['Choice B']

    output.plot('ratio', legend=True)
    return output


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
