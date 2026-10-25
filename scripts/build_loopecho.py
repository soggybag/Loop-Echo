"""Loop Echo v1.0 (SMD, JLC; 2026-10-25): single PT2399 delay with an effects loop in the FEEDBACK path, TONE on every
repeat, and delay-time modulation. PT2399 network from the user's Small Time. Ordered as a prototype (not breadboarded).
v0.1 (breadboard, TRS insert) is kept as build_loopecho_v0.1.py.
  - U2A input buffer (DRY); U2B inverting mixer (DRY + MIX)
  - U1 PT2399-SN on its own 5 V (U5 AMS1117-5.0); TIME = B50k + 2k7 from VCO (pin 6) to ground (~50-600 ms)
  - wet (W) -> U3A SEND buffer -> SEND pad.  RETURN jack (switched): no plug -> its normal contact = SEND (internal path).
    RET -> 1u -> TONE (B50k + 2k2 into 10n: ~7 kHz .. 300 Hz, every repeat) -> U3B -> 1k + 1N4148W limiter -> REPEAT -> PT2399
  - LFO U4 (LM358: integrator + Schmitt, RATE 47k + B1M, 1u) -> DEPTH -> 33k + 10u -> TMIN (the TIME / 2k7 node):
    even modulation depth across TIME (Dragonfish)
  - Power: SS14, 2 x 22u bulk, VB 10k/10k + 47u; status LED to the footswitch header (1 IN, 2 LED_K, 3 GND, 4 OUT)
usage: build_loopecho.py <out.kicad_sch>"""
from sch import *
import sys
OUT = sys.argv[1]
g = lambda n: round(n * 2.54, 3)
s = Sheet('LoopEcho', 'A1')
W = lambda *p: s.wire(*p)
P = s.P
FR = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
FC = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
FC12 = 'Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
FPOT = 'Potentiometer_THT:Potentiometer_Alpha_RD901F-40-00D_Single_Vertical'
FPAD = 'Connector_Wire:SolderWire-0.5sqmm_1x01_D0.9mm_OD2.1mm'
FSO8 = 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm'
LR = {'100': 'C17408', '1k': 'C17513', '2k2': 'C17520', '2k7': 'C17530', '10k': 'C17414', '15k': 'C17475', '22k': 'C17560',
      '33k': 'C17633', '47k': 'C17713', '100k': 'C149504', '1M': 'C17514', '4k7': 'C17673'}
LC = {'1n': ('C46653', FC), '2n2': ('C28260', FC), '10n': ('C1710', FC), '47n': ('C53134', FC), '100n': ('C49678', FC),
      '1u': ('C28323', FC), '4u7': ('C1779', FC), '10u': ('C15850', FC), '22u': ('C45783', FC), '47u': ('C96123', FC12)}
_n = {}
def nx(p):
    _n[p] = _n.get(p, 0) + 1
    return f'{p}{_n[p]}'
def GND(p): s.power('GND', p)
def V9(p): s.power('+9V', p)
def lab(n, p, side='r'): s.label(n, p, side)
def Rh(v, cx, y, d=''):
    r = nx('R'); s.part(r, 'Device', 'R', v, cx, y, 90, fp=FR, lcsc=LR[v], desc=d, text='t'); return r
def Rv(v, x, cy, side='r', d=''):
    r = nx('R'); s.part(r, 'Device', 'R', v, x, cy, 0, fp=FR, lcsc=LR[v], desc=d, text=side); return r
def Ch(v, cx, y, d=''):
    r = nx('C'); s.part(r, 'Device', 'C', v, cx, y, 90, fp=LC[v][1], lcsc=LC[v][0], desc=d, text='t'); return r
def Cv(v, x, cy, side='r', d=''):
    r = nx('C'); s.part(r, 'Device', 'C', v, x, cy, 0, fp=LC[v][1], lcsc=LC[v][0], desc=d, text=side); return r
