"""The generator must be deterministic and every flag must be solvable."""
import json
import os

import pytest
from PIL import Image

from conftest import TEST_ENV, generate, needs_solver, solve

FILES = ["ghost_telemetry.csv", "vector_telemetry.csv", "starmap.png"]


def test_all_files_created(data_dir):
    for f in FILES + [".hashes.json"]:
        assert (data_dir / f).exists(), f


def test_same_seed_same_files(tmp_path):
    a, b = generate(tmp_path / "a"), generate(tmp_path / "b")
    for f in FILES:
        assert (a / f).read_bytes() == (b / f).read_bytes(), f


def test_new_seed_changes_files(tmp_path):
    a, b = generate(tmp_path / "a"), generate(tmp_path / "b", SEED="778")
    for f in FILES:
        assert (a / f).read_bytes() != (b / f).read_bytes(), f


@needs_solver
def test_solver_recovers_every_flag(data_dir):
    got = solve(data_dir)
    assert got["G1"] == TEST_ENV["FLAG_G1"]
    assert got["G2"] == TEST_ENV["FLAG_G2"]
    assert got["G3"] == TEST_ENV["FLAG_G3"]
    assert got["V1"] == TEST_ENV["CODE_V1"]
    assert got["V2"] == TEST_ENV["CODE_V2"]
    assert got["V4"] == TEST_ENV["CODE_V4"]


@needs_solver
@pytest.mark.parametrize("seed", ["1", "42", "1420", "9999", "31337"])
def test_solvable_for_many_seeds(tmp_path, seed):
    d = generate(tmp_path, SEED=seed, FLAG_G1="AstroSec{s33d_" + seed + "}",
                 CODE_V2="NAV_SEED_" + seed)
    got = solve(d)
    assert got["G1"] == "AstroSec{s33d_" + seed + "}"
    assert got["V2"] == "NAV_SEED_" + seed
    assert got["V4"] == TEST_ENV["CODE_V4"]


def test_starmap_hides_text_in_near_black(data_dir):
    img = Image.open(data_dir / "starmap.png").convert("L")
    hist = img.histogram()
    assert hist[1] > 200, "V3 text pixels missing"
    assert sum(hist[2:90]) < 50, "too many mid-grey pixels would give the text away"


def test_no_plaintext_flags_in_player_files(data_dir):
    blob = b"".join((data_dir / f).read_bytes() for f in FILES).decode("latin-1")
    for k, v in TEST_ENV.items():
        if k.startswith(("FLAG_", "CODE_")):
            assert v not in blob, f"{k} leaked in plain text"


def test_hash_store_has_no_plaintext(data_dir):
    raw = (data_dir / ".hashes.json").read_text()
    for k, v in TEST_ENV.items():
        if k.startswith(("FLAG_", "CODE_")):
            assert v not in raw
    h = json.loads(raw)
    assert len(h["phase1"]) == 3 and len(h["markers"]) == 4


def test_marker_frequency_is_unique(data_dir):
    import csv
    rows = list(csv.DictReader(open(data_dir / "vector_telemetry.csv")))
    markers = [r for r in rows if r["Frequency_MHz"] == "1420.400"]
    from collections import Counter
    others = Counter(r["Frequency_MHz"] for r in rows if r["Frequency_MHz"] != "1420.400")
    assert len(markers) > 16
    assert max(others.values()) <= 5, "another frequency repeats like a marker"
