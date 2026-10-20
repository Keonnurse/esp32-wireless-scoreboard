import adsk.core, adsk.fusion, traceback, math

# ============== TUNABLE CONSTANTS (mm / degrees) ==============
TILT_DEG     = 12.0    # back-tilt of the frame from vertical
FRAME_T      = 36.5    # MEASURED full bottom-edge depth (front face -> proud rail back)
SLOT_CLR     = 1.0     # clearance added to FRAME_T for the groove
SLOT_DEPTH   = 28.0    # how deep the frame seats into the groove
GROOVE_BOT_Z = 14.0    # height of groove bottom-centre above table
SLOT_CX      = 28.0    # X of groove bottom-centre (distance back from front face)
FRONT_LIP_Z  = 30.0    # top height of the front retaining lip
BACK_FIN_Z   = 62.0    # top height of the rear support fin (lean surface)
FIN_T        = 10.0    # rear fin thickness, front-to-back
REAR_SHELF_Z = 8.0     # thickness of the rear counterweight shelf
BASE_DEPTH   = 150.0   # total front-to-back footprint
CRADLE_W     = 50.0    # width of ONE cradle (Y). Set 30 for a fit coupon.

# ---- orientation (these signs worked) ----
EXTRUDE_SIGN   = -1.0
ORIENT_UP_SIGN = -1.0
# Print TWO cradles - one under each end of the assembled frame.
# =============================================================

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('Open a Fusion design first.')
            return
        root = design.rootComponent

        MM = 0.1
        t = math.radians(TILT_DEG)
        s, c = math.sin(t), math.cos(t)
        SLOT_W = FRAME_T + SLOT_CLR
        hw = SLOT_W / 2.0
        ax = (s, c)          # up the frame / groove opening direction
        wx = (c, -s)         # across the groove, +X toward back

        def add(p, v, d):
            return (p[0] + v[0]*d, p[1] + v[1]*d)

        GBC = (SLOT_CX, GROOVE_BOT_Z)
        BF  = add(GBC, wx, -hw)                              # bottom front
        BB  = add(GBC, wx,  hw)                              # bottom back
        FLT = add(BF, ax, (FRONT_LIP_Z - BF[1]) / ax[1])    # front lip top
        BFT_in  = add(BB, ax, (BACK_FIN_Z - BB[1]) / ax[1]) # fin top, lean edge
        BFT_out = (BFT_in[0] + FIN_T, BFT_in[1])

        poly = [
            (0.0, 0.0),
            (0.0, FRONT_LIP_Z),
            FLT,
            BF,
            BB,
            BFT_in,
            BFT_out,
            (BFT_out[0], REAR_SHELF_Z),
            (BASE_DEPTH, REAR_SHELF_Z),
            (BASE_DEPTH, 0.0),
        ]

        sk = root.sketches.add(root.xZConstructionPlane)
        lines = sk.sketchCurves.sketchLines
        def P(p):
            return adsk.core.Point3D.create(p[0]*MM, ORIENT_UP_SIGN*p[1]*MM, 0.0)
        pts = [P(p) for p in poly]
        n = len(pts)
        for i in range(n):
            lines.addByTwoPoints(pts[i], pts[(i + 1) % n])

        if sk.profiles.count == 0:
            ui.messageBox('Profile failed to close - check constants.')
            return
        prof = sk.profiles.item(0)

        extrudes = root.features.extrudeFeatures
        ext_in = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        dist = adsk.core.ValueInput.createByReal(CRADLE_W * MM * EXTRUDE_SIGN)
        ext_in.setDistanceExtent(False, dist)
        extrudes.add(ext_in)

        ui.messageBox('Cradle built - 37.5mm groove. Print TWO.')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))