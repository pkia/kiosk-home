import app

client = app.app.test_client()


def test_index_serves_page():
    r = client.get("/")
    assert r.status_code == 200
    assert b"Kiosk Home" in r.data


def test_api_dashboards_lists_both(monkeypatch):
    monkeypatch.setattr(app, "port_open", lambda port, host="127.0.0.1": True)
    monkeypatch.setattr(app, "live_fact", lambda d: "fact")
    j = client.get("/api/dashboards").get_json()
    ids = [d["id"] for d in j["dashboards"]]
    assert ids == ["maritime", "cs2"]
    for d in j["dashboards"]:
        assert d["online"] is True
        assert d["port"] in (8000, 8001)
        assert d["icon"] and d["name"] and d["tagline"]


def test_api_dashboards_when_services_down(monkeypatch):
    """Every dashboard down still answers, marked offline with no fact."""
    monkeypatch.setattr(app, "port_open", lambda port, host="127.0.0.1": False)
    j = client.get("/api/dashboards").get_json()
    assert len(j["dashboards"]) == 2
    assert all(d["online"] is False and d["fact"] == "" for d in j["dashboards"])


def test_live_fact_is_best_effort(monkeypatch):
    """A dead upstream API (None from _get_json) yields an empty fact."""
    monkeypatch.setattr(app, "_get_json", lambda url: None)
    for d in app.DASHBOARDS:
        assert app.live_fact(d) == ""


def test_live_fact_maritime_ship_count(monkeypatch):
    monkeypatch.setattr(app, "_get_json",
                        lambda url: {"count": 12, "ships": []})
    d = next(x for x in app.DASHBOARDS if x["id"] == "maritime")
    assert "12 ships" in app.live_fact(d)


def test_live_fact_cs2_next_match(monkeypatch):
    monkeypatch.setattr(app, "_get_json", lambda url: {
        "live": [], "upcoming": [{
            "start_ts": 1787320500,
            "team1": {"name": "Legacy"},
            "team2": {"name": "Falcons"},
        }],
    })
    d = next(x for x in app.DASHBOARDS if x["id"] == "cs2")
    fact = app.live_fact(d)
    assert "Legacy v Falcons" in fact
