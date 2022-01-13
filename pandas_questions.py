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
    referendum = pd.read_csv("data/referendum.csv", sep=";")
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")
    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame."""
    departments = departments.drop(['id', 'slug'], axis=1)
    regions = regions.drop(['id', 'slug'], axis=1)
    regions.rename(columns={"code": "code_reg",
                            "name": "name_reg"}, inplace=True)
    departments.rename(columns={"region_code": "code_reg",
                                "code": "code_dep",
                                "name": "name_dep"},  inplace=True)
    merged = pd.merge(departments, regions, on="code_reg")
    return merged


def modif_dep_code(x):
    """Modify the dep_code to the right format."""
    if len(x) == 1:
        return "0{}".format(x)
    else:
        return x


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame."""
    temp = referendum["Department code"]
    temp = temp.astype(str).apply(modif_dep_code)
    referendum["Department code"] = temp
    referendum_area = pd.merge(regions_and_departments, referendum,
                               left_on='code_dep',
                               right_on="Department code")
    return referendum_area


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    col_to_delete = ["Department code", "Department name", "Town code",
                     "Town name", "code_dep", "name_dep"]
    ref_result_by_region = referendum_and_areas.drop(col_to_delete, axis=1)
    Nom_region = ref_result_by_region[['code_reg', 'name_reg']]
    Nom_region = Nom_region.drop_duplicates().set_index("code_reg")
    ref_result_by_region = ref_result_by_region.groupby("code_reg").sum()
    ref_result_by_region = pd.merge(ref_result_by_region, Nom_region,
                                    left_index=True, right_index=True)
    col_ordonnees = ['name_reg', 'Registered', 'Abstentions', 'Null',
                     'Choice A', 'Choice B']
    ref_result_by_region = ref_result_by_region[col_ordonnees]
    return ref_result_by_region


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    data_geo = gpd.read_file('data/regions.geojson')
    merge = data_geo.merge(referendum_result_by_regions,
                           left_on="code", right_on="code_reg", how="inner")
    merge["ratio"] = merge["Choice A"]/(merge["Choice A"] + merge["Choice B"])
    merge.plot(column="ratio")
    return merge


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
