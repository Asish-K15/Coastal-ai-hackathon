# CoastalVision AI — Demo Script

**Target duration:** 3–4 minutes · **4 speakers**

Before presenting, run once: `python run_demo.py` — this regenerates
`outputs/` and refreshes the `demo/fallback/` and
`integration/sample_stats.json` safety nets. Then open
`frontend/public/index.html` via a local server (see main `README.md`).

---

## Speaker 1 — The Problem (≈45s)

- Coastal erosion and accretion reshape shorelines constantly, threatening
  homes, infrastructure, and ecosystems.
- Monitoring change manually (site visits, survey teams) is slow, expensive,
  and hard to do at scale.
- Satellite imagery gives us repeat, wide-area coverage — but someone still
  has to turn raw imagery into an actionable, quantified answer.
- **CoastalVision AI** does that: point it at two dates of imagery for an
  Area of Interest (AOI) and it tells you what changed, by how much, and
  how risky the trend is.

## Speaker 2 — Data & Method (≈60s)

- Pipeline: satellite bands → **NDWI** → water/land masks → pixel-level
  **change detection** → area + percentage stats → **risk classification**
  → `stats.json` → frontend.
- NDWI = `(Green − NIR) / (Green + NIR)`. Water reflects less near-infrared
  light than land, so NDWI cleanly separates water from land pixels above
  a configurable threshold.
- Comparing the "before" and "after" water masks pixel-by-pixel gives three
  outcomes: **erosion** (land→water), **accretion** (water→land), or no
  change.
- For today's demo we use a small, clearly-labeled **synthetic sample
  dataset** (not real satellite imagery) so the whole pipeline runs
  instantly and offline — see `data/README.md`. The architecture is built
  so real Sentinel-2 Green/NIR bands can be swapped in without touching
  the NDWI, change-detection, or risk logic.

## Speaker 3 — Visualization (≈75s)

Live in the dashboard (`frontend/public/index.html`):

- **Before/After slider** — drag to compare the water/land mask across the
  two dates for the AOI.
- **Change overlay** — toggle between the combined change map, erosion-only,
  and accretion-only views. Legend: 🔴 red = erosion, 🟢 green = accretion.
- **Statistics panel** — area eroded, area accreted, net change, percentage
  change, and a **risk level** (Low / Medium / High), all loaded live from
  `outputs/stats.json` — nothing hard-coded in the UI.
- Flip to the **Report** tab for a one-page, judge-friendly summary with a
  plain-language interpretation of the numbers.

## Speaker 4 — Integration & Impact (≈45–60s)

- The whole pipeline — NDWI, masking, change detection, area math, risk
  tagging, JSON contract, and frontend — runs end-to-end offline in
  seconds, with automated tests (`tests/`) covering every stage.
- Practical impact: this kind of tool could help coastal managers,
  disaster-preparedness teams, and researchers triage which stretches of
  coastline need attention first, using nothing but publicly available
  satellite imagery.
- **What's next:** plug in real Sentinel-2 (or similar) Green/NIR bands
  for a real AOI, refine the pixel-resolution and risk thresholds against
  real-world outcomes, and explore ML extensions — coastline segmentation,
  change-detection models, and erosion-rate forecasting — on top of the
  same architecture.

---

### Fallback plan

If live computation or the browser demo fails during presentation:

1. Open `integration/report.html` instead — it reads a pre-generated,
   bundled snapshot (`integration/sample_stats.json`) and needs no
   pipeline run or network access.
2. Or show the static images directly from `demo/fallback/`.
