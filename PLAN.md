# Camellia Farmhouse — Build Plan

Status: **DRAFT, awaiting review.** Nothing is modeled yet. This file becomes the live checklist once approved; `HANDOFF.md` carries resume context after every stage.

## 1. What the references say

**Plans (source of truth)** — `plans/plans_main-floor.webp`, `plans_main-floor-2.webp` (same plan, two crops), `plans_bonus-room.webp`, four elevation sheets.

Single-storey house, roughly 95 ft wide, with a bonus room over the garage. The kitchen/pantry wing sits at 45° to the rest of the plan.

| Zone | Rooms (plan dimensions, ceiling) |
| --- | --- |
| Entry | Front Porch 35'8"×7'0" · Foyer 11'0"×14'8" (vault off 14') · Office 12'6"×14'4" (10', boxed to 11') |
| Core | Family Room 22'9"×21'0" · Kitchen 21'2"×16'0" (boxed to 11', 45°) · Pantry 21'2"×7'0" (45°) · Dining 14'0"×21'0" · coffee bar · hutch/wine niche |
| Primary wing | Primary Suite 17'2"×15'0" (vault off 10', fireplace) · Primary Bath (double vanity, freestanding tub, shower, WC, linen) · Closet 14'0"×8'0" |
| Service | Family Foyer/mudroom 5'8"×16'5" · Utility 11'3"×9'0" · 3-Car Garage 24'0"×33'3" · basement door (basement itself not drawn) |
| Bedroom wing | Bedroom 2 12'6"×12'0" · Bedroom 3 12'0"×15'0" · Bedroom 4 11'8"×13'0" · Game Room 15'8"×20'0" (vault) · hall bath · powder room · Jack-and-Jill bath · Holiday closet 7'1"×6'5" · closets 8'4"×4'0", 7'8"×6'7" |
| Outdoor | Back Porch 9' deep · Outdoor Living 25'4"×14'9" with fireplace |
| Upper | Stair up → Bonus Room 14'7"×33'3" (vault 4' to 9', 8' dormer with window seat) |

**Elevations** — brick lower walls and gable fronts, dark board-and-batten above, dark shingle roof with two dormers, standing-seam porch roofs, timber gable trusses and porch brackets, arched steel-and-glass entry doors, two brick chimneys, large sliders across the back.

**Photos (loose reference only)** — the house is photographed empty: wide-plank light oak floors, white walls and crown, limestone fireplace with oak mantel and floating shelves, oak-and-white kitchen with quartz tops and oak beams in the boxed ceiling, arched openings, a barrel-vaulted foyer with ring chandelier, charcoal panel-moulded walls in the primary suite and office.

## 2. Decisions I am making (change any before I start)