def gnd_down(p, n=1): W(p, (p[0], p[1] + g(n))); GND((p[0], p[1] + g(n)))
def lab_at(p, name, dx=2, side='r'):
    q = (p[0] + g(dx) * (1 if side == 'r' else -1), p[1]); W(p, q); lab(name, q, side)
def lab_v(p, name, dy, side='r'):
    q = (p[0], p[1] + g(dy)); W(p, q); lab(name, q, side)
PINS = {1: ('3', '2', '1'), 2: ('5', '6', '7')}
OPS = {'TL072': ('C6961', 'Dual JFET op-amp'), 'LM358': ('C7950', 'Dual op-amp (LFO: inputs to ground, low supply ripple)')}
def OP(ref, unit, x, ytop, sym='TL072'):
    s.part(ref, 'Amplifier_Operational', sym, sym, x, ytop + 2.54, 0, unit=unit, fp=FSO8, lcsc=OPS[sym][0], desc=OPS[sym][1], text='ic',
           extra={'FT Rotation Offset': '270'})
    pl, mi, ou = PINS[unit]
    return P(ref, pl), P(ref, mi), P(ref, ou)
def follower(ref, unit, x, ytop, sym='TL072'):
    pl, mi, ou = OP(ref, unit, x, ytop, sym)
    W(mi, (mi[0] - g(1), mi[1]), (mi[0] - g(1), mi[1] + g(3)), (ou[0] + g(1), mi[1] + g(3)), (ou[0] + g(1), ou[1]))
    W(ou, (ou[0] + g(1), ou[1]))
    return pl, (ou[0] + g(1), ou[1])
def pot(v, name, x, y, mirror='x', text=None):
    r = nx('RV')
    s.part(r, 'Device', 'R_Potentiometer', v, x, y, 0, mirror=mirror, fp=FPOT, desc=name, extra={'Panel': name}, bom=False,
           text=text or ((x - g(4), y + g(2)), (x - g(4), y + g(3.5)), 'right'))
    return r
def rheo(r):
    w = P(r, '2'); p3 = P(r, '3')
    W(w, (w[0] + g(1), w[1]), (w[0] + g(1), p3[1] + g(1)), (p3[0], p3[1] + g(1))); W(p3, (p3[0], p3[1] + g(1)))
    return (p3[0], p3[1] + g(1))
def D(x, y, rot, d, text='t'):
    r = nx('D'); s.part(r, 'Diode', '1N4148W', '1N4148W', x, y, rot, fp='Diode_SMD:D_SOD-123', lcsc='C81598', desc=d, text=text); return r
def PAD(name, x, y, right=True, d=''):
    r = nx('J')
    s.part(r, 'Connector_Generic', 'Conn_01x01', name, x, y, 0 if right else 180, fp=FPAD, desc=d or f'Wire pad: {name}', bom=False,
           text=((x + 2.54, y - 1.27), (x + 2.54, y + 1.27), 'left') if right else ((x - 2.54, y - 1.27), (x - 2.54, y + 1.27), 'right'))
    return P(r, '1')

# ================================================================ POWER, VB, LED, HEADER, PADS
s.box('POWER (SS14, AMS1117-5.0 for the PT2399), VB, STATUS LED, FOOTSWITCH HEADER, JACK PADS', g(4), g(6), g(60), g(96))
p = PAD('9V', g(8), g(12), d='Wire pad: +9 V from the DC jack'); W(p, (g(10), g(12)))
s.part('D1', 'Diode', 'SS14', 'SS14', g(13), g(12), 180, fp='Diode_SMD:D_SMA', lcsc='C2480', desc='Reverse-polarity protection', text='t'); _n['D'] = 1
W((g(10), g(12)), P('D1', '2')); W(P('D1', '1'), (g(18), g(12)))
V9((g(18), g(12))); s.power('PWR_FLAG', (g(18), g(12)))
W((g(18), g(12)), (g(42), g(12)))
for x, v, d in ((22, '22u', 'Bulk'), (26, '22u', 'Bulk'), (30, '100n', 'U2 decoupling'), (34, '100n', 'U3 decoupling'), (38, '100n', 'U4 decoupling'), (42, '10u', 'Regulator input')):
    c = Cv(v, g(x), g(15.5), d=d); W((g(x), g(12)), P(c, '1')); GND(P(c, '2'))
