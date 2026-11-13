STATUS: COMPLETE — house built, furnished, lit, rendered and exported; 33 stills and the walkthrough reviewed; 23 GLBs validated (2026-11-13).

# Handoff

## What exists
- `project-files/camellia-farmhouse.blend` — the whole house: structure, openings, roof and porches, materials, millwork, furniture in every room (garage, storage rooms and closets included), golden-hour lighting, 29 room and exterior cameras, 4 orthographic elevation cameras and a walkthrough rig, trees. Textures are external in `project-files/textures/` (git-ignored; Poly Haven sets are CC0 and re-downloadable by asset id, generated and baked textures are rewritten by the scripts).
- `output/renders/final/` — 1920×1080 Cycles renders of every still camera; `output/renders/contact_*.png` are the review sheets.
- `output/renders/walkthrough/camellia_walkthrough_preview.mp4` — the walkthrough rendered at review quality (640×360, every second frame).
- `project-files/export/` — 23 GLB packages (git-ignored; regenerate with `scripts/export_glb.py`, check with `scripts/validate_glb.py`). See `UNREAL_EXPORT.md`.
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
- Frames 2001–2031: one still camera per frame (markers bind them). `render_stills.py` jumps to the right frame per camera.

## Checks done
- Room areas match plan labels within a few percent (game room 29.15 vs 29.1 m², garage 75.3 vs 74.1, primary suite 23.4 vs 23.9, bedroom 3 16.6 vs 16.7).
- Every room reachable through a door or opening; every room has furniture or fitted storage.
- No roof geometry intrudes below any ceiling (numeric test over the roof mesh, plus a ray test over the kitchen tray).
- Materials: every `MAT-` material is one Principled BSDF with image textures or plain values (node-type audit returns no exceptions); every `GEO-` mesh has UVs.
- Walkthrough: camera stays inside the footprint for all 1080 frames with at least 0.30 m to the nearest surface; rendered end to end as an MP4.
- Export: all 23 GLBs (trees included) re-imported in an empty scene; meshes, UVs, textures, transmissive glass, 34 cameras, 180 lights and the baked walkthrough animation survive (`output/glb_validation.txt`).
- Roof against drawings: orthographic front, back, left and right renders compared side by side with the elevation sheets; ridge heights 9.2 / 8.5 / 8.6 m against 9.35 / 8.5 / 8.4 m scaled from the drawings.
- Lighting measured in the scene (`output/lighting_verification.txt`): sun 6.0 degrees above the horizon behind the house; a ray test toward the sun shows direct light entering 11 rooms through the glazing.
- Ray test from 5,045 points across every room: nothing but ceilings and fittings overhead; 1,800 points in the bonus room: roof never below the interior ceiling.
- All 33 still cameras rendered at 1080p and reviewed (`output/renders/contact_*.png`). Defects found and fixed along the way: roof slabs inside the foyer vault, primary bath, closet and kitchen tray; batten strips showing inside vaulted rooms and the bonus dormer; cameras blocked by furniture; dark bonus and storage rooms; rolled cameras; material slots lost on rebuild; daylight-looking sky retuned to a 6 degree golden-hour sun with dusk sky.

## Design decisions on record
- Roof: built from the four elevation sheets and checked against them with orthographic renders (`output/renders/contact_elevations.png`, `output/renders/elevation_check/`). Side-gabled main block on a 14 ft plate (ridge 9.2 m); north-south wing roofs with trussed gables; east-west upper wing roofs behind them (ridge 8.5 m, gable ends facing sideways); brick front gables; portico cross gable over the foyer vault; two front dormers; the tall rear north-south roof over the dining and service wing (ridge 8.6 m) with its back gable behind the outdoor chimney; bonus-room shed dormer; lean-to porch roofs; two chimneys.
- Primary suite back wall follows the floorplan (two end windows), because the plan is the source of truth; the back elevation sheet draws a triple window there.
- Furniture sources: Poly Haven models wherever a clean one exists (armchairs, lounge chairs, dining chairs, coffee, side and round tables, shelving, media cabinet, plants, vases, books, bowls, pendants, ceiling fans, trees). Poly Haven has only five sofas (all vintage) and no beds, cabinetry, appliances or plumbing fixtures in this style, so those are modeled here: cushioned sofas and channel-headboard beds upholstered in Poly Haven linen and herringbone wool, lathed hollow tubs, vessel basins and toilets, framed cabinetry, range, hood and refrigerator.
- Closet doors are closed except the linen and bedroom-4 storage doors, which are shown open.
- The plan set has a main floor and a bonus room; both are modeled in full. The plans draw no basement level (only a door labelled for it), so there is no basement.

## NEXT STEP
Nothing is owed. Optional polish: richer bath fixtures, window casings, more decor, an HDRI backdrop, a rendered walkthrough animation.

## Log
- 2026-11-13 (fourth pass): added the east-west upper wing roofs from the front and side elevations (clipped to the valleys of the lower wing roofs); measured the lighting; exteriors and elevations re-rendered; GLBs re-exported.
- 2026-11-13 (third pass): added the tall rear north-south roof shown on three elevation sheets; rebuilt sofas, beds, tubs, basins and toilets with cushion and lathe geometry and Poly Haven textiles; ceiling fans; trees added to the export set.
- 2026-11-13 (second pass): garage, storage rooms, linen closet, pantry goods and hall runners added; all materials rebuilt as image-based Principled (tints baked); cans converted to spot lights so the rig exports; sun lowered to 6 degrees with a dusk sky; walkthrough path checked and rendered.
- 2026-11-13: Gate A passed; Stages 3–8 built and checked. Final pass fixed a roof band crossing the kitchen tray and batten strips inside the bonus dormer; all 27 stills re-rendered from the saved file. Contact sheets: `output/renders/contact_*.png`.
