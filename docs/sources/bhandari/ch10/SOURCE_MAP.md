# Bhandari Chapter 10 — Source Map

## Source and coverage

- Supplied file: `V B Bhandari chapter 10.pdf` (51 PDF pages).
- Chapter title shown in the extract: **Springs**; printed pages 393–443 are present.
- PDF metadata identifies export software rather than a textbook edition, so edition and publication year are unverified.
- Page references below use the printed book page numbers.
- The current solver covers a single static, round-wire helical compression spring with supplied load, wire and mean-coil diameters, effective active-coil count, shear modulus, and allowable shear stress. It reports spring index, Wahl factor, maximum shear stress, deflection, spring rate, and shear-stress utilization.

## Relevant sections and equations

| Section | Topic | Printed pages | Relevance |
|---|---|---:|---|
| 10.3–10.5 | Helical spring terminology, end styles, stress and deflection | 395–400 | Defines mean coil diameter, wire diameter, active coils, stress, and deflection |
| 10.7 | Spring materials | 401–403 | Background for material strength and shear modulus; material selection is not performed by this solver |
| 10.8 | Design of helical springs | 403–404 | General design procedure |
| 10.9 | Spring design—trial and error method | 405–406 | Iterative wire/material selection, outside the solver boundary |
| 10.10 | Design against fluctuating stresses | 406–407 | Fatigue-related method, excluded from this static solver |

- §10.5, Eq. (10.7), printed p. 399: Wahl factor, `K_w = (4C − 1)/(4C − 4) + 0.615/C`, where `C = D/d`.
- §10.5, Eq. (10.8), printed p. 399: axial deflection, `δ = 8PD³N_a/(Gd⁴)`.
- §10.5, Eq. (10.9), printed p. 399: spring rate, `k = Gd⁴/(8D³N_a)`.
- §10.8, Eq. (10.13), printed p. 404: maximum torsional shear stress, `τ_max = K_w(8PC/(πd²))`; substituting `D = Cd` gives the equivalent `τ_max = K_w 8PD/(πd³)` used in the solver.
- Shear-stress utilization is calculated as the solver-specific ratio `τ_max/τ_allowable`; the source example supplies the allowable stress but does not name this ratio as a separate design equation.

## Worked-example validation

Example 10.1, printed pp. 407–408, is a helical compression spring under a maximum force of 1250 N. It specifies a target deflection of approximately 30 mm, spring index 6, modulus of rigidity 81,370 N/mm², ultimate tensile strength 1090 N/mm², and allowable shear stress equal to 50% of ultimate strength (545 N/mm²). The source calculates a 6.63 mm wire and rounds to 7 mm; it then uses a 42 mm mean coil diameter and rounds the active-coil count 7.91 to 8.

The regression test supplies those selected dimensions and independently applies Eqs. (10.7), (10.8), and (10.13). It reproduces `C = 6`, `K_w = 1.2525`, and actual deflection `30.34 mm`. Applying Eq. (10.13) at the selected 7 mm wire gives `τ_max = 488.18 MPa`; against the supplied 545 MPa allowable, utilization is `0.89575`. Spring rate, `41.20 N/mm`, is calculated from Eq. (10.9); Example 10.1 does not print a spring-rate result.

The source also assumes square and ground ends, two inactive coils, a 1 mm adjacent-coil gap, then sizes total coils, free length, and pitch. Those outputs are outside the frozen result contract and are not modeled. The frozen input's `active_coils` is treated as the effective count directly.

## Boundaries and extraction notes

The solver performs a generic static calculation only. It does not select a wire grade or diameter, iterate a design, infer end geometry, or assess fatigue, buckling, solid height/coil bind, surge, tolerances, or stress concentrations. These exclusions do not imply a standards-specific rating.

Text was extracted with `pypdf`. Equations and Example 10.1 pages 407–408 were rendered and visually inspected because the extracted equation layout obscures superscripts and fractions. The extract contains 51 pages, spanning printed pp. 393–443; no PDF pages were copied into the repository.