p = PAD('G', g(8), g(20), d='Wire pad: DC jack ground'); W(p, (g(10), g(20))); GND((g(10), g(20))); s.power('PWR_FLAG', (g(10), g(20)))
s.part('U5', 'Regulator_Linear', 'AMS1117-5.0', 'AMS1117-5.0', g(20), g(32), 0, fp='Package_TO_SOT_SMD:SOT-223-3_TabPin2', lcsc='C6187',
       desc='5 V for the PT2399', text='t')
q = P('U5', '3'); W(q, (q[0] - g(2), q[1])); V9((q[0] - g(2), q[1]))
GND(P('U5', '1'))
q = P('U5', '2'); W(q, (g(40), q[1])); s.power('+5V', (g(40), q[1]))
for x, v, d in ((30, '10u', 'Regulator output'), (34, '100n', 'PT2399 VCC decoupling (at pin 1)')):
    c = Cv(v, g(x), q[1] + g(3.5), d=d); W((g(x), q[1]), P(c, '1')); GND(P(c, '2'))
r1 = Rv('10k', g(9), g(44)); V9(P(r1, '1'))
r2 = Rv('10k', g(9), g(52)); GND(P(r2, '2'))
W(P(r1, '2'), P(r2, '1'))
c = Cv('47u', g(15), g(51.5), d='VB filter')
W((g(9), g(48)), (g(15), g(48)), P(c, '1')); GND(P(c, '2'))
W((g(15), g(48)), (g(19), g(48))); lab('VB', (g(19), g(48))); s.power('PWR_FLAG', (g(19), g(48)))
for ref, x, sym in (('U2', 28, 'TL072'), ('U3', 34, 'TL072'), ('U4', 40, 'LM358')):
    s.part(ref, 'Amplifier_Operational', sym, sym, g(x), g(56), 0, unit=3, fp=FSO8, lcsc=OPS[sym][0], desc=OPS[sym][1], text='ic',
           extra={'FT Rotation Offset': '270'})
    V9(P(ref, '8')); GND(P(ref, '4'))
r = Rv('4k7', g(10), g(68), side='l', d='Status LED current'); V9(P(r, '1'))
s.part('D6', 'Device', 'LED', 'LED', g(10), g(74), 90, fp='LED_THT:LED_D3.0mm', desc='Status LED (panel); cathode to the footswitch via the header', text='r', bom=False)
W(P(r, '2'), P('D6', '2')); W(P('D6', '1'), (g(10), g(78)), (g(13), g(78))); lab('LED_K', (g(13), g(78)))
s.part('J1', 'Connector_Generic', 'Conn_01x04', 'IN/LED/GND/OUT', g(30), g(80), 0, fp='Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical',
       desc='To the footswitch board: 1 IN, 2 LED_K, 3 GND, 4 OUT', text=((g(32), g(76)), (g(32), g(77.2)), 'left'), bom=False)
_n['J'] = 1
for pin, net in (('1', 'IN'), ('2', 'LED_K'), ('4', 'OUT')):
    q = P('J1', pin); W(q, (q[0] - g(3), q[1])); lab(net, (q[0] - g(3), q[1]), 'l')
q = P('J1', '3'); W(q, (q[0] - g(3), q[1])); GND((q[0] - g(3), q[1]))
PD = {'IG': 'Wire pad: input jack sleeve', 'OG': 'Wire pad: output jack sleeve', 'SEND': 'Wire pad: SEND jack tip',
      'SG': 'Wire pad: SEND jack sleeve', 'RET': 'Wire pad: RETURN jack tip',
      'RETN': 'Wire pad: RETURN jack switch (normal) contact: closes the loop internally with no plug', 'RG': 'Wire pad: RETURN jack sleeve'}
