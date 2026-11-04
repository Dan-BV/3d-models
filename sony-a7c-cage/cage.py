"""Parametric camera cage for the Sony a7C, modelled after the SmallRig 3212 / 3212B.

Run:  python cage.py    -> a7c_cage.step (frame + grip as two bodies) and a7c_cage.stl (one piece)

Coordinate system (same as the camera model it was fitted to):
  X  width   - grip side at -X, the port door / right-hand strap lug side at +X
  Y  height  - camera bottom at Y = 0, up is +Y
  Z  depth   - rear face of the body at Z = 0, lens side is +Z (body front face at Z = 38)
  Optical axis at X = 17.7, Y = 38.7. All units mm.

Overall size is the published 140 x 90.5 x 65.5 mm. Everything else was measured on the
four-view product photo (top / bottom / both sides) with a millimetre grid scaled to the
140 mm width and the 90.5 mm height, then checked against the camera mesh.
"""
import json
import math

import numpy as np
from pathlib import Path

from build123d import (Axis, Box, Compound, Cylinder, Face, Pos, Rot, Solid, Spline, Vector,
                       Wire, export_step, export_stl, fillet)
from shapely.geometry import Polygon as SPoly, box as _sbox

HERE = Path(__file__).resolve().parent

# ----------------------------------------------------------------------------- parameters
GAP = 0.6                       # clearance between camera and cage surfaces
X_L, X_R = -64.0, 76.0          # outer faces: grip side / right side (140 mm)
X_L_IN, X_R_IN = -55.6, 70.0    # inner faces of the two side walls
Y_BOT, Y_TOP = -9.5, 81.0       # base bottom / top of the top bar (90.5 mm)
Y_BAR = 75.0                    # underside of the top members (camera top is at 72.6)
OPT_X = 17.7                    # optical axis / tripod socket X

# base: main Arca plate under the body, frame around the battery door under the grip
PLATE_Z = (0.0, 38.5)           # main plate depth = Arca width, flush with the body front
PLATE_X0 = -20.0                # where the main plate meets the grip frame
FRAME_Z = (-7.2, 44.5)          # grip frame depth
BATT = (-56.0, -21.5, -5.0, 40.0)   # battery door opening x0, x1, z0, z1
SOCKET_Z = 23.5                 # tripod socket Z; the screw hole is a +-2.5 mm slot

# hole sizes (printable: tap 1/4"-20 and 3/8"-16 into the plastic, or drill and use inserts)
D_14 = 5.2             # 1/4"-20 tap drill
D_38 = 8.1             # 3/8"-16 tap drill
D_PIN = 3.0            # ARRI locating pin holes
D_M25 = 2.1            # M2.5 tap drill
D_SCREW = 6.7          # 1/4" camera screw clearance
D_SCREW_HEAD = 12.5    # counterbore for the captive screw head

# grip
GRIP_OFFSET = 3.5      # outer surface offset from the camera grip (front ends at ~58.5)
GRIP_Z0 = 27.0         # rear edge of the grip on the side (metal side plate behind it)
GRIP_X1 = -24.0        # lens-side edge of the grip

COL_L_Z = (1.5, 27.0)  # grip-side side plate
UPRIGHT_L_Z = (11.0, 17.5)
COL_R_Z = (27.0, 40.0)  # right-hand column

# ----------------------------------------------------------------------------- helpers
def _p3(axis, u, v, w):
    return {'y': Vector(u, w, v), 'x': Vector(w, v, u), 'z': Vector(u, v, w)}[axis]


def _dir(axis):
    return Vector(*{'x': (1, 0, 0), 'y': (0, 1, 0), 'z': (0, 0, 1)}[axis])


def prism(pts, axis, a0, a1):
    """Polygon prism. 2D coords: axis 'y' -> (x, z); 'x' -> (z, y); 'z' -> (x, y)."""
    wire = Wire.make_polygon([_p3(axis, u, v, a0) for u, v in pts], close=True)
    return Solid.extrude(Face(wire), _dir(axis) * (a1 - a0))


