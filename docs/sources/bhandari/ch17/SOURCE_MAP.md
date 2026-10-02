# Bhandari Chapter 17 — Source Map

## Source and coverage

- Supplied file: `V B Bhandari chapter 17 and 18.pdf` (61 PDF pages); Chapter 17 printed pages 646–690 are present.
- The chapter title shown in the extract is **Spur Gears**. The PDF metadata identifies export software, not a textbook edition; edition and publication year are unverified.
- Page references below use the book's printed page numbers.
- Chapter 17 Ex. 17.2 is a three-gear train with an idler. The current solver represents one external pair, so the regression test checks the A–B mesh geometry and force magnitudes rather than the complete train, the idler shaft reaction, or the driven C-shaft torque.

## Section and equation map

| Section | Topic | Printed pages | Method family / MechDAC boundary |
|---|---|---:|---|
| 17.1–17.4 | Mechanical drives, gear drives, classification, and selection | 646–650 | Application context |
| 17.5–17.7 | Law of gearing, spur-gear terminology, and tooth systems | 650–655 | Pitch geometry background; no tooth-form design |
| 17.8 | Gear trains | 656–657 | The solver does not compose idler, compound, or planetary trains |
| 17.9–17.10 | Interference/undercutting and backlash | 657–659 | Not checked or represented by the input model |
| 17.11 | Force analysis | 659–660 | Pitch-circle force magnitudes for ideal power transfer |
| 17.12–17.24 | Tooth failures, materials, gear design, strength, wear, and lubrication | 664–690 | Separate methods; none are inferred from force results |

- §17.11, Eq. (17.7), p. 660: transmitted torque is `T = 60×10^6 P/(2πn)` when power is in kW, speed in rpm, and torque in N·mm.
- §17.11, Eq. (17.8), p. 660: tangential tooth force is `P_t = 2T/d`, with pitch diameter in mm.
- §17.11, Eq. (17.9), p. 660: radial tooth force magnitude is `P_r = P_t tan(α)`.
- The chapter's force derivation assumes quasi-static pitch contact, neglects dynamic loading, and assumes a single tooth pair carries the full load; the current solver similarly reports ideal pitch-force magnitudes only.

## Worked-example validation

- Ex. 17.2, pp. 660–661, tests an idler train with 3.5 kW at 700 rpm, module 5 mm, 20° pressure angle, and tooth counts 30/60/40.
- `tests/test_gears.py` models the local A–B mesh and independently checks the printed 150 mm and 300 mm pitch diameters, 47,746.48 N·mm input torque, 636.62 N tangential force, and 231.71 N radial force.
- The source reports zero torque on the idler B shaft and 63,661.98 N·mm on output gear C. Those are train-level results, outside a single-pair solver's contract; they are not presented as outputs from this regression.
- The cited pages and equations were extracted and visually inspected. No PDF pages or textbook prose have been copied into the repository.

## Exclusions and dependencies

The pitch-force calculation depends on module, tooth count, transmitted power/speed, and pressure angle. Tooth strength, fatigue, wear, backlash, interference, undercut, dynamics, load sharing, bearing reactions, gear-train composition, and standards-based ratings are separate capabilities and are not inferred from this result.
