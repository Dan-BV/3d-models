import numpy as np, pyvista as pv, math, sys, os
from shapely.geometry import Polygon, Point, LineString, box as sbox
from shapely.ops import unary_union, triangulate
from shapely import affinity
pv.OFF_SCREEN = True
S = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

P = np.fromfile(S + '/nodes.bin', '<f8').reshape(-1, 3) * 10
T = np.fromfile(S + '/tris.bin', '<i4').reshape(-1, 3)
FIG = pv.PolyData(P, np.c_[np.full(len(T), 3), T].ravel())
FIG_C = '#efd9b4'

import standgeo
LEAF, LEAF_GROOVE = standgeo.emblem()


def prism(poly, z0, h):
    """Extrude a shapely polygon from z0 by h (holes are ignored; overlay them instead)."""
    meshes = []
    for g in getattr(poly, 'geoms', [poly]):
        g = g.buffer(0)
        if g.is_empty: continue
        for gg in getattr(g, 'geoms', [g]):
            ring = np.array(gg.exterior.coords)[:-1]
            if Polygon(ring).exterior.is_ccw is False: ring = ring[::-1]
            pts = np.c_[ring, np.full(len(ring), z0)]
            face = np.r_[len(ring), np.arange(len(ring))]
            m = pv.PolyData(pts, face).triangulate()
            meshes.append(m.extrude((0, 0, h), capping=True))
    return meshes


def cyl(c, r, h, z0=0, d=(0, 0, 1), res=60):
    d = np.array(d, float); d /= np.linalg.norm(d)
    if len(c) == 2: center = np.array([c[0], c[1], z0 + h / 2])
    else: center = np.array(c, float) + d * h / 2
    return pv.Cylinder(center=center, direction=d, radius=r, height=h, resolution=res)


def boxm(x0, x1, y0, y1, z0, z1):
    return pv.Box(bounds=(x0, x1, y0, y1, z0, z1))


def kunai(pos, yaw, tilt, scale=1.0):
    """Kunai lying along +x before transform; blade tip at origin side."""
    blade = Polygon([(0, 0), (9, 3.2), (16, 0), (9, -3.2)])
    parts = prism(blade, -0.9, 1.8)
    parts.append(pv.Cylinder(center=(21, 0, 0), direction=(1, 0, 0), radius=1.1, height=10))
    parts.append(pv.ParametricTorus(ringradius=2.2, crosssectionradius=0.7).rotate_y(90).translate((28.5, 0, 0)))
    m = parts[0]
    for p in parts[1:]: m = m.merge(p)
    m = m.scale(scale).rotate_y(tilt).rotate_z(yaw).translate(pos)
    return m


def shuriken(pos, r=9, h=1.8, rot=0):
    pts = []
    for i in range(8):
        a = math.radians(rot + i * 45)
        rr = r if i % 2 == 0 else r * 0.32
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    star = Polygon(pts).difference(Point(0, 0).buffer(r * 0.13))
    return [m.translate(pos) for m in prism(star, 0, h)]


def leaf(cx, cy, z0, h, s=1.0, rot=0):
    p = affinity.translate(affinity.rotate(affinity.scale(LEAF, s, s, origin=(0, 0)), rot, origin=(0, 0)), cx, cy)
    g = affinity.translate(affinity.rotate(affinity.scale(LEAF_GROOVE, s, s, origin=(0, 0)), rot, origin=(0, 0)), cx, cy)
    return prism(p, z0, h), prism(g, z0 + h, 0.05)


def render(name, items, cam=None, fig_items=None, size=(900, 1000)):
    pl = pv.Plotter(off_screen=True, window_size=size)
    pl.set_background('#f4f1ec', top='#ffffff')
    pl.add_mesh(FIG, color=FIG_C, smooth_shading=True, specular=0.15)
    for it in fig_items or []:
        pl.add_mesh(it[0], color=it[1], smooth_shading=True, opacity=it[2] if len(it) > 2 else 1.0)
    for m, col in items:
        ms = m if isinstance(m, list) else [m]
        for mm in ms:
            pl.add_mesh(mm, color=col, smooth_shading=True, specular=0.25)
    pl.enable_shadows() if False else None
    pl.camera_position = 'xz'
    pl.view_vector((0.55, -1.0, 0.55), viewup=(0, 0, 1))
    pl.reset_camera(); pl.camera.zoom(1.25)
    pl.screenshot(os.path.join(OUT, name + '.png'))
    pl.close()


