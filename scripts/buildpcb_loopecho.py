"""Build LoopEcho.kicad_pcb from the schematic netlist: Hammond/Tayda 1590BB, LANDSCAPE, all five jacks board-mounted on the
top (long) wall. Box centre = board (150, 100). Pots / LED on the back (B side, through the face); SMD + jacks on the front
(F side, facing into the box). Outside view of the face: X = 150 - x, Y = 100 - y.
Run with KiCad's python:  buildpcb_loopecho.py <netlist> <template.kicad_pcb (any board: setup copied)> <out.kicad_pcb>
Don't re-run after editing the board in KiCad: it overwrites it."""
import sys, math, pcbnew
import importlib.util
_sp = importlib.util.spec_from_file_location('sx_local', __file__.rsplit('/', 1)[0] + '/sx.py'); _sx = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_sx)
parse, dump, find, find1 = _sx.parse, _sx.dump, _sx.find, _sx.find1
NET, TEMPLATE, OUT = sys.argv[1:4]
PRJ = OUT.rsplit('/', 1)[0]
FPDIR = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'
mm = pcbnew.FromMM; tomm = pcbnew.ToMM
def V(x, y): return pcbnew.VECTOR2I(mm(x), mm(y))

# ---------------------------------------------------------------- geometry (mm, board coordinates)
BOX_IN = (94.67, 57.4, 205.33, 142.6)          # inside of the walls at the face (1590BB, from the GlitchStorm v3 drawing)
BOSS = [(95.25, 57.93), (204.75, 57.93), (95.25, 142.07), (204.75, 142.07)]   # lid-screw bosses, r ~5.2
EDGE = (100.0, 58.5, 200.0, 142.0)             # board outline (exactly 100 mm wide) before the corner cut-outs and the footswitch notch
BOSS_CUT = 6.0                                 # board corner arcs: r 6 around each boss
JACK_Y = 57.6                                  # jack front faces (touching the inside of the top wall)
JACKS = {'J3': 189.3, 'J5': 166.9, 'J6': 150.0, 'J4': 133.1, 'J2': 110.7}   # outside view L->R: OUT RETURN DC SEND IN
FSW = (150.0, 126.0)                           # footswitch centre (outside: X 0, Y -26)
NOTCH = (140.5, 116.5, 159.5, 142.0)           # board cut-out for the 3PDT body
ROW1, ROW2 = 85.0, 103.0                        # pot rows (outside Y +15 / -3)
POTS = {'TIME': (182, ROW1), 'REPEAT': (150, ROW1), 'MIX': (118, ROW1),
        'RATE': (182, ROW2), 'DEPTH': (150, ROW2), 'TONE': (118, ROW2)}
LED = (150.0, 114.2)                           # status LED (outside: X 0, Y -14.2), courtyard clear of DEPTH
HEADER = (137.75, 132.04)                      # J1 pin 1; pins run up (-y) beside the notch (user's placement 2026-10-25),
                                               # so the SwitchPCB, turned to match, takes a straight ribbon

# ---------------------------------------------------------------- netlist
t = parse(open(NET).read())
comps = {}
for c in find(find1(t, 'components'), 'comp'):
    ref = find1(c, 'ref')[1]
    fields = {}
    for f in find(find1(c, 'fields') or [], 'field'):
        fields[find1(f, 'name')[1]] = f[2] if len(f) > 2 and isinstance(f[2], str) else ''
    comps[ref] = dict(value=find1(c, 'value')[1], fp=find1(c, 'footprint')[1], tstamp=find1(c, 'tstamps')[1], fields=fields)
nets = {}
for n in find(find1(t, 'nets'), 'net'):
    name = find1(n, 'name')[1]
    for nd in find(n, 'node'): nets[(find1(nd, 'ref')[1], find1(nd, 'pin')[1])] = name

