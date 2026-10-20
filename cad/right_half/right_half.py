# ============================================================
# Scoreboard Casing - RIGHT HALF v2  (was v1; widened to close seam)
#   CHANGE vs v1: TOTAL_W 145 -> 160.3 to close the measured 15.3mm
#   gap at the seam. Registers off the panel's RIGHT edge (FLOOR_R),
#   so the rounded outer end stays 20mm past the panel; the extra
#   15.3mm extends the window + track toward the LEFT half. TEST_LEN
#   moved with it so STEP 8's chop never eats the seam.
#
#   Closed / rounded R20 corners on the RIGHT, solid right border,
#   panel right edge stops at FLOOR_R. Open FLAT seam on the LEFT
#   (the dovetail goes here later - left flat for now).
#
#   Mirrors every v23 feature L<->R:
#     + LED_TRIM opens aperture on RIGHT/top/bottom (seam fixed)
#     + panel track: stop slot on the right, slots run to the seam
#     + back railing cantilevers out to the seam, right strip closes
#     + back-plate track: closure wall on the right, plate slides in
#       from the seam, own back plate body printed beside the frame
#
#   WIDTH = 160.3mm  (was 145; +15.3 to meet the left half at the seam).
#   DOVETAIL: deferred - cut into both halves once the printed seam
#             thickness is measured.
#
#   TEST_LEN = TOTAL_W builds the full part (keeps the closed RIGHT
#   end). Set e.g. TEST_LEN = 60 for a fit coupon of the closed end.
#   Print FRONT FACE DOWN.
# ============================================================

import adsk.core, adsk.fusion, adsk.cam, traceback

TOTAL_W      = 160.3   # right half width  (was 145; +15.3 closes seam gap)
TOTAL_H      = 208.0
OUTER_R      = 20.0
BORDER       = 25.0
PANEL_H      = 158.0   # measured panel height
PANEL_T      = 13.9    # measured panel thickness
APERTURE_R   = 8.0     # cosmetic round on the FRONT FACE window only
PROTRUDE     = 5.0     # proud front bezel = the slot's front wall

LED_TRIM     = 1.5     # open aperture this much on RIGHT/top/bottom
SEAM_STRIP   = 25.0    # open strip at the seam (mirror of left's 175->200)

# -- Test coupon ----------------------------------------------
TEST_LEN     = 160.3   # = TOTAL_W -> full part; smaller keeps the closed end

# -- Fit tuning (same as v23) ---------------------------------
PANEL_CLR_Z  = 0.5     # front-to-back slide clearance in the track
PANEL_CLR_Y  = 2.0     # total vertical play between the slot floors

# -- Track slot tuning ---------------------------------------
OVERLAP      = 4.0     # how far the window lip overlaps the panel edge
CORNER_RELIEF = 2.0    # half-size of relief squares at right cavity corners

# -- Back railing tuning --------------------------------------
BACK_RAIL_T  = 3.0
BACK_REACH   = 4.0
BACK_ANCHOR  = 4.0

# -- Back-plate track tuning ----------------------------------
RISER_H      = 10.0    # railing top -> plate underside
PLATE_T      = 2.0     # back plate thickness
TRACK_GAP    = PLATE_T + 0.4   # 2.4  channel height
ROOF_T       = 1.5     # lip over the plate
RAIL_W       = 3.0     # ledge depth under the plate edge
WALL_W       = 1.5     # outer guide wall beside the plate edge
TRACK_CLR    = 0.3     # plate edge slide clearance
STOP_W       = 3.0     # right end-stop / closure wall width

# -- Back-plate notch (power cable) ---------------------------
NOTCH_CX     = 60.0    # centre of notch, from plate LEFT (seam) end
NOTCH_W      = 12.0
NOTCH_H      = 10.0
PLATE_OX     = 180.0   # X offset where the plate body is laid out

# Derived aperture width: seam strip + framed aperture + right border
APERTURE_W   = TOTAL_W - BORDER - SEAM_STRIP   # 110.3 framed reveal (was 95)

# Derived fit
RAIL_THICK = PANEL_T + PANEL_CLR_Z          # 14.4
SLOT_DEPTH = OVERLAP + PANEL_CLR_Y / 2.0    # 5.0

