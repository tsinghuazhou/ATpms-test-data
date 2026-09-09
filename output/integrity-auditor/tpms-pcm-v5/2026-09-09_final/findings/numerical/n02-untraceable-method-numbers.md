# N2 — Methodological numbers with no in-repo source

The following quantities appear in §2 (Experimental Section) but have no
source file, calibration record, or certificate anywhere in the workspace.
They are not claimed to be wrong — they are **untraceable to data** in this
repo (Level 1: needs author confirmation / raw documentation):

- "overall measurement uncertainty of ±0.5 °C … calibrated against a
  NIST-traceable reference thermometer" — no calibration log found.
- "lateral and top-surface heat losses remained below 3% of the total input
  power" — no loss-calibration dataset found.
- PCM properties: "latent heat of fusion of approximately 200 kJ/kg",
  "negligible supercooling", "42 °C nominal melting point" — no datasheet in
  repo (paraffin grade unnamed).
- Manufacturing: 30 µm layer, "relative density exceeding 99% as confirmed by
  micro-CT", 200 W laser / 800 mm/s / 0.12 mm hatch / 67° rotation,
  300 °C 2 h stress relief, −0.09 MPa vacuum infusion, PCM loading "±2%",
  weighing ±0.01 g — no build log or micro-CT report found.
- Type-K wire/bead geometry (0.25 mm / ~0.5 mm), NI-9213 DAQ, kapton heater
  paste "> 1.5 W/(m·K)", ambient 23 ± 1 °C — no instrument spec stored.
- Abstract/intro "exceeding 100 W/cm² in advanced microprocessors" — citation
  needed (would be supplied by [20]-class reference once list rebuilt).

Action: keep an `experimental_provenance/` folder (datasheet, calibration
sheet, micro-CT excerpt, DAQ config) or remove/adjust the claims; reviewers of
methods-heavy journals will ask for these.
