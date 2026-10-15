import numpy as np, pyvista as pv, sys, json
from shapely.geometry import Point, Polygon
from shapely import contains_xy
import paint
pv.OFF_SCREEN = True
G = json.load(open('train_geo.json'))
TOP = G['TOP']

P = np.fromfile('nodes.bin', '<f8').reshape(-1, 3) * 10
T = np.fromfile('tris.bin', '<i4').reshape(-1, 3)
FIG = pv.PolyData(P, np.c_[np.full(len(T), 3), T].ravel())
cols, _ = paint.paint(P, T)
FIG.cell_data['rgb'] = (cols * 255).astype(np.uint8)

hexc = lambda h: np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.uint8)
C = dict(grass='#78a24a', soil='#7b5636', bark='#7a4b2a', wood='#d8b27a', rope='#d9c38c',
         stone='#a19d93', bell='#e2b133', tuft='#4f8a2e', steel='#5f6873', steel_dk='#3f464f', ring='#b5884c')


def cell_info(m):
    m = m.compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=False)
    c = m.cell_centers().points
    return m, c, m.cell_data['Normals']


def paint_ground():
    m, c, n = cell_info(pv.read('tg_Ground.stl'))
    x, y, z = c.T
    lab = np.where(n[:, 2] > 0.55, 'grass', 'soil').astype(object)
    sx, sy, sr = G['STUMP']
    rs = np.hypot(x - sx, y - sy)
    st = (rs < sr + 0.2) & (z > TOP + 0.05)
    lab[st] = 'bark'
    lab[st & (n[:, 2] > 0.7) & (z > TOP + G['STUMP_H'] - 0.9)] = 'wood'
    for sx_, sy_, r in G['STONES']:
        lab[(np.hypot(x - sx_, y - sy_) < r + 0.1) & (z > TOP + 0.05)] = 'stone'
    for bx, by in G['BELLS']:
        lab[(np.hypot(x - bx, y - by) < 3.5) & (z > TOP + 0.05)] = 'bell'
    for tx, ty in G['TUFTS'] + [[38.0, -6.0], [-38.0, -18.0], [6.0, -36.0]]:
        for dx, dy in [(0, 0), (2.6, 1.0), (-2.3, 1.6)]:
            lab[(np.hypot(x - tx - dx, y - ty - dy) < 1.3) & (z > TOP + 0.05)] = 'tuft'
    star = Polygon(G['shuriken'])
    inside = contains_xy(star.buffer(0.15), x, y) & (z > TOP + 0.05) & (z < TOP + 1.7)
    lab[inside] = 'steel_dk'
    m.cell_data['rgb'] = np.array([hexc(C[k]) for k in lab])
    return m


def paint_log(name, lx, ly):
    m, c, n = cell_info(pv.read(name))
    x, y, z = c.T
    r = np.hypot(x - lx, y - ly)
    lab = np.full(len(c), 'bark', dtype=object)
    for zr in (40.0, 43.2):
        lab[(z > TOP + zr - 0.05) & (z < TOP + zr + 2.65) & (r > G['LOG_D'] / 2 + 0.05)] = 'rope'
    lab[(n[:, 2] > 0.7) & (z > TOP + G['LOG_H'] - 1.0)] = 'wood'
    m.cell_data['rgb'] = np.array([hexc(C[k]) for k in lab])
    return m


def paint_kunai(name):
    m, c, n = cell_info(pv.read(name))
    z = c[:, 2]
    lab = np.where(z > TOP + 16.0, 'steel_dk', 'steel').astype(object)
    lab[z > TOP + 26.5] = 'steel'
    m.cell_data['rgb'] = np.array([hexc(C[k]) for k in lab])
    return m


parts = [paint_ground()] + [paint_log(f'tg_Log{i + 1}.stl', *G['LOGS'][i]) for i in range(3)] + [paint_kunai(f'tg_Kunai{i}.stl') for i in (1, 2)]


def shot(fn, vec, zoom=1.25, size=(1600, 1600)):
    pl = pv.Plotter(off_screen=True, window_size=size, lighting='none')
    pl.set_background('#24252b', top='#4a4c55')
    pl.add_light(pv.Light(position=(160, -220, 260), focal_point=(0, 0, 40), intensity=0.85, light_type='scene light'))
    pl.add_light(pv.Light(position=(-220, -120, 120), focal_point=(0, 0, 40), intensity=0.45, light_type='scene light'))
    pl.add_light(pv.Light(position=(40, 260, 200), focal_point=(0, 0, 40), intensity=0.45, light_type='scene light'))
    pl.add_light(pv.Light(position=(0, -60, -150), focal_point=(0, 0, 40), intensity=0.2, light_type='scene light'))
    kw = dict(rgb=True, scalars='rgb', ambient=0.28, diffuse=0.8, specular=0.18, specular_power=25)
    pl.add_mesh(FIG, smooth_shading=True, **kw)
    for m in parts:
        pl.add_mesh(m, smooth_shading=False, **kw)
    pl.view_vector(vec, viewup=(0, 0, 1)); pl.reset_camera(); pl.camera.zoom(zoom)
    pl.enable_anti_aliasing('ssaa')
    pl.screenshot(fn); pl.close()


out = sys.argv[1]
shot(out + '/render_front.png', (0.45, -1, 0.32))
shot(out + '/render_back.png', (1.0, 0.75, 0.42))
print('ok')
