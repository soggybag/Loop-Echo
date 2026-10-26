"""Enclosure drilling files for Loop Echo (1590BB landscape), read from LoopEcho.kicad_pcb.
KiCad python:  make_enclosure.py <LoopEcho.kicad_pcb> <out dir>
Writes LoopEcho_1590BB_drill.csv, LoopEcho_1590BB_drill_template.svg (face + unfolded jack wall, 1:1),
LoopEcho_1590BB_mill_marks.svg (face only, Othermill marks).
Outside view of the face: origin = face centre = board (150, 100); X = 150 - x, Y = 100 - y (controls are on the back)."""
import sys, pcbnew
PCB, OUT = sys.argv[1:3]
T = pcbnew.ToMM
b = pcbnew.LoadBoard(PCB)
F = {f.GetReference(): f for f in b.GetFootprints()}
X = lambda x: round(150 - x, 2); Y = lambda y: round(100 - y, 2)

# depth of a side-wall hole centre below the OUTSIDE of the face: face ~3 + pot gap 9.91 (measured on GlitchStorm v3) + board 1.6
FACE, GAP, BOARD = 3.0, 9.91, 1.6
face, wall = [], []
for f in sorted(F.values(), key=lambda f: f.GetReference()):
    ref = f.GetReference()
    if ref.startswith('RV'):
        tabs = [p.GetPosition() for p in f.Pads() if p.GetNumber() == '']
        x = sum(T(p.x) for p in tabs) / 2; y = sum(T(p.y) for p in tabs) / 2
        face.append((f.GetFieldText('Panel'), X(x), Y(y), 7.5))
for ref, name in (('D7', 'LOOP LED'), ('D6', 'BYPASS LED')):
    p = [q.GetPosition() for q in F[ref].Pads()]
    face.append((name, X(sum(T(q.x) for q in p) / 2), Y(sum(T(q.y) for q in p) / 2), 3.2))
# footswitches: the r = 6 circles on Dwgs.User
fsw = sorted([d for d in b.GetDrawings() if d.GetLayer() == pcbnew.Dwgs_User and d.GetClass() == 'PCB_SHAPE'
              and d.GetShape() == pcbnew.SHAPE_T_CIRCLE and abs(T(d.GetRadius()) - 6.0) < 0.01], key=lambda d: -T(d.GetCenter().x))
for d, name in zip(fsw, ('LOOP footswitch', 'BYPASS footswitch')):
    face.append((name, X(T(d.GetCenter().x)), Y(T(d.GetCenter().y)), 12.2))
for ref, name, h, dia in (('J3', 'OUT', 8.0, 11.5), ('J5', 'RETURN', 8.0, 11.5), ('J6', 'DC 9V', 6.5, 8.1), ('J4', 'SEND', 8.0, 11.5), ('J2', 'IN', 8.0, 11.5)):
    wall.append((name, X(T(F[ref].GetPosition().x)), round(FACE + GAP + BOARD + h, 1), dia))
face.sort(key=lambda r: (-r[2], r[1]))

with open(f'{OUT}/LoopEcho_1590BB_drill.csv', 'w') as fh:
    fh.write('Side,Label,X landscape (mm),Y landscape (mm),X Tayda portrait (mm),Y Tayda portrait (mm),"Diameter (mm, raw aluminium)"\n')
    for n, x, y, d in face: fh.write(f'A,{n},{x:.2f},{y:.2f},{y:.2f},{-x:.2f},{d}\n')
    fh.write('\n"Jack wall (top long wall): ESTIMATED depths, test-fit one jack first (see README). Along = X on the face; Depth = from the face\'s outside surface"\n')
    fh.write('Wall,Label,Along (mm),Depth (mm),Diameter (mm)\n')
    for n, x, dp, d in wall: fh.write(f'jack wall,{n},{x:.2f},{dp},{d}\n')

