# Sony a7C cage

A printable copy of the SmallRig 3212 / 3212B cage for the Sony a7C, plus a lighter variant:
the same side grip on a bottom plate instead of the full cage. Both were fitted to a model of
the camera and checked so the camera slides in from the rear without touching anything.

| File | What |
|---|---|
| `a7c_cage.stl` | the cage in one piece, ready to print (frame + grip) |
| `a7c_cage_frame.step` / `.stl` | the cage frame alone |
| `a7c_grip.step` / `.stl` | the cage's side grip alone (e.g. to print it in TPU) |
| `a7c_platform_grip.step` / `.stl` | the grip on a bottom plate, one body |

All files are in millimetres in the camera's coordinates: X across (grip side at −X), Y up
(camera bottom at 0), Z front-back (rear face of the body at 0, lens side +Z). They are not
oriented for printing yet.

## Cage

140 × 90.5 × 65.5 mm, the published size of the original. Measured on the product's four-view
photo with a millimetre grid scaled to that size, and checked against the camera:

- base: Arca-Swiss plate 38.5 mm wide, flush with the body front, a 45° dovetail groove front
  and rear; a frame round the battery door under the grip; 1/4"-20 holes, pockets and a bay for
  a flat key underneath; recess for a 1 mm rubber pad on top;
- camera screw: 1/4" through a ±2.5 mm slot (z 21…26) with a counterbore for the head;
- top bar in front of the hot shoe with 1/4"-20 ×4 and an ARRI 3/8"-16 with pin holes on the
  optical axis, two 1/4"-20 on the arm over the dials, a cold shoe open to the front;
- side columns with 1/4"-20 and 3/8"-16 rows, oblique strap slots, the side-lock slider on the
  grip side and a pocket that takes the strap lug as the camera slides in (anti-twist).

Holes are tap-drill size (5.2 mm for 1/4"-20, 8.1 mm for 3/8"-16, 2.1 mm for M2.5): tap them
or fit inserts.

## Grip

A loft through horizontal sections (`grip_sections.py` → `grip_sections.json`) built in
Fusion by `grip_fusion.py`: plan outline traced on the photos, a waist round the grip under
the flared top, one top surface scooped across and rising to the front, R5 / R3 rounded top
and bottom. The pocket follows the camera grip with 0.6 mm clearance, narrower at the camera's
own finger recess.

The camera model's grip was 1.7 mm deeper than the real camera: screen to the front of the
grip is 54.0 mm measured (55.7 in the model, Sony states 53.5). The pocket is scaled to the
measurement; `measure_grip_depth.png` shows the dimension.

## Grip on a plate

`a7c_platform_grip` is the grip without the cage, on a bottom plate rebuilt after a downloaded
a7C plate (`grip_a7c.stl`, not included). The plate is cut to the grip's bottom (9.5 mm thick)
and keeps that plate's camera rims, 1/4" hole on the optical axis at z 27.4 and the Ø22
counterbore; the grip also wraps the camera's side back to the plate's rear corner, under the
strap lug. 132 × 72.5 × 60 mm, 66 cm³. It covers the battery door like the original plate.

## Rebuilding

```
python grip_sections.py                      # sections for the grip loft
# in Fusion (script, or Fusion MCP):
#   grip_fusion.run(ctx, 'cage')             -> a7c_grip.step / .stl
#   grip_fusion.run(ctx, 'platform')         -> a7c_platform_grip.step / .stl
#     (needs a7c_plate.json from: python platform_hybrid.py [path/to/grip_a7c.stl])
python cage.py                               # frame STEP/STL and the one-piece cage STL
python platform_hybrid.py --finish           # makes the platform STL watertight
```

`cage.py` needs build123d, shapely, trimesh and manifold3d. `a7c_outline_y0-62.json` is the
camera body outline the frame and the grip are fitted to.

## Not verified

- The tripod socket position. The cage slot covers z 21…26 (from the photos); the downloaded
  plate puts it at 27.4. Check on the camera before printing the cage.
- Nothing has been printed yet: print a test fit of the grip first.
