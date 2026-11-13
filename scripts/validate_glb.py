"""Re-import exported GLBs into an empty scene and report what survived:
  Blender -b --factory-startup -P scripts/validate_glb.py -- project-files/export/*.glb > log
  grep "^VALID " log | sed 's/^VALID //' > output/glb_validation.txt"""
import sys, os, bpy
files = sys.argv[sys.argv.index("--") + 1:]
for f in files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=f)
    mats = [m for m in bpy.data.materials if m.use_nodes]
    tex = trans = emis = plain = 0
    for m in mats:
        b = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if b is None:
            continue
        has_tex = any(l.to_node == b and l.to_socket.name == "Base Color" for l in m.node_tree.links)
        tex += has_tex
        plain += not has_tex
        tw = next((s.default_value for s in b.inputs if s.name == "Transmission Weight"), 0.0)
        trans += tw > 0.5
        es = next((s.default_value for s in b.inputs if s.name == "Emission Strength"), 0.0)
        ec = next((s for s in b.inputs if s.name == "Emission Color"), None)
        emis += bool(ec and (ec.is_linked or (es > 0 and sum(ec.default_value[:3]) > 0.01)))
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    uv = sum(1 for o in meshes if o.data.uv_layers)
    print(f"VALID {os.path.basename(f)}: meshes {len(meshes)} (with UVs {uv}), materials {len(mats)} "
          f"[textured {tex}, plain colour {plain}, transmissive {trans}, emissive {emis}], "
          f"cameras {sum(1 for o in bpy.data.objects if o.type == 'CAMERA')}, lights {sum(1 for o in bpy.data.objects if o.type == 'LIGHT')}, "
          f"actions {len(bpy.data.actions)}")
