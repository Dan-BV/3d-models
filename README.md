# Citroën Cold Air Intake Flange

A 3D-printable cold air intake duct for a Citroën engine bay. It takes air from the
radiator cross-member (a rectangular opening cut into the raised plastic bump in front of
the hood-seal lip) and delivers it through a bayonet socket to the OEM corrugated hose
(bellows) that plugs into the air-filter box.

The shape was designed in Autodesk Fusion against a photogrammetry scan of the engine bay,
scaled from the known Ø63 mm filter inlet, and checked for collisions with the scan.

## Repository layout

| Path | Contents |
|---|---|
| `parts/` | The three print parts and the clip, already oriented for printing (`.stl`, `.step`, `.f3d`) |
| `print/` | Print-ready Part 1 with its prop, the clip, the mouth stencil and the Cura profiles (`print/cura/`) |

Other projects in this folder:

| Path | Contents |
|---|---|
| `naruto/` | 120 mm Naruto figurine and its Cura profiles (see `naruto/README.md`) |
| `sherlock/` | 75 mm Sherlock bust on a podium (see `sherlock/README.md`) |
| `skeleton/` | Print-in-place skeleton plate, 100 / 70 / 50 % (see `skeleton/README.md`) |
| `tools/cura_slice/` | CuraEngine harness used to check profiles and supports |

All STL files are in millimetres. The full-resolution Part 1 and Part 2 STLs (≈ 105 / 55 MB,
0.01 mm chord tolerance) are too large for the repository, so they are stored zipped as
`parts/Part1_mouth_clips.stl.zip` and `parts/Part2_bend_tube.stl.zip`.

## Design summary

| Feature | Value |
|---|---|
| Inlet (mouth) | 160 × 45 mm (R9 corners) on the flat part of the rear wall of the cross-member bump, centred on it; window 140 × 25 mm (≈ 35 cm²) |
| Mounting face | Planar land offset 1 mm from the bump wall (measured profile) for 1 mm double-sided tape; land 10 mm wide all round on the flat wall |
| Inlet edge | Sharp edge; the inner walls run as straight ramps from the window to the duct over the seal lip |
| Wall thickness | 2.5 mm (wedge up to 10 mm at the mouth land) |
| Shape | Straight entry over the floor rib and the hood-seal lip (floor 16.9 mm above the floor of the apron, about 1.8 mm above the lip top), then one smooth bend down in which the section blends into a Ø63 tube, a straight Ø63 section (collar joint) and a short R55 bend onto the bellows-flange axis. Plan view: smooth trumpet 160 → ≈ 131 mm over the lip → Ø63. Narrowest section of the whole intake is the Ø54 ring of the bayonet flange (22.9 cm²); the duct over the lip is ≈ 23.5 cm² |
| Outlet | Separate bayonet flange (Part 3) on the Ø63 spigot, fitted to the measured bellows cuff with every diameter 1 mm larger than the cuff: OD 73 mm, height 46 mm; spigot sleeve Ø63.3 × 10 mm → 45° cone → Ø54 ring (flush with the cuff bore) → cuff stop → Ø62 → R4 shoulder → Ø64 up to the rim; two through windows 29° × 10 mm, two entry grooves (to Ø68) from the rim down to the windows, 30° twist; twist-lock counter-clockwise viewed into the filter inlet |
| Spigot / flange joint | The Part 2 bore narrows from Ø58 to Ø54 inside the spigot along an S-curve of two tangent R38.8 arcs (no kinks); the spigot tip is a 45° cone that seats on the flange cone, so the flow path is a continuous Ø54 from Part 2 through the flange ring into the bellows cuff, with no step or gap |
| Bellows fit | OEM bellows cuff (measured): end Ø59 with R1 edge, sealing bead Ø61, Ø60, R4 shoulder, Ø63, wall 2.5 mm (bore Ø54); two wedge lugs 15 mm wide × 9 mm long, rising to 2.5 mm (Ø67) at the back, 26 mm from the cuff end. Clearance 0.5 mm per side radially and around the lugs, 0.5 mm axial lug play. Free length ≈ 146 mm, fully compressed ≈ 109 mm; the rim position in the car is unchanged, the cuff stop is 1 mm closer to the filter than in the previous flange |
| Bellows position | Flange rim 81 mm from the filter-inlet rim (bellows close to its free length), bellows bend 25° |
| Collar joint | On the straight Ø63 section: the Part 2 collar (ID 63.3, OD 67.3, 10 mm) slides over the Part 1 tube end, butt joint with a flush Ø58 bore, 25° cone from the collar to the tube |
| Clip | Separate clip (`parts/Clip_v26`, 26 mm wide) at the mouth centre. Its tooth hooks 1.35 mm under the rear overhang of the hood-seal lip (0.30 mm below it). The roof (1.1 mm) and the front stop follow the lip with 0.25 mm clearance; the lip's front top corner is taken as R4 (measured on the car with test prints), and the rear hook cavity is square with 1.25 mm play at the overhang end. The front stop runs down the lip face onto the foot fillet. A release lever below the hook pulls the tooth out. The clip top is 0.4 mm below the Part 1 floor. It is bonded with epoxy to a tongue under the Part 1 floor through a glue tray on the clip. The tray lets the tongue sit 4 mm forward, 1.6–2 mm back and up to ±3° off nominal, because the lip is not parallel to the bump wall |