# ---------------------------------------------------------------- empty board with the template's setup
tp = parse(open(TEMPLATE).read())
keep = [x for x in tp if not isinstance(x, list) or (hasattr(x[0], 'lower') and str(x[0]) in ('version', 'generator', 'generator_version', 'general', 'paper', 'layers', 'setup'))]
EMPTY = OUT[:-10] + '_empty.kicad_pcb'   # LoadBoard picks the reader by extension
open(EMPTY, 'w').write(dump(keep) + '\n')
b = pcbnew.LoadBoard(EMPTY)
netinfo = {}
def net_of(name):
    if name not in netinfo:
        ni = pcbnew.NETINFO_ITEM(b, name); b.Add(ni); netinfo[name] = ni
    return netinfo[name]
def load(libid):
    lib, name = libid.split(':')
    path = f'{PRJ}/{lib}.pretty' if lib == 'SuperFreq' else f'{FPDIR}/{lib}.pretty'
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None: print('load failed', path, name)
    return fp
def setup(fp, ref):
    c = comps[ref]
    fp.SetReference(ref); fp.SetValue(c['value'])
    fp.SetPath(pcbnew.KIID_PATH('/' + c['tstamp']))
    if ref.startswith(('RV', 'J')) or ref == 'D6':
        fp.SetExcludedFromBOM(True); fp.SetExcludedFromPosFiles(True)
    for pad in fp.Pads():
        n = nets.get((ref, pad.GetNumber()))
        if n: pad.SetNet(net_of(n))
    return fp
def pads(fp): return {p.GetNumber(): (tomm(p.GetPosition().x), tomm(p.GetPosition().y)) for p in fp.Pads()}
placed = []

# ---------------------------------------------------------------- jacks (F side; footprint origin = barrel axis at the front face)
for ref, x in JACKS.items():
    fp = load(comps[ref]['fp']); b.Add(fp); setup(fp, ref)
    fp.SetOrientationDegrees(0); fp.SetPosition(V(x, JACK_Y)); placed.append(fp)
    fp.Reference().SetVisible(False)   # it would sit past the board edge; the silk names below say which jack

# ---------------------------------------------------------------- pots (B side): shaft at the target, pins toward the footswitch,
# and pin 1 on the left seen from outside (board: pin 1 at larger x)
by_panel = {comps[r]['fields'].get('Panel'): r for r in comps if r.startswith('RV')}
for name, (x, y) in POTS.items():
    ref = by_panel[name]
    fp = load(comps[ref]['fp']); b.Add(fp); setup(fp, ref)
    fp.SetPosition(V(x, y)); fp.Flip(V(x, y), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
    ok = False
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        p = pads(fp)
        tabs = [(tomm(q.GetPosition().x), tomm(q.GetPosition().y)) for q in fp.Pads() if q.GetNumber() == '']   # the two mounting tabs
        sx_, sy_ = (tabs[0][0] + tabs[1][0]) / 2, (tabs[0][1] + tabs[1][1]) / 2
        if p['1'][1] > sy_ + 5 and p['3'][1] > sy_ + 5 and p['1'][0] > p['3'][0]:
            fp.SetPosition(V(tomm(fp.GetPosition().x) + x - sx_, tomm(fp.GetPosition().y) + y - sy_)); ok = True; break
    if not ok: print('pot orientation not found', ref)
    placed.append(fp)

# LED (B side, legs long enough to reach the face) and the footswitch header (F side)
fp = load(comps['D6']['fp']); b.Add(fp); setup(fp, 'D6')
fp.SetPosition(V(*LED)); fp.Flip(V(*LED), pcbnew.FLIP_DIRECTION_LEFT_RIGHT); fp.SetOrientationDegrees(0)
p = pads(fp); cx = (p['1'][0] + p['2'][0]) / 2; cy = (p['1'][1] + p['2'][1]) / 2
fp.SetPosition(V(tomm(fp.GetPosition().x) + LED[0] - cx, tomm(fp.GetPosition().y) + LED[1] - cy)); placed.append(fp)
fp = load(comps['J1']['fp']); b.Add(fp); setup(fp, 'J1')
fp.SetOrientationDegrees(180); fp.SetPosition(V(*HEADER))
placed.append(fp)

# ---------------------------------------------------------------- outline
def seg(a, c, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*c)); s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)
def arc(a, mid, c, layer=pcbnew.Edge_Cuts, w=0.1):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_ARC); s.SetArcGeometry(V(*a), V(*mid), V(*c)); s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)
def circ(c, r, layer=pcbnew.Dwgs_User, w=0.1):
    s = pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_CIRCLE); s.SetCenter(V(*c)); s.SetEnd(V(c[0] + r, c[1])); s.SetLayer(layer); s.SetWidth(mm(w)); b.Add(s)