for i, (name, net) in enumerate((('IG', None), ('OG', None), ('SEND', 'SEND'), ('SG', None), ('RET', 'RET'), ('RETN', 'SEND'), ('RG', None))):
    yy = g(62) + g(3) * i
    p = PAD(name, g(42), yy, d=PD[name])
    q = (p[0] + g(4), p[1]); W(p, q)
    if net: lab(net, q)
    else: GND(q)

# ================================================================ INPUT + MIXER (U2)
s.box('INPUT BUFFER (U2A) + OUTPUT MIXER (U2B): as Small Time', g(64), g(6), g(134), g(70))
y = g(22)
lab('IN', (g(67), y), 'l'); W((g(67), y), (g(71), y))
r = Rv('1M', g(71), y + g(3.5), side='l', d='Input pull-down'); W((g(71), y), P(r, '1')); GND(P(r, '2'))
W((g(71), y), (g(73), y)); c = Ch('100n', g(74.5), y, d='Input coupling'); W((g(73), y), P(c, '1'))
r = Rh('100', g(80.5), y, d='Input stopper'); W(P(c, '2'), P(r, '1'))
W(P(r, '2'), (g(85), y))
r = Rv('1M', g(85), y + g(3.5), side='r', d='Bias to VB'); W((g(85), y), P(r, '1')); lab_v(P(r, '2'), 'VB', 1, 'l')
pl, o = follower('U2', 1, g(98), y)
W((g(85), y), pl); W(o, (o[0] + g(4), o[1])); lab('DRY', (o[0] + g(4), o[1]))
pl, mi, ou = OP('U2', 2, g(110), g(42))
W(pl, (pl[0] - g(6), pl[1])); lab('VB', (pl[0] - g(6), pl[1]), 'l')
tap = mi[0] - g(1); W(mi, (tap, mi[1]))
r = Rh('10k', tap - g(1) - 3.81, mi[1], d='Dry into the mixer'); W(P(r, '2'), (tap, mi[1])); lab_at(P(r, '1'), 'DRY', 2, 'l')
r = Rh('10k', tap - g(1) - 3.81, mi[1] + g(3), d='Echo into the mixer'); W(P(r, '2'), (tap, mi[1] + g(3)))
c = Ch('10u', P(r, '1')[0] - g(1) - 3.81, mi[1] + g(3), d='MIX coupling'); W(P(c, '2'), P(r, '1')); lab_at(P(c, '1'), 'MIXW', 2, 'l')
fy = mi[1] + g(7); rx = ou[0] + g(1)
W((tap, mi[1]), (tap, fy + g(3)))
r = Rh('10k', (tap + rx) / 2, fy, d='Mixer feedback'); W((tap, fy), P(r, '1')); W(P(r, '2'), (rx, fy))
c = Ch('1n', (tap + rx) / 2, fy + g(3), d='HF roll-off'); W((tap, fy + g(3)), P(c, '1')); W(P(c, '2'), (rx, fy + g(3)))
W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, fy + g(3)))
W((rx, ou[1]), (rx + g(1), ou[1])); r = Rh('100', rx + g(1) + 3.81, ou[1], d='Output stopper')
c = Ch('10u', P(r, '2')[0] + g(1) + 3.81, ou[1], d='Output coupling'); W(P(r, '2'), P(c, '1'))
q = (P(c, '2')[0] + g(3), ou[1]); W(P(c, '2'), q)
r = Rv('100k', q[0], q[1] + g(3.5), side='r', d='Output pull-down'); W(q, P(r, '1')); GND(P(r, '2'))
W(q, (q[0] + g(3), q[1])); lab('OUT', (q[0] + g(3), q[1]))

