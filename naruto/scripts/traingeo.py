"""2D layout for the training-ground stand. All units mm, figure front = -Y, sole z = 0."""
import json, math
import numpy as np
from shapely.geometry import Polygon, Point, box
from shapely.ops import unary_union

FIT = 0.05            # foot pocket offset per side (press fit)
TOP = 3.0             # ground top z (pocket floor at z = 0)
THK = 8.0             # ground thickness
CEN = (-2.0, 2.0)

# irregular ground outline (smooth, closed spline through these points)
N = 18
rng = np.random.default_rng(7)
R = 48 + 2.2 * np.sin(np.arange(N) * 2.1) + rng.uniform(-1.2, 1.2, N)
ang = np.linspace(0, 2 * math.pi, N, endpoint=False)
OUTLINE = [(CEN[0] + r * math.cos(a), CEN[1] + 0.92 * r * math.sin(a)) for r, a in zip(R, ang)]

feet = [Polygon(p).buffer(FIT, join_style=2) for p in json.load(open('feet_outline.json'))]

LOGS = [(-28.0, 27.0), (0.0, 31.0), (25.0, 25.0)]   # log axes
LOG_D = 9.0
PEG_D = 6.0
SOCKET_D = 6.1          # press fit for the peg
SOCKET_DEPTH = 5.0
LOG_H = 62.0

STUMP = (27.0, -15.0, 8.0)        # x, y, radius
STUMP_H = 9.0

KUNAI_SLOTS = [(-35.0, -14.0, 20.0), (-27.0, -27.0, -25.0)]   # x, y, yaw deg
KUNAI_T = 2.4
TAB_W = 4.0
TAB_DEPTH = 4.0
SLOT_CLR = 0.1          # per side

SHURIKEN = (-6.0, -33.0, 9.0, 15.0)   # x, y, r, rot
BELLS = [(16.0, -32.0), (21.0, -27.5)]
STONES = [(-25.0, -3.0, 2.8), (22.0, -4.0, 2.3), (-11.0, 20.0, 2.5), (40.0, 6.0, 2.0)]
TUFTS = [(-40.0, 4.0), (36.0, 16.0), (-14.0, 33.0), (14.0, 22.0), (42.0, -6.0), (-42.0, -20.0), (-36.0, 26.0), (6.0, -40.0)]


def shuriken_poly(x, y, r, rot):
    pts = []
    for i in range(8):
        a = math.radians(rot + i * 45)
        rr = r if i % 2 == 0 else r * 0.34
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    return Polygon(pts)


def kunai_slot(x, y, yaw):
    w = KUNAI_T + 2 * SLOT_CLR
    l = TAB_W + 2 * SLOT_CLR
    p = box(-l / 2, -w / 2, l / 2, w / 2)
    from shapely import affinity
    return affinity.translate(affinity.rotate(p, yaw, origin=(0, 0)), x, y)


def kunai_profile():
    """Flat kunai in its own XY plane; tab at bottom (y<0) goes into the slot. Total ~34 mm."""
    blade = Polygon([(-TAB_W / 2, 0), (-4.2, 6.0), (0, 15.5), (4.2, 6.0), (TAB_W / 2, 0)])
    tab = box(-TAB_W / 2, -TAB_DEPTH, TAB_W / 2, 0.01)
    guard = box(-1.6, 15.0, 1.6, 16.5)
    handle = box(-1.4, 16.3, 1.4, 27.0)
    ring = Point(0, 30.0).buffer(3.2).difference(Point(0, 30.0).buffer(1.7))
    body = unary_union([blade, tab, guard, handle, ring]).buffer(0.25).buffer(-0.25)
    wraps = [box(-1.6, y, 1.6, y + 0.6) for y in np.arange(17.5, 26.0, 1.6)]
    return body, wraps


if __name__ == '__main__':
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    ground = Polygon(OUTLINE).buffer(0)
    fig, ax = plt.subplots(figsize=(7, 7))
    def draw(g, **k):
        for q in getattr(g, 'geoms', [g]):
            x, y = q.exterior.xy; ax.fill(x, y, **k)
    draw(ground, fc='#9c6', ec='k')
    for f in feet: draw(f, fc='#48c')
    for x, y in LOGS: draw(Point(x, y).buffer(LOG_D / 2), fc='#853')
    draw(Point(STUMP[0], STUMP[1]).buffer(STUMP[2]), fc='#a74')
    for s in KUNAI_SLOTS: draw(kunai_slot(*s), fc='#444')
    draw(shuriken_poly(*SHURIKEN), fc='#555')
    for x, y in BELLS: draw(Point(x, y).buffer(3.5), fc='#eb3')
    for x, y, r in STONES: draw(Point(x, y).buffer(r), fc='#999')
    for x, y in TUFTS: draw(Point(x, y).buffer(2.6), fc='#363')
    # figure silhouette (projected) for clearance check
    P = np.fromfile('nodes.bin', '<f8').reshape(-1, 3) * 10
    hi = P[P[:, 2] > 3][::20]
    ax.scatter(hi[:, 0], hi[:, 1], s=0.2, c='#f80', alpha=0.3)
    ax.set_aspect('equal'); plt.savefig('train2d.png', dpi=80)
    allobj = {'logs': [Point(x, y).buffer(LOG_D / 2) for x, y in LOGS], 'stump': [Point(STUMP[0], STUMP[1]).buffer(STUMP[2])]}
    print('ground bounds', np.round(ground.bounds, 1))
    for k, v in allobj.items():
        for g in v: print(k, 'inside ground margin', round(ground.exterior.distance(g.centroid) - g.bounds[2] + g.centroid.x, 1))
