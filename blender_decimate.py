import bpy
import os

ratio = .12
output_folder = r"C:\path\to\project\output"
os.makedirs(output_folder, exist_ok=True)

def ensure_object_mode():
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

# Decimate the object using the ratio variable
def decimate_object(obj, ratio: float):
    if ratio >= 1.0:
        return
    ensure_object_mode()
    mod = obj.modifiers.new(name="Decimate", type="DECIMATE")
    mod.ratio = ratio
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.select_set(False)

# Export the object 
def export_obj(obj, out_path: str):
    ensure_object_mode()
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.wm.obj_export(
        filepath=out_path,
        export_selected_objects=True,
        apply_modifiers=True
    )

# decimate all meshes in the scene and export
def main():
    ensure_object_mode()
    bpy.ops.object.select_all(action="DESELECT")
    results = []
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            decimate_object(obj, ratio)
            export_obj(obj, f"{output_folder}/{obj.name}.obj")
    return results

main()