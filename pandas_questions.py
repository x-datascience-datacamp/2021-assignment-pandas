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
    referendum = pd.read_csv("./data/referendum.csv", ";")
    regions = pd.read_csv("./data/regions.csv", ",")
    departments = pd.read_csv("./data/departments.csv", ",")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    return pd.merge(regions, departments, left_on='code',
                    right_on='region_code', how='left'
                    ).drop(
        ['code_x', 'id_x', 'slug_x', 'slug_y', 'id_y'],
        axis=1
    ).rename(columns={'region_code': 'code_reg',
                      'name_x': 'name_reg',
                      'code_y': 'code_dep', 'name_y': 'name_dep'}
             )


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum[
        'Department code'].apply(lambda x: x.zfill(2))

    return pd.merge(
        regions_and_departments, referendum,
        left_on='code_dep', right_on='Department code',
        how='inner')


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_and_areas = referendum_and_areas.groupby([
        'code_reg', 'name_reg'], as_index=False)[
        ['Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
        ].sum()
    referendum_and_areas.set_index('code_reg', inplace=True)
    return referendum_and_areas


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_reg = gpd.read_file('./data/regions.geojson')

    geo_referundum = pd.merge(geo_reg, referendum_result_by_regions,
                              left_on='code', right_on='code_reg', how='inner')
    geo_referundum['ratio'] = geo_referundum['Choice A'] / (
            geo_referundum[
                'Registered'] - geo_referundum[
                    'Abstentions'] - geo_referundum['Null'])

    geo_referundum.rename({'nom': 'name_reg'})
    geo_referundum.plot(column='ratio', legend=True,
                        legend_kwds={
                            'label': "choice_A_ratio",
                            'orientation': "horizontal"})

    return geo_referundum


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
