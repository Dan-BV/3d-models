# Sherlock bust, 75 mm on a podium

`Sherlock_75mm_podium_eyes.stl` is the bust (53 × 42 × 75 mm, half of the 150 mm source) on a
two-tier round podium (Ø58 × 4 mm + Ø50 × 3 mm, chamfered), 81.6 mm tall in total. The sunken eyes
of the source are filled with eye inserts. The STL holds overlapping shells; the slicer unions them.

## Print (Ender 3 Pro, Bambu Lab PLA Basic)

Profile: `Ender3Pro_PLA_Sherlock_bust_008.curaprofile`.

0.08 mm layers, 210/215 °C, bed 60 °C, 3 walls, 10 % gyroid, tree supports everywhere at 55°
(hair curls, brows, nose, chin, scarf knot), skirt only, Z seam at the back,
`meshfix_union_all` on, `adhesion_z_offset = 1.1`.

- `minimum_support_area` must be 0: it is applied per layer, and at 0.08 mm the default 0.1 drops
  most small overhangs.
- Tree branch angle 60°, branch Ø2.5 mm and 3° widening make the branches merge.
- Left unsupported: eyelid ledges, single hair-tip facets and the 1.5 mm slot between the neck and
  the coat collar at the back, which bridges.
- Estimate: model 47 g + support 88 g, about 9 h.
