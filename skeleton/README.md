# Print-in-place skeleton (Skelet_v26) — 100 / 70 / 50 % plate

`Skelet_plate_100_70_50.stl` holds three copies of the skeleton on one plate (89.7 × 90.3 mm),
centred on the origin.

Uniform scaling also scales the joint gaps (70 % → 0.14 mm, 50 % → 0.10 mm), which fuses the
joints. Each copy was scaled and every shell offset inward, so all copies keep ~0.25 mm gaps:

| Copy | Inward offset | Size, mm | Min joint gap |
|------|---------------|----------|---------------|
| 100 % | 0.025 mm | 33.6 × 90.3 × 20.0 | 0.245 |
| 70 % | 0.055 mm | 23.4 × 63.2 × 13.9 | 0.247 |
| 50 % | 0.075 mm | 16.7 × 45.1 × 9.9 | 0.248 |

Profile: `Ender3Pro_PLA_Skelet_fast_020.curaprofile` — 0.20 layers, 2 walls, 15 % grid, skirt,
elephant-foot compensation −0.15, Z offset 1.1, build-plate-only supports (60°, zigzag 15 %, XY 0.6
so they cannot enter the 0.25 mm joint gaps), bridge settings on. CuraEngine: 2:49, ~16 g.

The lower rib blocks hang as a ~5 mm cantilever over the bed and need support; the head neck-slot
roof is a 6 mm bridge.
