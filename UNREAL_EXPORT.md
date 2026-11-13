# Export notes (Unreal Engine / other DCCs)

## What is exported
`project-files/export/` holds one GLB per package, written by `scripts/export_glb.py`
(`Blender -b project-files/camellia-farmhouse.blend -P scripts/export_glb.py`). The folder is git-ignored; re-run the script to regenerate it.

| File | Contents |
| --- | --- |
| `camellia_structure.glb` | walls, slab, ceilings, floors, stair, bonus-room shell, windows, doors, cladding battens |
| `camellia_millwork.glb` | base and crown, panel moulding, kitchen, coffee bar, pantry shelving, fireplaces, exterior timber |
| `camellia_exterior.glb` | roofs, gable walls, dormers, porches, chimneys, ground, paving |
| `camellia_furn_<room>.glb` | furniture and decor per room (Poly Haven instances are realised into meshes) |
| `camellia_cameras_lights.glb` | 27 still cameras, the walkthrough camera, all lights (punctual lights extension) |

## Conventions
- Units are metres; Blender is Z-up and the GLB is written Y-up. Import into Unreal with glTF import (Interchange): scale 100 (cm), no extra rotation.
- Origin is the front-left exterior corner of the house at finished-floor level, so every package drops in at 0,0,0 and lines up.
- All procedural meshes carry one UV set (`UVMap`) in real-world metres; tiling lives in the material's Mapping scale (1 / tile size, see `DESIGN_SYSTEM.md`). In Unreal set the material's UV tiling to the same value, or bake it into the UVs.
- No lightmap UVs are authored. Use Lumen, or let Unreal generate lightmap UVs on import (most meshes are boxes and flat panels, so auto-unwrap is clean).
- Materials are Principled BSDF with base colour, roughness and normal maps, plus plain colour/metal values, so they convert directly. Exceptions to rebuild by hand:
  - `MAT-glass`: mixes a transparent shader on shadow rays so sunlight passes in Cycles. Replace with a thin translucent glass material.
  - `MAT-lamp_shade`: diffuse + translucent mix. Use a two-sided foliage/subsurface shading model.
  - `MAT-grass`, `MAT-art_*`, fabric bump: procedural noise does not export. Assign engine materials or bake.
  - Hue/saturation tints on the Poly Haven sets (oak floor, brick, limestone, shingles, oak) are node adjustments. The GLB carries the untinted textures; apply the tint in the engine material or bake from Blender.
- Collision: use complex-as-simple for walls, floors and the stair; furniture can take auto convex hulls.
- Doors are separate objects with the origin on the hinge (`GEO-doorleaf_*`), ready to animate or to drive from Blueprints.

## Cameras
- Still cameras are `CAM-<room>`; timeline markers at frames 2001-2027 bind one camera per frame.
- The walkthrough is `CAM-walkthrough` on `CRV-walkthrough` (frames 1-1080 at 24 fps, 45 s) with a Track-To aim target riding the same path. Constraints do not export: bake the camera (Object > Animation > Bake Action, visual keying) before exporting it as animation, or rebuild it in Sequencer from the path.

## Lights
- Light powers are Blender watts. Unreal will need exposure-relative rescaling; keep the ratios (cans 8-22 W, lamps 22-30 W, chandeliers 55 W, sun strength 5.5).
- Sun: 11 degrees elevation, behind the house and slightly left as seen from the front. Sky: Blender's multiple-scattering sky at strength 0.22 (replace with Sky Atmosphere).

## FBX
Not written by default. For FBX, export the same collections with scale 1.0, "Apply Scalings: FBX All", forward -Y, up Z, and bake the walkthrough camera first.
