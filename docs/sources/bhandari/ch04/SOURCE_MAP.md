# Bhandari Chapter 4 — Source Map

## Source and coverage

- Supplied file: `V B Bhandari- chapter 4.pdf` (61 PDF pages).
- Chapter title shown in the PDF: **Design Against Static Load**; printed pages 76–136 are present.
- The contents list short-answer questions on p. 137 and practice problems on p. 138, but those pages are not present in this supplied extract.
- The PDF metadata identifies the export software, not a textbook edition. Edition and publication year are therefore unverified.
- Page references below use the book's printed page numbers.

## Section index and candidate methods

| Section | Topic | Printed pages | Method family / later use |
|---|---|---:|---|
| 4.1 | Modes of Failure | 76–77 | Background: deflection, yielding, fracture |
| 4.2 | Factor of Safety | 77–78 | Allowable stress from strength and requested factor |
| 4.3 | Stress–Strain Relationship | 79–80 | Material response; background |
| 4.4 | Shear Stress and Shear Strain | 80–81 | Shear modulus and allowable shear |
| 4.5 | Stresses Due to Bending Moment | 81–82 | Beam/shaft nominal bending stress |
| 4.6 | Stresses Due to Torsional Moment | 82–83 | Circular-shaft nominal torsional stress |
| 4.7 | Eccentric Axial Loading | 83–84 | Future combined axial/bending loads |
| 4.8 | Design of Simple Machine Parts | 84–85 | Design workflow and examples |
| 4.9 | Cotter Joint | 85–89 | Joint strength; out of current mission |
| 4.10 | Design Procedure for Cotter Joint | 90–93 | Joint design; out of current mission |
| 4.11 | Knuckle Joint | 94–98 | Joint strength; out of current mission |
| 4.12 | Design Procedure for Knuckle Joint | 99–103 | Joint design; out of current mission |
| 4.13 | Principal Stresses | 104–105 | Plane-stress transformation and principal values |
| 4.14 | Theories of Elastic Failure | 106–107 | Failure-criterion overview |
| 4.15 | Maximum Principal Stress | 107–108 | Rankine criterion; brittle-material candidate |
| 4.16 | Maximum Shear Stress Theory | 108–110 | Tresca criterion; documented comparator |
| 4.17 | Distortion-Energy Theory | 110–112 | Huber–von Mises–Hencky yield criterion |
| 4.18 | Selection and Use of Failure Theories | 112–116 | Criterion selection; worked comparisons |
| 4.19 | Levers | 117–117 | Component analysis; out of current mission |
| 4.20 | Design of Levers | 118–127 | Component design; out of current mission |
| 4.21 | Fracture Mechanics | 128–129 | Future fracture capability |
| 4.22 | Curved Beams | 130–134 | Future curved-member stress capability |
| 4.23 | Thermal Stresses | 135–135 | Future thermal-load capability |
| 4.24 | Residual Stresses | 136–136 | Future residual-stress capability |

## Equation index

- §§4.1–4.2, Eqs. (4.1)–(4.2), pp. 76–78: factor of safety and allowable stress.
- §§4.3–4.4, Eqs. (4.3)–(4.11), pp. 80–81: normal/shear stress and strain relationships.
- §4.5, Eqs. (4.12)–(4.16), pp. 81–82: flexure `σ = My/I`, circular-section area moment of inertia, and parallel-axis relation. For a solid circle these reduce to `σ_b = 32M_b/(πd³)`.
- §4.6, Eqs. (4.17)–(4.23), pp. 82–83: torsion, circular-section properties, and torsional stress. For a solid circle these reduce to `τ = 16T/(πd³)`.
- §§4.7–4.8, Eq. (4.24) and subsequent relations, pp. 83–85: eccentric axial loading and simple machine-part design.
- §§4.9–4.10, Eqs. (4.25a)–(4.25j), pp. 85–93: cotter-joint failure/design relations.
- §§4.11–4.12, Eqs. (4.26a)–(4.26p), pp. 94–103: knuckle-joint failure/design relations.
- §§4.13–4.14, Eqs. (4.27)–(4.34), pp. 104–106: stress state, plane-stress transformation, principal values, and maximum shear.
- §4.15, Eqs. (4.35)–(4.37), pp. 107–108: maximum-principal-stress limits.
- §4.16, Eqs. (4.38)–(4.39), pp. 108–110: maximum-shear criterion and its tensile-to-shear yield relation.
- §4.17, Eqs. (4.40)–(4.45), pp. 110–112: distortion-energy criterion; Eq. (4.44) is its biaxial form for `σ₃ = 0`, and Eq. (4.45) gives the pure-shear yield relation.
- §§4.19–4.20, Eqs. (4.46)–(4.51), pp. 117–128: lever force/bending design.
- §4.21, Eqs. (4.52)–(4.53), pp. 128–130: fracture mechanics.
- §4.22, Eqs. (4.54)–(4.67), pp. 130–134: curved-beam stress/design.
- §§4.23–4.24, Eqs. (4.68)–(4.72), pp. 135–136: thermal and residual stress.

