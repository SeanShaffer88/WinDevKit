#!/usr/bin/env python3
"""SettingsKit from Python (ctypes) in about forty lines.

Put settings_kit.dll (from the SettingsKit release zip in this
repository's Releases) next to this script and run:

    python settingskit.py

The pattern to notice: reading with a default never writes the
default into the file. Only values you set are stored, so changing
a default in your next release cannot silently change the meaning
of files already on your users' disks.

Strings returned by the DLL are caller-owned: every char* result is
copied out and then freed with sk_free_string, exactly as the header
requires. Version and last-error strings are borrowed - copied,
never freed.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "settings_kit.dll"))

dll.sk_version.restype = ctypes.c_char_p          # borrowed
dll.sk_last_error.restype = ctypes.c_char_p       # borrowed
dll.sk_get_string.restype = ctypes.c_void_p       # caller-owned
dll.sk_to_json.restype = ctypes.c_void_p          # caller-owned


def take_string(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.sk_free_string(ctypes.c_void_p(ptr))
    return text


def check(rc, what):
    if rc != 0:
        err = dll.sk_last_error().decode("utf-8")
        raise RuntimeError(f"{what} failed: {err} (code {rc})")


def main():
    print(f"SettingsKit version: {dll.sk_version().decode('utf-8')}")

    doc = ctypes.c_void_p()
    # Schema 1, no flags, no migrations needed for a fresh file.
    check(dll.sk_open(b"settings.json", 1, 0, ctypes.byref(doc)), "open")
    try:
        check(dll.sk_set_string(doc, b"downloads.preset", b"720p"), "set preset")
        check(dll.sk_set_i64(doc, b"ui.width", 1280), "set width")
        check(dll.sk_save(doc), "save")  # atomic replace on disk
        print("file contents:", take_string(dll.sk_to_json(doc)))
    finally:
        dll.sk_close(doc)


if __name__ == "__main__":
    main()
