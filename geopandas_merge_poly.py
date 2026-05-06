import geopandas as gpd

input_shapefile = r"C:\path\to\project\data\input.shp"
output_shapefile = r"C:\path\to\project\output.shp"


def merge_duplicate_su_polygons(input_shapefile, output_shapefile):

    gdf = gpd.read_file(input_shapefile)

    merged = gdf.dissolve(by="SU", aggfunc="first").reset_index()
    merged.to_file(output_shapefile)

    print("Merge complete.")
    print("Output:", output_shapefile)


merge_duplicate_su_polygons(input_shapefile, output_shapefile)