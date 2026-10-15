# Runs inside Fusion (execute_code): builds the training-ground stand as components.
import json, math
G = json.load(open('C:/Users/Danil/Desktop/Fusion/naruto/scripts/data/train_geo.json'))
root = design.rootComponent
P3 = adsk.core.Point3D.create
VI = adsk.core.ValueInput
NB = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
J = adsk.fusion.FeatureOperations.JoinFeatureOperation
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
cm = lambda v: v / 10.0
LOG = []

for o in root.occurrences:
    if o.component.name == 'Stand':
        o.isLightBulbOn = False


def new_comp(name):
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = name
    return occ.component


def plane(comp, zmm):
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(comp.xYConstructionPlane, VI.createByReal(cm(zmm)))
    pl = comp.constructionPlanes.add(pi)
    pl.isLightBulbOn = False
    return pl


def poly(sk, pts):
    L = sk.sketchCurves.sketchLines
    ps = [P3(cm(x), cm(y), 0) for x, y in pts]
    first = prev = None
    n = len(ps)
    for i in range(n):
        if i < n - 1:
            ln = L.addByTwoPoints(prev if prev else ps[i], ps[i + 1])
        else:
            ln = L.addByTwoPoints(prev, first)
        if i == 0:
            first = ln.startSketchPoint
        prev = ln.endSketchPoint


def circle(sk, x, y, r):
    return sk.sketchCurves.sketchCircles.addByCenterRadius(P3(cm(x), cm(y), 0), cm(r))


def profs(sk, pick=None):
    oc = adsk.core.ObjectCollection.create()
    for p in sk.profiles:
        if pick is None or pick(p):
            oc.add(p)
    return oc


def extrude(comp, prof, dist_mm, op, body=None):
    ex = comp.features.extrudeFeatures
    inp = ex.createInput(prof, op)
    inp.setDistanceExtent(False, VI.createByReal(cm(dist_mm)))
    if body is not None and op in (J, CUT):
        inp.participantBodies = [body]
    return ex.add(inp)


def edges_circle_at(body, r_mm, z_mm, tol=0.02):
    oc = adsk.core.ObjectCollection.create()
    for e in body.edges:
        g = e.geometry
        if g.objectType == adsk.core.Circle3D.classType() and abs(g.radius * 10 - r_mm) < tol and abs(g.center.z * 10 - z_mm) < tol:
            oc.add(e)
    return oc


def fillet(comp, oc, r_mm):
    if oc.count == 0:
        LOG.append('fillet: no edges'); return None
    fi = comp.features.filletFeatures.createInput()
    fi.addConstantRadiusEdgeSet(oc, VI.createByReal(cm(r_mm)), True)
    try:
        return comp.features.filletFeatures.add(fi)
    except Exception as e:
        LOG.append('fillet fail %s' % e); return None


def chamfer(comp, oc, d_mm):
    if oc.count == 0:
        LOG.append('chamfer: no edges'); return None
    ci = comp.features.chamferFeatures.createInput2()
    ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(oc, VI.createByReal(cm(d_mm)), True)
    try:
        return comp.features.chamferFeatures.add(ci)
    except Exception as e:
        LOG.append('chamfer fail %s' % e); return None


TOP = G['TOP']; THK = G['THK']; ZB = TOP - THK

# ---------------- Ground ----------------
gc = new_comp('TrainingGround')
sk = gc.sketches.add(plane(gc, ZB)); sk.name = 'Outline'
pts = adsk.core.ObjectCollection.create()
for x, y in G['OUTLINE']:
    pts.add(P3(cm(x), cm(y), 0))
spl = sk.sketchCurves.sketchFittedSplines.add(pts)
spl.isClosed = True
ground = extrude(gc, profs(sk), THK, NB).bodies.item(0)
ground.name = 'Ground'


def spline_edges_at(z_mm):
    oc = adsk.core.ObjectCollection.create()
    for e in ground.edges:
        if e.geometry.objectType == adsk.core.NurbsCurve3D.classType():
            bb = e.boundingBox
            if abs(bb.minPoint.z * 10 - z_mm) < 0.01 and abs(bb.maxPoint.z * 10 - z_mm) < 0.01:
                oc.add(e)
    return oc


fillet(gc, spline_edges_at(TOP), 1.5)
chamfer(gc, spline_edges_at(ZB), 0.5)

