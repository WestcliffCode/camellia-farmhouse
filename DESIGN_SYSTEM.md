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
| MAT-fab_*, MAT-curtain, MAT-towel | `rough_linen` dyed to palette colours | 0.27 m | sofas, beds, headboards, cushions, curtains, towels |
| MAT-rug_*, MAT-fab_grey, MAT-fab_char | `poly_wool_herringbone` dyed | 0.27-0.45 m | rugs, grey upholstery |
| MAT-leather_tan | `fabric_leather_01` | 0.4 m | stools |
| Value-only Principled | — | — | paints, quartz, metals, glass, porcelain (with a shared tileable noise normal map where texture is needed) |
| Generated textures | `TEX-lawn`, `TEX-art_*`, `TEX-noise_normal` (written by the scripts) | 9 m / 1.3-1.8 m / per material | lawn, artwork, surface grain |

All meshes built by the scripts carry world-scale box UVs in metres (`UVMap`), so a material's Mapping scale is 1 / tile size. Every `MAT-` material is one Principled BSDF fed only by image textures and plain values: colour tints and roughness changes on the Poly Haven sets are baked into new texture files, so nothing depends on procedural shader nodes. Textures live in `project-files/textures/` and are referenced relatively.

## Geometry rules
- Ceiling 3.048 m; doors, windows and cased openings head at 2.44 m; arched openings 2.6–2.75 m.
- Base 0.14 m, crown 0.11 m, casing 0.09 m, all trim white. Charcoal rooms get panel moulding painted wall colour.
- Counters 0.915 m, vanities 0.86 m, island seating overhang 0.3 m, bed platform 0.45 m, seat height 0.45 m, dining table 0.75 m.
- Walk paths stay at least 0.9 m clear. Rugs sit 0.3–0.45 m off walls; front sofa legs on the rug.

## Lighting philosophy
- Golden hour sliding into dusk, taken from a real capture: the sky is the Poly Haven HDRI `magalies_field_sunset` (clear-sky sunset over a dry field with bare trees), dimmed to strength 0.30 so it reads as dusk and supplies the horizon and treeline.
- The HDRI's sun was located in the image (4.1 degrees above the horizon) and the map rotated so it sits behind the house, slightly left as seen from the street. A sun lamp is aligned with it (deep orange 1.0, 0.48, 0.20, strength 4.2) to give crisp beams through the family room, kitchen, dining, game room and primary suite glazing.
- Practicals at 2700-3000 K carry the interiors: recessed cans (spot lights, 125 degree cone) on a grid, pendants over the island, ring chandeliers in foyer and dining, table and floor lamps in every sitting and sleeping room, under-cabinet spots in the kitchen, lanterns at the exterior doors.
- AgX view transform, exposure +0.6. Glass and lamp-shade objects are excluded from shadow rays so sun and bulbs light the rooms.

## Naming
`GEO-` meshes, `MAT-` materials, `LGT-` lights, `CAM-` cameras, `COL-` collections; furniture collections are `COL-furn_<room>`; Poly Haven imports keep their asset id in the object name.
