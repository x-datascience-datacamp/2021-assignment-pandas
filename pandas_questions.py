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
    referendum = pd.read_csv('./data/referendum.csv', sep=';')
    regions = pd.read_csv('./data/regions.csv')
    departments = pd.read_csv('./data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.rename(
        columns={'code': 'code_dep', 'region_code': 'code_reg',
                 'name': 'name_dep'})
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    output = pd.merge(departments, regions, on='code_reg', how='left')
    output = output.drop(columns=['slug_x', 'slug_y', 'id_x', 'id_y'])
    return output


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    mask = ~referendum.loc[:, 'Department code'].str.startswith('Z')
    referendum = referendum.loc[mask]

    regions_and_departments.loc[:, 'code_dep'] = \
        regions_and_departments.loc[:, 'code_dep'].str.lstrip('0')

    referendum.insert(1, 'code_dep', referendum['Department code'].values)
    return pd.merge(referendum, regions_and_departments, how='left')


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    columns = ['name_reg', 'Registered', 'Abstentions',
               'Null', 'Choice A', 'Choice B']
    Count_reg = referendum_and_areas.loc[:, columns].groupby('name_reg').sum()
    Count_reg = Count_reg.reset_index()
    return Count_reg


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodf = gpd.read_file('./data/regions.geojson')

    geodf_data = pd.merge(referendum_result_by_regions.reset_index(),
                          geodf.rename(columns={'nom': 'name_reg'}),
                          how='left')
    gpd.GeoDataFrame(geodf_data).plot(column='Choice A')

    geodf_ratio = gpd.GeoDataFrame()

    geodf_ratio['name_reg'] = geodf_data['name_reg']
    geodf_ratio['Null_ratio'] = geodf_data['Null'] / geodf_data['Registered']
    geodf_ratio['ratio'] = geodf_data['Choice A'] / \
        (geodf_data['Choice B'] + geodf_data['Choice A'])
    geodf_ratio['B_ratio'] = geodf_data['Choice B'] / geodf_data['Registered']

    return geodf_ratio


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
