# Naruto figurine and stands

The figurine is 100 mm tall, prints upright on an Ender 3 Pro, and uses Bambu Lab PLA Basic.

The Fusion cloud document is `Fusion Tutorial / Naruto / Naruto_figure_with_stand`. It contains:
- the figure mesh;
- `Stand`, the round stand (hidden);
- `TrainingGround`, `Logs` and `Kunai`, which make up the current training-ground stand.

## Files

| Path | Content |
|---|---|
| `Naruto_100mm.stl` | Figure mesh, mm units (insert into Fusion as **mm**) |
| `Ender3Pro_PLA_Naruto_fine_008_v3.curaprofile` | Current Cura profile (0.08 mm, tree supports, 9:35) |
| `Ender3Pro_PLA_Naruto_fine_008_v2.curaprofile` | Previous profile (12:13) |
| `supports_preview_v3.png` | Support layout from the v3 slice |
| `training_ground/` | Training-ground stand: painted renders, plain renders, local `.f3d` backup |
| `round_stand/` | Previews of the first round stand (Konoha emblem + NARUTO text) |
| `concepts/` | Seven stand concepts (`concepts_sheet.png`) |
| `scripts/` | Generators for geometry and renders (see below) |

## Training-ground stand

The stand has six parts. None of them has been exported for printing yet.

- **Ground (×1).** An irregular island ~97 × 90 × 8 mm with a stump, stones, bells, grass and a shuriken.
  - Foot pockets: 3 mm deep, outline +0.05 mm per side (press fit), 0.4 mm lead-in chamfer.
  - Log sockets: Ø6.1 × 5 mm.
  - Kunai slots: 2.6 × 4.2 × 4 mm.
- **Log (×3).** Ø9 × 62 mm with bark grooves and two rope bands, and a Ø6 peg. Print it top-down.
- **Kunai (×2).** Flat, 2.4 mm thick, 34 mm long. A tab goes into the slot. Print it flat.

Minimum clearances to the figure: 7.7 mm to the logs and 10 mm to the kunai.

## Scripts

Run the scripts with the working directory set to `scripts/data` and `PYTHONPATH=scripts`. They need numpy, shapely, pyvista, trimesh and Pillow.

- `outline.py`: foot sole outlines from the mesh. Writes `feet_outline.json`.
- `standgeo.py` / `traingeo.py`: 2D layouts of the round and training-ground stands.
- `build_train.py`: runs inside Fusion through the MCP `execute_code` tool and builds the training-ground components.
- `paint.py`: colours the figure triangles by zone to match the reference images.
- `final_render.py`: renders the painted figure on the painted stand. It reads the `data/tg_*.stl` stand meshes. Those are render previews only, not print files.
- `concepts.py`, `sheet.py`: the concept renders and the contact sheet.
- `data/nodes.bin`, `data/tris.bin`: the figure mesh as raw node coordinates (cm, float64) and triangle indices (int32), dumped from Fusion.
