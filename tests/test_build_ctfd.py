"""The CTFd pack builder: structure, flags, files, hints and prerequisites."""
import subprocess
import sys

import pytest
import yaml

from conftest import ROOT, TEST_ENV, generate
from build_ctfd import challenges, hint_costs, validate

NAMES = ["G1 Power Loss", "G2 Clock Drift", "G3 Thermal Whisper", "V1 SYNC",
         "V2 VECTOR", "V3 COORD", "V4 PRIME", "FINAL Bring It Home"]


@pytest.fixture(scope="module")
def pack(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("pack")
    env_file = tmp / "flags.env"
    env_file.write_text("\n".join(f"{k}={v}" for k, v in TEST_ENV.items()))
    out = tmp / "build"
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_ctfd.py"),
                    "--env", str(env_file), "--out", str(out)], check=True, capture_output=True)
    ymls = sorted(out.glob("*/challenge.yml"))
    return out, {yaml.safe_load(p.read_text())["name"]: (p.parent, yaml.safe_load(p.read_text()))
                 for p in ymls}


def test_eight_challenges_in_order(pack):
    out, chals = pack
    assert list(chals) == NAMES
    assert (out / "MANUAL_ENTRY.md").exists()
    assert not (out / "_data").exists()


def test_total_points(pack):
    assert sum(c["value"] for _, c in pack[1].values()) == 2050


def test_flags_match_config(pack):
    _, c = pack
    assert c["G1 Power Loss"][1]["flags"][0]["content"] == TEST_ENV["FLAG_G1"]
    v1 = [f["content"] for f in c["V1 SYNC"][1]["flags"]]
    assert v1 == [TEST_ENV["CODE_V1"], "AstroSec{" + TEST_ENV["CODE_V1"] + "}"]
    assert c["FINAL Bring It Home"][1]["flags"][0]["content"] == TEST_ENV["FLAG_FINAL"]
    for _, y in c.values():
        for f in y.get("flags", []):
            assert f["type"] == "static" and f["data"] == "case_insensitive"


def test_prerequisites(pack):
    _, c = pack
    for n in NAMES[:3]:
        assert "requirements" not in c[n][1]
    for n in NAMES[3:7]:
        assert c[n][1]["requirements"] == ["G1 Power Loss"]
    assert c["FINAL Bring It Home"][1]["requirements"] == NAMES[3:7]


def test_hints_and_costs(pack):
    _, c = pack
    for n in NAMES[:7]:
        h = c[n][1]["hints"]
        assert len(h) == 3 and [x["cost"] for x in h] == hint_costs(c[n][1]["value"])
        assert h[0]["cost"] == 0
    assert "hints" not in c["FINAL Bring It Home"][1]


def test_files_identical_to_terminal(pack, tmp_path):
    _, c = pack
    term = generate(tmp_path)
    for n, (d, y) in c.items():
        for f in y.get("files", []):
            assert (d / f).read_bytes() == (term / f.split("/")[-1]).read_bytes(), (n, f)


def test_final_links_terminal(pack):
    assert c_final(pack)["connection_info"].endswith("/handshake")


def c_final(pack):
    return pack[1]["FINAL Bring It Home"][1]


def test_dynamic_mode(tmp_path):
    env_file = tmp_path / "flags.env"
    env_file.write_text("\n".join(f"{k}={v}" for k, v in TEST_ENV.items()))
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_ctfd.py"), "--env", str(env_file),
                    "--out", str(tmp_path / "b"), "--dynamic"], check=True, capture_output=True)
    y = yaml.safe_load((tmp_path / "b" / "07-v4-prime" / "challenge.yml").read_text())
    assert y["type"] == "dynamic" and y["extra"]["initial"] == 350 and "value" not in y


def test_validate_catches_bad_config():
    bad = dict(TEST_ENV, CODE_V2="NAV-BAD!", FLAG_G1="has space")
    msgs = " ".join(validate(bad))
    assert "CODE_V2" in msgs and "FLAG_G1" in msgs
    assert validate(TEST_ENV) == []


def test_missing_flag_without_final_still_builds():
    names = [c["name"] for c in challenges(dict(TEST_ENV, FLAG_FINAL=""))]
    assert names == NAMES
