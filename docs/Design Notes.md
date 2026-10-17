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