def spline_prism(pts, axis, a0, a1):
    wire = Wire([Spline(*[_p3(axis, u, v, a0) for u, v in pts], periodic=True)])
    return Solid.extrude(Face(wire), _dir(axis) * (a1 - a0))


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl(d, axis, c, length=200):
    rot = {'x': Rot(0, 90, 0), 'y': Rot(90, 0, 0), 'z': Rot(0, 0, 0)}[axis]
    return Pos(*c) * rot * Cylinder(d / 2, length)


def slot(d, axis, c0, c1, length=200):
    """stadium-shaped cut between two centres; the cut runs along `axis`."""
    s = cyl(d, axis, c0, length) + cyl(d, axis, c1, length)
    v = Vector(*c1) - Vector(*c0)
    mid = (Vector(*c0) + Vector(*c1)) * 0.5
    if axis == 'x':
        s += Pos(mid) * Rot(-math.degrees(math.atan2(v.Y, v.Z)), 0, 0) * Box(length, d, v.length)
    elif axis == 'y':
        s += Pos(mid) * Rot(0, math.degrees(math.atan2(v.X, v.Z)), 0) * Box(d, length, v.length)
    else:
        s += Pos(mid) * Rot(0, 0, math.degrees(math.atan2(v.Y, v.X))) * Box(v.length, d, length)
    return s


def sbox(u0, u1, v0, v1):
    return _sbox(u0, v0, u1, v1)


def smooth(poly, r):
    """round convex and concave corners of a shapely polygon with radius r."""
    return poly.buffer(r, quad_segs=16).buffer(-2 * r, quad_segs=16).buffer(r, quad_segs=16)


def ring_pts(poly, step=1.2):
    ext = poly.exterior
    n = max(24, int(ext.length / step))
    return [tuple(ext.interpolate(i / n, normalized=True).coords[0]) for i in range(n)]


def rounded_prism(poly, axis, a0, a1, r, step=0.6):
    # polygonal (fine-step) prism: OCC booleans with periodic-spline prisms are unreliable
    return prism(ring_pts(smooth(poly, r).simplify(0.02), step), axis, a0, a1)


def chamfer_cut(axis, corner, dirs, size, a0, a1):
    """triangular prism that bevels the edge at `corner` (2D) running along `axis`.
    dirs = (du, dv): which way is outside along each 2D axis (+1 / -1)."""
    u, v = corner
    du, dv = dirs
    pts = [(u + du * 0.01, v + dv * 0.01), (u - du * size, v + dv * 0.01), (u + du * 0.01, v - dv * size)]
    return prism(pts, axis, a0, a1)


# ----------------------------------------------------------------------------- camera envelope
cam = SPoly(json.loads((HERE / 'a7c_outline_y0-62.json').read_text())['outline']).buffer(0)
# grip region of the body (the strap lug is left out, it gets its own pocket)
cam_grip = cam.difference(sbox(-70, -55.2, -10, 20)).union(sbox(-55.2, -21, -2, 38))


# ----------------------------------------------------------------------------- base
def arca_profile(z0, z1):
    """YZ profile of the main plate: flat faces front and rear, a 45 deg dovetail groove
    along the bottom of both faces (Arca-Swiss, 38.5 mm wide)."""
    land, u = 1.0, 3.2      # bottom land height, undercut depth
    g = -5.0                # groove ceiling
    return [(z0, Y_BOT), (z1, Y_BOT), (z1, Y_BOT + land), (z1 - u, Y_BOT + land + u),
            (z1 - u, g), (z1, g), (z1, 0.0), (z0, 0.0), (z0, g), (z0 + u, g),
            (z0 + u, Y_BOT + land + u), (z0, Y_BOT + land)]


