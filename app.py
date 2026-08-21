#!/usr/bin/env python3
"""Kiosk Home - the chooser screen the Pi touchscreen opens on boot.

Lists the dashboards installed on this host as big touch cards and
forwards to whichever one is picked. This is the only project that
knows about the individual dashboards; they know nothing about each
other, only how to come back here.
"""
import socket
import time
from urllib.request import urlopen

from flask import Flask, jsonify, render_template

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

FETCH_TIMEOUT = 3

DASHBOARDS = [
    {
        "id": "maritime",
        "name": "Maritime",
        "icon": "⛵",
        "tagline": "Ships · satellites · RF spectrum",
        "port": 8000,
        "href": "/",
    },
    {
        "id": "cs2",
        "name": "CS2 Esports",
        "icon": "🎯",
        "tagline": "Live matches · upcoming · results",
        "port": 8001,
        "href": "/",
    },
]


def port_open(port, host="127.0.0.1"):
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def _get_json(url):
    try:
        with urlopen(url, timeout=FETCH_TIMEOUT) as r:
            import json
            return json.loads(r.read().decode())
    except Exception:
        return None


def live_fact(d):
    """One short live fact per dashboard, best effort; empty if unknown."""
    if d["id"] == "maritime":
        j = _get_json("http://127.0.0.1:8000/api/onlineships")
        if j and j.get("count"):
            return f"{j['count']} ships on the online feed"
        return ""
    if d["id"] == "cs2":
        j = _get_json("http://127.0.0.1:8001/api/matches")
        if j:
            live = len(j.get("live") or [])
            upcoming = len(j.get("upcoming") or [])
            if live:
                return f"{live} match{'es' if live > 1 else ''} live now"
            if upcoming:
                import time as _t
                m = j["upcoming"][0]
                dt = time.strftime("%H:%M", _t.localtime(m["start_ts"]))
                who = f'{m["team1"]["name"]} v {m["team2"]["name"]}'
                return f"next {dt} · {who}"
        return ""
    return ""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/dashboards")
def api_dashboards():
    out = []
    for d in DASHBOARDS:
        online = port_open(d["port"])
        out.append({
            "id": d["id"],
            "name": d["name"],
            "icon": d["icon"],
            "tagline": d["tagline"],
            "port": d["port"],
            "online": online,
            "fact": live_fact(d) if online else "",
        })
    return jsonify({"time": time.time(), "dashboards": out})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8091, threaded=True)
