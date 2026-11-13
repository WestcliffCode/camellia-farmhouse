# Export notes (Unreal Engine / other DCCs)

## What is exported
`project-files/export/` holds one GLB per package, written by `scripts/export_glb.py`
(`Blender -b project-files/camellia-farmhouse.blend -P scripts/export_glb.py`). The folder is git-ignored; re-run the script to regenerate it. `scripts/validate_glb.py` re-imports the packages into an empty scene and reports what survived; the last run is summarised below.

| File | Contents |
| --- | --- |
| `camellia_structure.glb` | walls, slab, ceilings, floors, stair, bonus-room shell, windows, doors, cladding battens |
| `camellia_millwork.glb` | base and crown, casings, panel moulding, kitchen, coffee bar, pantry shelving, fireplaces, exterior timber |
| `camellia_exterior.glb` | roofs, gable walls, dormers, porches, chimneys, ground, paving |
| `camellia_furn_<room>.glb` (18 files) | furniture and decor per room; Poly Haven instances are realised into meshes |
| `camellia_cameras_lights.glb` | 29 still cameras, 4 orthographic elevation cameras, the walkthrough camera with its move baked to keyframes, 180 lights |
| `camellia_landscape.glb` | the 14 trees (one Poly Haven tree mesh, instanced) |

## Validation (re-import test)
- All 23 packages import. Every mesh carries a UV set.
- Textured materials arrive with their base-colour, roughness and normal maps; glass arrives as a transmissive material (KHR_materials_transmission); lamp shades, bulbs and can lenses arrive emissive.
- `camellia_cameras_lights.glb`: 34 cameras, 180 lights (145 spot, 34 point, 1 sun via KHR_lights_punctual) and the baked walkthrough animation.

## Conventions
- Units are metres; Blender is Z-up and the GLB is written Y-up. Import into Unreal with glTF import (Interchange): scale 100 (cm), no extra rotation.
- Origin is the front-left exterior corner of the house at finished-floor level, so every package drops in at 0,0,0 and lines up.
- All procedural meshes carry one UV set (`UVMap`) in real-world metres. Texture tiling is the material's UV scale (1 / tile size, see `DESIGN_SYSTEM.md`) and is exported as a texture transform (KHR_texture_transform).
- Materials are a single Principled BSDF with image textures or plain values. Colour tints on the Poly Haven sets are baked into the exported textures, so no node work needs recreating.
- No lightmap UVs are authored. Use Lumen, or let Unreal generate lightmap UVs on import (most meshes are boxes and flat panels, so auto-unwrap is clean).
- Collision: use complex-as-simple for walls, floors and the stair; furniture can take auto convex hulls.
- Doors are separate objects with the origin on the hinge (`GEO-doorleaf_*`), ready to animate or drive from Blueprints.
- The trees ship in their own package (`camellia_landscape.glb`, 116 MB: one 1.15 M-polygon Poly Haven tree instanced 14 times) so they can be loaded, swapped for engine foliage or skipped independently.

## Cameras
- Still cameras are `CAM-<room>`; in the .blend, timeline markers at frames 2001-2029 bind one camera per frame.
- The walkthrough is `CAM-walkthrough` on `CRV-walkthrough` (frames 1-1080 at 24 fps, 45 s). The export script bakes the path and aim constraints to keyframes in the exported file; the .blend keeps the live constraints for editing.

## Lights
- Light powers are Blender watts and need exposure-relative rescaling in Unreal; keep the ratios (cans 15-66 W spots with a 125 degree cone, lamps 22-30 W points, chandeliers 55 W, sun strength 3.4).
- Two Cycles-only settings to mirror in engine: glass and lamp-shade meshes do not cast shadows (so sun and bulbs light the rooms), and lights are hidden from camera and reflection rays.
- Sun: 6 degrees elevation, behind the house and slightly left as seen from the front. Sky: Blender's multiple-scattering sky at strength 0.13 (replace with Sky Atmosphere at a matching sun angle).

## FBX
Not written by default. For FBX, export the same collections with scale 1.0, "Apply Scalings: FBX All", forward -Y, up Z, and bake the walkthrough camera first (the export script shows the bake call).
