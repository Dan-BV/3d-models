"""Wall holder for four Oral-B brushes with their chargers hidden inside (Fusion API script).

Run it in Fusion (Utilities → Scripts, or through the Fusion MCP). It adds the component
"Wall holder" to the active design with two bodies:

  Plate  — a 6 mm wall plate with three vertical dovetail grooves, screwed to the wall.
  Base   — the back wall and the bottom plate in one piece. Its back wall stands 6 mm off the
           wall and slides down onto the plate on three dovetail tongues; the four chargers click into cradles on
           its plate, and two vertical dovetail rails stand on its back wall.
  Cover  — the front, the sides and the 45° top with the four bores, and under each bore
           a tube that guides the brush onto the charger peg. Two posts inside its back
           corners have dovetail grooves: the cover slides down onto the rails and hangs
           on their tops, and two pins near the top of the back wall run up wedges on
           tabs under the cover's roof and press it to the wall. To clean the chargers, take the brushes out, lift the cover off
           the rails and take it away.

Millimetres, Z up, the back face (wall side) at y = 0, the front at y = -D.
The charger and brush sizes come from the scanned Oral-B set (charger 46 × 57 mm plus a
5 mm cord tab, 25.8 mm tall, peg Ø12.4; the handle is at most Ø34 in the box).
"""
import math
import adsk.core
import adsk.fusion

# --- sizes, mm -----------------------------------------------------------------------
W, D = 222.0, 81.0          # outside width (x) and depth (y)
H_BACK, H_FRONT = 175.0, 94.0   # top slope 45°
T = 2.4                     # cover wall
TB = 4.0                    # back wall of the base
STANDOFF = 6.0              # the base's back wall stands this far off the wall: the wall plate and the cord channel
BW0, BW1 = -STANDOFF, -STANDOFF - TB   # rear and front faces of the base's back wall
R_BACK, R_FRONT = 3.0, 30.0 # plan corner radii; from R32 down the openings keep 13 mm to the edge all round
TOP_FILLET = 2.0

PITCH = 54.0
SLOTS = [-1.5 * PITCH, -0.5 * PITCH, 0.5 * PITCH, 1.5 * PITCH]
Y_PEG = -45.8               # charger centre / brush axis: the cord tab ends 2.3 mm off the back wall (clear of the corner fillet)

PLATE_T = 3.0               # bottom plate of the base
# the charger, measured: 46.7 wide, 59.7 long without the cord tab, 24.3 tall; the tab is 30 wide
# and 3.6 deep at the back. The outlines below are the scan's, scaled to these sizes.
CHARGER_HALF_L = 59.7 / 2
CHARGER_TOP = PLATE_T + 24.3  # brushes stand on the charger top
TUBE_Z0 = CHARGER_TOP + 4.2 # tube bottom, 4 mm above the charger top
# the brush handle, measured: Ø25 at the bottom, 28 × 29.3 at 97 mm up, 30.4 × 31.3 at 131 mm up
BORE_LOW_R = 13.25          # Ø26.5 ring at the tube bottom centres the Ø25 brush foot over the peg
BORE_R = 16.5               # Ø33 above it: under the roof the handle is at most ~30.7 wide
CONE_H = 10.0
TUBE_WALL = 1.8
HOLE_FILLET = 2.5

GAP = 0.25                  # plate to cover walls
# charger cradles: a wall round the charger's widest outline (taken from the scan at 10 mm up,
# relative to the peg), 0.3 mm off it, with a notch for the cord tab at the back. On both long
# sides a spring tongue carries a hook that sits on the charger's tapering side above its
# widest band: the charger clicks in, and the hook keeps pressing it down onto the plate.
CRADLE_INNER = [
    (-0.8, -30.26), (2.96, -29.88), (6.58, -28.8), (9.96, -27.1), (13.06, -24.88), (15.78, -22.17),
    (18.01, -19.03), (19.9, -15.66), (21.46, -12.12), (22.46, -8.35), (23.14, -4.54), (23.52, -0.66),
    (23.33, 3.24), (22.82, 7.09), (22.02, 10.89), (20.62, 14.52), (18.88, 17.97), (16.8, 21.21),
    (14.23, 24.08), (11.27, 26.48), (8.02, 28.44), (4.45, 29.65), (0.69, 30.2), (-3.08, 29.85),
    (-6.71, 28.83), (-10.04, 27.03), (-13.12, 24.78), (-15.84, 22.06), (-18.07, 18.92), (-19.97, 15.57),
    (-21.55, 12.03), (-22.55, 8.27), (-23.24, 4.44), (-23.64, 0.58), (-23.44, -3.32), (-22.95, -7.18),
    (-22.16, -10.99), (-20.76, -14.62), (-19.04, -18.07), (-16.96, -21.32), (-14.39, -24.18), (-11.41, -26.56),
    (-8.11, -28.43), (-4.55, -29.69),
]
CRADLE_OUTER = [
    (-0.61, -32.34), (3.44, -31.94), (7.34, -30.75), (10.98, -28.92), (14.31, -26.54), (17.25, -23.61),
    (19.66, -20.24), (21.71, -16.62), (23.39, -12.81), (24.46, -8.75), (25.17, -4.63), (25.54, -0.46),
    (25.34, 3.73), (24.74, 7.87), (23.8, 11.95), (22.29, 15.85), (20.34, 19.53), (18.01, 22.95),
    (15.24, 26.03), (11.97, 28.53), (8.42, 30.53), (4.54, 31.75), (0.5, 32.28), (-3.56, 31.9),
    (-7.47, 30.77), (-11.07, 28.85), (-14.39, 26.43), (-17.31, 23.5), (-19.73, 20.14), (-21.78, 16.53),
    (-23.47, 12.71), (-24.55, 8.67), (-25.27, 4.55), (-25.66, 0.37), (-25.45, -3.82), (-24.87, -7.97),
    (-23.94, -12.04), (-22.44, -15.94), (-20.5, -19.62), (-18.17, -23.05), (-15.4, -26.13), (-12.11, -28.61),
    (-8.51, -30.52), (-4.65, -31.78),
]
CRADLE_H = 8.0
TAB_NOTCH_HALF = 16.5       # the cord tab is 30 mm wide
# behind each charger an obround hole in the back wall lets the cord, plug and all, through to
# the channel behind the wall (a plug is 44 × 35 × 13 mm and goes through end first). The holes
# start at the height of the cradle walls, so the plug slides in over the cradles.
CORD_HOLE_W, CORD_HOLE_H, CORD_HOLE_Z0 = 44.0, 18.0, 11.0  # the 35 × 13 plug section fits with ~1 mm to spare
# the inner two holes sit 2 mm outboard of their chargers, so the cord channel between them is 16 mm wide
CORD_HOLE_XS = [-81.0, -29.0, 29.0, 81.0]
# under each hole a slot runs down to just above the plate, straight behind the cord tab, so the
# cord leaves the tab level and goes straight out; the corner fillet is cut away in front of it
CORD_SLOT_W, CORD_SLOT_Z0 = 6.0, 3.2
TONGUE_X0, TONGUE_T = 23.65, 1.6    # tongue inner face (from the peg axis) and thickness
TONGUE_HALF_W = 5.0
TONGUE_SLIT = 0.8
HOOK_TIP = 22.63            # the charger is about 22.8 here: ~0.15 mm of squeeze, 0.7 mm to snap past
HOOK_Z = 14.1               # hook tip above the plate; underside and top are 45° ramps of 1 mm

