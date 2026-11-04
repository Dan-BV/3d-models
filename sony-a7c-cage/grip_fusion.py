"""Builds the cage's side grip in Autodesk Fusion as a parametric solid.

Run inside Fusion (Utilities > Scripts, or through the Fusion MCP); run grip_sections.py first
if its data changed. It adds a component "a7c_grip" to the active design:

  loft     through the horizontal sections of grip_sections.json: the plan outline traced on
           the product photos with the waist that runs round the grip under its flared top
  top      loft of three XY sketches, intersect: scooped across, rising from the rear
  fillets  R5 round the top rim, R3 round the bottom
  pocket   for the camera grip in height bands (narrower at the camera's finger recess)
  battery  door opening under the grip

then exports a7c_grip.step and a7c_grip.stl next to this file.
Coordinates are the cage's (see cage.py), in mm, converted to cm for Fusion.
"""
import json
import os

import adsk.core
import adsk.fusion

MM = 0.1
HERE = os.path.dirname(os.path.abspath(__file__))

# top surface: the scooped top edge seen from the front, at three depths (z) so the top also
# rises from the rear (60.6) to the front (62.4). Lofted into one smooth cutting tool.
SCOOP = [(-19.0, -0.4), (-20.8, 0.4), (-23.5, 0.8), (-28.0, 0.7), (-34.0, -0.3), (-44.0, -1.4),
         (-54.0, -0.8), (-62.0, 0.3), (-70.0, 0.6)]     # (x, dy) relative to the base height
TOP_AT = [(20.0, 60.4), (45.0, 62.0), (70.0, 62.0)]     # (z, base height)

BATTERY = (-56.2, -21.3, -5.2, 40.2)   # cage.BATT grown 0.2 mm so the faces sit inside the frame
Y_BOT = -9.5
TOP_R, BOTTOM_R = 5.0, 3.0


def _plane(comp, base, offset_mm):
    if abs(offset_mm) < 1e-9:
        return base
    inp = comp.constructionPlanes.createInput()
    inp.setByOffset(base, adsk.core.ValueInput.createByReal(offset_mm * MM))
    return comp.constructionPlanes.add(inp)


def _profile_sketch(comp, plane, to3d, spline_pts, line_pts, name):
    """closed profile: fitted spline through spline_pts, then straight lines through
    line_pts back to the first spline point. to3d maps a 2D point (mm) to model mm."""
    sk = comp.sketches.add(plane)
    sk.name = name

    def sp(p):
        x, y, z = to3d(p)
        return sk.modelToSketchSpace(adsk.core.Point3D.create(x * MM, y * MM, z * MM))
    col = adsk.core.ObjectCollection.create()
    for p in spline_pts:
        col.add(sp(p))
    spl = sk.sketchCurves.sketchFittedSplines.add(col)
    lines = sk.sketchCurves.sketchLines
    prev = spl.endSketchPoint
    for p in line_pts:
        ln = lines.addByTwoPoints(prev, sp(p))
        prev = ln.endSketchPoint
    lines.addByTwoPoints(prev, spl.startSketchPoint)
    best = max((sk.profiles.item(i) for i in range(sk.profiles.count)),
               key=lambda pr: pr.areaProperties().area)
    return sk, best


def _closed_sketch(comp, y_mm, pts, name):
    """closed fitted spline through (x, z) points on the horizontal plane y = y_mm."""
    sk = comp.sketches.add(_plane(comp, comp.xZConstructionPlane, y_mm))
    sk.name = name
    col = adsk.core.ObjectCollection.create()
    for x, z in pts:
        col.add(sk.modelToSketchSpace(adsk.core.Point3D.create(x * MM, y_mm * MM, z * MM)))
    spl = sk.sketchCurves.sketchFittedSplines.add(col)
    spl.isClosed = True
    # a spline through sharp corners can make tiny loops: the outline is the biggest profile
    best = max((sk.profiles.item(i) for i in range(sk.profiles.count)),
               key=lambda pr: pr.areaProperties().area)
    return sk, best


def _extrude(comp, prof, dist_mm, op, symmetric=False, bodies=None):
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(prof, op)
    inp.setDistanceExtent(symmetric, adsk.core.ValueInput.createByReal(dist_mm * MM))
    if bodies:
        inp.participantBodies = bodies
    return ext.add(inp)


