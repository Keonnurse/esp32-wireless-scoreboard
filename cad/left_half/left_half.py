# ============================================================
# Scoreboard Casing - v23 LEFT HALF (full part)
#   Frame core + panel track  : verbatim from validated v22 coupon
#   + LED_TRIM                : window/bezel opened 1.5mm on
#                               left/top/bottom (panel track UNCHANGED
#                               so the tested fit does not move)
#   + Back-plate track        : C-channel on the back railing, plate
#                               rides 10mm above railing (8mm parts
#                               + 2mm clr), slides in from the right,
#                               left end-stop. Total depth 36.3mm.
#   + Back plate body         : printed beside the frame, 2mm, notched
#                               for the power cable.
#
# TEST_LEN = TOTAL_W builds the full part.
# Set TEST_LEN = 60.0 to build a fit coupon instead.
# Print FRONT FACE DOWN (same orientation as the coupon).
# ============================================================

import adsk.core, adsk.fusion, adsk.cam, traceback

TOTAL_W      = 200.0
TOTAL_H      = 208.0
OUTER_R      = 20.0
BORDER       = 25.0
PANEL_H      = 158.0   # measured panel height
PANEL_T      = 13.9    # measured panel thickness
APERTURE_W   = 150.0
APERTURE_R   = 8.0     # cosmetic round on the FRONT FACE window only
PROTRUDE     = 5.0     # proud front bezel = the slot's front wall

LED_TRIM     = 1.5     # open window/aperture this much on left/top/bottom

# -- Test coupon ----------------------------------------------
TEST_LEN     = 200.0   # = TOTAL_W -> full part; 60.0 -> fit coupon

# -- Fit tuning (same as v22) ---------------------------------
PANEL_CLR_Z  = 0.5     # front-to-back slide clearance in the track
PANEL_CLR_Y  = 2.0     # total vertical play between the slot floors

# -- Track slot tuning ---------------------------------------
OVERLAP      = 4.0     # how far the window lip overlaps the panel edge
CORNER_RELIEF = 2.0    # half-size of relief squares at left cavity corners

# -- Back railing tuning --------------------------------------
BACK_RAIL_T  = 3.0     # railing height behind the back face
BACK_REACH   = 4.0     # cantilever past the slot floor (catches the panel)
BACK_ANCHOR  = 4.0     # weld width onto the wall's back face

# -- Back-plate track tuning ----------------------------------
RISER_H      = 10.0    # railing top -> plate underside (8mm parts + 2mm clr)
PLATE_T      = 2.0     # back plate thickness
TRACK_GAP    = PLATE_T + 0.4   # 2.4  channel height (plate + slide play)
ROOF_T       = 1.5     # lip over the plate
RAIL_W       = 3.0     # ledge depth: how far the shelf/roof reach under the plate
WALL_W       = 1.5     # outer guide wall beside the plate edge
TRACK_CLR    = 0.3     # plate edge slide clearance
STOP_W       = 3.0     # left end-stop block width

# -- Back-plate notch (power cable) ---------------------------
NOTCH_CX     = 150.0   # centre of notch, from plate LEFT end
NOTCH_W      = 12.0
NOTCH_H      = 10.0
PLATE_OX     = 220.0   # X offset where the plate body is laid out (beside frame)

# Derived fit
RAIL_THICK = PANEL_T + PANEL_CLR_Z          # 14.4  body depth = track gap
SLOT_DEPTH = OVERLAP + PANEL_CLR_Y / 2.0    # 5.0   pocket depth per wall

