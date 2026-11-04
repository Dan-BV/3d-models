"""Section data for the Fusion-built grip (grip_fusion.py reads grip_sections.json).

Run:  python grip_sections.py

The grip is a loft through horizontal sections. Each section is the plan outline traced on
the product photos, pulled in by the waist depth at that height (the waist runs round the
front and both sides under the flared top, but not along the joint with the side plate), and
never thinner than MIN_WALL over the camera grip. The camera pocket is cut in height bands,
narrower where the camera's own grip has its finger recess.

Camera outline: from the camera mesh (a7c_outline_y0-62.json), with the grip's protrusion in
front of the body face scaled so screen-to-grip-front is the measured 54.0 mm (mesh: 55.7).
"""
import json
from pathlib import Path

import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon, box as _box
from shapely.geometry.polygon import orient

HERE = Path(__file__).resolve().parent

X_L, X1, Z0 = -64.0, -23.0, 27.0         # side face, lens-side edge, rear edge on the side plate
Y_BOT = -9.5
GAP, MIN_WALL = 0.6, 1.5
BODY_FRONT_Z, MESH_SCREEN_Z, MESH_GRIP_FRONT_Z, MEASURED_DEPTH = 38.0, -0.96, 54.78, 54.0
K = (MESH_SCREEN_Z + MEASURED_DEPTH - BODY_FRONT_Z) / (MESH_GRIP_FRONT_Z - BODY_FRONT_Z)

# plan outline traced on the bottom / top views (x, z)
PLAN = [(X_L, Z0), (X_L, 40.0), (-62.0, 46.0), (-59.1, 51.3), (-54.7, 55.7), (-50.0, 57.8),
        (-45.0, 58.5), (-40.0, 58.2), (-34.0, 56.8), (-28.5, 54.8), (-24.9, 51.0), (-23.0, 46.0),
        (X1, Z0)]
# waist round the grip under the flared top: depth and height (side view), gaussian in y
WAIST_DEPTH, WAIST_Y, WAIST_SIGMA = 3.2, 47.0, 6.5
BOTTOM_R = 0.0          # bottom edge is rounded by a fillet in Fusion instead
N_RING = 60             # points per section (the same for all, so the loft stays smooth)
SECTION_Y = [Y_BOT, 10.0, 30.0, 37.0, 42.0, 47.0, 52.0, 57.0, 63.0, 66.0]
# the camera grip's finger recess: (y0, y1, front z cap) of the narrower pocket band
POCKET_BANDS = [(-0.3, 43.5, None), (43.5, 52.5, 52.2), (52.5, 80.0, None)]


def box(x0, x1, z0, z1):
    return _box(x0, z0, x1, z1)


def smooth(p, r):
    return p.buffer(r, quad_segs=32).buffer(-2 * r, quad_segs=32).buffer(r, quad_segs=32)


def camera_grip():
    cam = Polygon(json.loads((HERE / 'a7c_outline_y0-62.json').read_text())['outline']).buffer(0)
    grip = cam.intersection(box(-80, -20, BODY_FRONT_Z, 80))
    grip = affinity.scale(grip, xfact=1.0, yfact=K, origin=(0, BODY_FRONT_Z))   # (x, z) -> z scaled
    body = cam.intersection(box(-80, 80, -20, BODY_FRONT_Z))
    return grip.union(body).difference(box(-70, -55.2, -10, 20)).union(box(-55.2, -21, -2, BODY_FRONT_Z))


CAM = camera_grip()


def pocket(cap=None, z0=24.0):
    p = CAM.buffer(GAP, quad_segs=32).intersection(box(-70, -18, z0, 80))
    if cap is not None:
        p = p.intersection(box(-70, -18, 0, cap))
    return p


# platform variant: the grip wraps the camera's side towards the rear, growing out of the plate's
# side edge (tangent at z = 6) to the full width at the grip
WRAP = [(X_L, 31.0), (X_L, 27.0), (-63.4, 21.0), (-62.0, 16.0), (-60.4, 11.8), (-58.9, 9.0),
        (-57.4, 7.4), (-55.6, 6.6), (-54.0, 6.6), (-54.0, 31.0)]   # flares out of the plate side from z = 6


