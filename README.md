# 3D models

3D-printable models designed or prepared in Autodesk Fusion, each with its print
profiles. Every project lives in its own folder with a README that describes the model
and how to print it.

| Folder | Model | Material |
|---|---|---|
| [`citroen-cold-air-intake/`](citroen-cold-air-intake/) | Cold air intake duct for a Citroën engine bay: three parts, a clip and a mouth stencil | PETG |
| [`window-stop/`](window-stop/) | 98.5 × 71 × 25 mm lattice window stop | PETG |
| [`naruto/`](naruto/) | 120 mm Naruto figurine | PLA |
| [`sherlock/`](sherlock/) | 75 mm Sherlock bust on a podium | PLA |
| [`skeleton/`](skeleton/) | Print-in-place skeleton plate, 100 / 70 / 50 % | PLA |

[`tools/cura_slice/`](tools/cura_slice/) is the CuraEngine harness used to check profiles and supports.

## Conventions

- All STL files are in millimetres and already oriented for printing.
- Profiles are for a Creality Ender 3 Pro in Cura (`.curaprofile`, import via
  Preferences → Profiles → Import). Profiles that set `adhesion_z_offset` need the Z Offset Setting
  plugin from the Cura Marketplace; adjust it to your own printer.
- STLs too large for GitHub are stored zipped (`*.stl.zip`).
