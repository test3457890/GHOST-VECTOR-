"""Shared fixtures for the GHOST VECTOR test suite."""
import hashlib
import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "tools"))

COORD = "GV-TEST-1234"
TEST_ENV = {
    "FLAG_G1": "AstroSec{t3st_p0wer}",
    "FLAG_G2": "AstroSec{t3st_cl0ck}",
    "FLAG_G3": "AstroSec{t3st_th3rmal}",
    "CODE_V1": "NAV_TEST_ONE_1",
    "CODE_V2": "NAV_TEST_TWO_2",
    "CODE_V3": "NAV_TEST_THREE_3",
    "CODE_V4": "NAV_TEST_FOUR_4",
    "FLAG_FINAL": "AstroSec{t3st_f1nal}",
    "PRIZE_KEY_HASH": hashlib.sha256(COORD.encode()).hexdigest(),
    "SEED": "777",
    "SECRET_KEY": "test-secret",
}


def generate(out_dir, **overrides):
    env = {**os.environ, **TEST_ENV, **overrides, "OUTPUT_DIR": str(out_dir)}
    subprocess.run([sys.executable, str(ROOT / "app" / "generator.py")], env=env,
                   check=True, capture_output=True)
    return Path(out_dir)


SOLVER = ROOT / "staff-unlocked" / "solvers" / "solve_all.py"


def _ensure_solver():
    """Unlock the staff pack automatically when STAFF_PACK_PASSWORD is set."""
    if not SOLVER.exists() and os.environ.get("STAFF_PACK_PASSWORD"):
        from staff_vault import unlock
        unlock(password=os.environ["STAFF_PACK_PASSWORD"])
    return SOLVER.exists()


HAVE_SOLVER = _ensure_solver()
needs_solver = pytest.mark.skipif(
    not HAVE_SOLVER, reason="solver is in the encrypted staff pack; set STAFF_PACK_PASSWORD to run")


def solve(data_dir):
    """Run the reference solver and return {'G1': ..., ...}."""
    out = subprocess.run([sys.executable, str(SOLVER), str(data_dir)],
                         capture_output=True, text=True, check=True, cwd=data_dir).stdout
    return dict(line.split(" ", 1) for line in out.strip().splitlines() if " " in line)


@pytest.fixture(scope="session")
def data_dir(tmp_path_factory):
    return generate(tmp_path_factory.mktemp("data"))


def make_client(monkeypatch, data_dir, **overrides):
    env = {**TEST_ENV, "OUTPUT_DIR": str(data_dir), "PHASE2_GATE": "gated", **overrides}
    for k, v in env.items():
        monkeypatch.setenv(k, v)
    import app as app_module
    app_module = importlib.reload(app_module)
    app_module.slow_down = lambda: None  # keep the suite fast
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


@pytest.fixture
def client(monkeypatch, data_dir):
    return make_client(monkeypatch, data_dir)
