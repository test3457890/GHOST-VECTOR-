#!/usr/bin/env python3
"""Lock and unlock the encrypted GHOST VECTOR staff pack.

The staff pack holds everything players must not see: the walkthrough, the
reference solver, the judge guide, the slate card, a tested flag set and a
ready-to-import CTFd pack. It is stored in the repo ONLY as an AES-256
encrypted 7z archive with encrypted file names:

    staff/ghost-vector-staff.7z

Usage:
    python3 tools/staff_vault.py unlock          # -> staff-unlocked/ (git ignored)
    python3 tools/staff_vault.py lock            # staff-unlocked/ -> staff/ghost-vector-staff.7z
    python3 tools/staff_vault.py lock --new-password
    python3 tools/staff_vault.py check           # verify the password without extracting

The password is read from STAFF_PACK_PASSWORD or asked for (hidden input).
No Python? Open the .7z with 7-Zip (Windows), Keka (macOS) or p7zip (Linux).

Needs: pip install py7zr
"""

import argparse
import getpass
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT / "staff" / "ghost-vector-staff.7z"
UNLOCKED = ROOT / "staff-unlocked"


def need_py7zr():
    try:
        import py7zr  # noqa: F401
        return py7zr
    except ImportError:
        sys.exit("py7zr is not installed. Run: pip install py7zr")


def get_password(confirm=False):
    pw = os.environ.get("STAFF_PACK_PASSWORD")
    if pw:
        return pw
    pw = getpass.getpass("Staff pack password: ")
    if confirm:
        if len(pw) < 12:
            sys.exit("Use at least 12 characters.")
        if getpass.getpass("Repeat password: ") != pw:
            sys.exit("Passwords did not match. Nothing changed.")
    return pw


def unlock(dest=UNLOCKED, password=None):
    py7zr = need_py7zr()
    if not ARCHIVE.exists():
        sys.exit(f"{ARCHIVE} not found.")
    password = password or get_password()
    tmp = dest.with_name(dest.name + ".partial")
    if tmp.exists():
        shutil.rmtree(tmp)
    try:
        with py7zr.SevenZipFile(ARCHIVE, "r", password=password) as z:
            z.extractall(path=tmp)
    except Exception as e:  # wrong password raises a decompression/CRC error
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(f"Could not unlock the staff pack (wrong password?): {type(e).__name__}")
    # Only replace an existing unlocked copy once extraction fully succeeded.
    if dest.exists():
        shutil.rmtree(dest)
    tmp.rename(dest)
    print(f"Unlocked to {dest}. It is git ignored. Run 'lock' after editing.")
    return dest


def lock(src=UNLOCKED, new_password=False):
    py7zr = need_py7zr()
    if not src.exists():
        sys.exit(f"{src} not found. Run 'unlock' first.")
    password = get_password(confirm=new_password)
    ARCHIVE.parent.mkdir(exist_ok=True)
    tmp = ARCHIVE.with_suffix(".tmp")
    with py7zr.SevenZipFile(tmp, "w", password=password, header_encryption=True,
                            filters=[{"id": py7zr.FILTER_LZMA2, "preset": 9},
                                     {"id": py7zr.FILTER_CRYPTO_AES256_SHA256}]) as z:
        for p in sorted(src.rglob("*")):
            if p.is_file():
                z.write(p, arcname=str(p.relative_to(src)))
    tmp.replace(ARCHIVE)
    print(f"Locked {src} into {ARCHIVE}.")
    print("Delete staff-unlocked/ when you are done, then commit staff/ghost-vector-staff.7z.")


def check():
    py7zr = need_py7zr()
    try:
        with py7zr.SevenZipFile(ARCHIVE, "r", password=get_password()) as z:
            names = z.getnames()
            ok = z.test()
    except Exception as e:
        sys.exit(f"Password check failed (wrong password?): {type(e).__name__}")
    if ok is False:
        sys.exit("Archive test failed.")
    print(f"Password OK. {len(names)} entries.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["unlock", "lock", "check"])
    ap.add_argument("--new-password", action="store_true", help="set a new password when locking")
    a = ap.parse_args()
    {"unlock": unlock, "check": check}.get(a.action, lambda: lock(new_password=a.new_password))()


if __name__ == "__main__":
    main()
