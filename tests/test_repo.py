"""Repository hygiene: no secrets, no em dashes, example config is sane."""
import subprocess

from conftest import ROOT
from build_ctfd import load_env, validate

DASHES = {chr(0x2014), chr(0x2013)}  # em dash and en dash
TEXT = {".py", ".md", ".html", ".css", ".yml", ".yaml", ".env", ".sh", ".txt", ""}


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return [p for p in out.split("\0") if p]


def repo_files():
    return [ROOT / p for p in tracked_files() if (ROOT / p).suffix in TEXT and (ROOT / p).is_file()]


def test_no_em_or_en_dashes():
    bad = [str(p) for p in repo_files() if DASHES & set(p.read_text())]
    assert not bad, bad


def test_real_config_not_tracked():
    tracked = tracked_files()
    assert "config/flags.env" not in tracked
    assert not any(p.startswith("ctfd/build/") for p in tracked)


def test_spoilers_not_tracked_in_plain_text():
    tracked = tracked_files()
    assert "docs/WALKTHROUGH.md" not in tracked
    assert not any(p.startswith(("solutions/", "staff-unlocked/")) for p in tracked)
    assert "staff/ghost-vector-staff.7z" in tracked


def test_staff_pack_is_encrypted():
    raw = (ROOT / "staff" / "ghost-vector-staff.7z").read_bytes()
    assert raw[:6] == b"7z\xbc\xaf\x27\x1c"
    for word in [b"WALKTHROUGH", b"STAFF_GUIDE", b"AstroSec{", b"solve_all", b"NAV_"]:
        assert word not in raw, word


def test_example_config_valid():
    env = load_env(ROOT / "config" / "flags.example.env")
    assert validate(env) == []
    assert all("CHANGE_ME" in env[k] for k in ["FLAG_G1", "FLAG_G2", "FLAG_G3", "FLAG_FINAL"])
    assert all("CHANGEME" in env[k] for k in ["CODE_V1", "CODE_V2", "CODE_V3", "CODE_V4"])