# ---------- 1. Medallion ----------
lf, lg = leaf(-3, -24, -0.2, 0.4, 0.9)
render('c1_medallion', [
    (cyl((-3, -6), 36, 5, -5), '#c9a45c'),
    (pv.ParametricTorus(ringradius=34.5, crosssectionradius=1.4).translate((-3, -6, 0)), '#a8843f'),
    (lf, '#7a5a22'), (lg, '#3a2a10'),
])

# ---------- 2. Headband plate ----------
plate = sbox(-40, -34, 34, 18).buffer(6, join_style=1)
cloth_l = sbox(-75, -26, -40, 10)
cloth_r = sbox(34, -26, 69, 10)
items = [(prism(plate, -8, 8), '#b8bec6')]
for cl in (cloth_l, cloth_r):
    items.append((prism(cl, -7, 5), '#2d4f9e'))
    x0, _, x1, _ = cl.bounds
    for x in np.linspace(x0 + 4, x1 - 4, 5):
        items.append((boxm(x - 0.6, x + 0.6, -26, 10, -2, -1.4), '#1f3a7a'))
for x, y in [(-41, -31), (35, -31), (-41, 15), (35, 15)]:
    items.append((pv.Sphere(radius=2.2, center=(x, y, 0)), '#8d949c'))
lf, lg = leaf(-3, -24, 0, 0.8, 0.85)
items += [(lf, '#6f767e'), (lg, '#30353b')]
render('c2_headband', items, cam=[(110, -190, 105), (-3, -5, 30), (0, 0, 1)])

# ---------- 3. Uzumaki spiral ----------
th = np.linspace(0, 3.2 * 2 * math.pi, 600)
r = 2 + 33 * th / th[-1]
sp = LineString(np.c_[-3 + r * np.cos(th), -6 + r * np.sin(th)]).buffer(2.4, cap_style=1)
render('c3_spiral', [
    (cyl((-3, -6), 40, 8, -8), '#c0392b'),
    (prism(sp.intersection(Point(-3, -6).buffer(39)), 0, 1.4), '#f08a24'),
])

# ---------- 4. Training ground ----------
rng = np.random.default_rng(3)
ang = np.linspace(0, 2 * math.pi, 40, endpoint=False)
ground = Polygon([(-2 + (48 + rng.uniform(-3, 3)) * math.cos(a), 2 + (44 + rng.uniform(-3, 3)) * math.sin(a)) for a in ang])
items = [(prism(ground, -7, 7), '#7a9a4a')]
for x in (-30, 0, 30):
    items.append((cyl((x, 30), 4.2, 62, 0, res=24), '#8b5a2b'))
    items.append((cyl((x, 30), 4.5, 3, 42, res=24), '#d9c08a'))
items.append((boxm(-30, 30, 29.3, 30.7, 44.5, 45.5), '#d9c08a'))
items.append((pv.Sphere(radius=3.2, center=(12, 30, 40)), '#e3b62e'))
items.append((cyl((12, 30), 0.5, 4.5, 43, res=12), '#d9c08a'))
items.append((cyl((30, -22), 8, 9, 0, res=30), '#9b6a3a'))
items.append((cyl((30, -22), 7, 0.6, 9, res=30), '#d6b27a'))
items.append((kunai((-30, -26, -2), 200, -60), '#5d6670'))
items.append((kunai((-14, -36, -2), 160, -65), '#5d6670'))
items.append((shuriken((14, -36, 0), rot=10), '#4b535c'))
for x, y in [(-38, 5), (36, 8), (-10, 24), (20, 20), (40, -5), (-42, -14)]:
    items.append((pv.Cone(center=(x, y, 2.5), direction=(0, 0, 1), height=5, radius=2.5, resolution=10), '#4f7a2a'))
for x, y, rr in [(-24, -10, 3), (22, -6, 2.4), (-6, 30, 2.6)]:
    items.append((pv.Sphere(radius=rr, center=(x, y, 0.5)), '#9a9a90'))
render('c4_training', items, cam=[(105, -200, 120), (-2, 5, 32), (0, 0, 1)])

# ---------- 5. Ichiraku ramen ----------
items = [(boxm(-50, 50, -40, 35, -6, 0), '#c8a06a')]
for y in np.linspace(-40, 35, 9)[1:-1]:
    items.append((boxm(-50, 50, y - 0.4, y + 0.4, -0.3, 0.05), '#a57f4c'))
