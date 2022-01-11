"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""

from json import load
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, MultiPolygon 

def load_data():


    """Load data from the CSV files referundum/regions/departments."""

    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')

    return referendum, regions, departments

def merge_regions_and_departments(regions, departments):


    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'}, inplace=True)
    departments.rename(columns={'region_code': 'code_reg', 'name': 'name_dep', 'code': 'code_dep'}, inplace=True)

    regions_and_departments = pd.merge(regions, departments, on='code_reg', how='left')[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    
    list_to_drop = ['975', '977', '978', '984', '986', '987', '988', '989', 
                    '971', '972', '973', '974', '976', 'ZA', 'ZB', 'ZC', 'ZD', 
                    'ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']

    referendum['code_dep'] = referendum['Department code'].copy()

    regions_and_departments['code_dep'] = regions_and_departments['code_dep'].apply(lambda x: x.split('0')[-1] if x.startswith('0') else x)
    regions_and_departments = regions_and_departments[~regions_and_departments['code_dep'].isin(list_to_drop)]
    referendum = referendum[~referendum['code_dep'].isin(list_to_drop)]

    referendum_and_areas = pd.merge(regions_and_departments, referendum, how='left', on='code_dep').dropna(axis=0)

    return pd.DataFrame(referendum_and_areas)


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum_result_by_regions = referendum_and_areas.groupby(['code_reg', 'name_reg'], as_index=False).sum()[['code_reg', 'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    referendum_result_by_regions.set_index('code_reg', inplace=True)

    return referendum_result_by_regions

def to_polygon_multipolygon(geometry):

    if geometry['type'] == 'Polygon':

        return Polygon(geometry['coordinates'][0])
    
    if geometry['type'] == 'MultiPolygon':

        return MultiPolygon([Polygon(geometry['coordinates'][i][0]) for i in range(len(geometry['coordinates']))])

def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    file = open('data/regions.geojson')
    data = load(file)

    geo_data = gpd.GeoDataFrame(data['features'])
    geo_data['code_reg'] = geo_data['properties'].apply(lambda x: x['code'])

    referendum_results_view = gpd.GeoDataFrame(pd.merge(referendum_result_by_regions, geo_data, how='left', on='code_reg'))

    referendum_results_view['geometry'] = referendum_results_view['geometry'].apply(to_polygon_multipolygon)
    referendum_results_view['ratio'] = referendum_results_view['Choice A']/ referendum_results_view[['Choice A', 'Choice B']].sum(axis=1)

    referendum_results_view.plot(column='ratio', legend=True)

    return referendum_results_view


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