# Bhandari Chapter 9 — Source Map

## Source and coverage

- Supplied file: `V B Bhandari chapter 9.pdf` (59 PDF pages).
- Chapter title shown in the PDF: **Shafts, Keys and Couplings**; printed pages 330–388 are present.
- The contents list practice problems on p. 389, but that page is not present in this supplied extract.
- The PDF metadata identifies the export software, not a textbook edition. Edition and publication year are therefore unverified.
- Page references below use the book's printed page numbers.

## Section index and candidate methods

| Section | Topic | Printed pages | Method family / later use |
|---|---|---:|---|
| 9.1 | Transmission Shafts | 330–331 | Shaft purpose, materials, stock sizes |
| 9.2 | Shaft Design on Strength Basis | 331–333 | Solid/hollow nominal stress, combined loads, failure criteria |
| 9.3 | Shaft Design on Torsional Rigidity Basis | 333–334 | Angle-of-twist sizing |
| 9.4 | ASME Code for Shaft Design | 334–341 | Standard-specific allowable stress and moment factors |
| 9.5 | Design of Hollow Shaft on Strength Basis | 342–344 | Hollow-section strength |
| 9.6 | Design of Hollow Shaft on Torsional Rigidity Basis | 344–345 | Hollow-section twist |
| 9.7 | Flexible Shafts | 346–347 | Flexible-shaft component |
| 9.8 | Keys | 346–347 | Torque transfer and key classification |
| 9.9 | Saddle Keys | 347–348 | Key type |
| 9.10 | Sunk Keys | 348–349 | Key type and dimensions |
| 9.11 | Feather Key | 349–350 | Sliding keyed connection |
| 9.12 | Woodruff Key | 350 | Key type |
| 9.13 | Design of Square and Flat Keys | 350–352 | Key shear/crushing design |
| 9.14 | Design of Kennedy Key | 352–354 | Multiple-key design |
| 9.15 | Splines | 354–356 | Splined torque-transfer connection |
| 9.16 | Couplings | 356–357 | Coupling selection/background |
| 9.17 | Muff Coupling | 357–358 | Rigid coupling |
| 9.18 | Design Procedure for Muff Coupling | 357–359 | Coupling component sizing |
| 9.19 | Clamp Coupling | 359–360 | Friction/clamp coupling |
| 9.20 | Design Procedure for Clamp Coupling | 360–362 | Coupling component sizing |
| 9.21 | Rigid Flange Couplings | 362–364 | Rigid coupling construction |
| 9.22 | Design Procedure for Rigid Flange Coupling | 364–368 | Shaft, key, flange, and bolt checks |
| 9.23 | Bushed-Pin Flexible Coupling | 368–371 | Flexible coupling |
| 9.24 | Design Procedure for Flexible Coupling | 371–376 | Coupling component sizing |
| 9.25 | Design for Lateral Rigidity | 376–380 | Shaft deflection limits |
| 9.26 | Castigliano’s Theorem | 380–382 | Deflection method |
| 9.27 | Area Moment Method | 382–383 | Deflection method |
| 9.28 | Graphical Integration Method | 383–385 | Deflection method |
| 9.29 | Critical Speed of Shafts | 385–388 | Rotor/shaft dynamics |

## Equation index

- §§9.1–9.2, Eqs. (9.1)–(9.12), pp. 331–333: axial/bending/torsional stresses, principal values, equivalent moments, and solid-shaft strength criteria. For a solid round section, Eqs. (9.2) and (9.3) give `σ_b = 32M_b/(πd³)` and `τ = 16M_t/(πd³)`. Eqs. (9.8)–(9.12) use maximum-principal or maximum-shear theory; the chapter favors maximum shear for ductile shafts.
- §9.3, Eq. (9.13), pp. 333–334: solid-shaft angle of twist.
- §9.4, Eqs. (9.14)–(9.15), p. 334: ASME allowable shear and shock/fatigue-adjusted moments; Table 9.2 supplies application factors.
- §§9.5–9.6, Eqs. (9.16)–(9.26), pp. 343–345: hollow-shaft strength and torsional rigidity.
- §§9.8–9.15, Eqs. (9.27)–(9.32), pp. 351–355: key failure/design and spline strength relations.
- §§9.17–9.24, Eqs. (9.33)–(9.52), pp. 357–373: muff/clamp/flange/flexible-coupling design relations.
- §§9.25–9.29, Eqs. (9.53)–(9.57), pp. 380–388: shaft deflection/rigidity methods and critical speed.