# dovetail rails on the base (vertical), grooves in posts inside the cover's back corners
RAIL_X = W / 2 - T - 5.0    # rail centre line
RAIL_A, RAIL_B = 5.0, 7.5   # rail width at the wall face and at its front (dovetail)
RAIL_H = 4.0                # how far it stands out of the back wall (y)
RAIL_TOP = 150.0            # rails run up to just under the cover's roof; the cover hangs on their tops
RAIL_Z0 = 33.0              # rails start above the cord holes and the rib, so the outer holes can sit behind their chargers
RAIL_CLEAR = 0.3            # per side: a long FDM dovetail slides without force; the top clamps take up the play
LEAD_IN = 0.8               # chamfer on the rail tops and the groove mouths
POST_W, POST_D, POST_TOP = 12.0, 10.0, 200.0   # posts run up into the roof (trimmed by the slope)
POST_Z0 = 6.0               # post bottoms clear the fillet between the base's back wall and plate

# top clamps: a pin on the back wall with a conical head; a tab hanging from the cover's
# roof has a slot open at the bottom and a wedge on its front face. In the last millimetres
# of the cover's travel the pin head runs up the wedge and presses the cover to the wall.
CLAMP_XS = [-40.0, 40.0]
CLAMP_Z = 150.0             # pin axis
PIN_R, HEAD_R = 2.0, 4.0
PIN_CONE_Y = BW1 - 2.65     # where the shank ends and the 45° head cone starts
HEAD_LEN = 1.0              # cylindrical part of the head after the cone
TAB_W = 14.0
TAB_BACK = BW1 - 0.1        # tab back face, 0.1 mm off the base's back wall
TAB_T_ENTRY, TAB_T_SEAT = 1.9, 2.9   # tab thickness below the wedge and at the pin (0.15 mm squeeze)
WEDGE_LOW, WEDGE_HIGH = 8.0, 2.0     # wedge runs from this far below the pin axis to this far below
TAB_BOTTOM = 14.0           # tab reaches this far below the pin axis
SLOT_W = 4.4
GUSSET_GAP = 0.8           # gusset starts this far above the pin head

# gussets between the bottom plate and the back wall, in the gaps between the chargers;
GUSSET_XS = [-55.0, 0.0, 55.0]      # in the middle of the webs between the cord holes
GUSSET_T = 5.0
GUSSET_L, GUSSET_H = 20.0, 90.0      # along the plate (stopping short of the cradles) and up the wall
# a horizontal rib on the front of the back wall just above the cord holes ties the webs together
STIFF_RIB_Z, STIFF_RIB_H, STIFF_RIB_D = 31.0, 6.0, 4.0

# cord management in the gap behind the back wall (6 mm to the wall): a channel down the middle,
# open at the bottom, made of two strips with lips; the four cords lie in it flat side by side.
# T-hooks above it to loop each cord (and wind up any slack) on its way to the channel.
CHAN_X, CHAN_POST, CHAN_LIP = 8.0, 2.0, 3.5     # channel half-width, post thickness, lip overhang
CHAN_Z0, CHAN_Z1 = 0.0, 50.0
CLIP_LIP_T = 1.2
CLIP_GAP = 0.5               # clips stop this far short of the wall
# the upper hooks sit outboard of the wall plate (±90), so the base still lifts off it
T_HOOKS = [(-100.0, 95.0), (-45.0, 65.0), (45.0, 65.0), (100.0, 95.0)]   # x, z of each T-hook
T_STEM, T_CAP, T_HEIGHT = 3.0, 10.0, 10.0