x0, y0, x1, y1 = EDGE
def corner(bx, by, ex_on_y, ey_on_x):
    """points where the r=BOSS_CUT circle around boss (bx, by) meets the horizontal edge y=ex_on_y and the vertical edge x=ey_on_x"""
    dy = abs(ex_on_y - by); px = bx + math.sqrt(BOSS_CUT ** 2 - dy ** 2) * (1 if bx < 150 else -1)
    dx = abs(ey_on_x - bx); py = by + (math.sqrt(BOSS_CUT ** 2 - dx ** 2) * (1 if by < 100 else -1))
    return (px, ex_on_y), (ey_on_x, py)
TL = corner(*BOSS[0], y0, x0); TR = corner(*BOSS[1], y0, x1); BL = corner(*BOSS[2], y1, x0); BR = corner(*BOSS[3], y1, x1)
def arcmid(bx, by, a, c):
    ang = (math.atan2(a[1] - by, a[0] - bx) + math.atan2(c[1] - by, c[0] - bx)) / 2
    return (bx + BOSS_CUT * math.cos(ang), by + BOSS_CUT * math.sin(ang))
OUTLINE = []
seg(TL[0], TR[0]); arc(TR[0], arcmid(*BOSS[1], TR[0], TR[1]), TR[1])
seg(TR[1], BR[1]); arc(BR[1], arcmid(*BOSS[3], BR[1], BR[0]), BR[0])
nx0, ny0, nx1, ny1 = NOTCH
seg(BR[0], (nx1, y1)); seg((nx1, y1), (nx1, ny0)); seg((nx1, ny0), (nx0, ny0)); seg((nx0, ny0), (nx0, y1)); seg((nx0, y1), BL[0])
arc(BL[0], arcmid(*BOSS[2], BL[0], BL[1]), BL[1]); seg(BL[1], TL[1]); arc(TL[1], arcmid(*BOSS[0], TL[1], TL[0]), TL[0])
POLY = [TL[0], TR[0], arcmid(*BOSS[1], TR[0], TR[1]), TR[1], BR[1], arcmid(*BOSS[3], BR[1], BR[0]), BR[0], (nx1, y1), (nx1, ny0),
        (nx0, ny0), (nx0, y1), BL[0], arcmid(*BOSS[2], BL[0], BL[1]), BL[1], TL[1], arcmid(*BOSS[0], TL[1], TL[0])]

# ---------------------------------------------------------------- enclosure / panel drawing (Dwgs.User)
D = pcbnew.Dwgs_User
for a, c in (((90.25, 53), (209.75, 53)), ((209.75, 53), (209.75, 147)), ((209.75, 147), (90.25, 147)), ((90.25, 147), (90.25, 53))):
    seg(a, c, D)                                    # outside of the box, 119.5 x 94
for a, c in (((BOX_IN[0], BOX_IN[1]), (BOX_IN[2], BOX_IN[1])), ((BOX_IN[2], BOX_IN[1]), (BOX_IN[2], BOX_IN[3])),
             ((BOX_IN[2], BOX_IN[3]), (BOX_IN[0], BOX_IN[3])), ((BOX_IN[0], BOX_IN[3]), (BOX_IN[0], BOX_IN[1]))):
    seg(a, c, D)                                    # inside of the walls at the face
