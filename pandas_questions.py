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

import os
import json


def load_data():
    """Load data from the CSV files referundum/regions/departments."""
    file_referendum = os.path.join(".", "data",
                                   "referendum.csv")
    file_regions = os.path.join(".", "data",
                                "regions.csv")
    file_departments = os.path.join(".", "data",
                                    "departments.csv")

    referendum = pd.read_csv(file_referendum, sep=";")
    regions = pd.read_csv(file_regions)
    departments = pd.read_csv(file_departments)

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions.drop(["id", "slug"], axis=1, inplace=True)
    regions.rename(columns={"code": "code_reg",
                            "name": "name_reg"}, inplace=True)

    departments.drop(["id", "slug"], axis=1, inplace=True)
    departments.rename(columns={"code": "code_dep",
                                "region_code": "code_reg",
                                "name": "name_dep"}, inplace=True)

    regions_and_departments = pd.merge(departments,
                                       regions,
                                       on="code_reg")

    return regions_and_departments


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    def modif_code_dpt(x):
        # Les dpt de No inférieur à 10 sont codés sur 2 caractères
        # par exemple '01' et non '1' afin d'avoir un merge correct
        if len(x) == 1:
            return "0{}".format(x)
        else:
            return x

    referendum["Department code"] = \
        referendum["Department code"].astype(str)\
        .apply(lambda x: modif_code_dpt(x))
    regions_and_departments["code_dep"] = \
        regions_and_departments["code_dep"].astype(str)
    referendum_and_areas = pd.merge(referendum,
                                    regions_and_departments,
                                    left_on="Department code",
                                    right_on="code_dep")

    return referendum_and_areas


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    col_to_delete = ['Department code',
                     'Department name',
                     'Town code',
                     'Town name',
                     'code_dep',
                     'name_dep']

    referendum_result_by_regions = \
        referendum_and_areas.drop(col_to_delete, axis=1)

    Nom_region = \
        referendum_result_by_regions[["code_reg", "name_reg"]] \
        .drop_duplicates().set_index("code_reg")

    referendum_result_by_regions = \
        referendum_result_by_regions.groupby("code_reg").sum()

    referendum_result_by_regions = \
        pd.merge(referendum_result_by_regions,
                 Nom_region,
                 left_index=True,
                 right_index=True)

    col_ordonnees = ['name_reg',
                     'Registered',
                     'Abstentions',
                     'Null',
                     'Choice A',
                     'Choice B']

    referendum_result_by_regions = \
        referendum_result_by_regions[col_ordonnees]

    return referendum_result_by_regions


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    def construit_ratio(A, B):
        Retour = A / (A + B)
        return Retour

    # Load geographic data
    carte_region_file = os.path.join(".", "data",
                                     "regions.geojson")
    with open(carte_region_file) as f:
        data = json.load(f)

    carte_region = \
        gpd.GeoDataFrame.from_features(data['features']) \
        .rename(columns={"code": "code_reg"})

    referendum_map = \
        carte_region.merge(referendum_result_by_regions,
                           on="code_reg").drop(["nom"], axis=1)
    Liste_colonnes = ["Choice A", "Choice B"]
    referendum_map["ratio"] = \
        referendum_map[Liste_colonnes] \
        .apply(lambda x: construit_ratio(*x), axis=1)
    col_ordonnees = ["code_reg",
                     "name_reg",
                     "Registered",
                     "Abstentions",
                     "Null",
                     "Choice B",
                     "ratio",
                     "geometry"]
    referendum_map = referendum_map[col_ordonnees]

    referendum_map.plot(column="ratio", cmap="coolwarm",
                        figsize=(12, 10), legend=True)
    plt.title("Rate of 'Choice A' over all expressed ballots")

    return referendum_map


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
