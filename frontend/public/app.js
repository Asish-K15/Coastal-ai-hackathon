/**
 * app.js
 * ------
 * Loads outputs/stats.json (+ meta.json) and wires up the before/after
 * slider, change-overlay toggle, and stats dashboard.
 *
 * IMPORTANT: values are NEVER hard-coded here — everything rendered on
 * screen comes from the JSON files produced by the Python pipeline
 * (see SCHEMA.md). Re-run the pipeline and refresh the page to see new
 * numbers.
 */

// Absolute path from the repo root. Serve the WHOLE repo root over HTTP
// (e.g. `python3 -m http.server 8080` run from the repo root — see
// frontend/README.md / run_demo.py) and open
// http://localhost:8080/frontend/public/index.html
const OUTPUTS_BASE = "/outputs";

async function loadJSON(path) {
  const res = await fetch(path, { cache: "no-store" });
  if (!res.ok) throw new Error(`Failed to load ${path}: ${res.status}`);
  return res.json();
}

async function loadCoastalData() {
  const [stats, meta] = await Promise.all([
    loadJSON(`${OUTPUTS_BASE}/stats.json`),
    loadJSON(`${OUTPUTS_BASE}/meta.json`).catch(() => null),
  ]);
  return { stats, meta };
}

function fmtArea(sqm) {
  if (Math.abs(sqm) >= 1_000_000) {
    return `${(sqm / 1_000_000).toFixed(2)} km\u00B2`;
  }
  return `${sqm.toLocaleString(undefined, { maximumFractionDigits: 0 })} m\u00B2`;
}

function fmtPercent(pct) {
  const sign = pct > 0 ? "+" : "";
  return `${sign}${pct.toFixed(2)}%`;
}

function riskClass(tag) {
  return (tag || "").toLowerCase();
}

function interpretation(stats) {
  const dir = stats.net_change_sqm < 0 ? "net land loss (erosion-dominant)" :
              stats.net_change_sqm > 0 ? "net land gain (accretion-dominant)" :
              "a stable coastline with no net change";
  return `Between ${stats.date_before} and ${stats.date_after}, the ${stats.aoi_name} ` +
    `experienced ${dir}. Detected erosion totaled ${fmtArea(stats.area_eroded_sqm)}, ` +
    `while accretion totaled ${fmtArea(stats.area_accreted_sqm)}, for a net change of ` +
    `${fmtArea(stats.net_change_sqm)} (${fmtPercent(stats.percent_change)} of the ` +
    `baseline land area). This places the AOI in the "${stats.risk_tag}" demo risk ` +
    `category.`;
}

/** Wire up a draggable before/after comparison slider inside `wrapEl`. */
function initSlider(wrapEl, handleEl, afterImgEl) {
  let dragging = false;

  function setPosition(clientX) {
    const rect = wrapEl.getBoundingClientRect();
    let pct = ((clientX - rect.left) / rect.width) * 100;
    pct = Math.max(0, Math.min(100, pct));
    afterImgEl.style.clipPath = `inset(0 0 0 ${pct}%)`;
    handleEl.style.left = `${pct}%`;
  }

  function start(e) {
    dragging = true;
    move(e);
  }
  function move(e) {
    if (!dragging) return;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    setPosition(clientX);
  }
  function end() {
    dragging = false;
  }

  handleEl.addEventListener("mousedown", start);
  wrapEl.addEventListener("mousedown", start);
  window.addEventListener("mousemove", move);
  window.addEventListener("mouseup", end);

  handleEl.addEventListener("touchstart", start, { passive: true });
  wrapEl.addEventListener("touchstart", start, { passive: true });
  window.addEventListener("touchmove", move, { passive: true });
  window.addEventListener("touchend", end);
}

/** Populate the stats dashboard elements given a stats object. */
function renderStats(root, stats) {
  root.querySelector("[data-aoi-name]").textContent = stats.aoi_name;
  root.querySelector("[data-date-before]").textContent = stats.date_before;
  root.querySelector("[data-date-after]").textContent = stats.date_after;
  root.querySelector("[data-eroded]").textContent = fmtArea(stats.area_eroded_sqm);
  root.querySelector("[data-accreted]").textContent = fmtArea(stats.area_accreted_sqm);
  root.querySelector("[data-net]").textContent = fmtArea(stats.net_change_sqm);
  root.querySelector("[data-percent]").textContent = fmtPercent(stats.percent_change);

  const riskEl = root.querySelector("[data-risk]");
  riskEl.textContent = stats.risk_tag;
  riskEl.classList.remove("low", "medium", "high");
  riskEl.classList.add(riskClass(stats.risk_tag));
}

window.CoastalVision = {
  loadCoastalData,
  fmtArea,
  fmtPercent,
  riskClass,
  interpretation,
  initSlider,
  renderStats,
};