# Derived layout (STRUCTURAL - drive panel track, seam, railing; NOT trimmed)
WIN_Y0  = BORDER + OVERLAP              # 29    window bottom edge
WIN_Y1  = BORDER + PANEL_H - OVERLAP    # 179   window top edge
WIN_H   = PANEL_H - 2 * OVERLAP         # 150   window height
FLOOR_B = WIN_Y0 - SLOT_DEPTH           # 24    bottom slot floor
FLOOR_T = WIN_Y1 + SLOT_DEPTH           # 184   top slot floor
FLOOR_L = BORDER - SLOT_DEPTH           # 20    left slot floor (end stop)
RUN_X1  = BORDER + APERTURE_W           # 175   open right region begins
Z_BACK  = PROTRUDE + RAIL_THICK         # 19.4  back face (railing behind it)
TOTAL_D = PROTRUDE + RAIL_THICK + BACK_RAIL_T   # 22.4 frame depth

# Derived back-plate track
RAIL_X0   = FLOOR_L - BACK_ANCHOR        # 16    rails start
Z_TRACK0  = TOTAL_D                       # 22.4  railing top (shelf base)
Z_FLOOR   = Z_TRACK0 + RISER_H            # 32.4  shelf top / plate underside
Z_GAPTOP  = Z_FLOOR + TRACK_GAP           # 34.8  roof underside
Z_ROOF    = Z_GAPTOP + ROOF_T             # 36.3  total depth

PLATE_W   = 180.7
PLATE_H   = 164.4
PLATE_Y0  = (TOTAL_H - PLATE_H) / 2.0     # 21.8  plate bottom edge (centred)
PLATE_Y1  = PLATE_Y0 + PLATE_H            # 186.2 plate top edge
PLATE_X0  = RAIL_X0 + STOP_W              # 19    left stop face

# Channel Y edges (top and bottom rails)
TOP_LEDGE_Y0 = PLATE_Y1 - RAIL_W                 # 183.2  shelf/roof reach
TOP_OUT_Y1   = PLATE_Y1 + TRACK_CLR + WALL_W     # 188.0  outer edge
TOP_WALL_Y0  = PLATE_Y1 + TRACK_CLR              # 186.5  outer guide wall
BOT_LEDGE_Y1 = PLATE_Y0 + RAIL_W                 # 24.8
BOT_OUT_Y0   = PLATE_Y0 - TRACK_CLR - WALL_W     # 20.0
BOT_WALL_Y1  = PLATE_Y0 - TRACK_CLR              # 21.5

CHOP_DEPTH = Z_ROOF + 5.0                  # chop clears frame + rails


def cm(mm):
    return mm / 10.0