# ---------------------------------------------------------------- 1:1 template: face (outside view) + jack wall unfolded above it
W, H, R = 119.5, 94.0, 5.0
vb = (-71.75, -100.0, 143.5, 180.0)
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{vb[2]}mm" height="{vb[3]}mm" viewBox="{vb[0]} {vb[1]} {vb[2]} {vb[3]}" font-family="Helvetica">',
     f'<rect x="{vb[0]}" y="{vb[1]}" width="{vb[2]}" height="{vb[3]}" fill="white"/>',
     f'<rect x="{-W / 2}" y="{-H / 2}" width="{W}" height="{H}" rx="{R}" fill="none" stroke="black" stroke-width="0.3"/>',
     f'<text x="{-W / 2}" y="{vb[1] + 6}" font-size="3">Loop Echo — 1590BB face (side A), outside view, landscape, 1:1. Origin = centre.</text>',
     '<line x1="-3" y1="0" x2="3" y2="0" stroke="#999" stroke-width="0.15"/><line x1="0" y1="-3" x2="0" y2="3" stroke="#999" stroke-width="0.15"/>']
def hole(x, y, d, label, below=True):
    sy = -y
    s.append(f'<circle cx="{x}" cy="{sy}" r="{d / 2}" fill="none" stroke="black" stroke-width="0.25"/>')
    s.append(f'<line x1="{x - 1}" y1="{sy}" x2="{x + 1}" y2="{sy}" stroke="red" stroke-width="0.15"/><line x1="{x}" y1="{sy - 1}" x2="{x}" y2="{sy + 1}" stroke="red" stroke-width="0.15"/>')
    ty = sy + d / 2 + 2.6 if below else sy - d / 2 - 1.2
    s.append(f'<text x="{x}" y="{round(ty, 2)}" font-size="2" text-anchor="middle">{label} Ø{d:g}</text>')
for n, x, y, d in face: hole(x, y, d, n)
# jack wall, unfolded upward: its edge with the face is the face's top edge (Y = +47); depth runs upward
DEPTH = 34.0
s.append(f'<rect x="{-W / 2}" y="{-H / 2 - DEPTH}" width="{W}" height="{DEPTH}" fill="none" stroke="black" stroke-width="0.2" stroke-dasharray="1.5 1"/>')
s.append(f'<text x="{-W / 2}" y="{-H / 2 - DEPTH - 2}" font-size="2.5">Jack wall (unfolded; face edge at the bottom): ESTIMATED depths, test-fit one jack first</text>')
for n, x, dp, d in wall: hole(x, H / 2 + dp, d, n)
s.append(f'<rect x="{-W / 2}" y="{H / 2 + 8}" width="50" height="10" fill="none" stroke="black" stroke-width="0.2"/>')
s.append(f'<text x="{-W / 2 + 1}" y="{H / 2 + 14.2}" font-size="2.5">Check: this box = 50 × 10 mm when printed</text>')
s.append('</svg>')
open(f'{OUT}/LoopEcho_1590BB_drill_template.svg', 'w').write('\n'.join(s) + '\n')

# ---------------------------------------------------------------- mill marks: page = the face, outside view, origin top-left
m = ['<?xml version="1.0" encoding="UTF-8"?>',
     f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">']
for n, x, y, d in face:
    cx, cy = round(W / 2 + x, 3), round(H / 2 - y, 3); ident = n.replace(' ', '_')
    m.append(f'<circle id="{ident}" cx="{cx:.3f}" cy="{cy:.3f}" r="{d / 2:.3f}" fill="none" stroke="#000" stroke-width="0.1"/>')
    m.append(f'<circle id="{ident}_centre" cx="{cx:.3f}" cy="{cy:.3f}" r="0.5" fill="none" stroke="#000" stroke-width="0.1"/>')
m.append('</svg>')
open(f'{OUT}/LoopEcho_1590BB_mill_marks.svg', 'w').write('\n'.join(m) + '\n')
for r in face: print('face', r)
for r in wall: print('wall', r)