The current shaft-strength verification uses §§9.1–9.2 only. Within the model boundary, the nominal bending/torsion equations apply to one selected section with one bending resultant and one torque; the current input omits axial load. The chapter's strength-sizing criterion is maximum shear (Tresca), while MechDAC's existing solver uses generic distortion energy (von Mises); see the source ledger for this difference.

## Tables, figures, examples, and standards

- Numbered tables: Table 9.1 standard bar diameters (p. 331); Table 9.2 ASME shock/fatigue factors (p. 334); Table 9.3 square/rectangular sunk-key sizes (pp. 348–349); Table 9.4 beam bending-moment/deflection cases (pp. 376–379).
- Figure groups: Fig. 9.1 transmission shaft (p. 330), 9.2 Mohr circle (p. 332), 9.3–9.15 shaft layouts/load and moment diagrams/solid and hollow shaft methods (pp. 335–345), 9.16–9.28 keys and splines (pp. 347–355), 9.29–9.37 rigid couplings (pp. 357–367), 9.38–9.46 flexible couplings (pp. 368–375), 9.47–9.51 shaft-deflection methods (pp. 379–384), and 9.52–9.55 critical-speed cases (pp. 386–388).
- Worked-example index: Ex. 9.1 p. 335; 9.2 p. 336; 9.3 p. 337; 9.4 p. 338; 9.5 p. 339; 9.6 p. 340; 9.7–9.8 p. 341; 9.9 p. 342; 9.10 p. 344; 9.11–9.12 p. 345; 9.13 p. 351; 9.14 p. 352; 9.15–9.16 p. 353; 9.17 p. 355; 9.18 p. 358; 9.19 p. 361; 9.20 p. 365; 9.21–9.22 p. 366; 9.23–9.24 p. 372; 9.25 p. 375; 9.26 p. 376; 9.27 p. 381; 9.28 p. 383; 9.29 p. 385; 9.30 p. 387.
- Standards cited in the extract: IS 1732–1989 (round/square bar dimensions, p. 331); IS 4600–1968 (flexible shafts, p. 346); IS 2048–1983, IS 2292–1974, IS 2293–1974, and IS 2294–1980 (key/keyway types, p. 347); IS 6196–1971 and IS 2693–1964 (couplings, p. 356); IS 2693–1980 (bush-type flexible coupling, p. 367). §9.4 also presents an ASME shaft-design method. None is implemented by the current solver.
- Ex. 9.1, pp. 335–336, is a multi-plane pulley shaft sized by maximum-shear theory. Fig. 9.3 on p. 335 was rendered and inspected. The source's final sizing step was independently recalculated from its stated maximum resultant bending moment, torque, and permissible shear stress; it returns 45.47 mm to the printed precision. It is not a like-for-like MechDAC regression case because both the load mapping and failure criterion differ.

## Dependencies and extraction notes

Strength sizing depends on the shaft-section stress equations in §9.2, material yield strength, factor of safety, and a chosen failure theory. Torsional rigidity and lateral rigidity are separate capabilities; ASME factors are standard-specific; keys, splines, and couplings are separate component methods; critical speed is dynamic rather than static strength sizing.

Text was extracted page by page with `pypdf`. Several equations and figure labels are spatially laid out and can be reordered in extracted text. Rendered pp. 332–333 and 335–336 were visually checked for the combined-stress equations and Example 9.1. The supplied extract omits p. 389 from the contents-listed practice problems. No PDF pages were copied into the repository.
