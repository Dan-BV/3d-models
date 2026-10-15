"""Assign reference-like colours to the Naruto mesh triangles by geometric zones."""
import numpy as np

PAL = {
    'hair':   (0.96, 0.72, 0.20),
    'skin':   (0.98, 0.82, 0.70),
    'orange': (0.95, 0.47, 0.13),
    'dark':   (0.22, 0.22, 0.25),
    'band':   (0.17, 0.17, 0.20),
    'metal':  (0.80, 0.82, 0.86),
    'white':  (0.95, 0.94, 0.90),
    'iris':   (0.25, 0.60, 0.92),
    'pupil':  (0.08, 0.10, 0.18),
    'eyewht': (0.99, 0.99, 0.99),
    'brown':  (0.52, 0.33, 0.20),
    'pouch':  (0.30, 0.30, 0.32),
    'mark':   (0.45, 0.28, 0.22),
}

XC = -3.0          # torso / head centre x
HX, HY = -2.8, 0.0  # head axis


def paint(P, T):
    V = P[T]
    C = V.mean(1)
    x, y, z = C[:, 0], C[:, 1], C[:, 2]
    N = np.cross(V[:, 1] - V[:, 0], V[:, 2] - V[:, 0])
    N /= np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
    n = len(T)
    lab = np.full(n, 'orange', dtype=object)
    rh = np.hypot(x - HX, y - HY)

    # ---- feet / sandals
    lab[z < 1.8] = 'dark'
    feet = (z >= 1.8) & (z < 5.2)
    lab[feet] = 'skin'
    lab[feet & (y > -5.5)] = 'dark'                     # heel strap / back of sandal
    lab[feet & (z > 3.6) & (y > -11) & (y <= -5.5)] = 'dark'  # instep strap
    lab[(z >= 5.2) & (z < 9.6)] = 'dark'                # ankle wrap

    # ---- shorts (orange by default), leg stripes, holster
    thigh_l = (x < -6.5) & (z > 14.8) & (z < 20.2) & (x > -19.5)
    lab[thigh_l & (z <= 16.6)] = 'white'
    lab[thigh_l & (z > 16.6) & (z <= 18.3)] = 'dark'
    lab[thigh_l & (z > 18.3)] = 'white'
    holster = (x < -15.8) & (z > 10.5) & (z < 23.0) & (y > -7) & (y < 5)
    lab[holster] = 'pouch'

    # ---- jacket
    hem = (z >= 23.8) & (z < 26.3) & (x > -18.6) & (x < 12.5)
    lab[hem] = 'dark'
    yoke = ((z >= 42.8) | ((z >= 40.0) & (y > 2))) & (z < 48.5)
    lab[yoke] = 'dark'
    zip_ = (z >= 23.8) & (z < 48.5) & (np.abs(x - XC) < 3.0) & (y < -6)
    lab[zip_] = 'dark'
    lab[zip_ & (np.abs(x - XC) < 0.45)] = 'metal'
    pads = (z > 43.5) & (z < 50.5) & (y > -9) & (y < 9) & (((x < -14.2) & (x > -20)) | ((x > 9.6) & (x < 14.8)))
    lab[pads] = 'brown'

    # hands + cuffs
    hand = (z > 17.5) & (z < 26.6) & ((x < -18.6) | (x > 12.6))
    lab[hand] = 'skin'
    cuff = (z >= 26.6) & (z < 30.8) & ((x < -19.3) | (x > 13.6))
    lab[cuff] = 'dark'

    # back: spiral emblem, pouch and strap
    r_sp = np.hypot(x + 3.1, z - 40.0)
    back_up = (y > 5) & (r_sp < 3.7)
    lab[back_up] = 'white'
    lab[back_up & (r_sp > 1.6) & (r_sp < 2.4)] = 'dark'
    pouch = (y > 8.4) & (z > 19.5) & (z < 43.6) & (x > -2.3) & (x < 9.9)
    pouch |= (y > 5.0) & (z >= 41.0) & (z < 47.0) & (x > 2.1) & (x < 4.7)
    lab[pouch] = 'pouch'

    # ---- collar (fur)
    collar = ((z >= 47.0) | ((z >= 46.2) & (y > 0))) & (z < 53.3)
    collar |= (z >= 53.3) & (z < 55.2) & (rh > 17.0) & (y > 3)
    lab[collar] = 'white'

    # ---- head: skin front, hair back
    head = (z >= 53.3) & ~collar & (z < 67.6)
    lab[head] = 'hair'
    lab[head & ((y < -7.0) | ((z < 64.5) & (y < 3.0)))] = 'skin'

    # eyes (front-facing ellipses)
    front = y < -12
    for ex, ez, rx, rz in [(-10.0, 62.8, 3.15, 2.85), (4.85, 63.1, 3.45, 2.95)]:
        e = front & (((x - ex) / rx) ** 2 + ((z - ez) / rz) ** 2 < 1)
        lab[e] = 'eyewht'
        ix = ex + (0.0 if ex < 0 else -0.85)
        ir = front & (((x - ix) / 2.25) ** 2 + ((z - 62.4) / 2.45) ** 2 < 1)
        lab[ir] = 'iris'
        pp = front & (((x - ix) / 0.95) ** 2 + ((z - 62.3) / 1.1) ** 2 < 1)
        lab[pp] = 'pupil'

    # ---- headband
    rx_, ry_ = (x - HX) / np.maximum(rh, 1e-6), (y - HY) / np.maximum(rh, 1e-6)
    radial = N[:, 0] * rx_ + N[:, 1] * ry_
    cand = (z >= 67.6) & (z < 79.2) & (rh < 22.2) & (np.abs(N[:, 2]) < 0.5) & (radial > 0.72)
    th = np.degrees(np.arctan2(y - HY, x - HX))
    bins = np.floor((th + 180) / 8).astype(int)
    ref = np.full(46, 99.0)
    for bi in np.unique(bins[cand]):
        rr = rh[cand & (bins == bi)]
        if len(rr) > 20: ref[bi] = np.percentile(rr, 15)
    band = cand & (rh < ref[bins] + 0.9) & (y < 6.0)
    lab[(z >= 67.6)] = 'hair'
    lab[band] = 'band'
    plate = (y < -12.5) & (x > -12.8) & (x < 7.2) & (z > 68.6) & (z < 78.0) & (rh < 22.6) & (N[:, 1] < -0.3)
    lab[plate] = 'metal'

    # ribbon tails
    ribbon = (x > 13.0) & (y > 2.0) & (z > 40) & (z < 70) & (rh > 15.5)
    lab[ribbon & ~(lab == 'skin')] = 'band'

    cols = np.array([PAL[k] for k in lab])
    return cols, lab
