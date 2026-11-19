"""Repository hygiene: no secrets, no em dashes, example config is sane."""
import subprocess

from conftest import ROOT
from build_ctfd import load_env, validate

TEXT = {".py", ".md", ".html", ".css", ".yml", ".yaml", ".env", ".sh", ".txt", ""}


def repo_files():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    return [ROOT / p for p in out.split() if (ROOT / p).suffix in TEXT and (ROOT / p).is_file()]


def test_no_em_or_en_dashes():
    bad = [str(p) for p in repo_files() if "—" in p.read_text() or "–" in p.read_text()]
    assert not bad, bad


def test_real_config_not_tracked():
    tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
    assert "config/flags.env" not in tracked.split()
    assert "ctfd/build" not in tracked


def test_example_config_valid():
    env = load_env(ROOT / "config" / "flags.example.env")
    assert validate(env) == []
    assert all("CHANGE_ME" in env[k] for k in ["FLAG_G1", "FLAG_G2", "FLAG_G3", "FLAG_FINAL"])