ptop = plane(gc, TOP)
# stump
sx, sy, sr = G['STUMP']
sk = gc.sketches.add(ptop); sk.name = 'Stump'
circle(sk, sx, sy, sr)
extrude(gc, profs(sk), G['STUMP_H'], J, ground)
sk = gc.sketches.add(plane(gc, TOP + G['STUMP_H'])); sk.name = 'StumpRings'
for r in (2.4, 5.0):
    circle(sk, sx, sy, r - 0.35); circle(sk, sx, sy, r + 0.35)
def _ring(p):
    ar = p.areaProperties().area
    return p.profileLoops.count == 2 and any(abs(ar - 2 * math.pi * cm(r) * cm(0.7)) < 0.004 for r in (2.4, 5.0))
extrude(gc, profs(sk, _ring), -0.6, CUT, ground)
fillet(gc, edges_circle_at(ground, sr, TOP + G['STUMP_H']), 0.8)

# stones (domes)
for x, y, r in G['STONES']:
    sk = gc.sketches.add(ptop); circle(sk, x, y, r)
    extrude(gc, profs(sk), r * 0.95, J, ground)
    fillet(gc, edges_circle_at(ground, r, TOP + r * 0.95), r * 0.85)

# bells (domes)
for x, y in G['BELLS']:
    sk = gc.sketches.add(ptop); circle(sk, x, y, 3.4)
    extrude(gc, profs(sk), 3.6, J, ground)
    fillet(gc, edges_circle_at(ground, 3.4, TOP + 3.6), 3.1)

# grass tufts: 3 rounded stubs each
for i, (x, y) in enumerate(G['TUFTS']):
    for k, (dx, dy, h) in enumerate([(0, 0, 5.0), (2.6, 1.0, 3.8), (-2.3, 1.6, 4.3)]):
        sk = gc.sketches.add(ptop); circle(sk, x + dx, y + dy, 1.2)
        extrude(gc, profs(sk), h, J, ground)
        fillet(gc, edges_circle_at(ground, 1.2, TOP + h), 1.1)

# shuriken lying on the ground
sk = gc.sketches.add(ptop); sk.name = 'Shuriken'
poly(sk, G['shuriken'])
extrude(gc, profs(sk), 1.6, J, ground)
sk = gc.sketches.add(plane(gc, TOP + 1.6)); circle(sk, G['SHURIKEN'][0], G['SHURIKEN'][1], 1.3)
extrude(gc, profs(sk), -1.0, CUT, ground)

# cuts: foot pockets, log sockets, kunai slots
sk = gc.sketches.add(ptop); sk.name = 'FootPockets'
for f in G['feet']:
    poly(sk, f)
extrude(gc, profs(sk), -3.0, CUT, ground)
oc = adsk.core.ObjectCollection.create()
for f in ground.faces:
    bb = f.boundingBox
    if abs(bb.maxPoint.z * 10 - TOP) < 1e-3 and abs(bb.minPoint.z * 10 - (TOP - 3)) < 1e-3:
        for e in f.edges:
            eb = e.boundingBox
            if abs(eb.minPoint.z * 10 - TOP) < 1e-3 and abs(eb.maxPoint.z * 10 - TOP) < 1e-3:
                oc.add(e)
chamfer(gc, oc, 0.4)

sk = gc.sketches.add(ptop); sk.name = 'LogSockets'
for x, y in G['LOGS']:
    circle(sk, x, y, G['SOCKET_D'] / 2)
extrude(gc, profs(sk), -G['SOCKET_DEPTH'], CUT, ground)
for x, y in G['LOGS']:
    chamfer(gc, edges_circle_at(ground, G['SOCKET_D'] / 2, TOP), 0.4)
    break

sk = gc.sketches.add(ptop); sk.name = 'KunaiSlots'
for s in G['slots']:
    poly(sk, s)
extrude(gc, profs(sk), -G['TAB_DEPTH'], CUT, ground)

