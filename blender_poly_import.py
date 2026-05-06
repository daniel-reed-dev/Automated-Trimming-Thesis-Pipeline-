import sys, os, bpy
from mathutils import Vector
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon


# Load shapefile
shapefile_path = r"C:\path\to\project\data\input.shp"
gdf = gpd.read_file(shapefile_path)

print("Loaded shapefile with", len(gdf), "features")
print("CRS:", gdf.crs)

# Import each polygon in shapefile
for idx, row in gdf.iterrows():
    geom = row.geometry
    su = row["SU"]
    desc = row["DESCRIPTIO"]
    name = f"SU{su}_{desc}"

    if isinstance(geom, Polygon):
        polygons = [geom]
    elif isinstance(geom, MultiPolygon):
        polygons = list(geom.geoms)
    
    # Skip if not a polygon shapefile
    else:
        print(f"Shapefile not a polygon source")
        continue

    for p_i, poly in enumerate(polygons):
        coords = list(poly.exterior.coords)

        # Force Z = 0
        verts = []
        for c in coords:
            x = float(c[0])
            y = float(c[1])
            verts.append((x, y, 0.0))

        # One face using all verts in order
        face_indices = [list(range(len(verts)))]

        # Creates flat mesh from polygon vertices
        mesh = bpy.data.meshes.new(f"{name}")
        mesh.from_pydata(verts, [], face_indices)
        mesh.update()

        # Creates linked object
        obj = bpy.data.objects.new(f"{name}", mesh)
        bpy.context.collection.objects.link(obj)

        print(f" Imported poly {idx}, part {p_i} with {len(verts)} verts at Z=0")

print("Import finished")