The current shaft-validation subset is §§4.2, 4.5–4.6, 4.13, and 4.17–4.18. The shaft validation test derives equivalent stress from principal stresses using §4.13 and Eq. (4.44), independently of the solver's direct `sqrt(σ_b² + 3τ²)` expression.

## Tables, figures, and worked examples

- No numbered `Table 4.x` caption was identified in the supplied chapter extract. Some worked examples present cross-section/property data in unnumbered tables, including standard rolled-section selection around pp. 101–102.
- Figure groups: Figs. 4.1–4.4 (basic normal/shear stress, pp. 79–81); 4.5–4.9 (bending, section properties, sign convention, torsion, eccentric loading, pp. 81–83); 4.10–4.29 (joint/component layouts and failure modes, pp. 85–103); 4.30–4.37 (stress state, Mohr circle, and failure envelopes, pp. 105–113); 4.38–4.41 (combined-load examples, including shaft geometry and Mohr circle, pp. 113–116); 4.42–4.60 (levers, pp. 117–128); 4.61–4.68 (fracture and curved beams, pp. 129–134); 4.69–4.70 (thermal stress, pp. 135–136).
- Worked-example index: Ex. 4.1 p. 84; 4.2 p. 91; 4.3 p. 93; 4.4 p. 94; 4.5 p. 100; 4.6 p. 101; 4.7–4.8 p. 102; 4.9–4.10 p. 103; 4.11 p. 113; 4.12 p. 114; 4.13 p. 115; 4.14 p. 116; 4.15 p. 121; 4.16 p. 123; 4.17 p. 124; 4.18 p. 126; 4.19 p. 132; 4.20 p. 133; 4.21 p. 134; 4.22 p. 136.
- Ex. 4.13, pp. 115–116, is the closest simple shaft comparison: an overhang crank under bending and torque, sized by maximum-shear theory. Fig. 4.40 on p. 115 was rendered and inspected to confirm the 250 mm and 500 mm moment arms.

No separate design standard is cited for the distortion-energy equations in this chapter. Material designations and rolled-section data appear in examples but are not part of the current solver.

## Dependencies and extraction notes

The flexure derivation assumes a straight uniform member under transverse planar loading, a homogeneous isotropic Hookean material, and plane sections remaining plane. The torsion derivation assumes a straight circular shaft, plane sections remaining plane after twist, and a homogeneous isotropic Hookean material. The failure-criterion workflow also depends on a ductile material with a yield strength. MechDAC now states these as assumptions in the shaft result; `MaterialSpec` does not infer ductility or validate the material law from a name. The workflow depends on the stress state (from §§4.5–4.6), principal stresses (§4.13), material yield property (§2 in the full book, not supplied here), and the selected criterion (§§4.15–4.18). Chapter 4 is a methods source, not a shaft-system load solver.

Text was extracted page by page with `pypdf`; displayed equations can be misordered by text extraction. Rendered pages 82, 105, 111–112, and 115–116 were visually checked for the equations and Fig. 4.40 used here. Remaining extraction issues do not affect the current verification. No PDF pages were copied into the repository.