# ---------------- Logs ----------------
lc = new_comp('Logs')
R_LOG = G['LOG_D'] / 2
for i, (x, y) in enumerate(G['LOGS']):
    sk = lc.sketches.add(plane(lc, TOP)); circle(sk, x, y, R_LOG)
    b = extrude(lc, profs(sk), G['LOG_H'], NB).bodies.item(0)
    b.name = 'Log%d' % (i + 1)
    ztop = TOP + G['LOG_H']
    chamfer(lc, edges_circle_at(b, R_LOG, ztop), 0.8)
    # bark grooves
    sk = lc.sketches.add(plane(lc, ztop))
    for k in range(7):
        a = 2 * math.pi * k / 7 + i
        ca, sa = math.cos(a), math.sin(a)
        r0, r1, w = R_LOG - 0.5, R_LOG + 0.5, 0.4
        pts = [(x + r0 * ca - w * sa, y + r0 * sa + w * ca), (x + r1 * ca - w * sa, y + r1 * sa + w * ca),
               (x + r1 * ca + w * sa, y + r1 * sa - w * ca), (x + r0 * ca + w * sa, y + r0 * sa - w * ca)]
        poly(sk, pts)
    extrude(lc, profs(sk, lambda p: p.areaProperties().area < 0.02), -(G['LOG_H'] - 4), CUT, b)
    # rope bands
    for zr in (40.0, 43.2):
        sk = lc.sketches.add(plane(lc, TOP + zr))
        circle(sk, x, y, R_LOG + 0.9); circle(sk, x, y, R_LOG - 0.6)
        extrude(lc, profs(sk, lambda p: p.profileLoops.count == 2), 2.6, J, b)
        fillet(lc, edges_circle_at(b, R_LOG + 0.9, TOP + zr), 0.7)
        fillet(lc, edges_circle_at(b, R_LOG + 0.9, TOP + zr + 2.6), 0.7)
    # peg
    sk = lc.sketches.add(plane(lc, TOP)); circle(sk, x, y, G['PEG_D'] / 2)
    extrude(lc, profs(sk, lambda p: p.areaProperties().area < math.pi * cm(G['PEG_D'] / 2 + 0.01) ** 2), -(G['SOCKET_DEPTH'] - 0.4), J, b)
    chamfer(lc, edges_circle_at(b, G['PEG_D'] / 2, TOP - G['SOCKET_DEPTH'] + 0.4), 0.4)

# ---------------- Kunai ----------------
kc = new_comp('Kunai')
for i, (x, y, yaw) in enumerate(G['KUNAI_SLOTS']):
    sk = kc.sketches.add(kc.xYConstructionPlane)
    poly(sk, [(px, py + 0.2) for px, py in G['kunai_ext']])
    for h in G['kunai_holes']:
        poly(sk, [(px, py + 0.2) for px, py in h])
    best = max(sk.profiles, key=lambda p: p.areaProperties().area)
    oc = adsk.core.ObjectCollection.create(); oc.add(best)
    b = extrude(kc, oc, G['KUNAI_T'], NB).bodies.item(0)
    b.name = 'Kunai%d' % (i + 1)
    sk = kc.sketches.add(plane(kc, G['KUNAI_T']))
    for w in G['kunai_wraps']:
        poly(sk, [(px, py + 0.2) for px, py in w])
    extrude(kc, profs(sk, lambda p: p.areaProperties().area < 0.05), -0.4, CUT, b)
    # pose: stand up (rot X +90), centre thickness, yaw, move to slot; tab bottom 0.2 above slot floor
    m = adsk.core.Matrix3D.create()
    m.setToRotation(math.pi / 2, adsk.core.Vector3D.create(1, 0, 0), P3(0, 0, 0))
    t = adsk.core.Matrix3D.create(); t.translation = adsk.core.Vector3D.create(0, cm(G['KUNAI_T'] / 2), 0); m.transformBy(t)
    rz = adsk.core.Matrix3D.create(); rz.setToRotation(math.radians(yaw), adsk.core.Vector3D.create(0, 0, 1), P3(0, 0, 0)); m.transformBy(rz)
    t2 = adsk.core.Matrix3D.create(); t2.translation = adsk.core.Vector3D.create(cm(x), cm(y), cm(TOP)); m.transformBy(t2)
    oc = adsk.core.ObjectCollection.create(); oc.add(b)
    mi = kc.features.moveFeatures.createInput2(oc); mi.defineAsFreeMove(m); kc.features.moveFeatures.add(mi)

res = {}
for c in (gc, lc, kc):
    for b in c.bRepBodies:
        bb = b.boundingBox
        res[b.name] = [round(v * 10, 1) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z, bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)] + [round(b.volume, 2)]
res['log'] = LOG
res
