# Lighting reference comparison

Reference: Poly Haven HDRI `magalies_field_sunset_2k.hdr`, a photographed clear sunset with the sun 4.3 degrees above the horizon. It is the scene's sky, and the sun lamp takes both its direction and its colour from the sun in that photograph.

Board: `output/renders/lighting_reference_board.png` (sky panorama and renders under the same view transform and exposure).

| Reference patch | display RGB | hue | R/B |
|---|---|---|---|
| sun disc (lamp colour) | 238, 187, 152 | 24 | 1.57 |
| sky glow within 14 degrees of the sun | 253, 238, 227 | 25 | 1.11 |
| sky opposite the sun | 183, 192, 199 | 206 | 0.92 |
| zenith | 131, 149, 167 | 210 | 0.78 |

| Render | sunlit patches RGB | hue | R/B | hue vs sun disc | hue vs sky glow | shade RGB | shade hue |
|---|---|---|---|---|---|---|---|
| ext_back | 243, 231, 221 | 28 | 1.10 | +4 | +3 | 83, 56, 33 | 27 |
| game_room | 208, 175, 149 | 26 | 1.39 | +2 | +1 | 117, 82, 52 | 28 |
| kitchen | 238, 214, 196 | 25 | 1.22 | +1 | -0 | 176, 126, 85 | 27 |
| foyer | 225, 205, 188 | 28 | 1.19 | +3 | +2 | 186, 164, 141 | 30 |
| primary_suite | 196, 172, 147 | 30 | 1.33 | +6 | +5 | 73, 52, 34 | 29 |
| family | 212, 188, 167 | 28 | 1.27 | +4 | +3 | 154, 107, 67 | 28 |

Criterion: the sunlit patches in a render should sit in the hue range the photograph spans between its sun disc (24) and the sky glow around it (25), within 12 degrees. Views meeting it: 6 of 6.

What the comparison does not show: the shade in these views is warm as well (hues in the table), not the cool blue of the sky opposite the sun. Indoors the shade is filled by 2700-3000 K lamps and light bounced off oak floors; the cool sky colour appears only in the sky seen through street-side windows and in the exterior views. The sunlit patches are less saturated than the sun disc swatch because the view transform desaturates bright values and the patches fall on white walls and pale floors.
