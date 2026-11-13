# Replacement shopping list

Every script-modeled soft furnishing, plumbing fixture and appliance in the scene, with the size it occupies now, so replacements can be bought to fit. Sizes are width × depth × height, inches first, metres in brackets. They come from the build scripts (`scripts/furnish_lib.py`, `scripts/furnish_rooms.py`, `scripts/millwork.py`).

A replacement within about 2 in (5 cm) of the listed width and depth drops in without moving anything else. Larger differences are fine; say so and I will shift the neighbouring pieces.

## How to hand models over

- Put files in `assets_incoming/` at the project root. That folder is git-ignored, so purchased models never reach the public repository.
- Name each file or folder after the slot id in the tables below, e.g. `sofa_family.blend` or `range_kitchen/`.
- Preferred formats, least rework first: `.blend`, then FBX / glTF / USD with their textures, then OBJ, then STEP. IFC and SketchUp work but look plainer. Revit `.rfa` needs converting before I can use it.
- Keep the texture folder next to the model. Orientation and origin do not matter; real-world scale helps but I will check it against the sizes here.

## Soft furniture

| Slot id | Room | Now | Size to fit | Qty | Notes |
|---|---|---|---|---|---|
| `sofa_family` | Family room | 3-seat track-arm sofa, oatmeal linen | 102 × 37 × 36 in (2.60 × 0.95 × 0.92 m) | 1 | Back to the kitchen side, facing the fireplace. Seat height 20 in. The hero piece: worth the best model. |
| `sofa_bonus` | Bonus room | 3-seat track-arm sofa, oatmeal linen | 94 × 37 × 36 in (2.40 × 0.95 × 0.92 m) | 1 | Against the west knee wall; ceiling slopes above it, so keep the back under 36 in. |
| `sofa_outdoor` | Outdoor living | 3-seat sofa, grey | 94 × 37 × 36 in (2.40 × 0.95 × 0.92 m) | 1 | Wants an outdoor frame (teak, aluminium or wicker). |
| `sofa_leather` | Game room, bonus room | Poly Haven tufted leather sofa | 71 × 32 × 28 in (1.81 × 0.82 × 0.71 m) | 2 | Optional. A real model already, but vintage in style and small. Room for up to 94 in wide in the game room. |
| `bed_king` | Primary suite | Upholstered platform bed, channel headboard, oatmeal | Overall 82 × 85 × 52 in (2.09 × 2.17 × 1.32 m); king mattress 76 × 80 in | 1 | Model should include mattress, duvet and pillows: dressed bedding is the hardest thing to script. Nightstands sit 53 in either side of centre. |
| `bed_queen` | Bedrooms 2, 3, 4 | Same bed, queen | Overall 67 × 85 × 52 in (1.69 × 2.17 × 1.32 m); queen mattress 60 × 80 in | 3 | One model reused three times works; bedding colours differ now (navy, sage, rust accents) and I can recolour. |
| `bench_primary` | Primary suite, foot of bed | Oak bench, upholstered top | 59 × 18 × 20 in (1.50 × 0.45 × 0.50 m) | 1 | |
| `bench_mudroom` | Mudroom | Oak bench, charcoal cushion | 61 × 18 × 20 in (1.55 × 0.45 × 0.50 m) | 1 | Built-in look, under the hooks. A cushion alone would do. |
| `cushion_window_seat` | Bonus room dormer | Seat pad and three back pillows on a built-in oak base | Pad 183 × 21 × 3 in (4.66 × 0.53 × 0.08 m); pillows about 17 in square | 1 pad, 3 pillows | Custom length, unlikely to exist off the shelf. Candidate for me to rebuild with cloth simulation. |
| `stool_counter` | Kitchen island | Round leather-top stool, black legs | Seat 14 in across, 27 in high (0.36 m, 0.70 m) | 4 | Optional. Counter height is 36.5 in. |

## Plumbing fixtures