# Derived layout (mirror: closed/stop on the RIGHT, open seam on the LEFT)
WIN_Y0  = BORDER + OVERLAP              # 29   window bottom edge
WIN_Y1  = BORDER + PANEL_H - OVERLAP    # 179  window top edge
WIN_H   = PANEL_H - 2 * OVERLAP         # 150  window height
FLOOR_B = WIN_Y0 - SLOT_DEPTH           # 24   bottom slot floor
FLOOR_T = WIN_Y1 + SLOT_DEPTH           # 184  top slot floor
FLOOR_R = TOTAL_W - (BORDER - SLOT_DEPTH)   # 140.3 RIGHT slot floor (panel stop)
APER_X0 = SEAM_STRIP                    # 25   aperture left edge (seam side)
APER_X1 = TOTAL_W - BORDER              # 135.3 aperture right edge (closed side)
RUN_X0  = SEAM_STRIP                    # 25   open seam strip is 0 -> RUN_X0
Z_BACK  = PROTRUDE + RAIL_THICK         # 19.4 back face
TOTAL_D = PROTRUDE + RAIL_THICK + BACK_RAIL_T   # 22.4 frame depth

# Derived back-plate track
RAIL_X1   = FLOOR_R + BACK_ANCHOR        # 144.3 closed-side anchor (railing/rails)
Z_TRACK0  = TOTAL_D                       # 22.4 railing top (shelf base)
Z_FLOOR   = Z_TRACK0 + RISER_H            # 32.4 shelf top / plate underside
Z_GAPTOP  = Z_FLOOR + TRACK_GAP           # 34.8 roof underside
Z_ROOF    = Z_GAPTOP + ROOF_T             # 36.3 total depth

PLATE_H   = 164.4
PLATE_X1  = RAIL_X1 - STOP_W              # 141.3 plate right edge (stop)
PLATE_W   = PLATE_X1 - 0.3                # 141.0 plate spans seam(0.3)->stop(141.3)
PLATE_Y0  = (TOTAL_H - PLATE_H) / 2.0     # 21.8
PLATE_Y1  = PLATE_Y0 + PLATE_H            # 186.2

# Channel Y edges (identical to left half)
TOP_LEDGE_Y0 = PLATE_Y1 - RAIL_W                 # 183.2
TOP_OUT_Y1   = PLATE_Y1 + TRACK_CLR + WALL_W     # 188.0
TOP_WALL_Y0  = PLATE_Y1 + TRACK_CLR              # 186.5
BOT_LEDGE_Y1 = PLATE_Y0 + RAIL_W                 # 24.8
BOT_OUT_Y0   = PLATE_Y0 - TRACK_CLR - WALL_W     # 20.0
BOT_WALL_Y1  = PLATE_Y0 - TRACK_CLR              # 21.5