def base():
    plate = prism(arca_profile(*PLATE_Z), 'x', PLATE_X0 - 2, X_R)
    # round the right-hand end in plan view
    end = sbox(PLATE_X0 - 2, X_R, *PLATE_Z)
    plate = plate & (rounded_prism(end, 'y', Y_BOT - 1, 1, 3.0))
    # frame under the grip (the grip itself sits on its front part)
    fr = sbox(X_L, PLATE_X0 + 1, *FRAME_Z).difference(
        SPoly([(X_L - 1, -1.5), (X_L - 1, FRAME_Z[0] - 1), (-57.0, FRAME_Z[0] - 1)]))
    frame = rounded_prism(fr, 'y', Y_BOT, 0.0, 3.0)
    return plate + frame


# ----------------------------------------------------------------------------- grip
def grip():
    # plan view: camera grip offset outward, side face flush with the side plate
    outer = cam_grip.buffer(GRIP_OFFSET, quad_segs=16).union(sbox(X_L, X_L_IN, GRIP_Z0 - 8, 50))
    plan = smooth(outer, 3.0).intersection(sbox(X_L, GRIP_X1, GRIP_Z0, 80))
    g = rounded_prism(plan, 'y', Y_BOT, 66, 1.5)
    # side view (Z, Y): finger groove on the front, rounded top-front and bottom-front corners
    side = SPoly([(GRIP_Z0 - 6, Y_BOT - 2), (58.5, Y_BOT - 2), (58.5, 30), (57.8, 37), (55.6, 44),
                  (55.4, 50), (57.6, 55), (58.6, 59), (58.0, 62.3), (45, 62.4), (27, 60.6),
                  (GRIP_Z0 - 6, 60.6)])
    g = g & (rounded_prism(side.intersection(sbox(0, 80, Y_BOT, 80)), 'x', X_L - 1, 0, 3.0))
    # front view (X, Y): scooped top edge, higher at both sides
    front = SPoly([(X_L - 6, Y_BOT - 2), (GRIP_X1 + 6, Y_BOT - 2), (GRIP_X1 + 6, 59.5),
                   (-26.5, 62.6), (-33, 62.4), (-44, 60.6), (-56, 61.6), (X_L - 6, 62.6)])
    g = g & (rounded_prism(front, 'z', 0, 80, 2.0))
    g = g & (box(X_L, GRIP_X1, Y_BOT, 70, GRIP_Z0, 70))
    # pocket for the camera grip
    cavity = rounded_prism(cam_grip.buffer(GAP, quad_segs=16).intersection(sbox(-80, -10, 20, 80)),
                           'y', 0.0, 100, 0.4)
    return g - cavity


# ----------------------------------------------------------------------------- side walls
def left_wall():
    w = box(X_L, X_L_IN, Y_BOT, 55.0, COL_L_Z[0], COL_L_Z[1] + 1)        # side plate
    w += box(X_L, X_L_IN, 50.0, 62.0, 5.0, COL_L_Z[1] + 1)               # top of the plate
    w += box(X_L, X_L_IN, 55.0, Y_TOP, *UPRIGHT_L_Z)                     # upright to the top
    return w


def right_column():
    return box(X_R_IN, X_R, -5.0, Y_TOP, *COL_R_Z)


# ----------------------------------------------------------------------------- top members
TOP_OUTLINE = [                    # plan view (x, z)
    (X_L, 0.0), (-52.0, 0.0), (-44.0, 10.5), (-28.0, 10.5),      # hook + arm, rear edge
    (-10.0, 32.5), (44.0, 32.5),                                  # diagonal, bar rear edge
    (44.0, 26.0), (66.0, 26.0), (66.0, 0.0), (X_R, 0.0),          # cold-shoe block + right rail
    (X_R, 44.5), (-16.0, 44.5),                                   # front edge of the bar
    (-30.0, 22.5), (-56.0, 22.5), (X_L, 17.5)                     # diagonal + arm front edge
]


