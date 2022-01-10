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


# DOM-TOM-COM
dom_tom_com = {
    'WALLIS-ET-FUTUNA',
    'SAINT PIERRE ET MIQUELON',
    'SAINT-MARTIN/SAINT-BARTHELEMY',
    "FRANCAIS DE L'ETRANGER",
    'MAYOTTE',
    'POLYNESIE FRANCAISE',
    'LA REUNION',
    'GUYANE',
    'GUADELOUPE',
    'MARTINIQUE',
    'NOUVELLE CALEDONIE'
}

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
    # Merge both
    ret = pd.merge(regions, departments, left_on='code', right_on='region_code')
    # Select columns
    ret = ret[['code_x','name_x','code_y','name_y']]
    # Rename columns
    ret.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return ret

def normalize_refendum(dep_code):
    """Normalize department code on refendum file.

    Return a well-formated department code.
    """
    if len(dep_code) == 1: return '0' + dep_code
    else: return dep_code

def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    # Clean referendum
    # NOTE: DOM-TOM-COM are encoded in Z. format but we won't care as we'll drop it
    referendum['Department code'] = referendum['Department code'].apply(normalize_refendum)
    # Merge both
    ret = pd.merge(referendum, regions_and_departments, left_on='Department code', right_on='code_dep', how='left')
    # Drop lines with DOM-TOM-COM
    ret = ret[~ret['Department name'].isin(dom_tom_com)]
    # Drop rows with missing values
    ret = ret.dropna()
    return ret

def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    # Build a mapping from code_reg to name_reg
    # NOTE: A warning tells me it's bad but it shouldn't
    m = referendum_and_areas[['code_reg','name_reg']].set_index('code_reg').T.to_dict()
    # Select the columns and do a group by
    cols = ['name_reg', 'code_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    ret = referendum_and_areas[cols].groupby(['code_reg']).sum()
    # Add the name_reg
    ret['name_reg'] = ret.index.map(lambda x : m[x]['name_reg'])
    return ret


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    # Load the geopandas
    regions_geo = gpd.read_file('data/regions.geojson')
    print(regions_geo)
    # Remove DOM-TOM-COM
    regions_geo = regions_geo[regions_geo['code'].apply(int) > 6]
    # Compute the ratios
    referendum_result_by_regions['ratio'] = referendum_result_by_regions['Choice A'] / (referendum_result_by_regions['Choice A']  + referendum_result_by_regions['Choice B'])
    # Merge with referendum_result_by_regions
    ret = pd.merge(referendum_result_by_regions, regions_geo, left_on='code_reg', right_on='code')
    # Build the output by selection columns
    output = gpd.GeoDataFrame(ret[['ratio','name_reg'] + list(regions_geo.columns)])
    # Plot everything
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