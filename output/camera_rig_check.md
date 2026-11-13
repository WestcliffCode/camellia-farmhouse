# Camera rig check

## Still cameras (37)

| Camera | type | lens | marker frame | clearance m | centre ray hits | at m |
|---|---|---|---|---|---|---|
| CAM-bedroom_2 | persp | 16 mm | 2015 | 0.49 | GEO-walls | 4.3 |
| CAM-bedroom_3 | persp | 16 mm | 2016 | 0.28 | GEO-walls | 4.2 |
| CAM-bedroom_4 | persp | 16 mm | 2017 | 0.33 | GEO-walls | 4.5 |
| CAM-bonus_room | persp | 16 mm | 2019 | 0.25 | GEO-bonus_shell | 9.6 |
| CAM-detail_bath | persp | 24 mm | 2032 | 0.73 | GEO-walls | 3.9 |
| CAM-detail_bed | persp | 30 mm | 2031 | 0.79 | GEO-furn_primary_fab_oat | 2.8 |
| CAM-detail_range | persp | 30 mm | 2033 | 0.53 | GEO-kitchen_quartz | 2.6 |
| CAM-detail_sofa | persp | 32 mm | 2030 | 0.59 | potted_plant_01_leaves | 4.5 |
| CAM-dining | persp | 17 mm | 2010 | 0.77 | GEO-furn_dining_curtain | 6.2 |
| CAM-elev_back | ortho | ortho 34.0 m | 2102 | 4.76 | GEO-roof_shingle | 76.2 |
| CAM-elev_front | ortho | ortho 34.0 m | 2101 | 4.76 | GEO-upper_walls | 60.0 |
| CAM-elev_left | ortho | ortho 34.0 m | 2104 | 4.76 | GEO-roof_shingle | 61.6 |
| CAM-elev_right | ortho | ortho 34.0 m | 2103 | 4.76 | GEO-roof_shingle | 64.3 |
| CAM-ext_back | persp | 30 mm | 2003 | 1.91 | GEO-porch_timber | 18.0 |
| CAM-ext_front | persp | 32 mm | 2001 | 1.88 | GEO-glass_frontdoor_25 | 23.7 |
| CAM-ext_front_left | persp | 28 mm | 2002 | 1.88 | GEO-walls | 23.7 |
| CAM-ext_garage | persp | 30 mm | 2004 | 1.91 | GEO-garagedoor_garage_53 | 19.6 |
| CAM-family | persp | 18 mm | 2006 | 0.45 | GEO-walls | 7.6 |
| CAM-family_from_hearth | persp | 18 mm | 2007 | 0.90 | GEO-walls | 7.5 |
| CAM-foyer | persp | 15 mm | 2005 | 1.32 | GEO-winframe_frontdoor_25 | 4.0 |
| CAM-game_room | persp | 15 mm | 2018 | 0.24 | GEO-glass_window_7 | 6.3 |
| CAM-garage | persp | 16 mm | 2026 | 0.47 | GEO-walls | 10.6 |
| CAM-hall_bath | persp | 14 mm | 2020 | 0.34 | GEO-walls | 0.9 |
| CAM-jj_bath | persp | 14 mm | 2021 | 0.25 | GEO-furn_jj_bath_glass | 2.2 |
| CAM-kitchen | persp | 18 mm | 2008 | 0.49 | GEO-kitchen_quartz | 4.9 |
| CAM-kitchen_from_dining | persp | 18 mm | 2009 | 0.74 | GEO-furn_foyer_mirror | 13.1 |
| CAM-linen_hall | persp | 14 mm | 2028 | 0.15 | GEO-walls | 1.6 |
| CAM-mudroom | persp | 15 mm | 2022 | 0.32 | GEO-walls | 4.7 |
| CAM-office | persp | 15 mm | 2014 | 0.33 | GEO-walls | 5.0 |
| CAM-outdoor_living | persp | 17 mm | 2029 | 0.76 | GEO-walls | 6.5 |
| CAM-pantry | persp | 15 mm | 2024 | 0.24 | GEO-kitchen_trim | 1.4 |
| CAM-primary_bath | persp | 15 mm | 2013 | 0.33 | GEO-glass_window_55 | 4.7 |
| CAM-primary_closet | persp | 15 mm | 2025 | 0.24 | GEO-walls | 4.0 |
| CAM-primary_suite | persp | 16 mm | 2011 | 0.29 | GEO-glass_window_1 | 5.7 |
| CAM-primary_suite_fire | persp | 17 mm | 2012 | 0.43 | GEO-fireplace_limestone | 5.2 |
| CAM-storage | persp | 16 mm | 2027 | 0.47 | GEO-jamb_door_15 | 0.5 |
| CAM-utility | persp | 15 mm | 2023 | 0.29 | GEO-walls | 3.6 |

## Walkthrough

- Camera `CAM-walkthrough`, lens 18 mm; constraints: FOLLOW_PATH, TRACK_TO.
- Follow Path target `CRV-walkthrough` (curve with 17 control points).
- Track To target `CAM-walkthrough_aim`.
- Frames 1-1080 at 24 fps (45 s); path length travelled 30.9 m; eye height 1.55-1.55 m.
- Frames with the camera outside the house footprint: 0.
- Smallest distance to any surface: 0.26 m (frame 1045; sampled every 4th frame, 82 directions).
- Largest move between consecutive frames: 2.9 cm (frame 812); largest turn between consecutive frames: 4.48 degrees.
- Segments between consecutive positions that cross geometry: 0.

## Result

No problems found.