CHOP_DEPTH = Z_ROOF + 5.0


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

        # LED_TRIM: aperture opens on RIGHT (closed) / top / bottom.
        # Seam (left) edge stays put. Structural WIN_*/FLOOR_*/RUN_X0
        # constants are untouched, so the panel track keeps its fit.
        ax = APER_X0                       # 25    seam side (fixed)
        aw = (APER_X1 - APER_X0) + LED_TRIM  # 111.8 grows toward closed right
        ar = APERTURE_R                    # 8
        ay = WIN_Y0 - LED_TRIM             # 27.5  bottom opens
        ah = WIN_H + 2 * LED_TRIM          # 153   top + bottom open

        def draw_pill(sk, include_aperture=False):
            # Outline: flat seam edge on the LEFT (x=0), R20 rounds on
            # the RIGHT (x=W). Mirror of the left half.
            l = sk.sketchCurves.sketchLines
            a = sk.sketchCurves.sketchArcs
            l.addByTwoPoints(pt(0, 0),     pt(W-R, 0))           # bottom edge
            a.addByCenterStartEnd(pt(W-R, R), pt(W-R, 0), pt(W, R))      # bottom-right arc
            l.addByTwoPoints(pt(W, R),     pt(W, H-R))           # right edge
            a.addByCenterStartEnd(pt(W-R, H-R), pt(W, H-R), pt(W-R, H))  # top-right arc
            l.addByTwoPoints(pt(W-R, H),   pt(0, H))             # top edge
            l.addByTwoPoints(pt(0, H),     pt(0, 0))             # seam edge (flat)
            if include_aperture:
                # Aperture: flat seam edge on the LEFT (ax), rounds on
                # the RIGHT (ax+aw).
                l.addByTwoPoints(pt(ax, ay),            pt(ax+aw-ar, ay))
                a.addByCenterStartEnd(pt(ax+aw-ar, ay+ar), pt(ax+aw-ar, ay), pt(ax+aw, ay+ar))
                l.addByTwoPoints(pt(ax+aw, ay+ar),      pt(ax+aw, ay+ah-ar))
                a.addByCenterStartEnd(pt(ax+aw-ar, ay+ah-ar), pt(ax+aw, ay+ah-ar), pt(ax+aw-ar, ay+ah))
                l.addByTwoPoints(pt(ax+aw-ar, ay+ah),   pt(ax, ay+ah))
                l.addByTwoPoints(pt(ax, ay+ah),         pt(ax, ay))

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
        body.name = "RightHalf_v2"

        # -- STEP 2: WINDOW CAVITY CUT (square, LED-trimmed) -----
        sk2 = sketches.add(front_plane); sk2.name = "Sketch_Window"
        draw_rect(sk2, ax, ax + aw, ay, ay + ah)
        cut_ap = extrudes.createInput(sk2.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_ap.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(RAIL_THICK)))
        extrudes.add(cut_ap)

        # -- STEP 3: OPEN SEAM SIDE (left) -----------------------
        sk_open = sketches.add(front_plane); sk_open.name = "Sketch_SeamOpen"
        draw_rect(sk_open, 0.0, RUN_X0, FLOOR_B, FLOOR_T)
        cut_open = extrudes.createInput(sk_open.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_open.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(RAIL_THICK)))
        extrudes.add(cut_open)

        # -- STEP 4: PROTRUSION (proud front bezel, Z 5 -> 0) ----
        sk7 = sketches.add(front_plane); sk7.name = "Sketch_Protrusion"
        draw_pill(sk7, include_aperture=True)
        # Pick the RING (proud bezel border) by bounding box, NOT by area.
        # The ring's outer loop is the full pill, so it always has the
        # largest extent. Area ranking is fragile: on a narrow part the
        # ring can be larger than the window, flipping the order and
        # grabbing the wrong profile.
        def _bbox_d2(p):
            bb = p.boundingBox
            dx = bb.maxPoint.x - bb.minPoint.x
            dy = bb.maxPoint.y - bb.minPoint.y
            return dx * dx + dy * dy
        ring_prof = max([sk7.profiles.item(i) for i in range(sk7.profiles.count)],
                        key=_bbox_d2)
        prot = extrudes.createInput(ring_prof, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        prot.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(cm(PROTRUDE))),
            adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes.add(prot)

        # -- STEP 4b: OPEN THE FRONT AT THE SEAM -----------------
        sk4b = sketches.add(front_plane); sk4b.name = "Sketch_FrontOpenSeam"
        draw_rect(sk4b, 0.0, RUN_X0, WIN_Y0, WIN_Y1)
        cut_front = extrudes.createInput(sk4b.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_front.setOneSideExtent(
            adsk.fusion.DistanceExtentDefinition.create(adsk.core.ValueInput.createByReal(cm(PROTRUDE))),
            adsk.fusion.ExtentDirections.NegativeExtentDirection)
        extrudes.add(cut_front)

        # -- STEP 5: U-SHAPED TRACK SLOTS + CORNER RELIEFS -------
        #    Stop slot + reliefs on the RIGHT (closed) side now.
        sk5 = sketches.add(front_plane); sk5.name = "Sketch_TrackSlots"
        draw_rect(sk5, APER_X1, FLOOR_R, FLOOR_B, FLOOR_T)    # right stop slot
        draw_rect(sk5, RUN_X0, FLOOR_R, FLOOR_B, WIN_Y0)      # bottom slot
        draw_rect(sk5, RUN_X0, FLOOR_R, WIN_Y1, FLOOR_T)      # top slot
        draw_rect(sk5, FLOOR_R - CORNER_RELIEF, FLOOR_R + CORNER_RELIEF,
                       FLOOR_T - CORNER_RELIEF, FLOOR_T + CORNER_RELIEF)  # top-right relief
        draw_rect(sk5, FLOOR_R - CORNER_RELIEF, FLOOR_R + CORNER_RELIEF,
                       FLOOR_B - CORNER_RELIEF, FLOOR_B + CORNER_RELIEF)  # bottom-right relief

        slot_profs = adsk.core.ObjectCollection.create()
        for i in range(sk5.profiles.count):
            slot_profs.add(sk5.profiles.item(i))
        cut_slots = extrudes.createInput(slot_profs, adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_slots.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(RAIL_THICK)))
        extrudes.add(cut_slots)

        # -- STEP 6: BACK RAILING (top + bottom + RIGHT) ---------
        back_plane = make_offset_plane(xy_plane, Z_BACK, "BackFacePlane")
        sk6 = sketches.add(back_plane); sk6.name = "Sketch_BackRailing"
        draw_rect(sk6, 0.0, RAIL_X1, FLOOR_T - BACK_REACH,  FLOOR_T + BACK_ANCHOR)   # top strip
        draw_rect(sk6, 0.0, RAIL_X1, FLOOR_B - BACK_ANCHOR, FLOOR_B + BACK_REACH)    # bottom strip
        draw_rect(sk6, FLOOR_R - BACK_REACH, RAIL_X1,
                       FLOOR_B - BACK_ANCHOR, FLOOR_T + BACK_ANCHOR)                  # right strip

        rail_profs = adsk.core.ObjectCollection.create()
        for i in range(sk6.profiles.count):
            rail_profs.add(sk6.profiles.item(i))
        join_rail = extrudes.createInput(rail_profs, adsk.fusion.FeatureOperations.JoinFeatureOperation)
        join_rail.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(BACK_RAIL_T)))
        extrudes.add(join_rail)

        # -- STEP 7: BACK-PLATE TRACK (C-channel, closure on right) --
        join_block("BPT_Shelf", Z_TRACK0, RISER_H, [
            (0.0, RAIL_X1, TOP_LEDGE_Y0, TOP_OUT_Y1),   # top shelf
            (0.0, RAIL_X1, BOT_OUT_Y0,   BOT_LEDGE_Y1), # bottom shelf
        ])
        join_block("BPT_OuterWall", Z_FLOOR, TRACK_GAP, [
            (0.0, RAIL_X1, TOP_WALL_Y0, TOP_OUT_Y1),    # top wall
            (0.0, RAIL_X1, BOT_OUT_Y0,  BOT_WALL_Y1),   # bottom wall
        ])
        # Right closure: full-height wall closing the channel into a
        # 3-sided tray; plate's right edge butts it as the end-stop.
        join_block("BPT_RightClose", Z_TRACK0, Z_ROOF - Z_TRACK0, [
            (PLATE_X1, RAIL_X1, BOT_OUT_Y0, TOP_OUT_Y1),
        ])
        join_block("BPT_Roof", Z_GAPTOP, ROOF_T, [
            (0.0, RAIL_X1, TOP_LEDGE_Y0, TOP_OUT_Y1),   # top roof
            (0.0, RAIL_X1, BOT_OUT_Y0,   BOT_LEDGE_Y1), # bottom roof
        ])

        # -- STEP 8: CHOP TO TEST LENGTH (coupon only) -----------
        # Keeps the closed RIGHT end. Skipped for the full part.
        if TEST_LEN < TOTAL_W - 0.001:
            sk8 = sketches.add(xy_plane); sk8.name = "Sketch_TestChop"
            draw_rect(sk8, -5.0, TOTAL_W - TEST_LEN, -5.0, TOTAL_H + 5.0)
            chop = extrudes.createInput(sk8.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
            chop.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(CHOP_DEPTH)))
            extrudes.add(chop)

        # -- STEP 9: BACK PLATE BODY (separate, beside the frame) --
        skp = sketches.add(xy_plane); skp.name = "Sketch_BackPlate"
        draw_rect(skp, PLATE_OX, PLATE_OX + PLATE_W, 0.0, PLATE_H)
        plate_ext = extrudes.createInput(skp.profiles.item(0), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        plate_ext.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(PLATE_T)))
        plate_feat = extrudes.add(plate_ext)
        plate_body = plate_feat.bodies.item(0)
        plate_body.name = "BackPlate_Right_v2"

        skn = sketches.add(xy_plane); skn.name = "Sketch_PlateNotch"
        nx0 = PLATE_OX + NOTCH_CX - NOTCH_W / 2.0
        nx1 = PLATE_OX + NOTCH_CX + NOTCH_W / 2.0
        draw_rect(skn, nx0, nx1, -1.0, NOTCH_H)
        cut_notch = extrudes.createInput(skn.profiles.item(0), adsk.fusion.FeatureOperations.CutFeatureOperation)
        cut_notch.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(PLATE_T + 1.0)))
        extrudes.add(cut_notch)

        ui.messageBox(
            "Right half v2 built (widened +15.3 to close seam).\n"
            "Width %.1f, aperture %.1f framed at x %.0f-%.1f (right opens with LED_TRIM).\n"
            "Panel stop FLOOR_R=%.1f. Back-plate track closure on the right, "
            "plate slides in from the seam.\n"
            "Back plate %.1f x %.1f x %.1f beside the frame, notch %.0f x %.0f "
            "at CX=%.0f from seam end.\n"
            "Seam (left) edge left FLAT for the dovetail. TEST_LEN = %.1f."
            % (TOTAL_W, APERTURE_W, APER_X0, APER_X1, FLOOR_R,
               PLATE_W, PLATE_H, PLATE_T, NOTCH_W, NOTCH_H, NOTCH_CX, TEST_LEN))

    except:
        ui.messageBox("Script failed:\n" + traceback.format_exc())
