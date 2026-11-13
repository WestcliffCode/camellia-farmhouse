STATUS: COMPLETE — all stages built; every room furnished; golden-hour lighting; 29 stills and the walkthrough rendered and reviewed; 22 GLBs exported and validated (2026-11-13).

# Handoff

## What exists
- `project-files/camellia-farmhouse.blend` — the whole house: structure, openings, roof and porches, materials, millwork, furniture in every room (garage, storage rooms and closets included), golden-hour lighting, 29 still cameras and a walkthrough rig, trees. Textures are external in `project-files/textures/` (git-ignored; Poly Haven sets are CC0 and re-downloadable by asset id, generated and baked textures are rewritten by the scripts).
- `output/renders/final/` — 1920×1080 Cycles renders of every still camera; `output/renders/contact_*.png` are the review sheets.
- `output/renders/walkthrough/camellia_walkthrough_preview.mp4` — the walkthrough rendered at review quality (640×360, every second frame).
- `project-files/export/` — 22 GLB packages (git-ignored; regenerate with `scripts/export_glb.py`, check with `scripts/validate_glb.py`). See `UNREAL_EXPORT.md`.
- `DESIGN_SYSTEM.md` — palette, material schedule, geometry and lighting rules.

## Conventions
- Blender is driven only through the community MCP (`mcp__blender__*`).
- Units metres. Origin at the front-left exterior corner, +X to the right (garage side), +Y toward the back, floor z = 0. Ceiling 3.048 m.
- Style: modern farmhouse per plans, elevations and exterior renders (the "New England / colonial revival" wording was dropped by the owner). Plan is the source of truth; photos are loose reference.
- Naming: `GEO-`, `MAT-`, `LGT-`, `CAM-`, `COL-`; furniture collections `COL-furn_<room>`; Poly Haven instances are empties named `INST-<asset id>` instancing collections parked in `COL-assets_src` (excluded from the view layer).

## Rebuild pipeline (each script wipes only what it owns)
1. Trace (only if the plan image changes): `scripts/trace/wallmask.py` → `scripts/trace/vectorize.py` → copy `trace_raw.json` into `scripts/trace/`.
2. `uv run --with shapely python scripts/plan_data.py` → `scripts/structure.json`.
3. In Blender, `exec(open("<repo>/scripts/<name>.py").read())` in this order:
   `build_structure` → `build_openings` → `build_shell` → `build_exterior` → `materials` → `millwork` → `furnish_rooms` → `lighting` → `cameras` → `landscape`.
   - `materials.py` needs the Poly Haven texture sets already imported (ids in DESIGN_SYSTEM.md); `furnish_rooms.py` and `landscape.py` need the Poly Haven models imported (ids in `furnish_lib.PH_ASSETS`, plus `tree_small_02`). Import with `mcp__blender__import_asset`, then run `externalize_images()` from `bl_common.py`.
   - `furnish_rooms.py` defines a function named `R`; don't keep a path in a variable called `R` when exec-ing scripts in a loop.
4. Walkthrough preview: `Blender -b project-files/camellia-farmhouse.blend -P scripts/render_walkthrough.py -- 640 48 2 output/renders/walkthrough/frames`, then `ffmpeg -framerate 12 -pattern_type glob -i 'output/renders/walkthrough/frames/walk_*.jpg' -vf fps=24 -c:v libx264 -pix_fmt yuv420p output/renders/walkthrough/camellia_walkthrough_preview.mp4`.
4b. Background renders: `Blender -b project-files/camellia-farmhouse.blend -P scripts/render_stills.py -- --cams all --pct 100 --samples 256 --out output/renders/final`. Review with `scripts/contact_sheet.py`. Walkthrough samples: `scripts/render_walk_samples.py`.
5. Export: `Blender -b project-files/camellia-farmhouse.blend -P scripts/export_glb.py`.

## Timeline
- Frames 1–1080 (24 fps): `CAM-walkthrough` follows `CRV-walkthrough` from the foyer through family room, kitchen, dining, mudroom arch and primary hall into the primary suite.
- Frames 2001–2029: one still camera per frame (markers bind them). `render_stills.py` jumps to the right frame per camera.

## Checks done
- Room areas match plan labels within a few percent (game room 29.15 vs 29.1 m², garage 75.3 vs 74.1, primary suite 23.4 vs 23.9, bedroom 3 16.6 vs 16.7).
- Every room reachable through a door or opening; every room has furniture or fitted storage.
- No roof geometry intrudes below any ceiling (numeric test over the roof mesh, plus a ray test over the kitchen tray).
- Materials: every `MAT-` material is one Principled BSDF with image textures or plain values (node-type audit returns no exceptions); every `GEO-` mesh has UVs.
- Walkthrough: camera stays inside the footprint for all 1080 frames with at least 0.30 m to the nearest surface; rendered end to end as an MP4.
- Export: all 22 GLBs re-imported in an empty scene; meshes, UVs, textures, transmissive glass, 30 cameras, 180 lights and the baked walkthrough animation survive.
- All 29 still cameras rendered at 1080p and reviewed. Defects found and fixed along the way: roof slabs inside the foyer vault, primary bath, closet and kitchen tray; batten strips showing inside vaulted rooms and the bonus dormer; cameras blocked by furniture; dark bonus and storage rooms; rolled cameras; material slots lost on rebuild; daylight-looking sky retuned to a 6 degree golden-hour sun with dusk sky.

## Design choices and limits (for whoever refines it)
- Roof is a designed approximation of the elevations, not a framing-accurate model; valleys are overlapping slabs.
- Primary suite back wall follows the plan (two end windows); the back elevation shows a triple window.
- Poly Haven has no clean transitional sofas, beds, cabinetry, appliances or plumbing fixtures, so those are built procedurally to the design system; Poly Haven supplies chairs, tables, shelving, plants, vases, books, pendants and all photographic textures.
- Closet doors are closed except the linen and bedroom-4 storage doors, which are shown open.
- Trees are one Poly Haven species instanced 14 times and are left out of the GLB export on purpose.
- Basement is not on the plans and is not modeled.

## NEXT STEP
Nothing is owed. Optional polish: richer bath fixtures, window casings, more decor, an HDRI backdrop, a rendered walkthrough animation.

## Log
- 2026-11-13 (second pass): garage, storage rooms, linen closet, pantry goods and hall runners added; all materials rebuilt as image-based Principled (tints baked); cans converted to spot lights so the rig exports; sun lowered to 6 degrees with a dusk sky; walkthrough path checked and rendered.
- 2026-11-13: Gate A passed; Stages 3–8 built and checked. Final pass fixed a roof band crossing the kitchen tray and batten strips inside the bonus dormer; all 27 stills re-rendered from the saved file. Contact sheets: `output/renders/contact_*.png`.