| Slot id | Room | Now | Size to fit | Qty | Notes |
|---|---|---|---|---|---|
| `toilet` | Primary bath, hall bath, powder, both Jack-and-Jill baths | Two-piece elongated toilet, white | 16 × 29 × 32 in (0.40 × 0.74 × 0.82 m); seat at 16.5 in | 5 | One model reused. |
| `basin_vessel` | All vanities | Round vessel basin, white | 16 in across, 5 in high (0.40 × 0.13 m), sitting on a 34 in counter | 6 | Primary bath has two; the others one each. An undermount or integrated basin also works: I would cut the counter. |
| `faucet_vanity` | All vanities | Single-hole vessel-height faucet, brushed brass | Spout 12 in above the counter, 7 in reach (0.30 m, 0.18 m) | 6 | If you change to undermount basins, choose a standard-height faucet. |
| `tub_primary` | Primary bath | Freestanding oval soaking tub, white | 69 × 32 × 23 in (1.75 × 0.82 × 0.58 m) | 1 | Under the window. |
| `tub_hall` | Hall bath | Freestanding oval tub, white | 59 × 30 × 23 in (1.50 × 0.76 × 0.58 m) | 1 | |
| `filler_tub` | Primary bath, hall bath | Floor-mounted tub filler, brushed brass | 39 in high (0.98 m) | 2 | At the head end of each tub. |
| `shower_head` | Primary bath, both Jack-and-Jill baths | Ceiling-mounted rain head, black | 10 in across (0.26 m), dropped from a 10 ft ceiling | 3 | |
| `shower_trim` | Same three showers | Not modeled | Valve trim, handles, hand shower | 3 sets | Missing from the scene today. Worth adding for close-ups. |
| `shower_glass` | Same three showers | Frameless glass with black header and pull | Primary: 67 × 68 in footprint, glass on two sides. Jack-and-Jill: 68 × 37 in and 65 × 37 in, glass front. Glass 85 in high | 3 | I can keep building these; listed only so a branded door or hardware can be swapped in. |
| `sink_kitchen` | Kitchen island | Undermount single-bowl sink, stainless | 33 × 16.5 in, 10 in deep (0.84 × 0.42 × 0.26 m) | 1 | Centred on the island's working side. |
| `faucet_kitchen` | Kitchen island | Gooseneck faucet, brushed brass | 16.5 in high, 8.5 in reach (0.42 m, 0.22 m) | 1 | |
| `pot_filler` | Kitchen, above the range | Wall-mounted pot filler, brushed brass | Mounted 54 in above the floor, 11 in reach | 1 | Currently a single rod: a real model would help. |

## Appliances

| Slot id | Room | Now | Size to fit | Qty | Notes |
|---|---|---|---|---|---|
| `range_kitchen` | Kitchen | 48 in range, six burners, double oven, stainless | 48 × 27 × 36.5 in (1.22 × 0.68 × 0.925 m) in a 49.5 in opening | 1 | Under the oak hood; the most-seen appliance. |
| `fridge_kitchen` | Kitchen | Built-in French-door refrigerator, stainless | 36 × 29 × 83 in (0.91 × 0.74 × 2.10 m) in a 36.5 in wide, 83.5 in high bay | 1 | Cabinet above runs to the ceiling. A panel-ready unit is an option; I would build the panels. |
| `hood_insert` | Kitchen | None: the oak hood is an empty shell | Liner for a 49.5 in wide hood, underside 68.5 in above the floor | 1 | Optional. Only seen from below. |
| `washer`, `dryer` | Utility | Front-load pair, white, side by side | Each 27 × 28.5 × 38.5 in (0.69 × 0.72 × 0.98 m) | 1 each | Under an oak shelf at 59 in. |
| `dishwasher` | Kitchen | Not modeled | 24 in, panel-ready or stainless | 1 | Missing today. Natural home is the island beside the sink. |
| `microwave` or `wall_oven` | Kitchen or pantry | Not modeled | Your choice | 0–1 | Missing today; say where you want it. |

## Optional, lower priority

These are also script-built and would benefit from real models, though you did not name them.

| Slot id | Where | Now | Size |
|---|---|---|---|
| `tv_family` | Family room, over the fireplace | Plain dark panel | 65 in class (58 × 33 in panel) |
| `tv_game` | Game room wall | Plain dark panel | 70–75 in class (63 × 35 in panel) |
| `lamp_table` | Bedside tables, family room, office, foyer | Ceramic base with drum shade | About 22 in high |
| `lamp_floor` | Office, game room, bonus room, primary suite | Slim black floor lamp with drum shade | About 66 in high |
| `chandelier_ring` | Dining room, foyer | Black ring chandelier with candle lights | About 43 in across |

## Staying as they are

Everything already from Poly Haven: armchairs, lounge chairs, dining chairs, coffee and side tables, shelving, media cabinet, plants, vases, books, framed prints, brass cookware, pendants and ceiling fans. Cabinetry, counters, the oak hood, fireplaces and built-in shelving are architecture and stay modeled in the scene.
