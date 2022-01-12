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
    referendum = pd.read_csv('data/referendum.csv',sep=None,engine='python')                     
    regions = pd.read_csv('data/regions.csv')                                 
    departments = pd.read_csv('data/departments.csv')

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    department = departments.rename(columns={'name':'name_dep','code':'code_dep','region_code':'code_reg'})
    region = regions.rename(columns={'code':'code_reg','name':'name_reg'})
    region_dep = pd.merge(department,region,on='code_reg')
    region_dep = region_dep[['code_reg', 'name_reg', 'code_dep', 'name_dep']]
    return region_dep


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    region_dep = regions_and_departments
    for i in range(len(region_dep['code_dep'])):
        if region_dep['code_dep'][i][0]=='0':
            region_dep['code_dep'][i]=region_dep['code_dep'][i][1:]
    referendums = referendum
    labels = [i for i in range(len(referendums['Department code'])) if referendums['Department code'][i] in ['ZA', 'ZB', 'ZC', 'ZD','ZM', 'ZN', 'ZP', 'ZS', 'ZW', 'ZX', 'ZZ']]
    referendums = referendums.drop(labels=labels,axis=0)
    referendums = referendums.rename(columns={'Department code':'code_dep'})
    ref_reg_dep = pd.merge(region_dep,referendums,on='code_dep')
    referendums = referendums.rename(columns={'code_dep':'Department code'})
    ref_reg_dep = pd.concat([ref_reg_dep,referendums['Department code']],axis=1)
    return ref_reg_dep


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    ref_res= referendum_and_areas[['code_reg','name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]
    ref_res = ref_res.groupby(['code_reg','name_reg']).sum().reset_index()
    ref_res = ref_res.set_index('code_reg')
    return ref_res


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data = gpd.read_file('data/regions.geojson')
    data = data.rename(columns={'code':'code_reg','nom':'name_reg'})
    merger = pd.merge(data,referendum_result_by_regions,on=['code_reg','name_reg'])
    merger.plot('Choice A')
    merger['ratio'] = merger['Choice A']/(merger['Choice A']+merger['Choice B'])
    return merger


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
