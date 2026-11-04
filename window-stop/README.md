# Window stop

A window stop (limiter) with a Voronoi-style lattice profile, extruded 25 mm.
`Window_stop.stl` is in millimetres and already oriented for printing: profile on the bed,
25 mm tall.

## Geometry

| Feature | Value |
|---|---|
| Overall | 98.5 × 71.27 × 25 mm |
| Lower-left step | 3 mm, 27.5 mm from the left edge |
| Slot | 12 mm wide between the step and the stem, sharp inner corners |
| Locating tab | 3.9 × 6 mm in the slot, 3.6 mm from the step, R1 tip corners |
| Upper block | 39 mm from the stem to the right vertical face |
| Right arm | 10.4 mm high above the slot level |
| Lattice | 8 through pockets, webs and outer walls ≈ 3 mm, R2 pocket corners |
| Outer vertical edges | R1, except the two slot corners |
| Volume | 50.1 cm³ (≈ 64 g PETG if solid) |

The slot is 12 mm (the drawing's 14 mm was corrected); the overall 98.5 mm and the 39 mm
dimension from the stem are kept, so the right arm is 2 mm longer than on the drawing.
The 25 mm thickness, the slanted edges and the pocket layout were taken from the drawing by scale.

## Printing

Ender 3 Pro, PETG, flat on the bed with no supports. The layers run parallel to the profile,
so the load from the sash acts along the layers rather than across them.

Profile: `Ender3Pro_PETG_WindowStop.curaprofile` (Preferences → Profiles → Import). It is the
`print/cura/Ender3Pro_PETG_CAI` profile with 5 walls, 5 top / 5 bottom layers, 40 % gyroid,
a 5 mm brim (for the narrow tab and the sharp slot corners) and a 0.4 mm z-hop. 235 / 240 °C first
layer, bed 80 °C with glue stick, fan 40 % from layer 3, Z offset 0.9 mm (Z Offset Setting plugin).

With 5 walls the ≈ 3 mm webs print solid; the infill only fills the corners and junctions.
For maximum stiffness raise the infill to 60 %.

The slot and the tab are nominal. PETG usually prints inner contours 0.1–0.2 mm tight, so
test-fit a 3–4 mm high slice first if the fit matters.