# wall plate (after the original holder's): screwed to the wall, three vertical dovetail grooves
# in its front, open at the top and closed at the bottom. Three dovetail tongues on the back of
# the base's back wall slide down into them until they sit on the groove floors.
MOUNT_W, MOUNT_H, MOUNT_Z0 = 180.0, 33.0, 125.0
MOUNT_GROOVE_XS = [-70.0, 0.0, 70.0]
GROOVE_A, GROOVE_DEPTH = 10.0, 4.0  # groove width at the plate face; 45° flanks, so 18 mm at the bottom
GROOVE_FLOOR = 3.0
MOUNT_CLEAR = 0.3
SCREW_XS, SCREW_R, SCREW_CSK_R = [-45.0, 45.0], 2.1, 4.5   # countersunk wood screws Ø4

# radii and chamfers in the loaded inside corners
FILLET_MAIN = 2.2           # back wall to bottom plate, and the gusset roots (R3 would touch the cord tabs)
RIB_CHAMFER = 3.5           # 45° under the stiffening rib (also takes away its overhang in print)
FILLET_CRADLE = 1.5         # cradle walls to the plate, inside and out (the charger's bottom edge is R4)
FILLET_TONGUE = 1.0         # roots of the spring tongues
FILLET_POST = 2.0           # cover: rail posts to the side walls

C = 0.1  # mm -> cm (Fusion's internal unit)

# The component is built Z up; its occurrence is turned so that the holder stands up in a
# Y-up design (as the scanned brushes are), its front toward +Z.
Y_UP = True
NAME = "Wall holder"   # a run replaces the component of this name
PLACE_X = 0.0          # where the occurrence stands along X, mm (to put variants side by side)


def P(x, y, z=0.0):
    return adsk.core.Point3D.create(x * C, y * C, z * C)


def V(mm):
    return adsk.core.ValueInput.createByReal(mm * C)


def slope_z(y):
    return H_BACK + y * (H_BACK - H_FRONT) / D


def rounded_rect(sk, x0, x1, y0, y1, rb, rf, z=0.0):
    """Rectangle in an XY sketch, back corners (y1) rounded rb, front corners (y0) rf; 0 = sharp."""
    L, A = sk.sketchCurves.sketchLines, sk.sketchCurves.sketchArcs
    q = -math.pi / 2
    S = lambda x, y: sk.modelToSketchSpace(P(x, y, z))
    L.addByTwoPoints(S(x0 + rb, y1), S(x1 - rb, y1))
    if rb:
        A.addByCenterStartSweep(S(x1 - rb, y1 - rb), S(x1 - rb, y1), q)
    L.addByTwoPoints(S(x1, y1 - rb), S(x1, y0 + rf))
    if rf:
        A.addByCenterStartSweep(S(x1 - rf, y0 + rf), S(x1, y0 + rf), q)
    L.addByTwoPoints(S(x1 - rf, y0), S(x0 + rf, y0))
    if rf:
        A.addByCenterStartSweep(S(x0 + rf, y0 + rf), S(x0 + rf, y0), q)
    L.addByTwoPoints(S(x0, y0 + rf), S(x0, y1 - rb))
    if rb:
        A.addByCenterStartSweep(S(x0 + rb, y1 - rb), S(x0, y1 - rb), q)


def poly(sk, pts):
    """Closed polygon from model-space points (mm), drawn in any sketch."""
    L = sk.sketchCurves.sketchLines
    sp = [sk.modelToSketchSpace(P(*p)) for p in pts]
    for a, b in zip(sp, sp[1:] + sp[:1]):
        L.addByTwoPoints(a, b)


def offset_plane(comp, base, mm):
    pi = comp.constructionPlanes.createInput()
    pi.setByOffset(base, V(mm))
    return comp.constructionPlanes.add(pi)


def plane_at(comp, base, axis, mm):
    """Construction plane parallel to `base` through axis = mm (the offset sign is checked)."""
    pl = offset_plane(comp, base, mm)
    if abs(getattr(pl.geometry.origin, axis) - mm * C) > 1e-6:
        pl.deleteMe()
        pl = offset_plane(comp, base, -mm)
    return pl