for bx, by in BOSS: circ((bx, by), 5.17); circ((bx, by), 1.4)
circ(FSW, 6.0); seg((FSW[0] - 8.5, FSW[1] - 8.5), (FSW[0] + 8.5, FSW[1] - 8.5), D); seg((FSW[0] + 8.5, FSW[1] - 8.5), (FSW[0] + 8.5, FSW[1] + 8.5), D)
seg((FSW[0] + 8.5, FSW[1] + 8.5), (FSW[0] - 8.5, FSW[1] + 8.5), D); seg((FSW[0] - 8.5, FSW[1] + 8.5), (FSW[0] - 8.5, FSW[1] - 8.5), D)
for x, y in POTS.values(): circ((x, y), 7.0)        # ~14 mm knobs
def txt(s, x, y, layer, size=1.2, mirror=False):
    t_ = pcbnew.PCB_TEXT(b); t_.SetText(s); t_.SetPosition(V(x, y)); t_.SetLayer(layer)
    t_.SetTextSize(V(size, size)); t_.SetTextThickness(mm(size * 0.15)); t_.SetMirrored(mirror); b.Add(t_)
txt('1590BB landscape, viewed from inside (F). Top wall jacks, outside L->R: OUT  RETURN  DC  SEND  IN', 150, 50.5, D, 1.0)
txt('Loop Echo', 150, 135.5, pcbnew.F_SilkS, 1.6)
txt('Super-Freq.com  V1.0', 150, 138.5, pcbnew.F_SilkS, 1.0)
for ref, x in JACKS.items():
    txt({'J2': 'IN', 'J3': 'OUT', 'J4': 'SEND', 'J5': 'RETURN', 'J6': 'DC'}[ref], x, 80.2 if ref != 'J6' else 74.2, pcbnew.F_SilkS, 1.0)

# ---------------------------------------------------------------- SMD placement (F side), clustered around the ICs by connectivity
INSET = 1.0
def inside(px, py):
    n = len(POLY); c = False
    for i in range(n):
        (ax, ay), (bx_, by_) = POLY[i], POLY[(i + 1) % n]
        if (ay > py) != (by_ > py) and px < (bx_ - ax) * (py - ay) / (by_ - ay) + ax: c = not c
    return c
def box(fp, infl=0.25):
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
    return (tomm(bb.GetLeft()) - infl, tomm(bb.GetTop()) - infl, tomm(bb.GetRight()) + infl, tomm(bb.GetBottom()) + infl)
obst = []
for fp in placed:
    for pad in fp.Pads():
        bb = pad.GetBoundingBox(); obst.append((tomm(bb.GetLeft()) - 0.6, tomm(bb.GetTop()) - 0.6, tomm(bb.GetRight()) + 0.6, tomm(bb.GetBottom()) + 0.6))
    if not fp.IsFlipped(): obst.append(box(fp, 0.3))
obst.append((NOTCH[0] - 1, NOTCH[1] - 1, NOTCH[2] + 1, NOTCH[3] + 1))
obst.append((140, 128, 160, 141))   # board ID text
def hit(a, c): return not (a[2] <= c[0] or c[2] <= a[0] or a[3] <= c[1] or c[3] <= a[1])
def free(bx):
    for px, py in ((bx[0] - INSET, bx[1] - INSET), (bx[2] + INSET, bx[1] - INSET), (bx[0] - INSET, bx[3] + INSET), (bx[2] + INSET, bx[3] + INSET)):
        if not inside(px, py): return False
    for bx_, by_ in BOSS:
        if math.hypot(min(max(bx_, bx[0]), bx[2]) - bx_, min(max(by_, bx[1]), bx[3]) - by_) < BOSS_CUT + INSET: return False
    return not any(hit(bx, o) for o in obst)