def top_members():
    t = prism(TOP_OUTLINE, 'y', Y_BAR, Y_TOP)
    try:
        t = fillet(t.edges().filter_by(Axis.Y), 2.0)
    except Exception as e:  # noqa: BLE001
        print('top outline fillet skipped:', e)
    return t


# ----------------------------------------------------------------------------- cuts
def cuts():
    c = []
    # --- base, top side
    c.append(prism(ring_pts(smooth(sbox(*BATT), 3.0)), 'y', Y_BOT - 1, 0.01))   # battery door
    c.append(rounded_prism(sbox(-11.0, 52.0, 4.5, 33.5), 'y', -1.0, 0.01, 4.0))  # rubber pad recess
    c.append(slot(D_SCREW, 'y', (OPT_X, 0, SOCKET_Z - 2.5), (OPT_X, 0, SOCKET_Z + 2.5)))
    # --- base, bottom side (as on the product: counterbored screw, pockets, key bay)
    c.append(slot(D_SCREW_HEAD, 'y', (OPT_X, Y_BOT, SOCKET_Z - 2.5), (OPT_X, Y_BOT, SOCKET_Z + 2.5), 8.0))
    for x, z in [(OPT_X, 9.5), (8.0, 32.5), (OPT_X, 32.5), (27.4, 32.5)]:
        c.append(cyl(D_14, 'y', (x, -5, z), 20))
    pk = Y_BOT + 1.5
    c.append(rounded_prism(sbox(-12.0, 8.0, 2.5, 30.5), 'y', Y_BOT - 1, pk, 2.0))
    c.append(rounded_prism(sbox(28.0, 63.0, 2.5, 19.0), 'y', Y_BOT - 1, pk, 2.0))
    c.append(rounded_prism(SPoly([(34, 27), (58, 27), (62, 31), (62, 35), (34, 35)]), 'y', Y_BOT - 1, pk, 1.5))
    c.append(rounded_prism(sbox(36.0, 70.0, 20.3, 23.3), 'y', Y_BOT - 1, Y_BOT + 2.6, 1.4))    # key shank
    c.append(rounded_prism(SPoly([(63.5, 3), (72, 3), (72, 30), (66, 30)]), 'y', Y_BOT - 1, Y_BOT + 2.6, 2.0))
    c.append(slot(3.2, 'x', (X_L, -4.5, 12.5), (X_L, -4.5, 24.5), 20))      # strap slot, grip frame

    # --- grip-side plate: side lock, M2.5, 1/4"-20 x3, ARRI 3/8"-16 with pin holes
    zc = 20.5
    c.append(box(X_L - 1, X_L + 0.8, 35.5, 62.0, 4.4, 4.9))      # side lock slider outline
    c.append(box(X_L - 1, X_L + 0.8, 35.5, 62.0, 11.1, 11.6))
    c.append(box(X_L - 1, X_L + 0.8, 35.5, 36.0, 4.4, 11.6))
    for k in range(6):                                            # grip ridges on the slider
        c.append(box(X_L - 1, X_L + 0.6, 44.0 + 1.3 * k, 44.6 + 1.3 * k, 5.5, 10.5))
    c.append(cyl(D_M25, 'x', (X_L, 40.0, 8.0), 30))
    for y, z in ((46.5, 14.8), (32.5, 9.8)):                      # slider screws
        c.append(cyl(D_M25, 'x', (X_L, y, z), 30))
    for y in (48.0, 38.5, 30.0):
        c.append(cyl(D_14, 'x', (X_L, y, zc), 40))
    c.append(cyl(D_M25, 'x', (X_L, 56.0, zc), 40))
    c.append(cyl(D_38, 'x', (X_L, 19.5, zc), 40))
    for y in (24.6, 9.8):
        c.append(cyl(D_PIN, 'x', (X_L, y, zc), 40))
    # strap-lug pocket (anti-twist): the lug slides in from the rear as the camera goes in
    c.append(box(-62.2, X_L_IN + 0.1, 56.8, 64.4, -10, 14.2))
    c.append(slot(3.4, 'x', (X_L, 74.5, 3.5), (X_L, 78.0, 10.5), 40))      # hook slot

    # --- right column: 1/4"-20 x4, ARRI 3/8"-16 + pins, oblique strap slot
    zc = 33.5
    for y in (57.5, 49.5, 40.5, 11.5):
        c.append(cyl(D_14, 'x', (X_R, y, zc), 40))
    c.append(cyl(D_38, 'x', (X_R, 26.5, zc), 40))
    for y in (34.0, 19.0):
        c.append(cyl(D_PIN, 'x', (X_R, y, zc), 40))
    c.append(slot(3.4, 'x', (X_R, 66.0, 35.5), (X_R, 71.5, 29.5), 40))
    c.append(chamfer_cut('y', (X_R, COL_R_Z[1]), (1, 1), 1.6, -6, Y_BAR))   # column front bevel
    c.append(chamfer_cut('y', (X_R_IN, COL_R_Z[1]), (-1, 1), 1.0, -6, Y_BAR))

    # --- top bar: 1/4"-20 x4, ARRI 3/8"-16 + pins centred on the optical axis
    zc = 38.5
    for dx in (-22.5, -13.5, 13.5, 22.5):
        c.append(cyl(D_14, 'y', (OPT_X + dx, 78, zc), 30))
    c.append(cyl(D_38, 'y', (OPT_X, 78, zc), 30))
    for dx in (-7.8, 7.8):
        c.append(cyl(D_PIN, 'y', (OPT_X + dx, 78, zc), 30))
    for x in (-38.7, -29.9):                                       # arm
        c.append(cyl(D_14, 'y', (x, 78, 16.5), 30))
    c.append(chamfer_cut('x', (44.5, Y_BAR), (1, -1), 2.2, -20, X_R + 1))   # bar front-bottom bevel
    # cold shoe, open to the front: 18.8 x 2.2 slot under rails with a 12.6 mm opening
    xc = 55.5
    c.append(box(xc - 9.4, xc + 9.4, 77.3, 79.5, 25.5, 60.0))
    c.append(box(xc - 6.3, xc + 6.3, 79.0, Y_TOP + 1, 25.5, 60.0))
    c.append(cyl(D_14, 'y', (xc, 77, 33.0), 30))
    return c


