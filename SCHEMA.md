# CoastalVision AI — Data Contract

## Purpose

This document defines the fixed JSON structure exchanged between
the backend/change-detection pipeline and the frontend.

The frontend must consume the field names defined below.

---

## stats.json

```json
{
  "aoi_name": "Primary Coastal AOI",
  "date_before": "2020-01-15",
  "date_after": "2025-01-15",
  "area_eroded_sqm": 12500.0,
  "area_accreted_sqm": 4200.0,
  "net_change_sqm": -8300.0,
  "percent_change": -5.6,
  "risk_tag": "High"
}