## Printing

Tested setup: Creality Ender 3 Pro (220 × 220 × 250 mm), **PETG** 1.75 mm.
PLA/PLA+ is not suitable under the hood (softens at 55–60 °C). PETG is fine at the
cross-member, especially with an external heat-reflective wrap. ASA/ABS or PA-CF are better
if you have an enclosed printer.

| Part | Size (mm) | Orientation (as exported) | Supports |
|---|---|---|---|
| `Part1_mouth_clips` | 161 × 94 × 241 | Standing on the long lower edge of the mouth, tube up (B2) | No slicer supports. Print `print/Part1_v25_B2_with_prop.stl.zip`, which includes a breakaway rib prop with a ≥ 0.32 mm gap. The prop keeps the tall part from tipping and is never inside the duct or the mouth window |
| `Clip_v26` | 24.6 × 11.0 × 26 | End face on the bed (`print/Clip_v26.stl`) | None. The only bridge is the tray end wall (≈ 5 × 12 mm). Print with `print/cura/Ender3Pro_PETG_CAI_clip.curaprofile` (100 % infill, 3 mm brim). The whole profile lies in each layer, so a finer layer height does not improve the fit |
| `Part2_bend_tube` | 67 × 84 × 92 | Spigot tip down, collar up (use the brim of the B2 profile) | None: no overhang inside the bore is steeper than 50° (the bend leans at most 39°); outside only the 45° spigot tip chamfer and ≈ 3 cm² under the collar cone |
| `Part3_bayonet_flange` | 73 × 73 × 46 | Base (spigot sleeve) down | None (45° cone under the stop ring, windows bridge ≈ 18 mm) |

The Cura profile used for the parts is `print/cura/Ender3Pro_PETG_CAI.curaprofile` (import it via
Preferences → Profiles → Import). For Part 1 with the prop use `print/cura/Ender3Pro_PETG_CAI_v25_B2.curaprofile`:
the same settings plus a 10 mm brim, a z-hop over printed parts, and supports off. Its +0.9 mm Z offset (`adhesion_z_offset`) needs the Z Offset
Setting plugin from the Cura Marketplace; adjust it to your own printer. For the clip use
`print/cura/Ender3Pro_PETG_CAI_clip.curaprofile`: the main settings with 100 % infill, a 3 mm brim,
an initial-layer expansion of −0.3 mm and 90 % initial-layer flow against elephant's foot, and a z-hop
on every travel.

Suggested PETG settings: nozzle 240–245 °C, bed 80 °C (glue stick as release layer),
fan 30–40 %, 40–50 mm/s, 4 perimeters, 30 % gyroid. Add a modifier over the clip area with
100 % infill and 5–6 perimeters. Brim 5–8 mm for parts 1 and 2. Dry the filament if it is not
fresh. Total material ≈ 400 g.

Part 1 in the B2 orientation has no overhang that needs support. The only downward face is the
underside of the tongue, ≈ 0.9 cm², which is only ≈ 1.2 mm above the duct wall below it. Use glue
stick and avoid drafts: the part is tall. After printing, snap off the prop and trim the brim flush
on the tape land. Parts 2 and 3 print with slicer supports restricted to "touching build plate"
(Z gap 0.2 mm), if any are needed.

### Mouth stencil

`print/Mouth_stencil.stl` is a 0.6 mm template of the tape land (outer 160 × 45 mm, window
140 × 25 mm). Lay it on the bump wall and cut along the window to make the mouth opening.

