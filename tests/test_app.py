"""The recovery terminal: routes, gating, final stage and security checks."""
from conftest import COORD, TEST_ENV, make_client


def unlock(c):
    return c.post("/api/uplink", json={"flag": TEST_ENV["FLAG_G2"]}).get_json()


CODES = [TEST_ENV[k] for k in ["CODE_V1", "CODE_V2", "CODE_V3", "CODE_V4"]]


def test_health_and_pages(client):
    assert client.get("/health").get_json() == {"status": "ok"}
    assert client.get("/").status_code == 200
    assert b"GHOST VECTOR" in client.get("/").data


def test_phase1_download(client):
    r = client.get("/download/ghost_telemetry.csv")
    assert r.status_code == 200 and r.data.startswith(b"Timestamp")


def test_phase2_locked_when_gated(client):
    assert client.get("/download/starmap.png").status_code == 403
    assert client.get("/vector").status_code == 302
    assert client.get("/handshake").status_code == 302
    assert client.post("/api/handshake", json={"codes": CODES}).status_code == 403


def test_wrong_uplink_rejected(client):
    assert unlock_wrong(client)["ok"] is False


def unlock_wrong(c):
    return c.post("/api/uplink", json={"flag": "AstroSec{nope}"}).get_json()


def test_uplink_case_insensitive_and_unlocks(client):
    r = client.post("/api/uplink", json={"flag": TEST_ENV["FLAG_G3"].upper()}).get_json()
    assert r["ok"] is True
    assert client.get("/vector").status_code == 200
    assert client.get("/download/starmap.png").status_code == 200
    assert client.get("/download/vector_telemetry.csv").status_code == 200


def test_open_gate(monkeypatch, data_dir):
    c = make_client(monkeypatch, data_dir, PHASE2_GATE="open")
    assert c.get("/vector").status_code == 200
    assert c.get("/download/starmap.png").status_code == 200


def test_hash_file_and_traversal_blocked(client):
    unlock(client)
    for path in ["/download/.hashes.json", "/download/..%2Fapp.py",
                 "/download/../app.py", "/download/%2e%2e%2fgenerator.py"]:
        assert client.get(path).status_code in (403, 404), path


def test_handshake_partial(client):
    unlock(client)
    r = client.post("/api/handshake", json={"codes": CODES[:3] + ["WRONG"]}).get_json()
    assert r["ok"] is False and r["results"] == [True, True, True, False]


def test_handshake_needs_four(client):
    unlock(client)
    assert client.post("/api/handshake", json={"codes": CODES[:2]}).get_json()["ok"] is False
    assert client.post("/api/handshake", json={"codes": "x"}).get_json()["ok"] is False


def test_handshake_accepts_wrapper_and_case(client):
    unlock(client)
    codes = ["AstroSec{" + CODES[0] + "}", CODES[1].lower(), " " + CODES[2] + " ", CODES[3]]
    assert client.post("/api/handshake", json={"codes": codes}).get_json()["ok"] is True


def test_transmit_requires_markers(client):
    unlock(client)
    assert client.post("/api/transmit", json={"coordinate": COORD}).status_code == 403


def test_full_final_stage_reveals_flag(client):
    unlock(client)
    assert client.post("/api/handshake", json={"codes": CODES}).get_json()["ok"]
    bad = client.post("/api/transmit", json={"coordinate": "GV-NOPE-0000"}).get_json()
    assert bad["ok"] is False and "flag" not in bad
    good = client.post("/api/transmit", json={"coordinate": COORD.lower()}).get_json()
    assert good["ok"] is True and good["flag"] == TEST_ENV["FLAG_FINAL"]


def test_transmitter_offline_without_hash(monkeypatch, data_dir):
    c = make_client(monkeypatch, data_dir, PRIZE_KEY_HASH="")
    unlock(c)
    c.post("/api/handshake", json={"codes": CODES})
    r = c.post("/api/transmit", json={"coordinate": COORD}).get_json()
    assert r["ok"] is False and "OFFLINE" in r["message"]


def test_judge_only_mode_without_final_flag(monkeypatch, data_dir):
    c = make_client(monkeypatch, data_dir, FLAG_FINAL="")
    unlock(c)
    c.post("/api/handshake", json={"codes": CODES})
    r = c.post("/api/transmit", json={"coordinate": COORD}).get_json()
    assert r["ok"] is True and r["flag"] is None and "judge" in r["message"]


def test_no_flags_in_any_page(client):
    unlock(client)
    html = b"".join(client.get(p).data for p in ["/", "/vector", "/handshake"]).decode()
    for k, v in TEST_ENV.items():
        if k.startswith(("FLAG_", "CODE_")):
            assert v not in html
