"""Slice an STL with a .curaprofile via CuraEngine and check that every overhang gets support.

usage: python slice_check.py <profile.curaprofile> <model.stl> <tag> [key=value ...]

The STL must be centred at XY 0 (the engine shifts it by +machine_width/2).
Overhang = downward facet steeper than support_angle from vertical with air below it
(a ray down from the facet travels more than 2 layers before hitting the model/bed).
Each overhang cluster is reported as covered when support extrusion exists right below it.
"""
import json, os, struct, subprocess, sys, time, zipfile
import numpy as np

S = os.path.dirname(os.path.abspath(__file__))
CURA = r'C:\Program Files\UltiMaker Cura 5.13.0'
R = CURA + r'\share\cura\resources'
sys.path.insert(0, S)
import curaeval

prof, stl, tag = sys.argv[1], sys.argv[2], sys.argv[3]
over = dict(a.split('=', 1) for a in sys.argv[4:])

vals = {}
z = zipfile.ZipFile(prof)
for n in z.namelist():
    for l in z.read(n).decode().split('[values]')[1].strip().splitlines():
        k, v = [s.strip() for s in l.split('=', 1)]
        vals[k] = v
vals.pop('adhesion_z_offset', None)
vals.update(over)
vals['center_object'] = 'false'
gv, ev = curaeval.resolve(vals)


def wr(name, inh, v):
    p = S + '/' + name + '.def.json'
    json.dump({"version": 2, "name": name, "inherits": inh, "metadata": {},
               "overrides": {k: {"default_value": x} for k, x in v.items() if x is not None}}, open(p, 'w'))
    return p


out = S + f'/{tag}.gcode'
gj = wr('g_' + tag, 'creality_ender3pro', gv)
ej = wr('e_' + tag, 'creality_base_extruder_0', ev)
cmd = [CURA + r'\CuraEngine.exe', 'slice', '-j', gj, '-e0', '-j', ej, '-l', stl, '-o', out]
t = time.time()
if os.environ.get('SKIP_SLICE'):
    p = type('P', (), {'returncode': 0})()
else:
  p = subprocess.run(cmd, capture_output=True, text=True,
                     env=dict(os.environ, CURA_ENGINE_SEARCH_PATH=R + r'\definitions;' + R + r'\extruders'))
print('engine rc', p.returncode, '%.0fs' % (time.time() - t))
if p.returncode:
    print(p.stdout[-2000:], p.stderr[-3000:])
    sys.exit(1)

# --- G-code: support extrusion points and outer wall (for the XY offset)
typ = None; zc = 0; x = y = 0; sup = []; W = []
for l in open(out):
    if l.startswith(';TYPE:'):
        typ = l[6:].strip(); continue
    if l.startswith('G1') or l.startswith('G0'):
        m = {}
        for tok in l.split(';')[0].split()[1:]:
            if tok[0] in 'XYZE':
                try: m[tok[0]] = float(tok[1:])
                except ValueError: pass
        x = m.get('X', x); y = m.get('Y', y); zc = m.get('Z', zc)
        if 'E' in m and typ and typ.startswith('SUPPORT'): sup.append((x, y, zc))
        if 'E' in m and typ == 'WALL-OUTER': W.append((x, y, zc))
sup = np.array(sup) if sup else np.zeros((0, 3))
W = np.array(W)
ox, oy = (W[:, 0].min() + W[:, 0].max()) / 2, (W[:, 1].min() + W[:, 1].max()) / 2
d = open(stl, 'rb').read(); n = struct.unpack('<I', d[80:84])[0]
T = np.frombuffer(d[84:], dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]), count=n)['v'].reshape(-1, 3, 3).astype(float)
mx, my = (T[:, :, 0].min() + T[:, :, 0].max()) / 2, (T[:, :, 1].min() + T[:, :, 1].max()) / 2
if len(sup):
    sup[:, 0] -= ox - mx; sup[:, 1] -= oy - my
print('support extrusion points', len(sup))

# --- overhang facets with air below
lh = float(gv['layer_height']); ang = float(os.environ.get('CHECK_ANGLE', gv['support_angle']))
c = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
A = np.linalg.norm(c, axis=1) / 2
nz = c[:, 2] / np.maximum(2 * A, 1e-12)
cen = T.mean(1)
cand = (nz < -np.sin(np.radians(ang))) & (cen[:, 2] > 1.0) & (A > 0)
idx = np.where(cand)[0]


def gap_below(px, py, pz):
    lo, hi = T.min(1), T.max(1)
    m = (lo[:, 0] <= px) & (hi[:, 0] >= px) & (lo[:, 1] <= py) & (hi[:, 1] >= py) & (lo[:, 2] < pz - 1e-3)
    a, b, cc = T[m, 0], T[m, 1], T[m, 2]
    v0, v1 = cc[:, :2] - a[:, :2], b[:, :2] - a[:, :2]
    v2 = np.array([px, py]) - a[:, :2]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    with np.errstate(all='ignore'):
        u = (v2[:, 0] * v1[:, 1] - v1[:, 0] * v2[:, 1]) / den
        v = (v0[:, 0] * v2[:, 1] - v2[:, 0] * v0[:, 1]) / den
    h = (u >= 0) & (v >= 0) & (u + v <= 1) & (den != 0)
    zz = a[h, 2] + u[h] * (cc[h, 2] - a[h, 2]) + v[h] * (b[h, 2] - a[h, 2])
    zz = zz[zz < pz - 0.05]
    # an odd number of surfaces below means the facet lies inside another shell
    # (bust bottom sunk into the podium, eye insert walls inside the head)
    return pz - (zz.max() if len(zz) else 0.0), len(zz) % 2 == 1


# cluster overhang facets on a 1 mm grid
keys = np.floor(cen[idx] / 1.0).astype(int)
clusters = {}
for i, k in zip(idx, map(tuple, keys)):
    clusters.setdefault(k, []).append(i)
rows = []
for k, ids in clusters.items():
    ids = np.array(ids); area = A[ids].sum()
    j = ids[np.argmin(cen[ids, 2])]
    px, py, pz = cen[j]
    g, inside = gap_below(px, py, pz)
    if inside or g <= 2 * lh + 0.2:     # internal, or bridged by the layer below
        continue
    near = (np.hypot(sup[:, 0] - px, sup[:, 1] - py) < 1.2) & (sup[:, 2] < pz) & (sup[:, 2] > pz - 1.0) if len(sup) else np.zeros(0, bool)
    rows.append((pz, px, py, area, g, int(near.sum())))
rows.sort()
need = [r for r in rows if r[3] >= 0.05]
bad = [r for r in need if r[5] == 0]
print('overhang clusters needing support: %d, covered: %d, NOT covered: %d' % (len(need), len(need) - len(bad), len(bad)))
big = [r for r in bad if r[4] > 1.0]
print('  of them with air gap > 1 mm: %d, total area %.1f mm2' % (len(big), sum(r[3] for r in big)))
for r in sorted(big, key=lambda r: -r[3])[:int(os.environ.get('SHOW', 25))]:
    print('  uncovered z=%.1f x=%.1f y=%.1f area=%.2f mm2 gap below=%.1f mm' % r[:5])
for line in open(out):
    if line.startswith(';TIME:') or line.startswith(';Filament used'):
        print(line.strip())
np.save(S + f'/{tag}_sup.npy', sup)