# ================================================================ PT2399
s.box('DELAY: PT2399 (U1), Small Time network. TIME = B50k + 2k7 (VCO to ground); the LFO enters at TMIN', g(138), g(6), g(264), g(80))
xu, yu = g(164), g(40)
s.part('U1', 'Audio', 'PT2399', 'PT2399', xu, yu, 0, fp='Package_SO:SOIC-16_3.9x9.9mm_P1.27mm', lcsc='C126407',
       desc='PT2399-SN echo processor (SOP-16 narrow)', text=((xu - g(3), yu - g(7)), (xu - g(3), yu - g(5.5)), 'left'))
q = P('U1', '1'); W(q, (q[0] - g(3), q[1])); s.power('+5V', (q[0] - g(3), q[1]))
q = P('U1', '2'); W(q, (q[0] - g(6), q[1])); c = Cv('47u', q[0] - g(6), q[1] + 3.81, side='l', d='REF'); gnd_down(P(c, '2'), 0)
p3_, p4_ = P('U1', '3'), P('U1', '4')
gx_ = p3_[0] - g(4)
W(p3_, (gx_, p3_[1])); W(p4_, (gx_, p4_[1])); W((gx_, p3_[1]), (gx_, p4_[1])); GND((gx_, p4_[1]))
s.noconnect(P('U1', '5'))
lab_at(P('U1', '6'), 'VCO', 3, 'l')
for pin, dx in (('7', 10), ('8', 6)):
    q = P('U1', pin); cc = (q[0] - g(dx), q[1]); W(q, cc)
    c = Cv('100n', cc[0], cc[1] + g(1) + 3.81, side='l', d=f'Compander (pin {pin})'); W(cc, P(c, '1')); GND(P(c, '2'))
for pin, name in (('9', 'OP1O'), ('10', 'OP1I'), ('11', 'OP2I'), ('12', 'OP2O'), ('13', 'LP2I'), ('14', 'LP2O'), ('15', 'LP1O'), ('16', 'LP1I')):
    lab_at(P('U1', pin), name, 3)
for a, b, x in (('OP1I', 'OP1O', 186), ('OP2I', 'OP2O', 200)):
    c = Ch('100n', g(x), g(70), d=f'{a}-{b} (PT2399 integrator)')
    lab_at(P(c, '1'), a, 2, 'l'); lab_at(P(c, '2'), b, 2, 'r')
xa, ya = g(190), g(18)
lab('DIN', (xa, ya), 'l')
r = Rh('10k', xa + g(1) + 3.81, ya, d='LPF1'); W((xa, ya), P(r, '1')); lab_at(P(r, '2'), 'LP1I', 2)
W((xa, ya), (xa, ya + g(4)))
r = Rh('15k', xa + g(1) + 3.81, ya + g(4), d='LPF1'); W((xa, ya + g(4)), P(r, '1')); lab_at(P(r, '2'), 'LP1O', 2)
c = Ch('2n2', xa + g(18), ya + g(8), d='LPF1 (C0G)'); lab_at(P(c, '1'), 'LP1I', 2, 'l'); lab_at(P(c, '2'), 'LP1O', 2, 'r')
W((xa, ya + g(4)), (xa, ya + g(6)))
c = Cv('10n', xa, ya + g(6) + 3.81, side='l', d='LPF1'); W((xa, ya + g(6)), P(c, '1')); GND(P(c, '2'))
for src, yy, d in (('DRY', 14, 'Dry into the delay'), ('RPT', 20, 'Repeats into the delay')):
    lab(src, (g(212), g(yy)), 'l'); W((g(212), g(yy)), (g(214), g(yy)))
    c = Ch('100n', g(215.5), g(yy), d=d); W((g(214), g(yy)), P(c, '1'))
    r = Rh('10k', P(c, '2')[0] + g(1) + 3.81, g(yy), d=d); W(P(c, '2'), P(r, '1'))
    lab_at(P(r, '2'), 'DIN', 2)
