STATUS: IN PROGRESS — Gate A (architectural structure) PASSED. Stage 3 (materials + millwork) is next.

# Handoff

## Conventions
- Blender is driven only through the community MCP (`mcp__blender__*`). File: `project-files/camellia-farmhouse.blend`.
- Units metres. Origin at the front-left exterior corner, +X to the right (garage side), +Y toward the back, floor z = 0. Ceiling 3.048 m (10 ft).
- Style: modern farmhouse per plans, elevations and exterior renders (the earlier "New England / colonial revival" wording is void, per the owner). Plan is the source of truth; photos are loose reference.
- Naming: `GEO-`, `MAT-`, `LGT-`, `CAM-`, `COL-` prefixes. Object names carry material roles (`GEO-winframe_*`, `GEO-glass_*`, `GEO-doorleaf_*`, `GEO-jamb_*`, `GEO-doorhw_*`, `GEO-garagedoor_*`, `GEO-ceiling_<room>`).
- Every stage is a rebuildable script run inside Blender with
  `exec(open("<repo>/scripts/<name>.py").read())`. Each script wipes only the collection it owns.

## Pipeline (run in this order to rebuild from scratch)
1. `uv run --with opencv-python-headless --with numpy python scripts/trace/wallmask.py plans/plans_main-floor.webp output/tmp 6`
   then `scripts/trace/vectorize.py plans/plans_main-floor.webp output/tmp/wallmask.png output/tmp` → copy `output/tmp/trace_raw.json` to `scripts/trace/` (already committed; only needed if the plan image changes).
2. `uv run --with shapely python scripts/plan_data.py` → `scripts/structure.json` (walls, openings, rooms, footprint in metres). Curation of the trace (dropped/added walls, opening types, room seeds) lives in this script. Set `PLAN_DEBUG=path.png` (needs opencv) for a debug picture.
3. In Blender: `build_structure.py` (COL-structure: GEO-walls, GEO-slab, COL-ceilings) → `build_openings.py` (COL-openings: windows, doors) → `build_shell.py` (COL-shell + special ceilings: foyer barrel vault, primary/game-room cathedral, kitchen and office trays, garage lid, stair, bonus-room shell) → `build_exterior.py` (COL-exterior: roofs, gable/upper walls, dormers, porches, chimneys).
- `scripts/bl_common.py` holds shared helpers (`PX()` px→m, `add_prism`, `add_profile`, `face_in`, `room()`, `room_bounds()`, `wipe_col`).
- Room names (from `structure.json`): great_room (family + kitchen + dining), foyer, office, primary_suite, primary_bath, primary_wc, primary_closet, primary_hall, family_foyer (mudroom), mud_vestibule, utility, garage, pantry, hutch_niche, linen, stair, bedroom_2/3/4, game_room, jj_bath_a/b, hall_bath, powder, holiday, storage_a/b, closet_b2/b3, bed_hall, bed_hall_s, back_vestibule, portico.

## Gate A evidence
- Room areas vs plan labels: game room 29.15 m² (label 29.1), garage 75.3 (74.1), primary suite 23.4 (23.9), bedroom 3 16.6 (16.7), office 16.0 (16.6). Footprint 27.2 × 26.1 m.
- Every room has at least one door or opening (only the dead triangular void by the stair has none).
- Exterior massing checked against the four elevation sheets from front, back, right and three-quarter views.

## Known simplifications / deviations
- Primary suite back wall has two end windows as drawn on the plan (the back elevation shows a triple window).
- Roof is a designed approximation of the elevations: main block side-gabled at a 14 ft plate, N-S wing gables, brick front gables, portico cross gable over the foyer vault, low lean-to roofs over the back porch and outdoor living.
- Basement is not modeled; the under-stair door is closed. Bonus room sits centred under the garage ridge with a stair alcove and an east shed dormer.
- The 45° kitchen/pantry walls were re-drawn by hand from the plan (see `plan_data.py`).

## NEXT STEP
Stage 3 in PLAN.md: `scripts/materials.py` (Poly Haven PBR sets, exterior cladding shell, per-room wall paint) and `scripts/millwork.py` (trim, kitchen, baths, fireplaces, built-ins). Then Stage 4 furnishing.

## Log
- Gate A passed 2026-11-13.
