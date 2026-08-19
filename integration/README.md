# integration/

Glue and safety-net artifacts that connect the backend and frontend, and
protect the demo against a bad-timing failure.

| File                  | Purpose                                                                 |
|------------------------|---------------------------------------------------------------------------|
| `sample_stats.json`     | A bundled snapshot of `outputs/stats.json`, refreshed by `run_demo.py`.  |
| `report.html`           | Standalone fallback report that reads `sample_stats.json` directly (not the live `outputs/`), so it works even if the live pipeline run fails right before you present. |

Regenerate `sample_stats.json` any time with:

```bash
python run_demo.py
```

See `../demo/README.md` for how this fits into the overall demo/fallback
strategy.
