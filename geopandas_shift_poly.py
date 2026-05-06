import geopandas as gpd

input_feature_class = r"C:\path\to\project\data\input.shp"
output_feature_class = r"C:\path\to\project\output.shp"

authority= "ESRI"
code= 102093
target_crs = f"{authority}:{code}"

dx= -2329500.0
dy= -4639400.0

def force_crs(gdf, crs):
    #If the CRS is geographic, reproject to local CRS
    if gdf.crs.is_geographic:
        gdf = gdf.to_crs(target_crs)
    # Force CRS to Gauss if in Monte Mario
    elif gdf.crs.to_authority() == ("EPSG", "3004"):
        gdf = gdf.set_crs(target_crs, allow_override=True)
    return gdf

def shift_polygons(gdf, output_feature_class, dx, dy):
    # Translate/shift geometries by dx and dy
    gdf["geometry"] = gdf.geometry.translate(xoff=dx, yoff=dy)
    # Save to new shapefile
    gdf.to_file(output_feature_class)
    return gdf

def main():
    # Read file
    gdf = gpd.read_file(input_feature_class)
    # Fix / force CRS
    gdf = force_crs(gdf, target_crs)
    #print("CRS:", gdf.crs)
    # Shift polygons into local coordinates
    gdf = shift_polygons(gdf, output_feature_class, dx, dy)
    # Save output
    gdf.to_file(output_feature_class)


if __name__ == "__main__":
    main()
print("Shift complete.")
print("Output:", output_feature_class)
print("dx:", dx, "dy:", dy)