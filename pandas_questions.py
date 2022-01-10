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
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    new_regions = regions.copy().drop(columns=['slug', 'id'])
    new_regions.rename(columns={
        'code': 'code_reg',
        'name': 'name_reg'
    }, inplace=True)

    new_departments = departments.copy().drop(columns=['id', 'slug'])
    new_departments.rename(columns={
        'region_code': 'code_reg',
        'name': 'name_dep',
        'code': 'code_dep'
    }, inplace=True)

    df = new_regions.merge(new_departments, on='code_reg', how='right')
    return df


def clean_dpt_code(dep_code):
    """
    Make the department code at a standard format.

    :param dep_code
    :return: clean dep_code
    """
    if len(dep_code) == 1:
        return '0' + dep_code
    else:
        return dep_code


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code']\
        .apply(clean_dpt_code)
    df = pd.merge(left=referendum, right=regions_and_departments,
                  left_on='Department code',
                  right_on='code_dep')
    return df


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    clean_df = referendum_and_areas[[
        'code_reg',  # future index
        'name_reg',
        'Registered',
        'Abstentions',
        'Null',
        'Choice A',
        'Choice B'
    ]]
    clean_df = clean_df.groupby(['code_reg', 'name_reg']).sum()
    clean_df = clean_df.reset_index()
    clean_df = clean_df.set_index('code_reg')
    return clean_df


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geo_regions = gpd.read_file('data/regions.geojson')
    geo_regions = geo_regions.set_index('code')

    geo_raf = pd.merge(referendum_result_by_regions,
                       geo_regions,
                       left_index=True,
                       right_index=True)

    geo_raf['ratio'] = (geo_raf['Choice A']
                        / (geo_raf['Choice A']
                           + geo_raf['Choice B']))

    geo_data = gpd.GeoDataFrame(geo_raf)
    geo_data.plot(column='ratio')
    return geo_data


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
