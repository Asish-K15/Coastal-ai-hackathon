# frontend/

CoastalVision AI dashboard: before/after slider, change overlay with
legend, live statistics panel, and a one-page report — all driven by
`outputs/stats.json` (and the PNG outputs), never hard-coded.

## Why static HTML/CSS/JS instead of React/Vite/Leaflet

The MVP spec's preferred stack is React + Vite + Leaflet. This build uses
plain HTML/CSS/JS (`public/index.html`, `public/report.html`,
`public/app.js`, `public/style.css`) instead, on purpose:

- **Zero network dependency.** Leaflet needs map tiles from a live tile
  server, and a Vite/React build needs `npm install` against the
  registry. Section 18 of the spec requires the demo to work with
  **no internet access**, so a zero-dependency, zero-build static page is
  the safer choice for the actual presentation.
- **Zero build step.** Nothing to compile; open two files in a browser
  (via a static server, see below) and it works.
- **Same JSON contract.** The page consumes `outputs/stats.json` exactly
  per `../SCHEMA.md`, so a React/Vite/Leaflet rebuild later is a drop-in
  replacement — none of the backend or data contract needs to change.

If your team has internet access and wants the React/Leaflet version,
this static app is a faithful reference implementation of exactly what
that version needs to do (same fetch calls, same DOM data).

## Running

The pages `fetch()` JSON/images from `/outputs/...`, so they must be
served from the **repo root**, not opened as local files:

```bash
# from the repo root
python3 -m http.server 8080
```

Then open:

- `http://localhost:8080/frontend/public/index.html` — dashboard
- `http://localhost:8080/frontend/public/report.html` — report

(`npm run dev` / `npm start` in this folder just run the same command
via `package.json`, for teammates used to that muscle memory.)

## Structure

```
frontend/
├── public/
│   ├── index.html   # dashboard: slider, overlay, stats
│   ├── report.html  # one-page report
│   ├── app.js        # data loading + slider + rendering logic
│   └── style.css
├── package.json
└── README.md
```