def all_profiles(sk):
    pr = adsk.core.ObjectCollection.create()
    for p in sk.profiles:
        pr.add(p)
    return pr


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    root = design.rootComponent
    for old in [o for o in root.occurrences if o.component.name == NAME]:
        old.deleteMe()
    place = adsk.core.Matrix3D.create()
    if Y_UP:
        place.setToRotation(-math.pi / 2, adsk.core.Vector3D.create(1, 0, 0), adsk.core.Point3D.create(0, 0, 0))
    place.translation = adsk.core.Vector3D.create(PLACE_X * C, 0, 0)
    occ = root.occurrences.addNewComponent(place)
    comp = occ.component
    comp.name = NAME
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    feats = comp.features
    XY, XZ, YZ = comp.xYConstructionPlane, comp.xZConstructionPlane, comp.yZConstructionPlane

    def extrude(prof, dist, op, body=None, start=0.0):
        ei = feats.extrudeFeatures.createInput(prof, op)
        ei.setDistanceExtent(False, V(dist))
        if start:
            ei.startExtent = adsk.fusion.OffsetStartDefinition.create(V(start))
        if body is not None and op != NEW:
            ei.participantBodies = [body]
        return feats.extrudeFeatures.add(ei)

    def xy_sketch(z, name):
        s = comp.sketches.add(plane_at(comp, XY, "z", z) if z else XY)
        s.name = name
        return s

    def slope_cut(body, drop=0.0):
        s = comp.sketches.add(YZ)
        s.name = "Top slope"
        yb, yf = 10.0, -D - 10.0
        poly(s, [(0, yb, slope_z(yb) - drop), (0, yf, slope_z(yf) - drop), (0, yf, 400), (0, yb, 400)])
        ei = feats.extrudeFeatures.createInput(s.profiles.item(0), CUT)
        ei.setSymmetricExtent(V(W + 40), True)
        ei.participantBodies = [body]
        feats.extrudeFeatures.add(ei)

    def top_face(body):
        return max((f for f in body.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType),
                   key=lambda f: f.pointOnFace.z)

    def fillet(edges, r):
        if edges.count:
            fi = feats.filletFeatures.createInput()
            fi.addConstantRadiusEdgeSet(edges, V(r), False)
            feats.filletFeatures.add(fi)

    # sketches on the XZ plane extrude toward -y (into the box), whichever way its normal points
    inward = (adsk.fusion.ExtentDirections.PositiveExtentDirection if XZ.geometry.normal.y < 0
              else adsk.fusion.ExtentDirections.NegativeExtentDirection)

    def xz_extrude(profs, op, start, depth, body):
        ei = feats.extrudeFeatures.createInput(profs, op)
        if start:
            ei.startExtent = adsk.fusion.OffsetStartDefinition.create(
                V(start if inward == adsk.fusion.ExtentDirections.PositiveExtentDirection else -start))
        ei.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(V(depth)), inward)
        ei.participantBodies = [body]
        return feats.extrudeFeatures.add(ei)

    # =================================================================================
    # Cover
    # =================================================================================
    sk = xy_sketch(0, "Cover plan")
    rounded_rect(sk, -W / 2, W / 2, -D, 0.0, 0.0, R_FRONT)      # sharp back corners: they sit on the wall
    cover = extrude(sk.profiles.item(0), H_BACK + 5, NEW).bodies.item(0)
    cover.name = "Cover"
    slope_cut(cover)

    # round the top edges, but not the back one: it meets the wall
    top = top_face(cover)
    edges = adsk.core.ObjectCollection.create()
    for e in top.edges:
        if e.boundingBox.minPoint.y < -0.5 * C:
            edges.add(e)
    fillet(edges, TOP_FILLET)

    # hollow it, open at the bottom and at the back
    bottom = min(cover.faces, key=lambda f: f.pointOnFace.z)
    back = [f for f in cover.faces if f.geometry.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType
            and abs(f.pointOnFace.y) < 1e-4 and abs(f.evaluator.getNormalAtPoint(f.pointOnFace)[1].y) > 0.99]
    faces = adsk.core.ObjectCollection.create()
    faces.add(bottom)
    for f in back:
        faces.add(f)
    si = feats.shellFeatures.createInput(faces, False)
    si.insideThickness = V(T)
    feats.shellFeatures.add(si)

    # tubes under the bores
    sk = xy_sketch(TUBE_Z0, "Tubes")
    for x in SLOTS:
        sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(P(x, Y_PEG, TUBE_Z0)),
                                                        (BORE_R + TUBE_WALL) * C)
    extrude(all_profiles(sk), H_BACK + 10 - TUBE_Z0, JOIN, cover)

    # posts in the back corners, carrying the dovetail grooves
    sk = xy_sketch(POST_Z0, "Rail posts")
    for sx in (-1, 1):
        xo = sx * (W / 2 - T + 0.5)
        xi = sx * (W / 2 - T - POST_W)
        a, b = min(xo, xi), max(xo, xi)
        poly(sk, [(a, BW1, POST_Z0), (b, BW1, POST_Z0),
                  (b, BW1 - POST_D, POST_Z0), (a, BW1 - POST_D, POST_Z0)])
    extrude(all_profiles(sk), POST_TOP - POST_Z0, JOIN, cover)
    slope_cut(cover)

    sk = xy_sketch(0, "Rail grooves")
    c = RAIL_CLEAR
    for sx in (-1, 1):
        xr = sx * RAIL_X
        poly(sk, [(xr - RAIL_A / 2 - c, BW1 + 0.5, 0), (xr + RAIL_A / 2 + c, BW1 + 0.5, 0),
                  (xr + RAIL_B / 2 + c, BW1 - RAIL_H - c, 0), (xr - RAIL_B / 2 - c, BW1 - RAIL_H - c, 0)])
    extrude(all_profiles(sk), RAIL_TOP, CUT, cover)

    # lead-in chamfers at the groove mouths (the posts' bottom faces)
    zb = POST_Z0 * C
    edges = adsk.core.ObjectCollection.create()
    for e in cover.edges:
        bb = e.boundingBox
        if abs(bb.minPoint.z - zb) < 1e-5 and abs(bb.maxPoint.z - zb) < 1e-5 and                 abs(abs((bb.minPoint.x + bb.maxPoint.x) / 2) - RAIL_X * C) < 0.5 and bb.minPoint.y < (BW1 - 0.2) * C:
            edges.add(e)
    if edges.count:
        ci = feats.chamferFeatures.createInput2()
        ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, V(LEAD_IN), False)
        feats.chamferFeatures.add(ci)

    # clamp tabs hanging from the roof, wedge on the front face
    def yz_extrude(pts, x, width, op, body):
        pl = plane_at(comp, YZ, "x", x)
        s = comp.sketches.add(pl)
        poly(s, [(x, y, z) for y, z in pts])
        ei = feats.extrudeFeatures.createInput(s.profiles.item(0), op)
        ei.setSymmetricExtent(V(width), True)
        ei.participantBodies = [body]
        return feats.extrudeFeatures.add(ei)

    zc = CLAMP_Z
    for x in CLAMP_XS:
        # above the pin head a 45° gusset runs from the tab's front face up to the roof
        yg, zg = TAB_BACK - TAB_T_SEAT, zc + HEAD_R + GUSSET_GAP
        yz_extrude([(TAB_BACK, zc - TAB_BOTTOM), (TAB_BACK, 200.0), (yg - (200.0 - zg), 200.0), (yg, zg),
                    (TAB_BACK - TAB_T_SEAT, zc - WEDGE_HIGH), (TAB_BACK - TAB_T_ENTRY, zc - WEDGE_LOW),
                    (TAB_BACK - TAB_T_ENTRY, zc - TAB_BOTTOM)], x, TAB_W, JOIN, cover)
    slope_cut(cover)
    s = comp.sketches.add(XZ)
    s.name = "Clamp slots"
    for x in CLAMP_XS:
        s.sketchCurves.sketchCircles.addByCenterRadius(s.modelToSketchSpace(P(x, 0, zc)), SLOT_W / 2 * C)
        poly(s, [(x - SLOT_W / 2, 0, zc - TAB_BOTTOM - 1), (x + SLOT_W / 2, 0, zc - TAB_BOTTOM - 1),
                 (x + SLOT_W / 2, 0, zc), (x - SLOT_W / 2, 0, zc)])
    xz_extrude(all_profiles(s), CUT, -TAB_BACK - 0.5, TAB_T_SEAT + 1.5, cover)

    # trim everything (tube tops, posts, clamp tabs) to the cover's rounded outer envelope, so a
    # large top rounding does not leave them standing proud of the roof
    sk = xy_sketch(0, "Envelope")
    rounded_rect(sk, -W / 2, W / 2, -D, 0.0, 0.0, R_FRONT)
    env = extrude(sk.profiles.item(0), H_BACK + 5, NEW).bodies.item(0)
    slope_cut(env)
    edges = adsk.core.ObjectCollection.create()
    for e in top_face(env).edges:
        if e.boundingBox.minPoint.y < -0.5 * C:
            edges.add(e)
    fillet(edges, TOP_FILLET)
    tools = adsk.core.ObjectCollection.create()
    tools.add(env)
    ci = feats.combineFeatures.createInput(cover, tools)
    ci.operation = adsk.fusion.FeatureOperations.IntersectFeatureOperation
    ci.isKeepToolBodies = False
    feats.combineFeatures.add(ci)

    # bores: Ø32 ring at the bottom, cone, Ø36.6 up through the top
    pl = plane_at(comp, XZ, "y", Y_PEG)
    for x in SLOTS:
        sk = comp.sketches.add(pl)
        sk.name = f"Bore x{x:+.0f}"
        z0, z1, zt = TUBE_Z0 - 1, TUBE_Z0 + CONE_H, H_BACK + 20
        poly(sk, [(x, Y_PEG, z0), (x + BORE_LOW_R, Y_PEG, z0), (x + BORE_LOW_R, Y_PEG, TUBE_Z0),
                  (x + BORE_R, Y_PEG, z1), (x + BORE_R, Y_PEG, zt), (x, Y_PEG, zt)])
        axis = sk.sketchCurves.sketchLines.item(5)
        ri = feats.revolveFeatures.createInput(sk.profiles.item(0), axis, CUT)
        ri.setAngleExtent(False, adsk.core.ValueInput.createByString("360 deg"))
        ri.participantBodies = [cover]
        feats.revolveFeatures.add(ri)

    edges = adsk.core.ObjectCollection.create()
    for e in cover.edges:
        bb = e.boundingBox
        cx, cy = (bb.minPoint.x + bb.maxPoint.x) / 2 / C, (bb.minPoint.y + bb.maxPoint.y) / 2 / C
        span = (bb.maxPoint.x - bb.minPoint.x) / C
        if bb.minPoint.z / C > H_FRONT and abs(span - 2 * BORE_R) < 0.5 and \
                any(abs(cx - x) < 0.5 for x in SLOTS) and abs(cy - Y_PEG) < 3:
            edges.add(e)
    fillet(edges, HOLE_FILLET)

    # =================================================================================
    # Base: back wall + bottom plate
    # =================================================================================
    # the back wall stands off the wall and sits inside the cover; its top stays under the roof
    sk = xy_sketch(0, "Back wall")
    inset = T + GAP
    poly(sk, [(-W / 2 + inset, BW1, 0), (W / 2 - inset, BW1, 0), (W / 2 - inset, BW0, 0), (-W / 2 + inset, BW0, 0)])
    base = extrude(sk.profiles.item(0), H_BACK + 5, NEW).bodies.item(0)
    base.name = "Base"
    slope_cut(base, (T + 0.5) * math.sqrt(2))

    # bottom plate inside the cover walls
    sk = xy_sketch(0, "Plate")
    inset = T + GAP
    rounded_rect(sk, -W / 2 + inset, W / 2 - inset, -D + inset, BW1 + 0.01, 0.0, R_FRONT - inset)
    extrude(sk.profiles.item(0), PLATE_T, JOIN, base)

    # charger cradles
    sk = xy_sketch(PLATE_T, "Charger cradles")
    for xs in SLOTS:
        for ring in (CRADLE_INNER, CRADLE_OUTER):
            pts = adsk.core.ObjectCollection.create()
            for x, y in ring:
                pts.add(sk.modelToSketchSpace(P(xs + x, Y_PEG + y, PLATE_T)))
            pts.add(sk.modelToSketchSpace(P(xs + ring[0][0], Y_PEG + ring[0][1], PLATE_T)))
            sk.sketchCurves.sketchFittedSplines.add(pts)
    rings = adsk.core.ObjectCollection.create()
    for p in sk.profiles:
        if p.profileLoops.count == 2:
            rings.add(p)
    extrude(rings, CRADLE_H, JOIN, base)
    # notches for the cord tabs, windows for the tongues, front trimmed to the plate edge
    sk = xy_sketch(PLATE_T, "Cradle cuts")
    y_front = -(D - T - GAP) + 0.05
    for xs in SLOTS:
        poly(sk, [(xs - TAB_NOTCH_HALF, Y_PEG + 20, PLATE_T), (xs + TAB_NOTCH_HALF, Y_PEG + 20, PLATE_T),
                  (xs + TAB_NOTCH_HALF, BW1 - 0.5, PLATE_T), (xs - TAB_NOTCH_HALF, BW1 - 0.5, PLATE_T)])
        for sx in (-1, 1):
            a0, a1 = sorted((xs + sx * (TONGUE_X0 - 1.5), xs + sx * (TONGUE_X0 + 3.5)))
            hw = TONGUE_HALF_W + TONGUE_SLIT
            poly(sk, [(a0, Y_PEG - hw, PLATE_T), (a1, Y_PEG - hw, PLATE_T),
                      (a1, Y_PEG + hw, PLATE_T), (a0, Y_PEG + hw, PLATE_T)])
    poly(sk, [(-W, y_front - 20, PLATE_T), (W, y_front - 20, PLATE_T), (W, y_front, PLATE_T), (-W, y_front, PLATE_T)])
    extrude(all_profiles(sk), CRADLE_H + 1, CUT, base)
    # spring tongues with hooks
    pl = plane_at(comp, XZ, "y", Y_PEG)
    for xs in SLOTS:
        for sx in (-1, 1):
            s = comp.sketches.add(pl)
            s.name = f"Tongue x{xs + sx * TONGUE_X0:+.0f}"
            z0, zh = PLATE_T - 0.5, PLATE_T + HOOK_Z
            xi, xo, xt = xs + sx * TONGUE_X0, xs + sx * (TONGUE_X0 + TONGUE_T), xs + sx * HOOK_TIP
            poly(s, [(xi, Y_PEG, z0), (xo, Y_PEG, z0), (xo, Y_PEG, zh + 1), (xi, Y_PEG, zh + 1),
                     (xt, Y_PEG, zh), (xi, Y_PEG, zh - 1)])
            ei = feats.extrudeFeatures.createInput(s.profiles.item(0), JOIN)
            ei.setSymmetricExtent(V(2 * TONGUE_HALF_W), True)
            ei.participantBodies = [base]
            feats.extrudeFeatures.add(ei)

    # dovetail rails on the back wall
    sk = xy_sketch(RAIL_Z0, "Rails")
    for sx in (-1, 1):
        xr = sx * RAIL_X
        poly(sk, [(xr - RAIL_A / 2, BW1 + 0.5, RAIL_Z0), (xr + RAIL_A / 2, BW1 + 0.5, RAIL_Z0),
                  (xr + RAIL_B / 2, BW1 - RAIL_H, RAIL_Z0), (xr - RAIL_B / 2, BW1 - RAIL_H, RAIL_Z0)])
    extrude(all_profiles(sk), RAIL_TOP - RAIL_Z0, JOIN, base)
    zt = RAIL_TOP * C
    edges = adsk.core.ObjectCollection.create()
    for e in base.edges:
        bb = e.boundingBox
        if abs(bb.minPoint.z - zt) < 1e-5 and abs(bb.maxPoint.z - zt) < 1e-5 and                 abs(abs((bb.minPoint.x + bb.maxPoint.x) / 2) - RAIL_X * C) < 0.5 and bb.minPoint.y < (BW1 - 0.2) * C:
            edges.add(e)
    if edges.count:
        ci = feats.chamferFeatures.createInput2()
        ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, V(LEAD_IN), False)
        feats.chamferFeatures.add(ci)

    # clamp pins: shank, 45° cone, short head with a chamfered tip
    pl = plane_at(comp, XY, "z", CLAMP_Z)
    for x in CLAMP_XS:
        s = comp.sketches.add(pl)
        s.name = f"Clamp pin x{x:+.0f}"
        y_end = PIN_CONE_Y - (HEAD_R - PIN_R) - HEAD_LEN
        z = CLAMP_Z
        poly(s, [(x, BW1 + 0.5, z), (x + PIN_R, BW1 + 0.5, z), (x + PIN_R, PIN_CONE_Y, z),
                 (x + HEAD_R, PIN_CONE_Y - (HEAD_R - PIN_R), z), (x + HEAD_R, y_end + 0.5, z),
                 (x + HEAD_R - 0.5, y_end, z), (x, y_end, z)])
        axis = s.sketchCurves.sketchLines.item(6)          # (x, y_end) -> (x, start): the pin axis
        ri = feats.revolveFeatures.createInput(s.profiles.item(0), axis, JOIN)
        ri.setAngleExtent(False, adsk.core.ValueInput.createByString("360 deg"))
        ri.participantBodies = [base]
        feats.revolveFeatures.add(ri)

    # gussets plate-to-wall
    for x in GUSSET_XS:
        yz_extrude([(BW1 + 0.5, PLATE_T - 0.5), (BW1 + 0.5, PLATE_T + GUSSET_H),
                    (BW1 - GUSSET_L, PLATE_T - 0.5)], x, GUSSET_T, JOIN, base)

    # cord holes through the back wall, one behind each charger
    s = comp.sketches.add(XZ)
    s.name = "Cord holes"
    r = CORD_HOLE_H / 2
    zc_h = CORD_HOLE_Z0 + r
    for x in CORD_HOLE_XS:
        hw = CORD_HOLE_W / 2 - r
        cc = s.sketchCurves
        cc.sketchCircles.addByCenterRadius(s.modelToSketchSpace(P(x - hw, 0, zc_h)), r * C)
        cc.sketchCircles.addByCenterRadius(s.modelToSketchSpace(P(x + hw, 0, zc_h)), r * C)
        poly(s, [(x - hw, 0, zc_h - r), (x + hw, 0, zc_h - r), (x + hw, 0, zc_h + r), (x - hw, 0, zc_h + r)])
    xz_extrude(all_profiles(s), CUT, STANDOFF - 0.5, TB + 1, base)

    # stiffening rib above the cord holes, between the rail posts of the cover
    sk = xy_sketch(STIFF_RIB_Z, "Stiffening rib")
    xr = RAIL_X - RAIL_B / 2 - 1.0 - 5.0
    poly(sk, [(-xr, BW1 + 0.5, STIFF_RIB_Z), (xr, BW1 + 0.5, STIFF_RIB_Z),
              (xr, BW1 - STIFF_RIB_D, STIFF_RIB_Z), (-xr, BW1 - STIFF_RIB_D, STIFF_RIB_Z)])
    extrude(sk.profiles.item(0), STIFF_RIB_H, JOIN, base)

    # cord channel and T-hooks on the back of the back wall (profiles in plan, extruded up)
    y_out = -CLIP_GAP                       # outer face of the lips, short of the wall
    y_lip = y_out - CLIP_LIP_T
    sk = xy_sketch(0, "Cord channel")
    for sx in (-1, 1):
        xi, xo, xl = sx * CHAN_X, sx * (CHAN_X + CHAN_POST), sx * (CHAN_X - CHAN_LIP)
        poly(sk, [(xi, BW0 - 0.5, 0), (xo, BW0 - 0.5, 0), (xo, y_out, 0), (xl, y_out, 0), (xl, y_lip, 0), (xi, y_lip, 0)])
    extrude(all_profiles(sk), CHAN_Z1 - CHAN_Z0, JOIN, base)
    for x, z in T_HOOKS:
        sk = xy_sketch(z, f"T-hook x{x:+.0f}")
        a, b = T_STEM / 2, T_CAP / 2
        poly(sk, [(x - a, BW0 - 0.5, z), (x + a, BW0 - 0.5, z), (x + a, y_lip, z), (x + b, y_lip, z),
                  (x + b, y_out, z), (x - b, y_out, z), (x - b, y_lip, z), (x - a, y_lip, z)])
        extrude(sk.profiles.item(0), T_HEIGHT, JOIN, base)

    # dovetail tongues on the back of the back wall, for the wall plate's grooves
    c = MOUNT_CLEAR
    z_t0, z_t1 = MOUNT_Z0 + GROOVE_FLOOR, MOUNT_Z0 + MOUNT_H
    sk = xy_sketch(z_t0, "Mount tongues")
    y_tip = BW0 + GROOVE_DEPTH - c
    for x in MOUNT_GROOVE_XS:
        a0 = GROOVE_A / 2 - c
        a1 = a0 + (GROOVE_DEPTH - c)
        poly(sk, [(x - a0, BW0 - 0.5, z_t0), (x + a0, BW0 - 0.5, z_t0), (x + a0, BW0, z_t0),
                  (x + a1, y_tip, z_t0), (x - a1, y_tip, z_t0), (x - a0, BW0, z_t0)])
    extrude(all_profiles(sk), z_t1 - z_t0, JOIN, base)

    # =================================================================================
    # Wall plate
    # =================================================================================
    sk = xy_sketch(MOUNT_Z0, "Wall plate")
    poly(sk, [(-MOUNT_W / 2, BW0, MOUNT_Z0), (MOUNT_W / 2, BW0, MOUNT_Z0),
              (MOUNT_W / 2, 0, MOUNT_Z0), (-MOUNT_W / 2, 0, MOUNT_Z0)])
    plate = extrude(sk.profiles.item(0), MOUNT_H, NEW).bodies.item(0)
    plate.name = "Wall plate"
    z = MOUNT_Z0 + GROOVE_FLOOR
    sk = xy_sketch(z, "Plate grooves")
    for x in MOUNT_GROOVE_XS:
        a0, a1 = GROOVE_A / 2, GROOVE_A / 2 + GROOVE_DEPTH
        poly(sk, [(x - a0, BW0 - 1, z), (x + a0, BW0 - 1, z), (x + a0, BW0, z),
                  (x + a1, BW0 + GROOVE_DEPTH, z), (x - a1, BW0 + GROOVE_DEPTH, z), (x - a0, BW0, z)])
    extrude(all_profiles(sk), MOUNT_H, CUT, plate)
    # countersunk screw holes
    s = comp.sketches.add(XZ)
    s.name = "Plate screws"
    zs = MOUNT_Z0 + MOUNT_H / 2
    for x in SCREW_XS:
        s.sketchCurves.sketchCircles.addByCenterRadius(s.modelToSketchSpace(P(x, 0, zs)), SCREW_R * C)
    xz_extrude(all_profiles(s), CUT, 0.0, STANDOFF + 1, plate)
    pl = plane_at(comp, XY, "z", zs)
    for x in SCREW_XS:
        s = comp.sketches.add(pl)
        s.name = f"Countersink x{x:+.0f}"
        poly(s, [(x, BW0 - 0.5, zs), (x + SCREW_CSK_R + 0.5, BW0 - 0.5, zs), (x + SCREW_CSK_R, BW0, zs),
                 (x + SCREW_R, BW0 + SCREW_CSK_R - SCREW_R, zs), (x, BW0 + SCREW_CSK_R - SCREW_R, zs)])
        axis = s.sketchCurves.sketchLines.item(4)          # (x, deep) -> (x, front): the screw axis
        ri = feats.revolveFeatures.createInput(s.profiles.item(0), axis, CUT)
        ri.setAngleExtent(False, adsk.core.ValueInput.createByString("360 deg"))
        ri.participantBodies = [plate]
        feats.revolveFeatures.add(ri)

    # =================================================================================
    # Radii and chamfers in the inside corners
    # =================================================================================
    def pick(body, test):
        out = adsk.core.ObjectCollection.create()
        for e in body.edges:
            bb = e.boundingBox
            mn = (bb.minPoint.x / C, bb.minPoint.y / C, bb.minPoint.z / C)
            mx = (bb.maxPoint.x / C, bb.maxPoint.y / C, bb.maxPoint.z / C)
            if test(mn, mx, e):
                out.add(e)
        return out

    near = lambda a, b, tol=0.02: abs(a - b) < tol
    flat_y = lambda mn, mx, y: near(mn[1], y) and near(mx[1], y)
    flat_z = lambda mn, mx, z: near(mn[2], z) and near(mx[2], z)
    flat_x = lambda mn, mx: near(mn[0], mx[0])

    def round_edges(name, edges, r, chamfer=False):
        """Round (or chamfer) the edges; if the kernel refuses r, try smaller sizes and say so."""
        if not edges.count:
            print(name, "no edges")
            return
        for size in (r, r * 0.67, r * 0.4):
            try:
                if chamfer:
                    ci = feats.chamferFeatures.createInput2()
                    ci.chamferEdgeSets.addEqualDistanceChamferEdgeSet(edges, V(size), False)
                    f = feats.chamferFeatures.add(ci)
                else:
                    fi = feats.filletFeatures.createInput()
                    fi.addConstantRadiusEdgeSet(edges, V(size), False)
                    f = feats.filletFeatures.add(fi)
            except RuntimeError:
                continue
            f.name = name
            print(name, edges.count, "edges, size", round(size, 2))
            return
        print(name, "FAILED on", edges.count, "edges")

    round_edges("Fillet wall-plate",
                pick(base, lambda mn, mx, e: flat_y(mn, mx, BW1) and flat_z(mn, mx, PLATE_T) and mx[0] - mn[0] > 1),
                FILLET_MAIN)
    on_gusset = lambda mn, mx: flat_x(mn, mx) and any(near(abs(mn[0] - g), GUSSET_T / 2) for g in GUSSET_XS)
    round_edges("Fillet gussets to wall",
                pick(base, lambda mn, mx, e: on_gusset(mn, mx) and near(mn[1], mx[1], 0.05)
                     and abs(mn[1] - BW1) < FILLET_MAIN + 0.1 and mx[2] - mn[2] > 5), FILLET_MAIN)
    round_edges("Fillet gussets to plate",
                pick(base, lambda mn, mx, e: on_gusset(mn, mx) and near(mn[2], mx[2], 0.05)
                     and abs(mn[2] - PLATE_T) < FILLET_MAIN + 0.1 and mx[1] - mn[1] > 5), FILLET_MAIN)
    round_edges("Chamfer under the rib",
                pick(base, lambda mn, mx, e: flat_y(mn, mx, BW1) and flat_z(mn, mx, STIFF_RIB_Z) and mx[0] - mn[0] > 1),
                RIB_CHAMFER, chamfer=True)
    NURBS = adsk.core.Curve3DTypes.NurbsCurve3DCurveType
    round_edges("Fillet cradles",
                pick(base, lambda mn, mx, e: flat_z(mn, mx, PLATE_T) and e.geometry.curveType == NURBS
                     and mn[1] < Y_PEG + 32 and mx[1] > Y_PEG - 32),
                FILLET_CRADLE)

    def tongue_root(mn, mx, e):
        if not (flat_z(mn, mx, PLATE_T) and flat_x(mn, mx) and mx[1] - mn[1] > 5):
            return False
        return any(near(abs(mn[0] - xs), TONGUE_X0) or near(abs(mn[0] - xs), TONGUE_X0 + TONGUE_T) for xs in SLOTS)
    round_edges("Fillet tongue roots", pick(base, tongue_root), FILLET_TONGUE)
    xw = W / 2 - T
    round_edges("Fillet rail posts",
                pick(cover, lambda mn, mx, e: flat_x(mn, mx) and near(abs(mn[0]), xw) and near(mn[1], mx[1])
                     and near(mn[1], BW1 - POST_D) and mx[2] - mn[2] > 10),     # front edges only: the base sits behind
                FILLET_POST)

    # cord slots under the holes, cut last so the corner fillet is cleared in front of them
    s = comp.sketches.add(XZ)
    s.name = "Cord slots"
    hw = CORD_SLOT_W / 2
    zc_s = CORD_SLOT_Z0 + hw
    for x in SLOTS:
        s.sketchCurves.sketchCircles.addByCenterRadius(s.modelToSketchSpace(P(x, 0, zc_s)), hw * C)
        poly(s, [(x - hw, 0, zc_s), (x + hw, 0, zc_s), (x + hw, 0, CORD_HOLE_Z0 + 2), (x - hw, 0, CORD_HOLE_Z0 + 2)])
    slot_cut = xz_extrude(all_profiles(s), CUT, STANDOFF - 0.5, TB + 3.5, base)

    for b in (cover, base, plate):
        bb = b.boundingBox
        print(b.name, [round(v / C, 1) for v in (bb.minPoint.x, bb.minPoint.y, bb.minPoint.z,
                                                 bb.maxPoint.x, bb.maxPoint.y, bb.maxPoint.z)],
              "vol cm3", round(b.volume, 1))
