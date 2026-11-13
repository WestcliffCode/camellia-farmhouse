STATUS: COMPLETE — house built, furnished, lit from a captured golden-hour sky, rendered and exported; audits and quality checks pass (2026-11-13).

# Handoff

## What exists
- `project-files/camellia-farmhouse.blend` — the whole house: structure, openings, roof and porches, materials, millwork, furniture in every room (garage, storage rooms and closets included), golden-hour lighting, 29 room and exterior cameras, 4 close-up cameras, 4 orthographic elevation cameras and a walkthrough rig, trees. Textures are external in `project-files/textures/` (git-ignored; Poly Haven sets are CC0 and re-downloadable by asset id, generated and baked textures are rewritten by the scripts).
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
   - `materials.py` needs the Poly Haven texture sets already imported (ids in DESIGN_SYSTEM.md, including `marble_01`, `beige_wall_001` and `rubber_tiles`); `lighting.py` needs the HDRI `magalies_field_sunset` imported (it falls back to a procedural sky if missing); `furnish_rooms.py` and `landscape.py` need the Poly Haven models imported (ids in `furnish_lib.PH_ASSETS`, plus `tree_small_02`). Import with `mcp__blender__import_asset`, then run `externalize_images()` from `bl_common.py`.
   - `furnish_rooms.py` defines a function named `R`; don't keep a path in a variable called `R` when exec-ing scripts in a loop.
4. Walkthrough preview: `Blender -b project-files/camellia-farmhouse.blend -P scripts/render_walkthrough.py -- 640 48 2 output/renders/walkthrough/frames`, then `ffmpeg -framerate 12 -pattern_type glob -i 'output/renders/walkthrough/frames/walk_*.jpg' -vf fps=24 -c:v libx264 -pix_fmt yuv420p output/renders/walkthrough/camellia_walkthrough_preview.mp4`.
4b. Background renders: `Blender -b project-files/camellia-farmhouse.blend -P scripts/render_stills.py -- --cams all --pct 100 --samples 256 --out output/renders/final`. Review with `scripts/contact_sheet.py`. Walkthrough samples: `scripts/render_walk_samples.py`.
5. Export: `Blender -b project-files/camellia-farmhouse.blend -P scripts/export_glb.py`.

## Timeline
- Frames 1–1080 (24 fps): `CAM-walkthrough` follows `CRV-walkthrough` from the foyer through family room, kitchen, dining, mudroom arch and primary hall into the primary suite.
- Frames 2001–2033: one still camera per frame (markers bind them); frames 2101–2104: the four elevation cameras. `render_stills.py` sets the camera directly.