def put(ref, ax, ay):
    fp = load(comps[ref]['fp']); b.Add(fp); setup(fp, ref)
    for r in range(0, 160):
        rad = r * 0.5; k_n = max(1, int(2 * math.pi * rad / 0.5))
        for k in range(k_n):
            ang = 2 * math.pi * k / k_n
            x, y = round((ax + rad * math.cos(ang)) * 4) / 4, round((ay + rad * math.sin(ang)) * 4) / 4
            for rot in (0, 90):
                fp.SetOrientationDegrees(rot); fp.SetPosition(V(x, y))
                if free(box(fp)):
                    obst.append(box(fp, 0.3)); return fp
    print('NO SPACE for', ref); return fp
IC_AT = {'U5': (152, 82), 'U3': (137, 93), 'U2': (113, 118), 'U1': (166, 117), 'U4': (190, 120)}
POWER = {'GND', '+9V', '+5V', '/VB'}
pins_of = {}
for (r, pn), n in nets.items(): pins_of.setdefault(r, set()).add(n)
for ref, at in IC_AT.items(): put(ref, *at)
smd = [r for r in comps if r[0] in 'RCDQ' and not r.startswith('RV') and r != 'D6']
home = {}
frontier = {u: pins_of[u] - POWER for u in IC_AT}
left = set(smd)
for hop in range(4):
    for r in sorted(left):
        mine = pins_of.get(r, set()) - POWER
        for u, ns in frontier.items():
            if mine & ns: home[r] = u; break
    left -= set(home)
    for r in home: frontier[home[r]] = frontier[home[r]] | (pins_of.get(r, set()) - POWER)
for r in left: home[r] = 'U5'      # power-only parts (bulk caps, VB divider): near the regulator
for r in sorted(smd, key=lambda r: (home[r], r)):
    ax, ay = IC_AT[home[r]]
    if r == 'D1': ax, ay = JACKS['J6'] + 7, 82     # SS14 next to the DC jack
    put(r, ax, ay)
missing = set(comps) - {f.GetReference() for f in b.GetFootprints()}
print('footprints', len(b.GetFootprints()), 'missing', sorted(missing))

# ---------------------------------------------------------------- GND zones, both sides, over the whole outline
for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
    z = pcbnew.ZONE(b); z.SetLayer(layer); z.SetNet(net_of('GND'))
    ol = z.Outline(); ol.NewOutline()
    for x, y in ((90, 52), (210, 52), (210, 148), (90, 148)): ol.Append(mm(x), mm(y))
    z.SetLocalClearance(mm(0.3)); z.SetMinThickness(mm(0.25)); z.SetThermalReliefGap(mm(0.3)); z.SetThermalReliefSpokeWidth(mm(0.4))
    b.Add(z)
# keep tracks and vias 0.6 mm off the footswitch notch (Freerouting's edge margin only covers the outer edge)
ka = pcbnew.ZONE(b); ka.SetIsRuleArea(True); ka.SetDoNotAllowTracks(True); ka.SetDoNotAllowVias(True); ka.SetDoNotAllowPads(False)
ka.SetDoNotAllowZoneFills(False); ka.SetDoNotAllowFootprints(False); ka.SetLayerSet(pcbnew.LSET.AllCuMask())
ol = ka.Outline(); ol.NewOutline()
for x, y in ((NOTCH[0] - 0.6, NOTCH[1] - 0.6), (NOTCH[2] + 0.6, NOTCH[1] - 0.6), (NOTCH[2] + 0.6, NOTCH[3] + 1), (NOTCH[0] - 0.6, NOTCH[3] + 1)):
    ol.Append(mm(x), mm(y))
b.Add(ka)
b.Save(OUT)
import os; os.remove(EMPTY)
print('saved', OUT)
