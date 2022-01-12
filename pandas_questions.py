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

DOM_TOM_COM_Names = [
    'GUADELOUPE',
    'MARTINIQUE',
    'GUYANE',
    'LA REUNION',
    'MAYOTTE',
    'SAINT PIERRE ET MIQUELON',
    'SAINT-MARTIN/SAINT-BARTHELEMY',
    'WALLIS-ET-FUTUNA',
    'POLYNESIE FRANCAISE',
    'NOUVELLE CALEDONIE',
    "FRANCAIS DE L'ETRANGER"
]


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    referendum = pd.DataFrame({})
    regions = pd.DataFrame({})
    departments = pd.DataFrame({})
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    # Merge regions and departments
    regions_and_departments = pd.merge(regions, departments,
                                       left_on='code', right_on='region_code')

    # Select and rename wanted columns
    regions_and_departments = regions_and_departments[['code_x', 'name_x',
                                                       'code_y', 'name_y']]
    regions_and_departments.columns = ['code_reg', 'name_reg',
                                       'code_dep', 'name_dep']
    return regions_and_departments


def wrap_departement_code(departement_code):
    # Make all departement codes at two digits
    if len(departement_code) == 1:
        return '0' + departement_code
    else:
        return departement_code


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.
    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Wrap department codes
    referendum['Department code'] = \
        referendum['Department code'].apply(wrap_departement_code)

    # Merge referendum and regions_and_departments
    referendum_and_areas = pd.merge(referendum, regions_and_departments,
                                    left_on='Department code',
                                    right_on='code_dep',
                                    how='left')

    # Drop lines relative to DOM-TOM-COM departments and NaN values
    referendum_and_areas =  \
        referendum_and_areas[~referendum_and_areas['Department name']
                             .isin(DOM_TOM_COM_Names)]
    referendum_and_areas = referendum_and_areas.dropna()
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    # Compute the absolute results for earch region
    referendum_results = referendum_and_areas\
        .groupby(by=['code_reg', 'name_reg']).sum()

    # Index by 'code-reg'
    referendum_results = referendum_results.\
        reset_index(level='name_reg')[['name_reg',
                                       'Registered',
                                       'Abstentions',
                                       'Null',
                                       'Choice A',
                                       'Choice B']]
    return referendum_results


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """

    # Read the geojson region file
    regional_map = gpd.read_file('data/regions.geojson')

    # Drop the DOM-TOM-COM of the map
    regional_map = regional_map[regional_map['code'].apply(int) > 6]

    # Get the different results per region
    referendum_result_by_regions['ratio'] = \
        referendum_result_by_regions['Choice A'] / \
        (referendum_result_by_regions['Choice A'] +
         referendum_result_by_regions['Choice B'])

    # Merge the results with the regional map
    referendum_map = pd.merge(referendum_result_by_regions,
                              regional_map,
                              left_on='code_reg',
                              right_on='code')

    # Select important columns
    output = gpd.GeoDataFrame(referendum_map[['ratio', 'name_reg']
                              + list(regional_map .columns)])

    # Plot the map
    output.plot('ratio')
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