def build_frame():
    frame = base() + left_wall() + right_column() + top_members()
    for k in cuts():
        frame = frame - k
    return frame


def assemble(frame_stl, grip_mesh):
    """one-piece print mesh: frame (from the STEP model) united with the organic grip."""
    import manifold3d as mf
    import trimesh

    def to_mf(m):
        return mf.Manifold(mf.Mesh(vert_properties=np.asarray(m.vertices, np.float32),
                                   tri_verts=np.asarray(m.faces, np.uint32)))
    f = trimesh.load(frame_stl)
    u = (to_mf(f) + to_mf(grip_mesh)).to_mesh()
    return trimesh.Trimesh(u.vert_properties[:, :3], u.tri_verts)


if __name__ == '__main__':
    import trimesh

    frame = build_frame()
    frame.label = 'frame'
    export_step(frame, str(HERE / 'a7c_cage_frame.step'))
    export_stl(frame, str(HERE / 'a7c_cage_frame.stl'), tolerance=0.02, angular_tolerance=0.15)
    # the grip is built in Fusion by grip_fusion.py, which writes a7c_grip.step / a7c_grip.stl
    g = trimesh.load(HERE / 'a7c_grip.stl')
    whole = assemble(HERE / 'a7c_cage_frame.stl', g)
    whole.export(HERE / 'a7c_cage.stl')
    print('frame bbox', frame.bounding_box().size, 'cage bbox', whole.extents.round(2),
          'watertight', whole.is_watertight, 'volume cm3', round(whole.volume / 1000, 1))