## Assembly and installation

1. Slide the collar of **Part 2** over **Part 1** (0.15 mm clearance, 10 mm overlap) and bond
   with epoxy or CA glue (acetone does not work on PETG).
2. Slide **Part 3** (bayonet flange) over the Ø63 spigot of Part 2 (0.15 mm radial clearance,
   10 mm overlap) until the conical spigot tip seats on the internal cone. It rotates freely.
3. Cut a rectangular opening in the rear wall of the cross-member bump (use `print/Mouth_stencil.stl`).
4. Fit the **clip** (`Clip_v26`) on the hood-seal lip at the mouth centre: pull the release lever
   back, hook the tooth under the rear overhang, press the clip down and let the lever go.
   Sand the tray and the Part 1 tongue (P80–P120), scratch a few grooves, degrease with isopropyl
   alcohol, then fill the tray about half full with thick two-part epoxy.
5. Apply 1 mm double-sided silicone (or VHB) tape to the mouth land and press Part 1 onto the bump
   wall, so that its tongue sinks into the epoxy. Hold it until the epoxy sets. After that the
   assembly can be removed and refitted: pull the release lever back to free the tooth from the
   lip and lift the part off; to refit, press it down until the tooth snaps under the overhang.
6. Insert the bellows cuff into the flange with the lugs in the entry grooves, push it down to the
   stop ring and twist counter-clockwise so the lugs move into the windows. Do the same at the
   filter inlet, then rotate the flange to its final position and fix it to the spigot (glue or a
   small screw).

Check hood clearance above the seal lip on the car before final assembly.

## Notes

- The master Fusion file with the engine-bay scan is kept locally and is not published.
- v25 (current `parts/`): Part 1 refitted to a hand-measured seal-lip profile (the land is 1.0 mm
  from the wall, the floor over the lip is lower, there is no saddle on Part 1, and the clip is a
  separate glued piece). It is confirmed on the car with a v25 test piece.
  The clip is v26, refined with test prints on the car: 1.35 mm tooth 0.30 mm below the overhang
  (v25: 0.65 mm), a release lever, 0.25 mm clearance along the roof and the lip face, an R4 front top
  corner (the measured lip is rounder than the R2 of the drawn profile), a square rear cavity with
  1.25 mm play, a 1.1 mm roof, a larger tray (tongue play 4 mm forward, 1.6–2 mm back) and a longer
  front stop.
  Part 2 and Part 3 are unchanged from v22, except that a hairline crack (≈ 0.005 mm, half the wall
  ring) at the spigot / bend junction of Part 2 was filled; the repaired Part 2 matches the master
  within 0.005 mm everywhere else.
- v22: Parts 1 and 2 were redesigned against a new, true-size engine-bay scan
  (the first scan turned out ≈ 7.8 % oversized; confirmed with caliper measurements). Part 3 is
  unchanged.
- Earlier iterations (166 mm mouth, integrated OD 69 socket), superseded by `parts/`:
  - Parts 1 and 2 were regenerated from the loft sections with a 160 mm mouth and monotonically
    decreasing widths, the clips were re-fitted to the new walls, and the Part 2 collar (0.15 mm
    clearance, 2 mm wall, 10 mm overlap) and Ø63 spigot were rebuilt. Checked against the
    engine-bay scan: only the intended clip snap / floor contact points (≤ 0.35 mm), Part 2 is clear.
  - Part 3: the first version was too shallow (23 mm instead of 31.5 mm to the cuff stop) and its
    bore (Ø62) was too small for the bellows cuff; rebuilt to the measured OEM flange (Ø64 bore,
    Ø69 lug recesses). Same spigot sleeve and base plane; the rim end is 13 mm closer to the filter
    (≥ 12 mm clearance to the engine-bay scan).
  - Part 3 was rebuilt again from a hand-measured bellows cuff (all diameters +1 mm, wedge lugs
    with a cylindrical outer face), the spigot sleeve shortened from 15 to 10 mm, and the Part 2
    spigot given an internal Ø58 → Ø54 S-taper and a conical tip. Re-checked in the car
    assembly: Part 2 outside is unchanged, the flange rim is at the same position, no interference
    between parts or with the bellows, ≥ 12 mm to the engine-bay scan.
- Dimensions of the OEM flange and bellows come from 3D scans of the OEM parts and hand
  measurements; verify fit with a test print of a clip section before printing the full part.