def _fillet(comp, body, pick, radius_mm, tries=(1.0, 0.8, 0.6, 0.45)):
    edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        if pick(e):
            edges.add(e)
    if edges.count == 0:
        return 'no edges'
    for f in tries:
        try:
            inp = comp.features.filletFeatures.createInput()
            inp.edgeSetInputs.addConstantRadiusEdgeSet(
                edges, adsk.core.ValueInput.createByReal(radius_mm * f * MM), True)
            comp.features.filletFeatures.add(inp)
            return f'{edges.count} edges R{radius_mm * f:.1f}'
        except RuntimeError:
            continue
    return 'failed'


def _bbox_mm(e):
    b = e.boundingBox
    return [v / MM for v in (b.minPoint.x, b.minPoint.y, b.minPoint.z,
                             b.maxPoint.x, b.maxPoint.y, b.maxPoint.z)]


# ---- platform variant: the grip on the grip_a7c bottom plate instead of the cage ----------
# Same loft, but its sections already include the wrap along the camera side (see
# grip_sections.WRAP) and its top falls from the grip to the rear, under the strap lug.
TOP_AT_PLATFORM = [(3.0, 51.0), (10.0, 53.5), (19.0, 57.2), (27.0, 60.4), (45.0, 62.0), (70.0, 62.0)]

VARIANTS = {
    'cage': dict(name='a7c_grip', sections='sections', top_at=TOP_AT, bottom_fillet=True,
                 battery=True, pockets='pockets', trim_z=27.0),
    'platform': dict(name='a7c_platform_grip', sections='sections_platform', top_at=TOP_AT_PLATFORM, plate='a7c_plate.json',
                     bottom_fillet=True, battery=False, pockets='pockets_side', trim_z=-2.0),
}


