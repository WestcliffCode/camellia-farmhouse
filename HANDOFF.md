STATUS: IN PROGRESS — all eight stages built; final check renders being reviewed.

# Handoff

## What exists
- `project-files/camellia-farmhouse.blend` — the whole house: structure, openings, roof and porches, materials, millwork, furniture in every room, lighting, 27 still cameras and a walkthrough rig, trees. Textures are external in `project-files/textures/` (git-ignored, CC0, re-downloadable from Poly Haven by asset id).
- `output/renders/final/` — 1920×1080 Cycles renders of every still camera. `output/renders/preview/` — half-size previews and walkthrough sample frames.
- `project-files/export/` — GLB packages (git-ignored; regenerate with `scripts/export_glb.py`). See `UNREAL_EXPORT.md`.
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
4. Background renders: `Blender -b project-files/camellia-farmhouse.blend -P scripts/render_stills.py -- --cams all --pct 100 --samples 256 --out output/renders/final`. Review with `scripts/contact_sheet.py`. Walkthrough samples: `scripts/render_walk_samples.py`.
5. Export: `Blender -b project-files/camellia-farmhouse.blend -P scripts/export_glb.py`.

## Timeline
- Frames 1–1080 (24 fps): `CAM-walkthrough` follows `CRV-walkthrough` from the foyer through family room, kitchen, dining, mudroom arch and primary hall into the primary suite.
- Frames 2001–2027: one still camera per frame (markers bind them). `render_stills.py` jumps to the right frame per camera.

## Checks done
- Room areas match plan labels within a few percent (game room 29.15 vs 29.1 m², garage 75.3 vs 74.1, primary suite 23.4 vs 23.9, bedroom 3 16.6 vs 16.7).
- Every room reachable through a door or opening.
- No roof geometry intrudes below any ceiling (numeric test over the roof mesh).
- All 27 cameras rendered and reviewed; defects found and fixed: roof slabs inside the foyer vault, primary bath and closet; batten strips showing inside vaulted rooms; three cameras blocked by furniture; dark bonus room; rolled cameras; material slots lost on rebuild.

## Known limitations (what to refine)
- Roof is a designed approximation of the elevations, not a framing-accurate model; valleys are overlapping slabs.
- Primary suite back wall follows the plan (two end windows); the back elevation shows a triple window.
- Sofas, beds, cabinets, appliances and bath fixtures are tidy procedural geometry (Poly Haven has no clean transitional versions). Tubs and sinks are simple ellipsoid forms.
- No interior window casings; no door stops or switch plates; cabinet doors are single-panel shaker.
- Hall bath camera is tight; some door leaves stand open into small rooms.
- Trees are one Poly Haven species (1.15 M polygons, instanced 14 times) and are not part of the GLB export.
- Basement not modeled. Garage is empty apart from shelving.
- Procedural materials (lawn, fabric bump, art, glass shadow trick) need rebuilding in a game engine; see UNREAL_EXPORT.md.

## NEXT STEP
Review the final renders, then mark complete. Optional polish: richer bath fixtures, window casings, more decor, an HDRI backdrop, a rendered walkthrough animation.

## Log
- 2026-11-13: Gate A passed; Stages 3–8 built and checked.