xb, yb = g(190), g(46)
lab('OP2O', (xb, yb), 'l')
r = Rh('10k', xb + g(1) + 3.81, yb, d='LPF2'); W((xb, yb), P(r, '1'))
N = (P(r, '2')[0] + g(2), yb); W(P(r, '2'), N)
W(N, (N[0], yb + g(2))); c = Cv('10n', N[0], yb + g(2) + 3.81, side='l', d='LPF2'); GND(P(c, '2'))
r = Rh('10k', N[0] + g(1) + 3.81, yb, d='LPF2'); W(N, P(r, '1')); lab_at(P(r, '2'), 'LP2I', 2)
W(N, (N[0], yb - g(4)))
r = Rh('10k', N[0] + g(1) + 3.81, yb - g(4), d='LPF2'); W((N[0], yb - g(4)), P(r, '1')); lab_at(P(r, '2'), 'LP2O', 2)
c = Ch('2n2', N[0] + g(16), yb + g(8), d='LPF2 (C0G)'); lab_at(P(c, '1'), 'LP2I', 2, 'l'); lab_at(P(c, '2'), 'LP2O', 2, 'r')
lab('LP2O', (g(228), g(46)), 'l'); W((g(228), g(46)), (g(230), g(46)))
c = Ch('10u', g(232), g(46), d='Wet coupling'); W((g(230), g(46)), P(c, '1'))
r = Rh('1k', P(c, '2')[0] + g(1) + 3.81, g(46), d='Wet out'); W(P(c, '2'), P(r, '1'))
lab_at(P(r, '2'), 'W', 2)
lab('VCO', (g(146), g(64)), 'l'); W((g(146), g(64)), (g(150), g(64)))
rv = pot('B50k', 'TIME', g(150), g(64) + 3.81, mirror=None, text=((g(146), g(68)), (g(146), g(69.5)), 'right'))
q = rheo(rv)
r = Rv('2k7', q[0], q[1] + 3.81 + g(1), side='r', d='Minimum delay (~50 ms); sets the LFO injection gain'); W(q, P(r, '1')); GND(P(r, '2'))
lab_at(q, 'TMIN', 3, 'l')
lab('W', (g(238), g(64)), 'l'); W((g(238), g(64)), (g(240), g(64)))
r = Rh('1k', g(242), g(64), d='Wet to MIX'); W((g(240), g(64)), P(r, '1'))
M = (P(r, '2')[0] + g(2), g(64)); W(P(r, '2'), M)
W(M, (M[0], g(66))); c = Cv('47n', M[0], g(66) + 3.81, side='l', d='Echo top-cut'); GND(P(c, '2'))
W(M, (M[0] + g(4), g(64)))
rv = pot('B10k', 'MIX', M[0] + g(4), g(64) + 3.81, text=((M[0] + g(7), g(68)), (M[0] + g(7), g(69.5)), 'left'))
GND(P(rv, '1')); lab_at(P(rv, '2'), 'MIXW', 3)