def build(design, variant='cage'):
    v = VARIANTS[variant]
    y_bot = Y_BOT
    data = json.loads(open(os.path.join(HERE, 'grip_sections.json'), encoding='utf-8').read())
    root = design.rootComponent
    for i in range(root.occurrences.count - 1, -1, -1):
        if root.occurrences.item(i).component.name == v['name']:
            root.occurrences.item(i).deleteMe()
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    comp = occ.component
    comp.name = v['name']
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    AND = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    log = []

    # 1. loft through the sections
    lofts = comp.features.loftFeatures
    inp = lofts.createInput(NEW)
    for s in data[v['sections']]:
        _, prof = _closed_sketch(comp, s['y'], s['pts'], f"section y={s['y']:g}")
        inp.loftSections.add(prof)
    inp.isSolid = True
    body = lofts.add(inp).bodies.item(0)
    body.name = 'grip'
    # 3. top: one lofted surface (scoop across, rising to the front)
    lofts = comp.features.loftFeatures
    inp = lofts.createInput(NEW)
    for z, h in v['top_at']:
        pts = [(x, h + dy) for x, dy in SCOOP]
        _, prof = _profile_sketch(comp, _plane(comp, comp.xYConstructionPlane, z),
                                  lambda p, z=z: (p[0], p[1], z), pts,
                                  [(-70.0, -12.0), (-19.0, -12.0)], f'grip top z={z:g}')
        inp.loftSections.add(prof)
    inp.isSolid = True
    tool = lofts.add(inp).bodies.item(0)
    comb = comp.features.combineFeatures
    tools = adsk.core.ObjectCollection.create()
    tools.add(tool)
    ci = comb.createInput(body, tools)
    ci.operation = AND
    comb.add(ci)
    body = comp.bRepBodies.item(0)
    # 4. round the top rim and the exposed bottom edges
    log.append('top ' + _fillet(comp, body, lambda e: _bbox_mm(e)[1] > 40.0, TOP_R,
                                tries=(1.0, 0.8, 0.6, 0.45, 0.3)))
    body = comp.bRepBodies.item(0)
    if v['bottom_fillet']:          # over the plate the rounding is buried in the plate
        log.append('bottom ' + _fillet(comp, body, lambda e: _bbox_mm(e)[4] < y_bot + 0.05, BOTTOM_R,
                                       tries=(1.0, 0.8, 0.6, 0.4)))
        body = comp.bRepBodies.item(0)
    # 4d. trim flush with the side plate (the section splines overshoot a little)
    sk = comp.sketches.add(_plane(comp, comp.xZConstructionPlane, y_bot - 1))
    sk.name = 'trim'
    a = sk.modelToSketchSpace(adsk.core.Point3D.create(-64.0 * MM, (y_bot - 1) * MM, v['trim_z'] * MM))
    c = sk.modelToSketchSpace(adsk.core.Point3D.create(-10.0 * MM, (y_bot - 1) * MM, 70.0 * MM))
    sk.sketchCurves.sketchLines.addTwoPointRectangle(a, c)
    f = _extrude(comp, sk.profiles.item(0), 90.0, AND, bodies=[comp.bRepBodies.item(0)])
    if f.healthState != adsk.fusion.FeatureHealthStates.HealthyFeatureHealthState:
        log.append('trim: ' + f.errorOrWarningMessage)
    body = comp.bRepBodies.item(0)
    # 5. camera pocket, band by band
    #    The bands are made as one tool body (overlapping by 0.1 mm) and cut in one go: Fusion
    #    silently cuts nothing when a band's sketch lies on or in the void of the previous cut.
    body_token = body.entityToken
    tools = []
    for k, pk in enumerate(data[v['pockets']]):
        y0 = pk['y0'] - (0.1 if k else 0.0)
        _, prof = _closed_sketch(comp, y0, pk['pts'], f"pocket y={pk['y0']:g}..{pk['y1']:g}")
        f = _extrude(comp, prof, pk['y1'] - y0, NEW)
        if _bbox_mm(f.bodies.item(0))[4] < y0 + 0.5:       # went down: flip
            f.deleteMe()
            f = _extrude(comp, prof, -(pk['y1'] - y0), NEW)
        tools.append(f.bodies.item(0))
    if len(tools) > 1:
        col = adsk.core.ObjectCollection.create()
        for t in tools[1:]:
            col.add(t)
        ci = comp.features.combineFeatures.createInput(tools[0], col)
        ci.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        comp.features.combineFeatures.add(ci)
    tool = [b for b in comp.bRepBodies if b.entityToken != body_token][0]
    body = [b for b in comp.bRepBodies if b.entityToken == body_token][0]
    v0 = body.volume
    col = adsk.core.ObjectCollection.create()
    col.add(tool)
    ci = comp.features.combineFeatures.createInput(body, col)
    ci.operation = CUT
    comp.features.combineFeatures.add(ci)
    body = comp.bRepBodies.item(0)
    log.append(f'pocket cut {v0 - body.volume:.2f} cm3')
    # 6. battery door opening below the seat
    #    (cage only: on the grip_a7c plate the door is under the plate anyway)
    if v['battery']:
        x0, x1, z0, z1 = BATTERY
        sk = comp.sketches.add(_plane(comp, comp.xZConstructionPlane, Y_BOT))
        sk.name = 'battery opening'
        a = sk.modelToSketchSpace(adsk.core.Point3D.create(x0 * MM, Y_BOT * MM, z0 * MM))
        c = sk.modelToSketchSpace(adsk.core.Point3D.create(x1 * MM, Y_BOT * MM, z1 * MM))
        sk.sketchCurves.sketchLines.addTwoPointRectangle(a, c)
        prof = sk.profiles.item(0)
        v0 = body.volume
        f = _extrude(comp, prof, -Y_BOT, CUT, bodies=[body])
        if abs(comp.bRepBodies.item(0).volume - v0) < 1e-6:
            f.deleteMe()
            _extrude(comp, prof, Y_BOT, CUT, bodies=[comp.bRepBodies.item(0)])
        body = comp.bRepBodies.item(0)
    for skt in comp.sketches:
        skt.isLightBulbOn = False
    for pl in comp.constructionPlanes:
        pl.isLightBulbOn = False
    log.append('bbox mm ' + ', '.join(f'{v:.1f}' for v in _bbox_mm(body)))
    log.append(f'volume cm3 {body.volume:.2f}')
    return occ, body, log


