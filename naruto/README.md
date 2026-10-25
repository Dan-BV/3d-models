# Naruto figurine, 120 mm

`Naruto_120mm.stl` is the figure at 120 mm, in mm units. Compared with the source mesh:
- the headband ribbon roots are thickened;
- stray debris triangles are removed, so the mesh is watertight;
- each leg has a smooth bridge from the ankle wrap to the trouser cuff, under a 45° contour bevel,
  so the cuffs print without supports.

## Printing

Ender 3 Pro, Bambu Lab PLA Basic, printed upright on the soles.

| Profile | Layer | Time |
|---|---|---|
| `Ender3Pro_PLA_Naruto120_fine_008_v8_maxstrength.curaprofile` | 0.08 mm | ~18:16 |
| `Ender3Pro_PLA_Naruto120_012_v9_maxstrength.curaprofile` | 0.12 mm | ~12:30 |

Both profiles: no brim on the model, an 8 mm support brim, 5 walls, 20 % gyroid with 20 % overlap,
215 °C, and the fan ramping to 100 % by 16 mm for better layer bonding in the legs.

The Fusion cloud document is `Fusion Tutorial / Naruto / Naruto_figure_with_stand`.
