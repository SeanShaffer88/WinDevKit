#!/usr/bin/env python3
"""ArchiveKit from Python (ctypes) — the smallest runnable example.

Create, list, test and extract ZIP and TAR archives from any language that can call C — zero dependencies, DEFLATE included

Put archive_kit.dll (from the ArchiveKit release zip in this repository's
Releases) next to this script and run:

    python archivekit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with ak_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/ArchiveKit/include/archivekit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "archive_kit.dll"))

dll.ak_version.restype = ctypes.c_char_p        # borrowed
dll.ak_free_string.argtypes = [ctypes.c_void_p]
dll.ak_list_json.restype = ctypes.c_void_p     # caller-owned


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.ak_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("ArchiveKit version:", dll.ak_version().decode("utf-8"))


def main():
    print_version()
    # A real call: build a tiny zip with Python's own zipfile,
    # then let ArchiveKit list it as JSON.
    import tempfile, zipfile
    with tempfile.TemporaryDirectory() as td:
        zp = os.path.join(td, "demo.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr("hello.txt", "hello from the example")
        print(take(dll.ak_list_json(zp.encode("utf-8"))))


if __name__ == "__main__":
    main()
