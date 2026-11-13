# Camellia Farmhouse — Design System

Source of truth: floorplan and elevations. Style reference: the exterior renders and the (unfurnished) interior photos.

## Character
Modern farmhouse: buff brick and near-black board-and-batten outside, calm white rooms with light oak, limestone and black metal inside, two charcoal rooms (primary suite, office) for contrast. Furniture is transitional: clean silhouettes, natural linen and wool, warm leather, oak and black steel. Nothing ornate, nothing glossy.

## Palette
| Role | Colour (linear RGB) | Where |
| --- | --- | --- |
| Wall white | 0.86, 0.85, 0.82 | all rooms unless noted |
| Charcoal | 0.075, 0.08, 0.085 | primary suite, office, powder room |
| Trim white (semi-gloss) | 0.90, 0.90, 0.88 | doors, casings, base, crown, stools |
| Siding black | 0.04, 0.042, 0.045 | board-and-batten, garage doors |
| Black metal | 0.012 | window and door frames, hardware, light fittings |
| Brass | 0.78, 0.57, 0.27 | kitchen and bath taps |
| Accent textiles | sage, oatmeal, rust, navy (one per room, small doses) | cushions, throws, rugs |

## Material schedule (Poly Haven ids, all CC0)
| Material | Source | Real-world tile | Used on |
| --- | --- | --- | --- |
| MAT-floor_oak | `oak_wood_planks` (lightened) | 1.5 m | all living, bed and hall floors, stair treads |
| MAT-tile_marble | `floor_tiles_04` | 2.4 m | baths, powder, utility floors, shower walls |
| MAT-limestone | `concrete_brick_wall_001` (lightened) | 2.4 m | fireplaces |
| MAT-brick | `brick_wall_003` | 3.2 m | wainscot, front gables, portico, chimneys |
| MAT-roof_shingle | `roof_slates_03` (darkened) | 3.0 m | roofs |
| MAT-concrete | `concrete_floor` (desaturated) | 2.08 m | slab, porches, garage floor, paving |
| MAT-oak / MAT-timber / MAT-oak_ceiling | `oak_veneer_03` | 1.0 m | cabinetry, beams, mantels, shelves, posts, porch ceilings |
| Procedural | — | — | paints, quartz, metals, glass, porcelain, lawn |

All meshes built by the scripts carry world-scale box UVs in metres (`UVMap`), so a material's Mapping scale is 1 / tile size. Textures live in `project-files/textures/` and are referenced relatively.

## Geometry rules
- Ceiling 3.048 m; doors, windows and cased openings head at 2.44 m; arched openings 2.6–2.75 m.
- Base 0.14 m, crown 0.11 m, casing 0.09 m, all trim white. Charcoal rooms get panel moulding painted wall colour.
- Counters 0.915 m, vanities 0.86 m, island seating overhang 0.3 m, bed platform 0.45 m, seat height 0.45 m, dining table 0.75 m.
- Walk paths stay at least 0.9 m clear. Rugs sit 0.3–0.45 m off walls; front sofa legs on the rug.

## Lighting philosophy
- Golden hour: low sun (about 8°) from behind the house, raking through the family room, kitchen, dining and primary suite glazing; cool sky fill from the front.
- Practicals at 2700–3000 K: recessed cans on a grid, pendants over the island, chandeliers in foyer and dining, table and floor lamps in every sitting and sleeping room, under-cabinet strips in the kitchen.
- AgX view transform; exposure set so the window view holds detail and rooms stay readable without flat fill.

## Naming
`GEO-` meshes, `MAT-` materials, `LGT-` lights, `CAM-` cameras, `COL-` collections; furniture collections are `COL-furn_<room>`; Poly Haven imports keep their asset id in the object name.
