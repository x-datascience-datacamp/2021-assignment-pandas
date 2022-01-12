"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/2021-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame(pd.read_csv('data/referendum.csv'))
    regions = pd.DataFrame(pd.read_csv("data/regions.csv"))
    departments = pd.DataFrame(pd.read_csv("data/departments.csv"))
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """

    regions = regions.rename(columns={
        "code": "code_reg", "name": "name_reg", "slug": "slug_reg"
        }
        )
    departments = departments.rename(columns={
        "code": "code_dep", "name": "name_dep", "slug": "slug_dep",
        "region_code": "code_reg"
        }
        )

    regions_and_departments = pd.merge(
        departments,
        regions,
        how='left', on="code_reg")

    regions_and_departments = regions_and_departments[
        ['code_dep', 'name_dep', 'code_reg', 'name_reg']
        ]

    print(regions)
    print(departments)
    print(regions_and_departments)

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    referendum = referendum.rename(columns={
        "Department code": "code_dep"
        }

        )
    mask = [str(i) for i in range(1, 96)]
    referendum = referendum[referendum["code_dep"].isin(mask)]
    referendum['code_dep'] = referendum[
        'code_dep'].apply(lambda x: "%02d" % int(x))

    referendum_and_areas = pd.merge(
        referendum, regions_and_departments,
        how='left', on='code_dep'
        )

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum_result_by_regions = referendum_and_areas[
        [
            'code_reg',
            'name_reg',
            'Registered',
            'Abstentions',
            'Null',
            'Choice A',
            'Choice B'
         ]
    ]

    referendum_result_by_regions.set_index('code_reg')

    referendum_result_by_regions = referendum_result_by_regions.groupby(
        'code_reg').sum()

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    geo_region = gpd.read_file('data/regions.geojson')
    geo_region = geo_region.rename(columns={'code': 'code_reg'})
    referendum_result_by_regions = pd.merge(referendum_result_by_regions,
                                            geo_region, on='code_reg',
                                            how='left')

    referendum_result_by_regions = gpd.GeoDataFrame(
                                                referendum_result_by_regions
                                                    )

    referendum_result_by_regions.plot(column="Choice A")
    referendum_result_by_regions['ratio'] = referendum_result_by_regions[
                    'Choice A']/referendum_result_by_regions['Choice B']

    plt.show()

    return referendum_result_by_regions


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