# counter + stool
items.append((boxm(28, 48, -20, 18, 0, 32), '#a0522d'))
items.append((boxm(26, 50, -22, 20, 32, 35), '#d2a679'))
items.append((cyl((14, -16), 6, 2.5, 18), '#c0392b'))
items.append((cyl((14, -16), 1.6, 18, 0, res=16), '#5c3a1e'))
# bowl on counter
bowl = pv.Sphere(radius=10, center=(38, -2, 45), theta_resolution=60, phi_resolution=60).clip('z', origin=(0, 0, 45), invert=True)
items.append((bowl, '#c0392b'))
items.append((cyl((38, -2), 9.3, 0.6, 43.5), '#f2d16b'))
items.append((cyl((33, -5), 3.2, 1.2, 44, res=40), '#fdfdfd'))
items.append((pv.ParametricTorus(ringradius=1.6, crosssectionradius=0.35).translate((33, -5, 45.3)), '#e86a8e'))
items.append((pv.ParametricEllipsoid(3.2, 2.4, 1.2).translate((41, 1, 44.6)), '#fff6dc'))
items.append((pv.Sphere(radius=1.4, center=(41.6, 1, 45.4)), '#f0a020'))
items.append((boxm(36, 40, -6, 2, 44, 47), '#3d6b35'))
for dy in (-1.2, 1.2):
    items.append((pv.Cylinder(center=(40, 8 + dy, 47), direction=(1, 0.15, 0.6), radius=0.5, height=26), '#e7cf9a'))
# noren sign behind
items.append((boxm(-48, 48, 26, 30, 0, 4), '#7a4a22'))
for x in (-46, 46):
    items.append((boxm(x - 2, x + 2, 26, 30, 0, 140), '#7a4a22'))
items.append((boxm(-48, 48, 26, 30, 136, 142), '#7a4a22'))
for i, x in enumerate(np.linspace(-44, 44, 5)[:-1]):
    items.append((boxm(x + 0.6, x + 21.4, 24.5, 25.5, 108, 136), '#f5f0e6'))
txt = pv.Text3D('ICHIRAKU', depth=1.2, height=10).rotate_x(90).translate((-30, 24, 117))
items.append((txt, '#c0392b'))
render('c5_ichiraku', items, cam=[(110, -205, 130), (0, 0, 45), (0, 0, 1)])

# ---------- 6. Scroll ----------
items = [(boxm(-48, 44, -36, 26, -3, 0), '#efe2c0')]
for x in (-50, 46):
    items.append((pv.Cylinder(center=(x, -5, 3), direction=(0, 1, 0), radius=6.5, height=66, resolution=40), '#b23a2a'))
    for yy in (-40, 30):
        items.append((pv.Cylinder(center=(x, yy, 3), direction=(0, 1, 0), radius=3, height=4, resolution=30), '#d9b45a'))
for i, (x, y) in enumerate([(-38, -20), (-38, -8), (-38, 4), (30, -24), (30, -12), (30, 0)]):
    items.append((boxm(x - 3.5, x + 3.5, y - 3.5, y + 3.5, 0, 0.3), '#2b2b2b'))
lf, lg = leaf(-3, -27, 0, 0.5, 0.75)
items += [(lf, '#c0392b'), (lg, '#5a1a12')]
clones = []
for dx, dy in [(-32, 22), (28, 22)]:
    c = FIG.copy().scale(0.62).translate((dx, dy, 0))
    clones.append((c, '#f2a65a', 0.55))
render('c6_scroll', items, fig_items=clones, cam=[(105, -200, 115), (-3, 0, 35), (0, 0, 1)])

# ---------- 7. Konoha gate ----------
items = [(boxm(-50, 50, -42, 34, -6, 0), '#b9b2a3')]
for i, y in enumerate(np.arange(-40, 30, 7)):
    for j, x in enumerate(np.arange(-14 + (i % 2) * 3.5, 14, 7)):
        items.append((boxm(x + 0.4, x + 6.6, y + 0.4, y + 6.6, 0, 0.6), '#d8d1c0'))
for x in (-40, 34):
    items.append((boxm(x - 4.5, x + 4.5, 22, 31, 0, 112), '#2f7a3a'))
    items.append((boxm(x - 6, x + 6, 20.5, 32.5, 0, 6), '#7a6a55'))
items.append((boxm(-50, 44, 21, 32, 104, 112), '#2f7a3a'))
roof = Polygon([(-56, 0), (50, 0), (44, 10), (-50, 10)])
r_m = prism(roof, 0, 16)
items.append(([m.rotate_x(90, point=(0, 0, 0)).translate((0, 34, 112)) for m in r_m], '#1f5a2a'))
items.append((boxm(-14, 8, 19.5, 21, 82, 100), '#e8dcc0'))
lf, lg = leaf(0, 0, 0, 1.0, 0.6)
items.append(([m.rotate_x(90, point=(0, 0, 0)).translate((-3, 19.5, 91)) for m in lf], '#c0392b'))
render('c7_gate', items, cam=[(120, -215, 150), (-3, 0, 55), (0, 0, 1)])
print('done')