# ================================================================ FEEDBACK LOOP (U3)
s.box('FEEDBACK LOOP: SEND (U3A) -> loop -> RETURN (no plug = internal) -> TONE -> U3B -> limiter -> REPEAT', g(138), g(84), g(264), g(156))
ys = g(98)
lab('W', (g(141), ys), 'l'); W((g(141), ys), (g(143), ys))
c = Ch('1u', g(144.5), ys, d='Send coupling'); W((g(143), ys), P(c, '1'))
W(P(c, '2'), (g(150), ys))
r = Rv('1M', g(150), ys + g(3.5), side='r', d='Bias'); W((g(150), ys), P(r, '1')); lab_v(P(r, '2'), 'VB', 1, 'l')
pl, o = follower('U3', 1, g(162), ys)
W((g(150), ys), pl)
c = Ch('10u', o[0] + g(1) + 3.81, o[1], d='Send coupling'); W(o, P(c, '1'))
r = Rh('1k', P(c, '2')[0] + g(1) + 3.81, o[1], d='Send output protection'); W(P(c, '2'), P(r, '1'))
SN = (P(r, '2')[0] + g(3), o[1]); W(P(r, '2'), SN)
W(SN, (SN[0], SN[1] + g(2))); r = Rv('100k', SN[0], SN[1] + g(2) + 3.81, side='l', d='Send pull-down'); GND(P(r, '2'))
lab_at(SN, 'SEND', 3)
yr = g(128)
lab('RET', (g(141), yr), 'l'); W((g(141), yr), (g(145), yr))
r = Rv('1M', g(145), yr + g(3.5), side='l', d='Return pull-down'); W((g(145), yr), P(r, '1')); GND(P(r, '2'))
W((g(145), yr), (g(147), yr)); c = Ch('1u', g(148.5), yr, d='Return coupling'); W((g(147), yr), P(c, '1'))
W(P(c, '2'), (g(154), yr))
rv = pot('B50k', 'TONE', g(154), yr + 3.81, mirror=None, text=((g(150), yr + g(3)), (g(150), yr + g(4.5)), 'right'))
q = rheo(rv)
r = Rv('2k2', q[0], q[1] + 3.81 + g(1), side='r', d='Brightest TONE (~7 kHz with 10n)'); W(q, P(r, '1'))
TN = (q[0], P(r, '2')[1] + g(1)); W(P(r, '2'), TN)
W(TN, (TN[0] - g(4), TN[1])); c = Cv('10n', TN[0] - g(4), TN[1] + g(1) + 3.81, side='l', d='TONE cap: ~7 kHz .. ~300 Hz on every repeat')
W((TN[0] - g(4), TN[1]), (TN[0] - g(4), TN[1] + g(1))); GND(P(c, '2'))
W(TN, (TN[0] + g(6), TN[1]))
r = Rv('1M', TN[0] + g(6), TN[1] + g(3.5), side='r', d='Bias'); W((TN[0] + g(6), TN[1]), P(r, '1')); lab_v(P(r, '2'), 'VB', 1, 'l')
pl, o = follower('U3', 2, g(176), TN[1])
W((TN[0] + g(6), TN[1]), pl)
c = Ch('10u', o[0] + g(1) + 3.81, o[1], d='Return coupling'); W(o, P(c, '1'))
r = Rh('1k', P(c, '2')[0] + g(1) + 3.81, o[1], d='Limiter series R'); W(P(c, '2'), P(r, '1'))
L = (P(r, '2')[0] + g(3), o[1]); W(P(r, '2'), L)
for dx, rot in ((0, 90), (4, 270)):
    d = D(L[0] + g(dx), L[1] + g(1) + 3.81, rot, 'Loop limiter: keeps self-oscillation musical', text='l' if dx == 0 else 'r')
    a, b = P(d, '1'), P(d, '2'); top, bot = (a, b) if a[1] < b[1] else (b, a)
    W(L, (top[0], L[1]), top); gnd_down(bot, 1)
W(L, (L[0] + g(8), L[1]))
rv = pot('B10k', 'REPEAT', L[0] + g(8), L[1] + 3.81, text=((L[0] + g(11), L[1] + g(3)), (L[0] + g(11), L[1] + g(4.5)), 'left'))
GND(P(rv, '1')); lab_at(P(rv, '2'), 'RPT', 3)
s.text('No plug in RETURN: the jack\'s switch ties RET to SEND (internal path). TONE acts on every repeat in both cases.', g(140), g(150))
s.text('A fuzz in the loop adds gain every pass: the 1N4148W pair caps the loop at about +-0.6 V.', g(140), g(153))

