# Enclosure: Hammond/Tayda 1590BB (landscape)

Made 2026-10-25 by `scripts/make_enclosure.py` (KiCad python), which reads every hole from `LoopEcho.kicad_pcb`: pot shafts (mid-point of the mounting tabs), LED centres, the footswitch circles on Dwgs.User, and the jack positions. Re-run it if the board changes.

| File | Use |
|---|---|
| `LoopEcho_1590BB_drill.csv` | Tayda Box Tool. Face: origin = face centre, mm, +X right / +Y toward the jack wall, outside view; plus "Tayda portrait" columns (landscape turned 90° clockwise, as for GlitchStorm v3). Jack wall: along = face X, depth from the face's outside surface. Raw-aluminium diameters. |
| `LoopEcho_1590BB_drill_template.svg` | 1:1 printable template: the face, with the jack wall unfolded above it. Check the 50 × 10 mm box when printed. |
| `LoopEcho_1590BB_mill_marks.svg` | Othermill face marks: page = the 119.5 × 94 mm face, outside view, jack wall at the top; a circle per hole + a 1 mm centre circle. |

## Face (outside view, jack wall at the top)

```
     TIME      REPEAT      MIX           (Y +15)
     RATE      DEPTH       TONE          (Y -3)       X -32 / 0 / +32
   LOOP LED            BYPASS LED        (Y -14.2)    X -28 / +28
   LOOP FSW            BYPASS FSW        (Y -26)      X -28 / +28
```

- Pots (Alpha RD901F, M7 bushing): 7.5 mm. LEDs: 3.2 mm. Footswitches: 12.2 mm.

## Jack wall (top long wall, outside, left to right)

| Jack | Along X | Depth | Hole |
|---|---|---|---|
| OUT | −39.3 | 22.5 | 11.5 (7/16" bushing) |
| RETURN | −16.9 | 22.5 | 11.5 |
| DC 9V | 0 | 21.0 | 8.1 |
| SEND | +16.9 | 22.5 | 11.5 |
| IN | +39.3 | 22.5 | 11.5 |

**The depths are estimates:** face ~3 mm + the 9.91 mm pot gap measured on GlitchStorm v3 + 1.6 mm board + the jack's centre height (8 mm PJ-646F, 6.5 mm DC). Before drilling the wall: fit the pots and the board in the face, then measure from the outside of the face to the centre of one jack barrel and correct all five.

**Checks:**
- The PJ-646F body hangs ~30 mm below the outside of the face; the 1590BB is ~34 mm deep. Test-fit before drilling.
- The DC jack has no bushing: the plug must reach through the wall. If a plug doesn't seat, open the hole until the plug's shell enters.
- The box walls have a slight draft: measure your box and centre on it, not on the corners.
