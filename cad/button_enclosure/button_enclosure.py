import os, traceback
import cadquery as cq

# ============================================================
#  SLIDE-PANEL BUTTON ENCLOSURE v7  (CadQuery)
#  Tall tower: 32 wide x 58 deep x 95 TALL.
#  BUTTON on the true TOP (points up).
#  Removable SIDE panel (58 x 95) slides out the BACK horizontally
#  (tab no longer sticks up). Type-C slot near top, cut fully through.
# ============================================================

# ---- BOX (mm) ----  X=width, Y=depth, Z=height(vertical)
WIDTH   = 32.0
DEPTH   = 95.0
HEIGHT  = 58.0
WALL    = 2.5

# ---- SLIDE / GROOVE SYSTEM (panel = open -X side, slides along Y) ----
LIP         = 1.2
PLATE_T     = 2.5
CLR         = 0.45
GROOVE_DEP  = 1.5
GROOVE_H    = PLATE_T + CLR
TAB         = 8.0     # pull tab, sticks out the BACK horizontally (set 0 for flush)

# ---- BUTTON (19mm) on the TOP (+Z) face ----
BTN_D   = 19.6
BTN_X   = 0.0     # across width (0 = center)
BTN_Y   = 0.0     # along depth  (0 = center)

# ---- USB-C CUTOUT on the FRONT END (-Y), TOP-LEFT; rounded, cuts through ----
USB_W   = 9.5
USB_H   = 4.0
USB_X   = -8.0    # toward the left/panel side (flip to +8 for the other side)
USB_Z   = 20.0    # near the top

# ============================================================
stop_y = -DEPTH/2.0 + WALL
side_x = -WIDTH/2.0

def block(x0, x1, y0, y1, z0, z1):
    return (cq.Workplane("XY").box(x1-x0, y1-y0, z1-z0)
            .translate(((x0+x1)/2, (y0+y1)/2, (z0+z1)/2)))

# BOX: 5 walls, open on -X (left side)
box = cq.Workplane("XY").box(WIDTH, DEPTH, HEIGHT)
box = box.cut(block(-WIDTH/2-1, WIDTH/2-WALL, stop_y, DEPTH/2-WALL, -HEIGHT/2+WALL, HEIGHT/2-WALL))

# grooves in top & bottom walls
gx0, gx1 = side_x + LIP, side_x + LIP + GROOVE_H
box = box.cut(block(gx0, gx1, stop_y, DEPTH/2+1,  HEIGHT/2-WALL,             HEIGHT/2-WALL+GROOVE_DEP))
box = box.cut(block(gx0, gx1, stop_y, DEPTH/2+1, -HEIGHT/2+WALL-GROOVE_DEP, -HEIGHT/2+WALL))

# entry cut-down on +Y (back) so the panel feeds in
box = box.cut(block(-WIDTH/2-1, gx1+0.5, DEPTH/2-WALL-0.01, DEPTH/2+1, -HEIGHT/2-1, HEIGHT/2+1))

# USB-C cutout on the FRONT END (-Y) wall - vertical rounded slot, through
usb = (cq.Workplane("XY").slot2D(USB_W, USB_H, 90).extrude((WALL+8)/2, both=True)
       .rotate((0,0,0),(1,0,0),90)
       .translate((USB_X, -DEPTH/2 + WALL/2, USB_Z)))
box = box.cut(usb)

# BUTTON hole through the TOP (+Z) wall
btn = (cq.Workplane("XY").cylinder(WALL+4, BTN_D/2)
       .translate((BTN_X, BTN_Y, HEIGHT/2 - WALL/2)))
box = box.cut(btn)

# SLIDE PANEL (plain, prints flat) + back pull tab
panel_len = (DEPTH - WALL - CLR) + TAB
panel_h   = (HEIGHT - 2*WALL) + 2*(GROOVE_DEP - CLR)
plate = cq.Workplane("XY").box(panel_len, panel_h, PLATE_T)
plate_disp = plate.translate((-WIDTH/2 - panel_h/2 - 25, 0, 0))

try:
    from ocp_vscode import show_object
except Exception:
    pass
try:
    show_object(box,        name="box")
    show_object(plate_disp, name="panel")
except NameError:
    print("Open in OCP CAD Viewer to preview. 3MF files exported below.")

try:
    out = os.path.dirname(os.path.abspath(__file__))
    cq.exporters.export(box,   os.path.join(out, "button_box.3mf"))
    cq.exporters.export(plate, os.path.join(out, "button_panel.3mf"))
    print("Exported button_box.3mf + button_panel.3mf to", out)
except Exception:
    traceback.print_exc()
