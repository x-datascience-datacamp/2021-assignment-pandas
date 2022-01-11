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
    referendum = pd.read_csv('data/referendum.csv', sep=';')
    regions = pd.read_csv('data/regions.csv', sep=',')
    departments = pd.read_csv('data/departments.csv', sep=',')
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    departments = departments.rename(columns={
        "region_code": "code_reg", "code": "code_dep",
        "name": "name_dep", "slug": "slug_dep"})

    regions = regions.rename(columns={
        "code": "code_reg",
        "name": "name_reg", "slug": "slug_reg"})
    regions_and_departments = pd.merge(
        regions, departments,
        on="code_reg")[['code_reg', 'name_reg',
                        'code_dep', 'name_dep']]
    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """

    to_drop = ["Guadeloupe", 'Martinique',
               "Guyane", "La Réunion", "Mayotte",
               "Collectivités d'Outre-Mer"]
    regions_and_departments = regions_and_departments.drop(
        regions_and_departments[regions_and_departments["name_reg"].apply(
            lambda x:x in to_drop)].index)

    to_drop = ["FRANCAIS DE L'ETRANGER", 'POLYNESIE FRANCAISE', "MARTINIQUE",
               "NOUVELLE CALEDONIE", 'GUADELOUPE', "LA REUNION", "GUYANE",
               "MAYOTTE", 'SAINT-MARTIN/SAINT-BARTHELEMY',
               'SAINT PIERRE ET MIQUELON', 'WALLIS-ET-FUTUNA']
    referendum = referendum.drop(
        referendum[referendum["Department name"].apply(
            lambda x:x in to_drop)].index)
    referendum["code_dep"] = referendum["Department code"]
    idx = regions_and_departments[
        regions_and_departments["code_dep"].apply(
            lambda x:x.startswith('0'))].index
    regions_and_departments.loc[idx, "code_dep"] = regions_and_departments.loc[
        idx, "code_dep"].apply(
            lambda x: x.split('0')[1])
    dic_dep_codereg = regions_and_departments.groupby(
        'code_dep')['code_reg'].unique().to_dict()
    dic_dep_namereg = regions_and_departments.groupby(
        'code_dep')['name_reg'].unique().to_dict()
    dic_dep_namedep = regions_and_departments.groupby(
        'code_dep')['name_dep'].unique().to_dict()

    referendum_and_areas = referendum.copy()
    referendum_and_areas["code_reg"] = referendum[
        'Department code'].map(
            dic_dep_codereg).apply(lambda x: str(x[0]))
    referendum_and_areas["name_reg"] = referendum[
        'Department code'].map(
            dic_dep_namereg).apply(lambda x: str(x[0]))
    referendum_and_areas["name_dep"] = referendum[
        'Department code'].map(
            dic_dep_namedep).apply(lambda x: str(x[0]))
    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """

    referendum_and_areas2 = referendum_and_areas.groupby(
        by="code_reg")[['name_reg', 'Registered', 'Abstentions',
                        "Null", 'Choice A', 'Choice B']].sum()

    ids = referendum_and_areas2.index.tolist()
    names = [referendum_and_areas[
        referendum_and_areas["code_reg"] == str(i)][
            "name_reg"].iloc[0] for i in ids]
    dico = dict(zip(ids, names))
    referendum_and_areas2["name_reg"] = referendum_and_areas2.index.map(dico)
    referendum_result_by_regions = referendum_and_areas2[[
        'name_reg', 'Registered', 'Abstentions',
        'Null', 'Choice A', 'Choice B']]

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    dd = gpd.read_file('data/regions.geojson')
    dd = dd.rename(columns={'code': "code_reg"})
    dd2 = pd.merge(referendum_result_by_regions, dd, on='code_reg')
    dd2["ratio"] = dd2["Choice A"].div(dd2[[
        "Choice A", "Choice B"]].sum(axis=1))
    dd2 = gpd.GeoDataFrame(dd2)

    dd2.plot("ratio")
    plt.show()

    return dd2


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
