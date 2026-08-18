# demo/

Everything needed to run and present the CoastalVision AI demo reliably,
even without internet access.

## Contents

- **`demo_script.md`** — 3–4 minute, 4-speaker presentation script.
- **`fallback/`** — a static, pre-generated copy of everything in
  `outputs/` (stats.json + all PNGs), refreshed each time you run
  `python run_demo.py`. If live computation fails right before
  presenting, you can show these files directly, or point the browser at
  `integration/report.html`, which is a standalone page built specifically
  to read a bundled snapshot instead of live output.

## Running the demo

From the repo root:

```bash
python run_demo.py          # regenerates outputs/ + refreshes fallback/
python3 -m http.server 8080 # serve the whole repo
```

Then open in a browser:

- `http://localhost:8080/frontend/public/index.html` — main dashboard
- `http://localhost:8080/frontend/public/report.html` — one-page report
- `http://localhost:8080/integration/report.html` — offline fallback report

No internet connection, satellite API, or Google Earth Engine access is
required at any point — the demo pipeline runs entirely on the bundled
synthetic sample dataset (see `data/README.md`).
