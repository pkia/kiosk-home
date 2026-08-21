# Kiosk Home

![CI](https://github.com/pkia/kiosk-home/actions/workflows/ci.yml/badge.svg)

The chooser screen the Raspberry Pi touchscreen opens on boot: big
touch cards for each dashboard installed on the host, a live status dot
per service, and one live fact per card (ship count, next match…).
Tapping a card opens that dashboard; its ⌂ Home button comes back here.

This is deliberately the **only** project that knows the dashboards
exist. The dashboards themselves (maritime on :8000, CS2 on :8001) know
nothing about each other — they only know this screen on :8091 — so
adding, removing or renaming one touches this repo alone:

```python
DASHBOARDS = [
    {"id": "maritime", "name": "Maritime",  "icon": "⛵", "port": 8000, ...},
    {"id": "cs2",      "name": "CS2 Esports", "icon": "🎯", "port": 8001, ...},
]
```

Card facts are best-effort reads of each dashboard's own API; if one is
down the card just shows its OFFLINE dot and stays tappable.

## How it runs

Flask on port 8091 (`kiosk-home.service`), started by the same
pull-based CD pipeline as the other projects. The kiosk's chromium
(`ais-kiosk.service`) opens `http://localhost:8091` as its start page.

## Local development

```bash
venv/bin/python app.py        # chooser on :8091
venv/bin/python -m pytest -v
```