def run(context):
    app = adsk.core.Application.get()
    ui  = app.userInterface
    try:
        des      = adsk.fusion.Design.cast(app.activeProduct)
        root     = des.rootComponent
        sketches = root.sketches
        extrudes = root.features.extrudeFeatures
        planes   = root.constructionPlanes
        xy_plane = root.xYConstructionPlane

        def pt(x, y):
            return adsk.core.Point3D.create(cm(x), cm(y), 0)

        R, W, H = OUTER_R, TOTAL_W, TOTAL_H

        # -- LED_TRIM: only the cosmetic window/aperture opens up.
        #    Right edge stays at the 175 seam; left/top/bottom open by
        #    LED_TRIM. The structural WIN_*/FLOOR_*/RUN_X1 constants are
        #    untouched, so the panel track keeps its tested fit.
        ax = BORDER - LED_TRIM            # 23.5  window/aperture left
        aw = APERTURE_W + LED_TRIM        # 151.5 width (right stays at 175)
        ar = APERTURE_R                   # 8.0
        ay = WIN_Y0 - LED_TRIM            # 27.5  window/aperture bottom
        ah = WIN_H + 2 * LED_TRIM         # 153   height (top + bottom open)

        def draw_pill(sk, include_aperture=False):
            l = sk.sketchCurves.sketchLines
            a = sk.sketchCurves.sketchArcs
            l.addByTwoPoints(pt(R, 0),   pt(W, 0))
            l.addByTwoPoints(pt(W, 0),   pt(W, H))
            l.addByTwoPoints(pt(W, H),   pt(R, H))
            a.addByCenterStartEnd(pt(R, H-R), pt(R, H), pt(0, H-R))
            l.addByTwoPoints(pt(0, H-R), pt(0, R))
            a.addByCenterStartEnd(pt(R, R),   pt(0, R), pt(R, 0))
            if include_aperture:
                l.addByTwoPoints(pt(ax+ar, ay),       pt(ax+aw, ay))
                l.addByTwoPoints(pt(ax+aw, ay),       pt(ax+aw, ay+ah))
                l.addByTwoPoints(pt(ax+aw, ay+ah),    pt(ax+ar, ay+ah))
                a.addByCenterStartEnd(pt(ax+ar, ay+ah-ar), pt(ax+ar, ay+ah), pt(ax, ay+ah-ar))
                l.addByTwoPoints(pt(ax, ay+ah-ar),    pt(ax, ay+ar))
                a.addByCenterStartEnd(pt(ax+ar, ay+ar), pt(ax, ay+ar), pt(ax+ar, ay))

        def draw_rect(sk, x0, x1, y0, y1):
            l = sk.sketchCurves.sketchLines
            l.addByTwoPoints(pt(x0, y0), pt(x1, y0))
            l.addByTwoPoints(pt(x1, y0), pt(x1, y1))
            l.addByTwoPoints(pt(x1, y1), pt(x0, y1))
            l.addByTwoPoints(pt(x0, y1), pt(x0, y0))

        def make_offset_plane(base, offset_mm, name):
            inp = planes.createInput()
            inp.setByOffset(base, adsk.core.ValueInput.createByReal(cm(offset_mm)))
            p = planes.add(inp)
            p.name = name
            return p

        def join_block(name, z_base, thickness, rects):
            """Join-extrude a set of rectangles up +Z from an offset plane."""
            pl = make_offset_plane(xy_plane, z_base, name + "_plane")
            sk = sketches.add(pl); sk.name = name
            for (x0, x1, y0, y1) in rects:
                draw_rect(sk, x0, x1, y0, y1)
            profs = adsk.core.ObjectCollection.create()
            for i in range(sk.profiles.count):
                profs.add(sk.profiles.item(i))
            e = extrudes.createInput(profs, adsk.fusion.FeatureOperations.JoinFeatureOperation)
            e.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(thickness)))
            extrudes.add(e)

        # -- STEP 1: RAIL BODY -----------------------------------
        front_plane = make_offset_plane(xy_plane, PROTRUDE, "FrontFacePlane")
        sk1 = sketches.add(front_plane); sk1.name = "Sketch_RailBody"
        draw_pill(sk1)
        outer_prof = max([sk1.profiles.item(i) for i in range(sk1.profiles.count)],
                         key=lambda p: p.areaProperties().area)
        ext1 = extrudes.createInput(outer_prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ext1.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(RAIL_THICK)))
        extrudes.add(ext1)
        body = root.bRepBodies.item(root.bRepBodies.count - 1)
        body.name = "LeftFrame_v23"

        # -- STEP 2: WINDOW CAVITY CUT (square corners, LED-trimmed) ---
        sk2 = sketches.add(front_plane); sk2.name = "Sketch_Window"
        draw_rect(sk2, ax, ax + aw, ay, ay + ah)
        cut_ap = extrudes.createInput(sk2.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_ap.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(RAIL_THICK)))
        extrudes.add(cut_ap)

        # -- STEP 3: OPEN RIGHT SIDE -----------------------------
        sk_open = sketches.add(front_plane); sk_open.name = "Sketch_RightOpen"
        draw_rect(sk_open, RUN_X1, TOTAL_W, FLOOR_B, FLOOR_T)
        cut_open = extrudes.createInput(sk_open.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_open.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(RAIL_THICK)))
        extrudes.add(cut_open)

        # -- STEP 4: PROTRUSION (proud front bezel, Z 5 -> 0) ----
        sk7 = sketches.add(front_plane); sk7.name = "Sketch_Protrusion"
        draw_pill(sk7, include_aperture=True)
        profiles_sorted = sorted([sk7.profiles.item(i) for i in range(sk7.profiles.count)],
                                 key=lambda p: p.areaProperties().area)
        ring_prof = profiles_sorted[1] if len(profiles_sorted) >= 3 else profiles_sorted[0]
        prot = extrudes.createInput(ring_prof, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        prot.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(cm(PROTRUDE))),
            adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes.add(prot)

        # -- STEP 4b: OPEN THE FRONT AT THE SEAM -----------------
        sk4b = sketches.add(front_plane); sk4b.name = "Sketch_FrontOpenSeam"
        draw_rect(sk4b, RUN_X1, TOTAL_W, WIN_Y0, WIN_Y1)
        cut_front = extrudes.createInput(sk4b.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_front.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(cm(PROTRUDE))),
            adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes.add(cut_front)

        # -- STEP 5: U-SHAPED TRACK SLOTS + CORNER RELIEFS -------
        #    (UNCHANGED by LED_TRIM - this is the dialed-in panel fit)
        sk5 = sketches.add(front_plane); sk5.name = "Sketch_TrackSlots"
        draw_rect(sk5, FLOOR_L, BORDER, FLOOR_B, FLOOR_T)     # left slot
        draw_rect(sk5, FLOOR_L, RUN_X1, FLOOR_B, WIN_Y0)      # bottom slot
        draw_rect(sk5, FLOOR_L, RUN_X1, WIN_Y1, FLOOR_T)      # top slot
        draw_rect(sk5, FLOOR_L - CORNER_RELIEF, FLOOR_L + CORNER_RELIEF,
                       FLOOR_T - CORNER_RELIEF, FLOOR_T + CORNER_RELIEF)  # top-left relief
        draw_rect(sk5, FLOOR_L - CORNER_RELIEF, FLOOR_L + CORNER_RELIEF,
                       FLOOR_B - CORNER_RELIEF, FLOOR_B + CORNER_RELIEF)  # bottom-left relief

        slot_profs = adsk.core.ObjectCollection.create()
        for i in range(sk5.profiles.count):
            slot_profs.add(sk5.profiles.item(i))
        cut_slots = extrudes.createInput(slot_profs, adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_slots.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(RAIL_THICK)))
        extrudes.add(cut_slots)

        # -- STEP 6: BACK RAILING (top + bottom + left) ----------
        back_plane = make_offset_plane(xy_plane, Z_BACK, "BackFacePlane")
        sk6 = sketches.add(back_plane); sk6.name = "Sketch_BackRailing"
        draw_rect(sk6, FLOOR_L - BACK_ANCHOR, TOTAL_W,
                       FLOOR_T - BACK_REACH,  FLOOR_T + BACK_ANCHOR)   # top strip
        draw_rect(sk6, FLOOR_L - BACK_ANCHOR, TOTAL_W,
                       FLOOR_B - BACK_ANCHOR, FLOOR_B + BACK_REACH)    # bottom strip
        draw_rect(sk6, FLOOR_L - BACK_ANCHOR, FLOOR_L + BACK_REACH,
                       FLOOR_B - BACK_ANCHOR, FLOOR_T + BACK_ANCHOR)   # left strip

        rail_profs = adsk.core.ObjectCollection.create()
        for i in range(sk6.profiles.count):
            rail_profs.add(sk6.profiles.item(i))
        join_rail = extrudes.createInput(rail_profs, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        join_rail.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(BACK_RAIL_T)))
        extrudes.add(join_rail)

        # -- STEP 7: BACK-PLATE TRACK (C-channel on the railing) -
        # Shelf (riser): base at railing top, 10mm tall. Plate rests on
        # its top face at Z=32.4. Reaches RAIL_W under the plate edge.
        join_block("BPT_Shelf", Z_TRACK0, RISER_H, [
            (RAIL_X0, TOTAL_W, TOP_LEDGE_Y0, TOP_OUT_Y1),   # top shelf
            (RAIL_X0, TOTAL_W, BOT_OUT_Y0,   BOT_LEDGE_Y1), # bottom shelf
        ])
        # Outer guide wall: fills the channel height at the very outer
        # edge so the plate is captured on the outside.
        join_block("BPT_OuterWall", Z_FLOOR, TRACK_GAP, [
            (RAIL_X0, TOTAL_W, TOP_WALL_Y0, TOP_OUT_Y1),    # top wall
            (RAIL_X0, TOTAL_W, BOT_OUT_Y0,  BOT_WALL_Y1),   # bottom wall
        ])
        # Left closure: one solid wall across the full height (railing top
        # -> roof line) spanning the whole channel, closing the open left
        # end into a 3-sided tray. Sits on the back-railing left strip, so
        # it is fully supported; the plate's left edge butts it as the stop.
        join_block("BPT_LeftClose", Z_TRACK0, Z_ROOF - Z_TRACK0, [
            (RAIL_X0, PLATE_X0, BOT_OUT_Y0, TOP_OUT_Y1),
        ])
        # Roof lip: caps over the plate edge, holding it down.
        join_block("BPT_Roof", Z_GAPTOP, ROOF_T, [
            (RAIL_X0, TOTAL_W, TOP_LEDGE_Y0, TOP_OUT_Y1),   # top roof
            (RAIL_X0, TOTAL_W, BOT_OUT_Y0,   BOT_LEDGE_Y1), # bottom roof
        ])

        # -- STEP 8: CHOP TO TEST LENGTH (coupon only) -----------
        # Cut away everything right of X = TEST_LEN, through the FULL
        # depth (bezel + body + railing + track). Skipped for the full
        # part: at TEST_LEN = TOTAL_W the cut lands past the body and
        # Fusion raises "No target body found to cut or intersect".
        if TEST_LEN < TOTAL_W - 0.001:
            sk8 = sketches.add(xy_plane); sk8.name = "Sketch_TestChop"
            draw_rect(sk8, TEST_LEN, TOTAL_W + 5.0, -5.0, TOTAL_H + 5.0)
            chop = extrudes.createInput(sk8.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
            chop.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(CHOP_DEPTH)))
            extrudes.add(chop)

        # -- STEP 9: BACK PLATE BODY (separate, printed beside frame) --
        # Built AFTER the chop and offset in +X so it is untouched.
        skp = sketches.add(xy_plane); skp.name = "Sketch_BackPlate"
        draw_rect(skp, PLATE_OX, PLATE_OX + PLATE_W, 0.0, PLATE_H)
        plate_ext = extrudes.createInput(skp.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        plate_ext.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(PLATE_T)))
        plate_feat = extrudes.add(plate_ext)
        plate_body = plate_feat.bodies.item(0)
        plate_body.name = "BackPlate_v23"

        # Cable notch in the plate's bottom edge.
        skn = sketches.add(xy_plane); skn.name = "Sketch_PlateNotch"
        nx0 = PLATE_OX + NOTCH_CX - NOTCH_W / 2.0
        nx1 = PLATE_OX + NOTCH_CX + NOTCH_W / 2.0
        draw_rect(skn, nx0, nx1, -1.0, NOTCH_H)
        cut_notch = extrudes.createInput(skn.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_notch.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(PLATE_T + 1.0)))
        extrudes.add(cut_notch)

        ui.messageBox(
            "v23 left half built.\n"
            "LED reveal: window 151.5 x 153 at (23.5, 27.5), right at seam.\n"
            "Back-plate track: plate floor Z=%.1f, channel %.1f, roof %.1f, "
            "total depth %.1f.\n"
            "Back plate %0.1f x %0.1f x %0.1f printed beside the frame, "
            "notch %0.0f x %0.0f at CX=%0.0f.\n"
            "TEST_LEN = %.0f."
            % (Z_FLOOR, TRACK_GAP, ROOF_T, Z_ROOF,
               PLATE_W, PLATE_H, PLATE_T, NOTCH_W, NOTCH_H, NOTCH_CX, TEST_LEN))

    except:
        ui.messageBox("Script failed:\n" + traceback.format_exc())