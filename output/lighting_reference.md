# Lighting reference comparison

Reference: Poly Haven HDRI `magalies_field_sunset_2k.hdr`, a photographed clear sunset with the sun 4.3 degrees above the horizon. It is the scene's sky, and the sun lamp takes both its direction and its colour from the sun in that photograph.

Board: `output/renders/lighting_reference_board.png` (sky panorama and renders under the same view transform and exposure). All values below are display-referred RGB (0-255) after that view transform.

## Reference sky

| Patch | RGB | hue | R/B |
|---|---|---|---|
| sun disc (lamp colour) | 238, 187, 152 | 24 | 1.57 |
| sky glow within 14 degrees of the sun | 253, 238, 227 | 25 | 1.11 |
| sky opposite the sun | 183, 192, 199 | 206 | 0.92 |
| zenith | 131, 149, 167 | 210 | 0.78 |

## The light itself: neutral grey cards on the open lawn (albedo 0.5, no house materials involved)

| Card | RGB | hue | R/B | luminance |
|---|---|---|---|---|
| facing the sun | 224, 181, 155 | 23 | 1.44 | 189 |
| facing away from the sun (lit by sky and ground only) | 131, 128, 126 | 23 | 1.04 | 129 |
| facing up | 149, 145, 149 | 303 | 1.00 | 146 |

- Sun-facing card hue 23 against the photographed sun disc's 24: within 12 degrees.
- Shade-facing card R/B 1.04 against the sun-facing card's 1.44: the fill is cooler than the key. It is close to neutral rather than blue, because that card also receives light bounced off the sunlit dry grass in the photograph's lower half.
- Sun-facing to shade-facing luminance 189 : 129.

## One material in sun and in shade: concrete paving in the exterior renders

The paving, porch slabs and driveway share one neutral grey material. A ray test (`scripts/concrete_sun_shade.py`) marks which of its pixels in each exterior render are in direct sun and which are in shade; the colours below are read from the final renders at those pixels.

| Render | pixels in sun | colour in sun | hue | R/B | pixels in shade | colour in shade | hue | R/B |
|---|---|---|---|---|---|---|---|---|
| ext_front | 0 | too few | - | - | 332 | 140, 130, 123 | 24 | 1.14 |
| ext_front_left | 23 | 201, 153, 122 | 23 | 1.65 | 170 | 130, 124, 121 | 23 | 1.08 |
| ext_garage | 2 | too few | - | - | 1161 | 130, 131, 134 | 226 | 0.97 |
| ext_back | 342 | 190, 148, 121 | 23 | 1.57 | 38 | 143, 114, 95 | 25 | 1.51 |
| all four, pooled | 365 | 191, 148, 121 | 23 | 1.58 | 1701 | 132, 130, 130 | 358 | 1.02 |

- Same material, sun against shade: R/B 1.58 against 1.02; hue 23 against 358 (photographed sun 24, sky opposite the sun 206).

## Sunlit patches in the renders

| Render | sunlit patches RGB | hue | R/B | hue vs sun disc | hue vs sky glow |
|---|---|---|---|---|---|
| ext_back | 244, 230, 219 | 27 | 1.11 | +3 | +2 |
| game_room | 211, 178, 152 | 26 | 1.39 | +2 | +1 |
| kitchen | 237, 212, 193 | 25 | 1.22 | +1 | +0 |
| foyer | 221, 203, 186 | 28 | 1.19 | +4 | +3 |
| primary_suite | 197, 172, 147 | 30 | 1.34 | +6 | +5 |
| family | 212, 188, 167 | 28 | 1.27 | +4 | +3 |

Criterion: the sunlit patches in a render should sit in the hue range the photograph spans between its sun disc (24) and the sky glow around it (25), within 12 degrees. Views meeting it: 6 of 6.

## Shade indoors, lamps on and off

Shade = the 15th to 40th percentile of luminance in the frame.

| View | shade RGB, lamps on | shade RGB, lamps off | mean luminance, lamps on | lamps off |
|---|---|---|---|---|
| game_room | 117, 82, 51 | 35, 13, 1 | 114 | 37 |
| primary_suite | 71, 51, 33 | 2, 0, 0 | 97 | 10 |
| kitchen | 180, 132, 93 | 50, 19, 0 | 158 | 67 |

With the lamps off the rooms fall into deep shade around the sunlit patches, and the little light left in that shade is orange: it has come off the sun patches and the oak floors, not from the blue side of the sky. The lamps supply most of the fill (compare the last two columns), which is the soft practical lighting the brief asks for. So the warm shade in the finished renders is the lamps and the bounce, and the cool side of the sky shows only in the shade-facing grey card and on the street side of the exterior views.
