"""Filament mass per feature type and a rough print time from a Cura G-code file."""
import math, sys
for path in sys.argv[1:]:
    typ = None; E = 0; tot = {}; x = y = z = 0; f = 1500; t = 0.0
    for l in open(path):
        if l.startswith(';TYPE:'): typ = l[6:].strip(); continue
        if l.startswith('G92') and 'E0' in l: E = 0; continue
        if l[:3] in ('G1 ', 'G0 '):
            m = {}
            for tok in l.split(';')[0].split()[1:]:
                try: m[tok[0]] = float(tok[1:])
                except ValueError: pass
            f = m.get('F', f)
            nx, ny, nz = m.get('X', x), m.get('Y', y), m.get('Z', z)
            dist = math.dist((x, y, z), (nx, ny, nz))
            if 'E' in m:
                de = m['E'] - E; E = m['E']
                if de > 0: tot[typ] = tot.get(typ, 0) + de
                if dist == 0: dist = abs(de)
            t += dist / (f / 60) * 1.25 if f else 0   # +25 % for acceleration
            x, y, z = nx, ny, nz
    gpm = math.pi * (1.75 / 2) ** 2 * 1.24 / 1000
    sup = sum(v for k, v in tot.items() if k and k.startswith('SUPPORT')) * gpm
    print('%s: total %.1f g, support %.1f g, model %.1f g, ~%.1f h'
          % (path, sum(tot.values()) * gpm, sup, sum(tot.values()) * gpm - sup, t / 3600))
