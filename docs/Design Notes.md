# Loop Echo: design notes

## Signal path

| Block | Parts | Notes |
|---|---|---|
| Input | R3 1M, C8 100n, R4 100 Ω, R5 1M to VB, **U2A** follower → DRY | As Small Time |
| Delay input (DIN) | DRY → C19 + R14 10k; repeats (RPT) → C20 + R15 10k | Summed at DIN, as Small Time (R9 / R16) |
| PT2399 (U1) | LPF1: R12 10k, R13 15k, C17 2n2, C18 10n. Integrators: C15 / C16 100n. LPF2: R16 / R17 / R18 10k, C21 10n, C22 2n2. Compander: C13 / C14 100n. REF: C12 47µ | Exactly Small Time's values. 5 V from U5 78L05 |
| TIME | VCO (pin 6) → B50k rheostat → R11 1k → GND | ≈ 30 ms to ≈ 340 ms. Higher resistance = longer and noisier |
| Wet | LP2O → C23 10µ → R19 1k → **W** | W feeds MIX and the SEND buffer |
| **Send** | W → C25 1µ → **U3A** follower → C26 10µ → R22 1k → **TIP**; R23 100k pull-down | Instrument-level, buffered |
| **Return** | **RING** → R24 1M, C27 1µ → **U3B** follower → C28 10µ → R26 1k → **1N4148 pair to ground** → **REPEAT** → RPT | **No plug:** the ring-normal contact (RN) ties RING to SEND, so the loop is closed internally and it's a normal delay |
| Mix + output | W → R20 1k → C24 47n (top-cut) → MIX → **U2B** inverting mixer (DRY + echo, 10k / 10k / 10k ∥ 1n) → R9 100 Ω → C11 → OUT | As Small Time. The output is inverted relative to the input, as Small Time was |
| **LFO** | **U4A** integrator (R27 47k + RATE B1M, C29 1µ) + **U4B** Schmitt (R28 10k / R29 22k) | ≈ 0.5 Hz to ≈ 12 Hz triangle, about ±1.4 V |
| **Modulation** | TRI → C30 4µ7 → **DEPTH** (pot to ground) → R30 100k → C31 1µ → VCO pin | AC-coupled, so DEPTH and RATE never shift the set delay time. About ±15 µA into pin 6 at full DEPTH |

**Op-amps:** U2 / U3 / U4 = 3 × TL072. U1 PT2399 (socket it: they vary a lot, per the 1776 doc). U5 78L05.

## Why it's built this way

- **Loop in the feedback only:** the first repeat is untouched, and each pass adds the effect again. That's the cumulative "degrading echo" sound.
- **REPEAT after the return:** the external pedal's own gain adds to every pass, and REPEAT sets the overall loop gain after it.
- **The limiter:** a fuzz or boost in the loop adds gain on every pass and would otherwise run away to full-scale oscillation. The 1N4148s cap the loop at about ±0.6 V, so self-oscillation stays musical.
  - If it clips the clean repeats too early, swap in red LEDs (±1.8 V).
  - Or raise R26 to 4k7 (softer).
- **True bypass:** no tails. Tails needs buffered bypass, because the true-bypass footswitch disconnects the output. That's why Small Time's tails didn't do much.
- **Levels:** PT2399 output is around the input level. The send is a unity buffer, so pedals in the loop see roughly guitar level.

## On the breadboard

1. **Without the loop (no plug):** TIME range; REPEAT up to self-oscillation (it should be the limiter-capped "musical" kind); MIX; noise. Try a few PT2399s.
2. **Modulation:** RATE range, DEPTH amount. Watch for clicks from the square wave (TRI is used, so there should be none). If depth is too much or too little, change R30 (47k–220k).
3. **Loop tests,** with a TRS Y-cable or two jacks wired to a TRS plug:
   - **Fuzz:** each repeat dirtier. Find the REPEAT setting where it sustains without exploding.
   - **Wah or filter** in the loop, rocked while repeats ring.
   - **Pitch shifter / octave:** cascading repeats.
   - **Phaser or trem:** modulated repeats.
   - **A boost:** check that the limiter holds.
4. **Levels:** with a unity pedal in the loop, REPEAT should behave the same as with no plug. If not, check the send and return levels.

## Ideas for later (from the discussion)

