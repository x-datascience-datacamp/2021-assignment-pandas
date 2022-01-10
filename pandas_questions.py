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
import json

from shapely.geometry import Polygon, MultiPolygon


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
    regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'}, inplace=1)
    columns = {
        'region_code': 'code_reg',
        'code': 'code_dep',
        'name': 'name_dep'
        }
    departments.rename(columns=columns, inplace=1)

    df_res = regions.merge(departments, on='code_reg')
    df_res = df_res[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return df_res


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    def transform_type(code):
        list_codes = [str(i) for i in range(10)]
        if code in list_codes:
            code = '0' + code
        return code

    liste = [f'0{i}' for i in range(1, 7)]
    filter = ~regions_and_departments['code_reg'].isin(liste)
    regions_and_departments = regions_and_departments[filter]

    filter = regions_and_departments['code_reg'] != 'COM'
    regions_and_departments = regions_and_departments[filter]

    referendum['Department code'] = \
        referendum['Department code'].apply(transform_type)

    df_res = pd.merge(referendum, regions_and_departments, how='right',
                      left_on='Department code', right_on='code_dep')

    return df_res


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    col = ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    df = referendum_and_areas.groupby('name_reg').agg('sum')[col].reset_index()
    return df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    with open('./data/regions.geojson') as f:
        regions = json.load(f)

    liste = [[r['geometry']['type'], r['geometry']['coordinates'],
              r['properties']['code'], r['properties']['nom']]
             for r in regions['features']]
    col = ['type', 'coordinates', 'code', 'name_reg']
    df_geo = gpd.GeoDataFrame(liste, columns=col)

    def to_polygon(row):
        if row.type == 'Polygon':
            return Polygon([tuple(r) for r in row.coordinates][0])
        if row.type == 'MultiPolygon':
            coordinates = row.coordinates
            return MultiPolygon([Polygon([tuple(r) for r in coordinates[i][0]])
                                 for i in range(len(coordinates))])

    df_geo['geometry'] = df_geo.apply(to_polygon, axis=1)
    df_tmp = referendum_result_by_regions.copy()
    total = df_tmp['Choice A'] + df_tmp['Choice B']
    ratio = df_tmp['Choice A'] / total
    referendum_result_by_regions['ratio'] = ratio
    df = df_geo.merge(referendum_results.reset_index())
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
