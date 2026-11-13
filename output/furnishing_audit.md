# Furnishing audit

- Poly Haven instances: 82 placements of 20 assets. Modeled furniture meshes: 166.
- Instances with a footprint corner inside a wall: 0 
- Modeled meshes with more than 1% of sampled vertices more than 4 cm inside a wall: 0 
- Materials on modeled furniture (32), all from the design-system palette: art_a, art_b, art_c, brass, bulb, ceramic_matte, curtain, fab_char, fab_grey, fab_navy, fab_oat, fab_rust, fab_sage, fab_white, glass, glass_dark, hardware_black, lamp_shade, leather_tan, mat_rubber, mirror, oak, porcelain, quartz, rug_blue, rug_cream, rug_warm, siding_dark, stainless, tile_marble, towel, trim_white
- Surface of modeled furniture carrying Poly Haven photographic textures (linen, wool, leather, oak, marble, painted plaster, rubber tile) or generated artwork: 89% by area; the rest is plain-value materials (porcelain, metals, glass, lamp shades).
- Upholstered and porcelain meshes with bevel + weighted-normal modifiers for soft edges: 41.
- Wall-backed pieces are snapped to the built wall faces by ray cast (`facing_frame` in `furnish_lib.py`); curtain panels are clamped to their room; shower tile is snapped to the walls.

| Room group | Poly Haven pieces | Modeled pieces |
| --- | --- | --- |
| family | ASSET-books_a x1, ASSET-books_b x1, ASSET-books_c x1, ceiling_fan x1, ceramic_vase_01 x2, ceramic_vase_03 x1, modern_arm_chair_01 x2, modern_coffee_table_01 x1, potted_plant_01 x1, potted_plant_04 x1, side_table_01 x1, wooden_bowl_01 x1 | sofa x1, console x1, rug x1, table_lamp x1, art x1 |
| kitchen | ceramic_vase_01 x1, modern_ceiling_lamp_01 x1, potted_plant_04 x1, wooden_bowl_01 x1 | stool x1 |
| dining | ASSET-books_a x1, ASSET-books_c x1, ceramic_vase_01 x2, ceramic_vase_03 x1, dining_chair_02 x4, potted_plant_01 x1, wooden_bowl_01 x1 | table x1, rug x1, ring_chandelier x1, curtains x1, base_cabinet x1 |
| foyer | ceramic_vase_03 x1, potted_plant_02 x1 | console x1, rug x1, table_lamp x1, ring_chandelier x1, art x1, round_mirror x1 |
| office | dining_chair_02 x1, mid_century_lounge_chair x1, potted_plant_04 x1, steel_frame_shelves_03 x1 | table x1, rug x1, table_lamp x1, floor_lamp x1, art x1, curtains x1 |
| primary | ceiling_fan x1, ceramic_vase_01 x1, mid_century_lounge_chair x1, potted_plant_02 x1, side_table_01 x1 | bed x1, bench x1, dresser x1, rug x1, table_lamp x1, floor_lamp x1, art x1, curtains x2 |
| bedroom_2 | potted_plant_04 x1, side_table_01 x1 | bed x1, dresser x1, rug x1, table_lamp x1, art x1, curtains x1 |
| bedroom_3 | ceramic_vase_03 x1, side_table_01 x1 | bed x1, dresser x1, rug x1, table_lamp x1, art x1, curtains x1 |
| bedroom_4 | potted_plant_04 x1, side_table_01 x1 | bed x1, dresser x1, rug x1, table_lamp x1, art x1, curtains x1 |
| game_room | coffee_table_round_01 x1, dining_chair_02 x1, modern_wooden_cabinet x1, potted_plant_01 x1, steel_frame_shelves_01 x2 | sofa x1, round_table x1, rug x1, floor_lamp x1 |
| bonus | mid_century_lounge_chair x1, modern_coffee_table_01 x1, steel_frame_shelves_01 x1 | sofa x2, rug x1, floor_lamp x1 |
| primary_bath | potted_plant_04 x1 | rug x1, toilet x1, vanity x1, tub x1, shower x1 |
| hall_bath |  | toilet x2, vanity x2, tub x1 |
| jj_bath |  | toilet x2, vanity x2, shower x2 |
| service |  | bench x1, appliance x2, shelf_wall x7, base_cabinet x1 |
| outdoor | coffee_table_round_01 x1, modern_arm_chair_01 x6, potted_plant_01 x3, side_table_01 x1 | sofa x1, rug x1 |
| garage | steel_frame_shelves_01 x2 | table x1, rug x1, stock x3 |
| storage |  | rug x4, art x2, shelf_wall x3, stock x4 |