- **Ducking:** use the Flatline / Clean-Up envelope detector to turn the repeats down while playing.
- **"Age" built in:** an internal filter or clipper in the feedback, with a toggle for INTERNAL / LOOP.
- **Ramp footswitch:** a vactrol (LED/LDR) on TIME with RC ramps, for pitch dives and swells (the Multiplex's "tape speed", done our own way).
- **Second PT2399 modes:** series or parallel, our own version of the Multiplex idea.
- **Tap tempo:** needs a microcontroller.

The Multiplex document (1776 Effects) says it's for personal use only. We're using its ideas, not its circuit or layout, and won't use the trademarked mode names.

## Ideas from the Dragonfish (2026-10-25)

Source: madbean **Dragonfish** (`~/Documents/Guitar/Effects/Schematics/Dragonfish.pdf`, schematic p.13; close to the Tonepad Rebote 2.5 plus LFO). Ideas only.

### 1. LFO injection point: even modulation depth across TIME (adopt)

The PT2399 holds pin 6 (VCO) at about **2.8 V**; the clock follows the current drawn out of it, I = 2.8 V / (R_TIME + R_min).
- **Current way (ours):** LFO current straight into **pin 6**. Its share of I is tiny at short delays and large at long ones (with ±15 µA: about ±2 % at 3.7k total, ±27 % at 51k). Depth swings wildly as TIME turns.
- **Dragonfish way:** inject into the node **between the TIME pot and the fixed minimum resistor** (TIME → node → R_min → GND), through **33k + 10 µ**. Solving the node: ΔI / I = −I_lfo · R_min / 2.8 V, **independent of TIME**. Even depth across the range (pitch wobble still grows a little with delay time, but far less).
- **Change:** R_min 1k → **2k7** (also sets the shortest delay, ~50 ms) and LFO → DEPTH → **33k + 10 µ** → the TIME / R_min node (instead of 100k + 1 µ → pin 6). Re-trim DEPTH range on the breadboard (R_min sets the injection gain).

### 2. Darker, "analog-voiced" repeats (option)

Dragonfish adds RC poles **before** the chip (IC1A → 1 µ → **10k / 22n → 10k / 10n** → the PT2399 LPF1 with 10k, 33k, 1n) and uses **15n** caps in LPF2 (vs 10n / 2n2), then **1k5 + 22n** before MIX / RPT. Repeats are darker and get darker each pass, and more clock noise is filtered.

### 3. Low-power op-amp for the LFO

TL022 / TL062-class: much less (and less varying) supply current than a TL072, so less LFO tick on the supply. Check JLC basic status (LM358 C7950 is a known option).

### Skip

The **1N914 in the 78L05 ground leg** that runs the PT2399 at ~5.6–5.7 V for "headroom": above the 5.5 V datasheet maximum (madbean admits the early-failure risk). Keep the PT2399 at 5.0 V.

**Loop Echo specifics:** #1 replaces the current modulation feed (TRI → C30 4µ7 → DEPTH → R30 100k → C31 1µ → VCO pin 6) and R11 1k: R11 → 2k7, DEPTH wiper → 33k + 10 µ → the TIME / R11 node. #2 is a voicing option; with the effects loop the repeats are already re-processed, so try the stock (brighter) values first.

## v1.0 (2026-10-25): SMD, ordered as a prototype

- **Jacks:** separate SEND and RETURN (the user's choice), board-mounted (see *Board* below). RETURN's tip switch (TN) is wired to SEND: no plug = the loop closes internally.
- **TONE** (new, user request): B50k rheostat + 2k2 into 10n between the return coupling cap and U3B. ~7 kHz (CW) to ~300 Hz (CCW). It sits in the feedback path, so it acts on **every repeat** whether the loop or the internal path is used: repeats darken (or stay bright) cumulatively, like an analog delay.
- **Dragonfish fixes:** TIME minimum 1k → 2k7; LFO → DEPTH → 33k + 10µ into TMIN (the TIME / 2k7 node); LFO op-amp LM358.
- **Parts (JLC):** PT2399-SN C126407 (the only extended part), TL072 C6961 ×2, LM358 C7950, AMS1117-5.0 C6187, SS14 C2480, 1N4148W C81598; 0805 resistors / caps (2n2 C0G C28260), 47µ 1206 C96123 (REF, VB), 22µ ×2 C45783 bulk. `FT Rotation Offset` 270 on the SOIC op-amps (the pattern seen this month); check the PT2399 and SOT-223 in JLC's preview.
- **Not breadboarded:** order as v1.0 prototype boards. If something needs changing, it's a v1.1.

## Board (v1.0, 2026-10-25): 1590BB landscape, all jacks on top

Generated by `scripts/buildpcb_loopecho.py` (KiCad python), then `scripts/pcb_fields.py`, then `_tools/autoroute.py "Loop Echo" --passes 300 --edge-margin 0.55`. **Hand-edited since (don't re-run the generator):** J1 turned vertical beside the notch by the user; outline cut to exactly 100 mm wide (x 100–200); then **two footswitches** (below): second notch, J7 / D7 / R33 added, the U2, U1 and U4 groups re-placed into the centre and right, re-routed. **DRC 0 errors, 0 unconnected, schematic parity clean**; silk warnings only (silk pass to do). 47 vias.

**Why the 1590BB:** four PJ-646F bodies (20 mm each) + the DC jack (9 mm) = 89 mm. A 125B is 60.5 mm inside, and a 1590BB on its short side is ~88 mm. On the long side (landscape) it is ~110.7 mm inside; the lid-screw bosses in the corners take ~5.8 mm at each end, which leaves ~2.4 mm between jack bodies.

**Outside view of the face** (origin = face centre, +X right, +Y toward the jack wall; board → outside: X = 150 − x, Y = 100 − y):

| Part | X | Y | Notes |
|---|---|---|---|
| TIME · REPEAT · MIX | −32 · 0 · +32 | +15 | Alpha RD901F 9 mm, back side, 7.5 mm holes |
| RATE · DEPTH · TONE | −32 · 0 · +32 | −3 | |
| LOOP LED · BYPASS LED | −28 · +28 | −14.2 | 3 mm, back side |
| LOOP · BYPASS footswitches | −28 · +28 | −26 | 3PDT + SwitchPCB v2 each; a 19 × 25.5 mm board notch around each |

**Top wall (outside, left → right):** OUT −39.3 · RETURN −16.9 · DC 0 · SEND +16.9 · IN +39.3 mm from the centre.
- Jack centre depth from the outside of the face, estimated as for GlitchStorm v3 (face ~3 + measured 9.9 pot gap + 1.6 board + jack height): **PJ-646F ≈ 22.5 mm (8 mm above the board), DC ≈ 21 mm (6.5 mm).** Holes: 11.5 mm for the 7/16" bushings, ~8 mm for the DC jack (no bushing: the plug goes through the wall).
- The jack fronts sit against the inside of the top wall (footprint origin = barrel axis at the body front, board y 57.6).
- **Fit to check:** the PJ-646F body is 15.5 mm tall, so its bottom sits ~30 mm below the outside of the face. A 1590BB is ~34 mm deep with the lid, so there's only ~1 mm or so to spare: test-fit one jack before drilling.
- **DC plug reach:** the A-4118 has no bushing, so a 2.1 mm plug has to reach through the ~3 mm wall. Check that a typical 9.5 mm-barrel plug still seats; if not, open the DC hole so the plug's shell can enter (as noted for GlitchStorm v3).

**Footswitch wiring:** two identical SwitchPCB v2 boards. Each header is a 1×6 in the SwitchPCB pad order **IJ · IN · LED · GND · OUT · OJ**, standing vertically beside its notch (seen from inside: on the notch's left; pin 1 at the end away from the jacks). Turn each footswitch so its SwitchPCB's pads face the header, and the ribbons run straight.
- **J1 → BYPASS** (right, outside view): IJ input jack, IN circuit input, LED status LED (D6), OUT circuit output, OJ output jack. True bypass as on every Super-Freq pedal.
- **J7 → LOOP** (left, outside view), the same board wired as a loop selector: **IJ = SEND** (U3A buffer, after its 1k), **IN = SEND jack**, **LED = LOOP LED (D7, R33 4k7)**, **OUT = RETURN jack**, **OJ = RET** (into TONE → U3B → REPEAT).
  - **LOOP on:** OJ = OUT, so the repeats go out the SEND jack and come back from RETURN (with no plug in RETURN, its tip switch ties it to SEND: still the internal path). LOOP LED lit.
  - **LOOP off:** the SwitchPCB's bypass link makes OJ = IJ, so RET = SEND: a plain delay with TONE. IN is grounded, so the SEND jack is muted (a noisy pedal in the loop stays quiet).
  - SEND and RET both sit at 0 V DC (100k / 1M pull-downs), so switching shouldn't thump; expect at most a faint click on a circulating repeat. No more wire pads: the jacks, DC and loop are all on the board.

**Footprints** (`SuperFreq.pretty`, made from the Tayda drawings):
- `Jack_6.35mm_PJ-646F_Horizontal`: 6 × 1.6 mm holes, columns 16.2 mm apart, rows 4.2 / 10.5 / 16.8 mm behind the body front. Tip column on the left seen from the component side (the datasheet layout is the copper side, mirrored). **Before soldering, check one jack with a meter:** plug tip → pad T (square pad), sleeve → S, and TN opens when the plug goes in. If they're swapped across the columns, don't solder: the footprint needs mirroring.
- `DC_Jack_2.1mm_A-4118_Horizontal`: plated slots, pad 1 = centre pin (datasheet pin 4, GND: centre negative), pads 2 and 3 (datasheet pins 2 and 3) **both** to the SS14 anode, so it works whichever blade is the sleeve.

**Board size:** 100.0 × 83.5 mm (inside JLC's 100 × 100 price tier). The outer jack bodies end 0.7 mm inside the side edges, so the jacks didn't move.

