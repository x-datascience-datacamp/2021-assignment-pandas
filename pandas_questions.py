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

from json import load
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

    regions.rename(
        columns={'code': 'code_reg', 'name': 'name_reg'},
        inplace=True)
    departments.rename(
        columns={
            'region_code': 'code_reg', 'name': 'name_dep', 'code': 'code_dep'
            },
        inplace=True)

    regions_and_departments = pd.merge(
        regions,
        departments,
        on='code_reg',
        how='left')[['code_reg', 'name_reg', 'code_dep', 'name_dep']]

    return regions_and_departments


def aux_fun(x):

    if x.startswith('0'):

        return x.split('0')[-1]

    else:

        return x


def merge_referendum_and_areas(referendum, reg_and_dep):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    list_to_drop = ['975', '977', '978', '984', '986', '987', '988', '989',
                    '971', '972', '973', '974', '976', 'ZA', 'ZB', 'ZC', 'ZD',
                    'ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']

    referendum['code_dep'] = referendum['Department code'].copy()

    reg_and_dep['code_dep'] = reg_and_dep['code_dep'].apply(aux_fun)
    reg_and_dep = reg_and_dep[~reg_and_dep['code_dep'].isin(list_to_drop)]
    referendum = referendum[~referendum['code_dep'].isin(list_to_drop)]

    referendum_and_areas = pd.merge(
        reg_and_dep,
        referendum, how='left',
        on='code_dep').dropna(axis=0)

    return pd.DataFrame(referendum_and_areas)


def compute_referendum_result_by_regions(ref_and_ar):
    """Return a table with the absolute count for each region.
    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    attr_reg = ['code_reg',
                'name_reg',
                'Registered',
                'Abstentions',
                'Null',
                'Choice A',
                'Choice B']

    code_name_reg = ['code_reg', 'name_reg']

    ref_res_reg = ref_and_ar.groupby(code_name_reg, as_index=False).sum()
    ref_res_reg = ref_res_reg[attr_reg]
    ref_res_reg.set_index('code_reg', inplace=True)

    return ref_res_reg


def to_poly_multi(geometry):

    if geometry['type'] == 'Polygon':

        return Polygon(geometry['coordinates'][0])

    elif geometry['type'] == 'MultiPolygon':

        n = len(geometry['coordinates'])
        val = geometry['coordinates']

        return MultiPolygon([Polygon(val[i][0]) for i in range(n)])


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

    ref_res_v = gpd.GeoDataFrame(
        pd.merge(
            referendum_result_by_regions, geo_data, how='left', on='code_reg'
            )
        )

    ref_res_v['geometry'] = ref_res_v['geometry'].apply(to_poly_multi)

    num = ref_res_v['Choice A']
    den = ref_res_v[['Choice A', 'Choice B']].sum(axis=1)
    ref_res_v['ratio'] = num / den

    ref_res_v.plot(column='ratio', legend=True)

    return ref_res_v


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