## Checks done (all re-runnable)
- Geometry against the plan: room areas match plan labels within a few percent (game room 29.15 vs 29.1 m², garage 75.3 vs 74.1, primary suite 23.4 vs 23.9, bedroom 3 16.6 vs 16.7). Every room is reachable through a door or opening.
- Roof against the elevation sheets: orthographic front, back, left and right renders (`output/renders/contact_elevations.png`) compared side by side with the drawings; ridge heights 9.2 / 8.5 / 8.6 m against 9.35 / 8.5 / 8.4 m scaled from the drawings.
- Nothing overhead but ceilings: ray test from 5,045 points across every room, and 1,800 points in the bonus room.
- Furnishing audit (`scripts/audit_furnishing.py` → `output/furnishing_audit.md`): per-room inventory; no Poly Haven instance has a footprint corner inside a wall; no modeled piece touches into a wall (zero flags); 89% of the modeled furniture's surface carries Poly Haven photographic textures or the generated artwork (artwork is about 1%; the rest is porcelain, metal, glass and lamp shades); every material on the furniture comes from the design-system palette. Wall-backed pieces are snapped to the built wall faces.
- Materials: every `MAT-` material is one Principled BSDF with image textures or plain values (node-type audit returns no exceptions); every `GEO-` mesh has UVs.
- Lighting (`output/lighting_verification.txt`): sky is the captured Poly Haven sunset HDRI `magalies_field_sunset`; its sun (4.1 degrees) was located in the image and the sun lamp aligned with it; the sun lamp's colour is measured from the sun disc in the same photograph; a sweep of sun directions (`scripts/sun_coverage.py`) shows the chosen one (28 degrees west of the back axis) gives the most direct sun indoors, including the office and bedroom 4, and that no direction lights every room; a ray test shows direct sun in 12 rooms; the sun's 4.1 degrees sits inside the conventional golden-hour band (6 degrees above to 4 below the horizon).
- Lighting against its reference (`scripts/hdri_reference_strip.py` + `scripts/lighting_reference_board.py` → `output/renders/lighting_reference_board.png`, `output/lighting_reference.md`): the captured sky panorama beside six renders under the same view transform and exposure; the hue of the sunlit patches in all six is within 6 degrees of the hue of the photographed sun and its glow. `scripts/lighting_cards.py` adds neutral grey cards rendered on the lawn (sun-facing card hue 23 against the photographed sun's 24; shade-facing card near neutral) and three interiors rendered with every lamp off.
- Two lighting presets (`output/lighting_verification.txt`): sunset (default; sun behind the house, used for all main renders and the walkthrough) and sunrise (`LGT-sun_sunrise` + `WORLD-camellia_sunrise`, stored switched off; `render_stills.py --preset sunrise`). All 16 rooms with exterior glazing get direct sun in at least one (24 of the plan's 34 rooms in all; the other 10 are windowless closets, storage, powder, WC and hall); sunrise renders are in `output/renders/final_sunrise/`.
- Camera rig (`scripts/check_camera_rig.py` → `output/camera_rig_check.md`): 37 still cameras each bound to a marker frame, clear of geometry and aimed at a surface; walkthrough evaluated on all 1080 frames: inside the footprint throughout, at least 0.26 m from any surface, no segment crossing geometry, largest step 2.9 cm.
- Render quality (`scripts/render_qc.py` → `output/render_qc.md`): all 33 room, exterior and detail renders pass a stated bar for mean luminance, clipped highlights, crushed shadows and warmth.
- Walkthrough: rendered end to end as an MP4 (540 frames at 640×360, 45 s), tracked in the repository; path checks are under Camera rig above.
- Export (`scripts/validate_glb.py` → `output/glb_validation.txt`): all 23 GLBs re-import in an empty scene with meshes, UVs, textures, transmissive glass, cameras, lights and the baked walkthrough animation.

## Design decisions on record
- Roof: built from the four elevation sheets and checked against them with orthographic renders (`output/renders/contact_elevations.png`, `output/renders/elevation_check/`). Side-gabled main block on a 14 ft plate (ridge 9.2 m); north-south wing roofs with trussed gables; east-west upper wing roofs behind them (ridge 8.5 m, gable ends facing sideways); brick front gables; portico cross gable over the foyer vault; two front dormers; the tall rear north-south roof over the dining and service wing (ridge 8.6 m) with its back gable behind the outdoor chimney; bonus-room shed dormer; lean-to porch roofs; two chimneys.
- Back gables: plan and back elevation agree and the model matches both. Seen from behind, the left gable is the primary suite with two flanking windows and the right gable is the game room with a triple window. (An earlier note here claimed a mismatch; that was a mirror-reading error.)
- Furniture sources: Poly Haven models wherever a clean one exists (armchairs, lounge chairs, an ottoman, dining chairs, coffee, side and round tables, shelving, media cabinet, plants, vases, books, bowls, framed prints and standing frames, brass cookware, pendants, ceiling fans, trees, and the leather sofas in the game and bonus rooms): 98 placements of 28 assets. Poly Haven has only five sofas (all vintage; the tufted leather one is used where leather seating already sets the tone) and no beds, cabinetry, appliances or plumbing fixtures in this style, so those are modeled here: the fabric sofas in the family room, bonus room and outdoor living and channel-headboard beds upholstered in Poly Haven linen and herringbone wool, lathed hollow tubs, vessel basins and toilets, framed cabinetry, range, hood and refrigerator.
- Closet doors are closed except the linen and bedroom-4 storage doors, which are shown open.
- Owner decisions, 2026-11-13: the 10 rooms the plan draws without windows (closets, storage, linen, powder, primary WC, primary hall) stay as planned, lit by ceiling lights only, with no added skylights and no doors staged open; the sunrise sun stays at 152 degrees rather than turning east toward the primary bath, closet and utility.
- The plan set has a main floor and a bonus room; both are modeled in full. The plans draw no basement level (only a door labelled for it), so there is no basement.

## NEXT STEP
Nothing is owed. Optional polish: richer bath fixtures, window casings, more decor, a full-resolution walkthrough render.

## Log
- 2026-11-13 (eleventh pass): Poly Haven tufted leather sofa (`sofa_02`) replaces the modeled sofa in the game room and the second sofa in the bonus room (98 placements of 28 assets); sun coverage recounted at full room height (24 of 34 rooms get direct sun in one preset or the other; the other 10 have no windows on the plan).
- 2026-11-13 (tenth pass): second lighting preset added (sunrise: sun in front of the house) so every glazed room gets direct golden-hour sun in one preset or the other, with 12 views rendered under it; same-material sun-against-shade measurement added to the lighting reference; camera rig check script added (it found the four elevation cameras without markers; fixed).
- 2026-11-13 (ninth pass): sun turned to 28 degrees west of the back axis so it reaches the office and bedroom 4 (12 rooms with direct sun); 14 more Poly Haven pieces placed (framed prints, standing frames, vases, brass cookware on the range, an ottoman): 96 placements of 27 assets; grey-card and lamps-off lighting measurements added to the reference board; bonus-room cans raised after the view fell under the brightness bar; everything re-rendered, re-exported and re-validated.
- 2026-11-13 (eighth pass): counters, painted cabinetry and millwork, and garage mats moved from plain values to Poly Haven texture sets (89% of furniture surface now textured, up from 68%); sun lamp colour taken from the HDRI's sun; lighting reference board and per-room sun coverage script added; all stills and the walkthrough re-rendered; GLBs re-exported and re-validated.
- 2026-11-13 (seventh pass): last three wall contacts removed (audit at zero); sun coverage checked against glazing orientation; golden-hour band check recorded.
- 2026-11-13 (sixth pass): furnishing audit added and its findings fixed (primary bath vanity and mirrors were set into the wall; curtains and shower tile clamped to walls); render quality check added and garage, office, outdoor living and primary suite lighting raised until every view passes; four close-up cameras added.
- 2026-11-13 (fifth pass): sky switched to the captured golden-hour HDRI with the sun lamp aligned to its measured sun; back-gable window note corrected; everything re-rendered.
- 2026-11-13 (fourth pass): added the east-west upper wing roofs from the front and side elevations (clipped to the valleys of the lower wing roofs); measured the lighting; exteriors and elevations re-rendered; GLBs re-exported.
- 2026-11-13 (third pass): added the tall rear north-south roof shown on three elevation sheets; rebuilt sofas, beds, tubs, basins and toilets with cushion and lathe geometry and Poly Haven textiles; ceiling fans; trees added to the export set.
- 2026-11-13 (second pass): garage, storage rooms, linen closet, pantry goods and hall runners added; all materials rebuilt as image-based Principled (tints baked); cans converted to spot lights so the rig exports; sun lowered to 6 degrees with a dusk sky; walkthrough path checked and rendered.
- 2026-11-13: Gate A passed; Stages 3–8 built and checked. Final pass fixed a roof band crossing the kitchen tray and batten strips inside the bonus dormer; all 27 stills re-rendered from the saved file. Contact sheets: `output/renders/contact_*.png`.
