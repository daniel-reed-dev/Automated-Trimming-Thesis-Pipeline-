import bpy

TARGET_PREFIX = "PM"       # PM meshes should start with PM / pm
POLY_PREFIX = "SU"         # SU polygon cutters should start with SU
KEEP_BOUNDINGBOX = True
BOOLEAN_SOLVER = "FAST"
BOOLEAN_HOLE_TOLERANT = True


# Forces OBJECT mode
def ensure_object_mode():
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')


# Recalculates face normals
def recalc_normals_outside(obj):
    ensure_object_mode()
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.select_set(False)


# Returns list of vertices in Blender coords for a mesh
def world_verts(obj):
    matrix_world = obj.matrix_world
    return [matrix_world @ v.co for v in obj.data.vertices]


# Returns (zmin, zmax) of target mesh vertices that fall within the polygon's coordinate space.
def target_z_range_within_poly_xy(poly_obj, mesh_obj, target_verts=None):
    # Get polygon XY bounds (world)
    poly_w = world_verts(poly_obj)

    if target_verts is None:
        # Get target mesh vertices (world)
        target_verts = world_verts(mesh_obj)

    minx = min(v.x for v in poly_w); maxx = max(v.x for v in poly_w)
    miny = min(v.y for v in poly_w); maxy = max(v.y for v in poly_w)

    # Filter by XY box
    zvals = [
        v.z for v in target_verts
        if minx <= v.x <= maxx and miny <= v.y <= maxy
    ]

    if not zvals:
        # fallback: whole mesh
        zvals = [v.z for v in target_verts]

    return min(zvals), max(zvals)


# Takes flat polygon and extrudes into a boundingbox
def build_boundingbox_from_flat_poly(poly_obj, mesh_obj, target_verts=None):
    ensure_object_mode()

    outline = world_verts(poly_obj)
    count = len(outline)
    # Get mesh's z-range within the poly's XY footprint
    zmin, zmax = target_z_range_within_poly_xy(poly_obj, mesh_obj, target_verts)

    bottom = [(v.x, v.y, 0) for v in outline]
    top = [(v.x, v.y, zmax + 1.0) for v in outline]
    frame = bottom + top

    faces = []
    faces.append(list(reversed(range(count))))
    faces.append([count + i for i in range(count)])
    # Create side faces connecting bottom and top outlines
    for i in range(count):
        j = (i + 1) % count
        faces.append([i, j, count + j, count + i])


    mesh_data = bpy.data.meshes.new(f"{poly_obj.name}_boundingbox")
    mesh_data.from_pydata(frame, [], faces)
    mesh_data.update()

    boundingbox = bpy.data.objects.new(f"{poly_obj.name}_boundingbox", mesh_data)
    # Ensure normals face outside so boolean behaves
    bpy.context.collection.objects.link(boundingbox)
    recalc_normals_outside(boundingbox)
    boundingbox.select_set(False)

    return boundingbox


# Applies Boolean modifier on a copy of target mesh using boundingbox
def boolean_intersect_copy(target, boundingbox, output_name):
    ensure_object_mode()

    # Duplicate the target mesh
    trim = target.copy()
    trim.data = target.data.copy()
    trim.name = output_name
    bpy.context.collection.objects.link(trim)

    # Apply rotation/scale on the cut copy, keep location
    bpy.context.view_layer.objects.active = trim
    trim.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    trim.select_set(False)

    # Add Boolean modifier on the copy
    bpy.context.view_layer.objects.active = trim
    trim.select_set(True)

    mod = trim.modifiers.new(name=f"Intersect_{boundingbox.name}", type='BOOLEAN')
    mod.operation = 'INTERSECT'
    mod.solver = BOOLEAN_SOLVER
    mod.object = boundingbox

    # Guards Boolean parameters in between versions of Blender
    if hasattr(mod, "use_hole_tolerant"):
        mod.use_hole_tolerant = BOOLEAN_HOLE_TOLERANT

    if hasattr(mod, "use_self"):
        mod.use_self = False

    # Apply the modifier to the copy
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except RuntimeError as e:
        print(f"Boolean failed for {output_name}: {e}")
        bpy.data.objects.remove(trim, do_unlink=True)
        trim = None

    if trim:
        trim.select_set(False)

    return trim


def main():
    ensure_object_mode()

    # All imported PM meshes
    targets = [
        o for o in bpy.context.scene.objects
        if o.type == 'MESH' and o.name.upper().startswith(TARGET_PREFIX)
    ]

    # Selected SU polygon cutters
    polys = [
        o for o in bpy.context.selected_objects
        if o.type == 'MESH' and o.name.upper().startswith(POLY_PREFIX)
    ]

    if not targets:
        raise RuntimeError("No PM mesh targets found.")

    if not polys:
        raise RuntimeError("Select one or more SU polygon cutters, then run again.")

    print(f"Targets: {[t.name for t in targets]}")
    print(f"Polygons: {[p.name for p in polys]}")

    results = []

    # For each PM mesh, cut it by each selected SU polygon
    for target in targets:
        cache = world_verts(target)
        for poly in polys:
            
            # Check if SU number is in poly name
            su_num = poly.name.split("_")[0].upper()
            if su_num not in target.name.upper():
                continue
            
            boundingbox = build_boundingbox_from_flat_poly(poly, target, cache)

            output_name = f"{target.name.split('_')[0]}_{poly.name}"

            trimmed_obj = boolean_intersect_copy(target, boundingbox, output_name)

            if trimmed_obj:
                results.append(trimmed_obj)

            if not KEEP_BOUNDINGBOX:
                bpy.data.objects.remove(boundingbox, do_unlink=True)

    print(f"Done. Created {len(results)} cut meshes.")
    return results


main()