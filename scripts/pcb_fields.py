"""Copy LCSC / Description / Panel / FT Rotation Offset from the schematic netlist into the board's footprints (by reference)."""
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from sx import parse, dump, find, find1, Sym
NET, PCB = sys.argv[1:3]
SOLID = {('R20', '2'), ('R4', '2'), ('J1', '4')}   # GND pads that only get one thermal spoke, or sit on a small enclosed B.Cu island: solid
t = parse(open(NET).read())
want = {}
libid = {}
for c in find(find1(t, 'components'), 'comp'):
    ref = find1(c, 'ref')[1]; d = {}
    for f in find(find1(c, 'fields') or [], 'field'):
        nm = find1(f, 'name')[1]
        if nm in ('LCSC', 'Panel', 'FT Rotation Offset') and len(f) > 2 and isinstance(f[2], str): d[nm] = f[2]
    ds = find1(c, 'description')
    if ds and len(ds) > 1: d['Description'] = ds[1]
    want[ref] = d
    libid[ref] = find1(c, 'footprint')[1]
b = parse(open(PCB).read())
n = 0
for fp in find(b, 'footprint'):
    props = find(fp, 'property'); ref = next(p[2] for p in props if p[1] == 'Reference')
    if ref in libid: fp[1] = libid[ref]
    for pad in find(fp, 'pad'):
        if (ref, pad[1]) in SOLID and not find1(pad, 'zone_connect'): pad.append([Sym('zone_connect'), 2])
    for k, v in want.get(ref, {}).items():
        ex = [p for p in props if p[1] == k]
        if ex: ex[0][2] = v
        else:
            at = find1(fp, 'at')
            fp.insert(fp.index(props[-1]) + 1, [Sym('property'), k, v, [Sym('at'), 0, 0, 0], [Sym('layer'), 'F.Fab'], [Sym('hide'), Sym('yes')],
                                                [Sym('effects'), [Sym('font'), [Sym('size'), 1, 1], [Sym('thickness'), 0.15]]]])
            props = find(fp, 'property')
        n += 1
open(PCB, 'w').write(dump(b) + '\n')
print('fields set:', n)
