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
    referendum = pd.read_csv('data/referendum.csv', skipfooter=4, sep=';',
                             engine='python')
    regions = pd.read_csv('data/regions.csv')
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    merged = departments.merge(regions, how='left', left_on='region_code',
                               right_on='code')
    merged = merged[['code_y', 'name_y', 'code_x', 'name_x']].rename(columns={
        'code_y': 'code_reg',
        'name_y': 'name_reg',
        'code_x': 'code_dep',
        'name_x': 'name_dep'
    })
    merged['code_dep'] = merged['code_dep'].apply(
        lambda x: x[1:] if x[0] == '0' else x)
    return merged


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    return referendum[~referendum['Department code'].str.startswith('Z')].\
        merge(regions_and_departments, how='left', left_on='Department code',
              right_on='code_dep')


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    grouped = referendum_and_areas.groupby('code_reg').sum()[[
        'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    grouped['name_reg'] = [referendum_and_areas[
        referendum_and_areas['code_reg'] == i]['name_reg'].iloc[0]
        for i in grouped.index
        ]

    return grouped[['name_reg', 'Registered', 'Abstentions', 'Null',
                    'Choice A', 'Choice B']]


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    coordinates = gpd.read_file('data/regions.geojson')
    merged = referendum_result_by_regions.merge(coordinates[
        ['code', 'geometry']], how='left', left_index=True, right_on='code')

    geodata = gpd.GeoDataFrame(merged[[
        'name_reg', 'Registered', 'Abstentions', 'Null',
        'Choice A', 'Choice B', 'geometry']])

    geodata['ratio'] = geodata['Choice A'] / (
        geodata['Choice A'] +
        geodata['Choice B']
        )

    fig, ax = plt.subplots(figsize=(12, 12))
    ax.axis('off')
    vmin, vmax = geodata['ratio'].min(), geodata['ratio'].max()

    _ = geodata[['ratio', 'geometry']].plot(
        cmap='Blues', ax=ax, edgecolor='white', legend=True,
        vmin=vmin, vmax=vmax)

    fig = ax.get_figure()
    cax = fig.add_axes([0.9, 0.1, 0.03, 0.8])
    sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(
        vmin=vmin, vmax=vmax))
    sm._A = []
    fig.colorbar(sm, cax=cax)

    return geodata


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
