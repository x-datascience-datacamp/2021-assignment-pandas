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
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    res = pd.merge(regions, departments,
                   left_on="code", right_on="region_code")
    res = res[["region_code", "name_x", "code_y", "name_y"]]
    res.columns = ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    return res


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    def add_zero(x):
        if len(x) == 1:
            return "0" + x
        else:
            return x
    referendum["Department code"] = referendum[
        "Department code"].apply(add_zero)
    res = pd.merge(referendum, regions_and_departments,
                   left_on="Department code", right_on="code_dep")

    return res


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    referendum_result_by_regions = referendum_and_areas.loc[:, \
    ['code_reg', 'name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']] \
            .groupby(['code_reg', 'name_reg']).sum()
    
    return referendum_result_by_regions.reset_index().set_index('code_reg')


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    geodata = gpd.read_file('data/regions.geojson')
    data = pd.merge(referendum_result_by_regions, geodata, left_on = 'name_reg', right_on = 'nom')
    data.index = referendum_result_by_regions.index
    data['rate'] = data['Choice A']/(data['Registered'] - data['Abstentions'] - data['Null'])
    output = gpd.GeoDataFrame(data, geometry='geometry')
    title = 'Percentage of votes expressed for A in every metroplitan region'
    plt.plot(output, column='rate', legend=True)
    plt.title(title)
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