# ================================================================ LFO (U4, LM358) -> TMIN
s.box('MODULATION: LFO (U4, LM358) -> DEPTH -> 33k + 10u -> TMIN (even depth across TIME). ~0.5-12 Hz', g(4), g(100), g(134), g(156))
yl = g(114)
pl, mi, ou = OP('U4', 1, g(40), yl, 'LM358')
W(pl, (pl[0] - g(6), pl[1])); lab('VB', (pl[0] - g(6), pl[1]), 'l')
r27 = Rh('47k', mi[0] - 6.35, mi[1], d='Max rate'); W(P(r27, '2'), mi)
q = P(r27, '1')
rv = pot('B1M', 'RATE', q[0] - g(2), q[1] + 3.81, mirror=None, text=((q[0] - g(6), q[1] + g(3)), (q[0] - g(6), q[1] + g(4.5)), 'right'))
W(q, (q[0] - g(2), q[1]))
e = rheo(rv); W(e, (e[0], e[1] + g(2))); lab('SQR', (e[0], e[1] + g(2)), 'l')
fy = mi[1] + g(4); rx = ou[0] + g(1)
W(P(r27, '2'), (P(r27, '2')[0], fy))
c = Ch('1u', (P(r27, '2')[0] + rx) / 2, fy, d='LFO timing'); W((P(r27, '2')[0], fy), P(c, '1')); W(P(c, '2'), (rx, fy))
W(ou, (rx, ou[1])); W((rx, ou[1]), (rx, fy)); W((rx, ou[1]), (rx + g(4), ou[1])); lab('TRI', (rx + g(4), ou[1]))
pl, mi, ou = OP('U4', 2, g(80), yl, 'LM358')
W(mi, (mi[0] - g(6), mi[1])); lab('VB', (mi[0] - g(6), mi[1]), 'l')
ra = Rh('10k', pl[0] - 6.35, pl[1], d='Schmitt input')
W(P(ra, '2'), pl); q = P(ra, '1'); W(q, (q[0] - g(2), q[1])); lab('TRI', (q[0] - g(2), q[1]), 'l')
W((P(ra, '2')[0], pl[1]), (P(ra, '2')[0], pl[1] - g(4)))
rb = Rh('22k', (P(ra, '2')[0] + ou[0] + g(1)) / 2, pl[1] - g(4), d='Schmitt hysteresis')
W((P(ra, '2')[0], pl[1] - g(4)), P(rb, '1')); W(P(rb, '2'), (ou[0] + g(1), pl[1] - g(4)), (ou[0] + g(1), ou[1]))
W(ou, (ou[0] + g(1), ou[1])); W((ou[0] + g(1), ou[1]), (ou[0] + g(4), ou[1])); lab('SQR', (ou[0] + g(4), ou[1]))
ym = g(140)
lab('TRI', (g(10), ym), 'l'); W((g(10), ym), (g(13), ym))
c = Ch('4u7', g(15), ym, d='LFO coupling'); W((g(13), ym), P(c, '1'))
W(P(c, '2'), (g(24), ym))
rv = pot('B100k', 'DEPTH', g(24), ym + 3.81, text=((g(20), ym + g(3)), (g(20), ym + g(4.5)), 'right'))
GND(P(rv, '1'))
w = P(rv, '2')
r = Rh('33k', w[0] + g(1) + 3.81, w[1], d='LFO injection (~+-5 % delay change at full DEPTH)'); W(w, P(r, '1'))
c = Ch('10u', P(r, '2')[0] + g(1) + 3.81, w[1], d='Coupling into TMIN (ceramic, non-polar)'); W(P(r, '2'), P(c, '1'))
lab_at(P(c, '2'), 'TMIN', 3)

s.write(OUT, title_block={'title': 'Loop Echo', 'rev': '1.0', 'company': 'Super-Freq', 'date': '2026-10-25',
                         'comments': ['PT2399 delay, effects loop in the feedback (SEND / switched RETURN), TONE on every repeat, TIME modulation',
                                      'PT2399 network from Small Time; SMD for JLC (all basic parts except the PT2399)']})
print('written', OUT)
