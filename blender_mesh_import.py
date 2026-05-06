import bpy
import os
import glob

input_folder = r"C:\path\to\project\data\obj\folder"
# Iterate through all .obj files in folder
for obj_path in glob.glob(os.path.join(input_folder, "*.obj")):
    name = os.path.basename(obj_path)
    print(f"Importing {name}...")

    bpy.ops.wm.obj_import(
        filepath=obj_path,
        forward_axis='Y',
        up_axis='Z'
    )

print("Finished importing OBJ files.")