1. **Style reconciliation.** The plans and elevations are a modern farmhouse, not shingle-style or colonial revival. Because the plans are the source of truth, the exterior follows the elevations as drawn. The "affluent New England estate" brief drives the interiors: refined transitional furniture, warm woods, soft neutrals, quality textiles, on the bones the photos show.
2. **Scope.** Whole main floor, bonus room and stair, porches and outdoor living, garage as a finished shell. Basement is excluded (door only). Site is a lawn, entry walk and driveway apron; no pool, no landscaping beyond a few plants.
3. **Units and origin.** Metres, 1 unit = 1 m, plan dimensions converted from feet-inches. Origin at the front-left exterior corner, +Y toward the back of the house, floor at z = 0.
4. **Sun.** The back of the house faces the low sun, so golden-hour light rakes through the family room, dining and primary suite windows.
5. **Engine.** Cycles on the M4 Max GPU (Metal) with denoising. Previews 960×540; finals 1920×1080 at 512 samples or fewer.
6. **Furniture reality.** Poly Haven has about 350 furniture-type models and they skew vintage, worn and Gothic. Clean transitional sofas and beds, all kitchen cabinetry and appliances, and all plumbing fixtures will be procedural. Poly Haven supplies textures everywhere, the HDRI, and the furniture and decor pieces that fit the style.
7. **Public repo.** The GitHub repo is public and the reference photos and plans are third-party marketing material, so the reference folders are git-ignored and stay local. Scripts, docs and check renders are pushed.
8. **Commits.** Straight to `main` at each stage gate (no PR flow for this project). The `.blend` is committed only while it stays under 95 MB (GitHub's limit is 100 MB and git-lfs is not installed); textures stay external in `project-files/textures/` and are ignored.

## 3. Stages and gates

Hard rule from the brief: **no furnishing, texturing, lighting or rendering until Gate A passes.**

### Stage 1 — Analysis and design system
- [ ] Trace the plan: load it as a top-view reference, calibrate scale against at least six labelled room dimensions, record every wall segment, opening, door and window in `scripts/plan_data.py`
- [ ] Reconcile conflicts between labelled dimensions and drawn geometry (labels win; log each in HANDOFF.md)
- [ ] Write `DESIGN_SYSTEM.md`: palette, material schedule, furniture scale rules, lighting philosophy, naming and collection conventions

### Stage 2 — Architectural structure (`scripts/build_structure.py`, rebuildable)
- [ ] Slab and floor plates per room
- [ ] Exterior walls (2×6, ~0.165 m) and interior walls (2×4, ~0.115 m) from the traced segments, including the 45° wing
- [ ] Door and window openings cut; arched openings where the photos show them
- [ ] Windows (frames, mullions, glass) and doors (panel, arched steel entry, sliders, garage doors), interior doors left ajar so every room is reachable
- [ ] Ceilings: 10' flat; boxed 11' in kitchen and office; vaults in primary suite, game room, foyer (barrel vault per photo) and bonus room
- [ ] Stair to bonus room, bonus room shell and dormer
- [ ] Fireplaces: family room, primary suite, outdoor living; chimneys
- [ ] Porches, columns, timber brackets and gable trusses
- [ ] Roof: main gables, front gables, dormers, porch roofs, fascia

**Gate A — structure complete**
- Top-down orthographic view overlaid on the plan: walls within 5 cm of traced positions
- Every room's interior dimensions within 2% of the plan label
- A 1.6 m eye-height camera placed in every room sees a door opening; no sealed rooms
- Clay views of all four sides compared against the four elevation sheets
- No wall, floor or ceiling gaps visible from inside any room
- Save, commit, push, update HANDOFF.md

### Stage 3 — Architectural materials and fixed millwork
- [ ] Poly Haven PBR sets at 2k (4k for hero floors): oak plank floor, painted walls, tile in baths and utility, limestone, brick, board-and-batten, shingles, standing-seam metal, concrete
- [ ] UVs at real-world scale so nothing stretches or tiles visibly
- [ ] Baseboards, crown, door and window casings, panel moulding in primary suite and office
- [ ] Kitchen: perimeter cabinets, island, hood, range, fridge, sink, quartz tops, ceiling beams; pantry and coffee bar shelving
- [ ] Baths: vanities, mirrors, tub, showers, toilets; utility counters, washer and dryer; closet systems; mudroom bench and hooks; fireplace surrounds, mantels, floating shelves

**Gate B** — material-preview views of every room and all four exterior sides: no missing or pink materials, no stretched textures, grain and plank direction sensible. Save, commit, push.

### Stage 4 — Furnishing
- [ ] Asset manifest (`scripts/furnish_manifest.json`): Poly Haven id, target size, room, transform; every download recorded
- [ ] Room by room in priority order: family room, kitchen, dining, foyer, primary suite, primary bath, office, bedrooms 2–4, game room, bonus room, baths, utility, mudroom, closets, outdoor living, porches, garage
- [ ] Rugs, curtains, bedding, art, books, plants and lamps so no room reads as staged-empty

**Gate C** — per-room checks: nothing floating or intersecting, clearances of at least 0.9 m on walk paths, furniture at real-world scale against a 1.8 m reference. Save, commit, push.

### Stage 5 — Lighting
- [ ] Sky: Nishita sun at low elevation (about 6–10°) from the back of the house, or a Poly Haven golden-hour HDRI if it reads better in tests
- [ ] Practicals: recessed cans, lamps, chandeliers, pendants, under-cabinet strips, sconces, all warm (2700–3000 K)
- [ ] AgX view transform, exposure balanced so windows hold detail and interiors are not flat

**Gate D** — 960×540 Cycles previews of the eight key rooms: readable sun patches, no blown-out or black rooms, no light leaks at wall and ceiling joints.

### Stage 6 — Camera rig
- [ ] One named still camera per room (18–24 mm, 1.5 m height, verticals upright) plus front, back and twilight exterior heroes
- [ ] Walkthrough: camera on a path from the front walk through foyer, family room, kitchen, dining and primary suite, with timeline markers binding cameras

### Stage 7 — QA renders and fixes
- [ ] 1920×1080 finals of key views: exterior front, foyer, family room, kitchen, dining, primary suite, primary bath, office
- [ ] Previews of every remaining camera
- [ ] Up to four fix passes; anything still wrong is listed in HANDOFF.md
- Long renders run in a background Blender process so the live session stays responsive

### Stage 8 — Export and delivery
- [ ] GLB exports per collection (structure, millwork, furniture per zone) in `project-files/export/`, textures alongside
- [ ] `UNREAL_EXPORT.md`: scale, axis, collision, lightmap UV and material notes
- [ ] Final save, HANDOFF.md with what was built, what was checked and what remains imperfect; commit and push

## 4. File layout

```
PLAN.md  DESIGN_SYSTEM.md  HANDOFF.md  UNREAL_EXPORT.md
scripts/            plan_data.py, build_structure.py, materials.py, furnish.py, lighting.py, cameras.py
project-files/      camellia-farmhouse.blend, textures/ (ignored), export/
output/checkpoints/ gate screenshots        output/renders/ final and preview renders
plans/ exterior/ <room folders>/            references, local only
```

## 5. Running unattended

- **Saves.** The `.blend` is saved after every sub-stage; a separate copy is kept at each gate.
- **Resume context.** HANDOFF.md is rewritten after every stage, so a compacted or fresh session can continue from the checklist.
- **Blockers.** Missing Poly Haven asset → procedural substitute. Failed download or import → retry once, then substitute and log. A defect that survives two fix attempts → different approach, logged. Nothing in the existing references or outside this folder is deleted or overwritten.
- **Usage limit.** I cannot wake myself once the usage window is exhausted. With your approval I will create an hourly scheduled task that opens a fresh session, checks a heartbeat file so it never runs alongside a live session, and resumes from HANDOFF.md. It only fires while the Claude app is open, and each run starts with no memory beyond the files here.
- **Sleep.** I will ask the app to keep the Mac awake; a closed lid still sleeps it.
- **Blender crash.** If Blender itself quits I can relaunch it, but I have not verified that the MCP add-on restarts its server without a click. If it does not, work stops at the last save.

## 6. Honest expectations

By morning this should be a complete, correctly proportioned, fully walkable house with materials, furniture in every room, golden-hour lighting, cameras and check renders. The core rooms get the most polish. It will read as a solid archviz scene to refine, not a finished magazine render in every room: procedural sofas, beds and fixtures are tidy but simple, and the furnishing is my design since the photos show an empty house.