def plan_outline(wrap=False):
    """traced outline, grown where the camera grip needs a MIN_WALL cover."""
    cover = pocket().buffer(MIN_WALL, quad_segs=32).intersection(box(-80, -21.0, Z0, 80))
    raw = Polygon(PLAN).union(cover)
    if wrap:
        raw = raw.union(Polygon(WRAP))
        raw = raw.buffer(6.0, quad_segs=32).buffer(-6.0, quad_segs=32)        # fill inside corners
        raw = raw.buffer(-1.5, quad_segs=32).buffer(1.5, quad_segs=32)         # soften outside ones
        return raw.intersection(box(X_L, -21.0, 5.0, 80))
    soft = smooth(raw, 5.0).union(raw.intersection(box(-80, 0, 0, Z0 + 3.0)))   # keep the joint square
    return smooth(soft, 1.0).intersection(box(X_L, -21.0, Z0, 80))


def base_ring(wrap=False):
    """the plan outline as N_RING points, counter-clockwise from the rear-inner corner, and
    the inward unit normal at each point."""
    xy = np.array(ring(plan_outline(wrap), N_RING + (100 if wrap else 0)), float)
    t = np.roll(xy, -1, axis=0) - np.roll(xy, 1, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True)
    n = np.stack([-t[:, 1], t[:, 0]], axis=1)                 # left of the tangent = inside
    return xy, n


def circ_smooth(v, sigma):
    k = np.arange(-int(3 * sigma) - 1, int(3 * sigma) + 2)
    w = np.exp(-0.5 * (k / sigma) ** 2)
    w /= w.sum()
    return sum(wi * np.roll(v, -ki) for wi, ki in zip(w, k))


def softmin(a, b, k=0.4):
    return -k * np.logaddexp(-a / k, -b / k)


def section(y, wrap=False):
    """base ring pulled in along its normals: waist + rounded bottom, nothing at the joint with
    the side plate, never closer than MIN_WALL to the camera pocket."""
    xy, n = base_ring(wrap)
    free = np.clip((xy[:, 1] - 30.0) / 6.0, 0, 1)
    free = free * free * (3 - 2 * free)                        # 0 along the joint, 1 from z = 36
    waist = WAIST_DEPTH * np.exp(-0.5 * ((y - WAIST_Y) / WAIST_SIGMA) ** 2)
    yc = Y_BOT + BOTTOM_R
    bottom = BOTTOM_R - np.sqrt(max(BOTTOM_R ** 2 - (yc - y) ** 2, 0.0)) if (BOTTOM_R and y < yc) else 0.0
    if y >= 0:
        cap = next((c for y0, y1, c in POCKET_BANDS if y0 <= y < y1), None)
        pk = pocket(cap).exterior
        allowed = np.array([pk.distance(Point(p)) for p in xy]) - MIN_WALL - 0.1
        allowed = np.maximum(allowed, 0.0)
        inside = np.array([pocket(cap).contains(Point(p)) for p in xy])
        allowed[inside] = 0.0
    else:
        allowed = np.full(len(xy), 1e3)
    d = softmin(waist * free, allowed) + bottom * free
    d = np.minimum(circ_smooth(np.maximum(d, 0.0), 1.5), np.maximum(allowed, 0) + bottom)
    pts = xy + n * d[:, None]
    return [[round(float(x), 3), round(float(z), 3)] for x, z in pts]


def ring(poly, n=36):
    """n points round the outline, counter-clockwise, starting at the rear-inner corner."""
    poly = orient(poly, 1.0)
    ext = poly.exterior
    pts = [ext.interpolate(i / n, normalized=True) for i in range(n)]
    xy = np.array([[p.x, p.y] for p in pts])
    start = int(np.argmin(np.hypot(xy[:, 0] - X1, xy[:, 1] - Z0)))
    xy = np.roll(xy, -start, axis=0)
    return [[round(float(x), 3), round(float(z), 3)] for x, z in xy]


def main():
    data = {
        'note': 'generated by grip_sections.py; (x, z) in mm, cage coordinates',
        'sections': [{'y': y, 'pts': section(y)} for y in SECTION_Y],
        'pockets': [{'y0': y0, 'y1': y1, 'pts': ring(pocket(c), 60)} for y0, y1, c in POCKET_BANDS],
        # the platform variant also wraps the camera's side back to the rear edge
        'sections_platform': [{'y': y, 'pts': section(y, wrap=True)} for y in SECTION_Y],
        'pockets_side': [{'y0': y0, 'y1': y1, 'pts': ring(pocket(c, z0=-8.0), 80)}
                         for y0, y1, c in POCKET_BANDS],
    }
    (HERE / 'grip_sections.json').write_text(json.dumps(data, indent=1))
    for s in data['sections']:
        p = Polygon(s['pts'])
        print(f"y {s['y']:6.1f}  front z {max(z for _, z in s['pts']):5.1f}  area {p.area:7.1f}")


if __name__ == '__main__':
    main()