def attach_plate(design, variant='platform'):
    """platform variant, second step (kept apart because of the time it takes): the bottom plate,
    rebuilt as a solid from the outlines platform_hybrid.py takes off the downloaded grip_a7c
    plate (a7c_plate.json), joined to the grip into one body."""
    v = VARIANTS[variant]
    root = design.rootComponent
    occ = [root.occurrences.item(i) for i in range(root.occurrences.count)
           if root.occurrences.item(i).component.name == v['name']][0]
    comp = occ.component
    pd = json.loads(open(os.path.join(HERE, v['plate']), encoding='utf-8').read())
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    log = []
    grip = comp.bRepBodies.item(0)
    grip_token = grip.entityToken
    bot, top, rim_top = pd['bottom'], pd['top'], pd['rim_top']

    def up(prof, dist, op, bodies=None):
        """extrude upwards (+y) whatever way the sketch plane faces."""
        f = _extrude(comp, prof, dist, op, bodies=bodies)
        b = _bbox_mm(f.bodies.item(0)) if f.bodies.count else None
        if b is not None and b[1] < bot - 0.5:
            f.deleteMe()
            f = _extrude(comp, prof, -dist, op, bodies=bodies)
        return f
    # slab
    _, prof = _closed_sketch(comp, bot, pd['slab'], 'plate slab')
    slab = up(prof, top - bot, NEW).bodies.item(0)
    slab.name = 'plate'
    log.append('plate bottom edge ' + _fillet(comp, slab, lambda e: _bbox_mm(e)[4] < bot + 0.05, 1.5,
                                              tries=(1.0, 0.6)))
    slab = [b for b in comp.bRepBodies if b.entityToken != grip_token][0]
    # fill under the grip's rear bottom edge (its rounding would leave a groove across the bottom)
    sk = comp.sketches.add(_plane(comp, comp.xZConstructionPlane, bot))
    sk.name = 'plate fill under the grip'
    a = sk.modelToSketchSpace(adsk.core.Point3D.create(-55.6 * MM, bot * MM, 26.0 * MM))
    c = sk.modelToSketchSpace(adsk.core.Point3D.create(-21.0 * MM, bot * MM, 30.5 * MM))
    sk.sketchCurves.sketchLines.addTwoPointRectangle(a, c)
    up(sk.profiles.item(0), top - bot, JOIN, bodies=[slab])
    slab = [b for b in comp.bRepBodies if b.entityToken != grip_token][0]
    # rims the camera stands on
    for i, r in enumerate(pd['rims']):
        _, prof = _closed_sketch(comp, top, r, f'plate rim {i + 1}')
        up(prof, rim_top - top, JOIN, bodies=[slab])
        slab = [b for b in comp.bRepBodies if b.entityToken != grip_token][0]
    # screw hole and the counterbore for its head
    h, cb = pd['hole'], pd['counterbore']
    for d, depth, name in ((h['d'], top - bot + 1, 'screw hole'), (cb['d'], cb['depth'], 'counterbore')):
        sk = comp.sketches.add(_plane(comp, comp.xZConstructionPlane, bot))
        sk.name = name
        c = sk.modelToSketchSpace(adsk.core.Point3D.create(h['x'] * MM, bot * MM, h['z'] * MM))
        sk.sketchCurves.sketchCircles.addByCenterRadius(c, d / 2 * MM)
        prof = min((sk.profiles.item(k) for k in range(sk.profiles.count)),
                   key=lambda pr: pr.areaProperties().area)
        v0 = slab.volume
        f = _extrude(comp, prof, depth, CUT, bodies=[slab])
        slab = [b for b in comp.bRepBodies if b.entityToken != grip_token][0]
        if slab.volume > v0 - 1e-6:
            f.deleteMe()
            _extrude(comp, prof, -depth, CUT, bodies=[slab])
            slab = [b for b in comp.bRepBodies if b.entityToken != grip_token][0]
    # one body with the grip
    grip = [b for b in comp.bRepBodies if b.entityToken == grip_token][0]
    tools = adsk.core.ObjectCollection.create()
    tools.add(slab)
    ci = comp.features.combineFeatures.createInput(grip, tools)
    ci.operation = JOIN
    comp.features.combineFeatures.add(ci)
    body = comp.bRepBodies.item(0)
    log.append('joint ' + _fillet(
        comp, body,
        lambda e: (_bbox_mm(e)[0] > -58.0 and _bbox_mm(e)[3] < -54.0 and _bbox_mm(e)[2] > 2.0
                   and _bbox_mm(e)[5] < 12.0 and _bbox_mm(e)[4] < 0.5 and _bbox_mm(e)[1] > bot + 0.5),
        2.0, tries=(1.0, 0.6, 0.3)))
    body = comp.bRepBodies.item(0)
    for skt in comp.sketches:
        skt.isLightBulbOn = False
    for pl in comp.constructionPlanes:
        pl.isLightBulbOn = False
    log.append('bbox mm ' + ', '.join(f'{x:.1f}' for x in _bbox_mm(body)))
    log.append(f'volume cm3 {body.volume:.2f}')
    return occ, body, log


def export(design, occ, body, folder):
    """STEP of the grip component and a fine binary STL of the body."""
    em = design.exportManager
    name = occ.component.name
    em.execute(em.createSTEPExportOptions(os.path.join(folder, name + '.step'), occ.component))
    opt = em.createSTLExportOptions(body, os.path.join(folder, name + '.stl'))
    opt.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    opt.isBinaryFormat = True
    em.execute(opt)


def run(_context: str, variant='cage'):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    occ, body, log = build(design, variant)
    if VARIANTS[variant].get('plate'):
        occ, body, more = attach_plate(design, variant)
        log += more
    export(design, occ, body, HERE)
    log.append('exported to ' + HERE)
    print('\n'.join(log))
