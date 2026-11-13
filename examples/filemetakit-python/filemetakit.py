#!/usr/bin/env python3
"""FileMetaKit from Python (ctypes) — the smallest runnable example.

File metadata toolkit behind a small C ABI: read, edit and compare metadata across images, audio, video and documents

Put file_meta_kit.dll (from the FileMetaKit release zip in this repository's
Releases) next to this script and run:

    python filemetakit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with fm_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/FileMetaKit/include/filemetakit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "file_meta_kit.dll"))

dll.fm_version.restype = ctypes.c_char_p        # borrowed
dll.fm_free_string.argtypes = [ctypes.c_void_p]
dll.fm_read.restype = ctypes.c_void_p          # caller-owned


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.fm_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("FileMetaKit version:", dll.fm_version().decode("utf-8"))


def main():
    print_version()
    # A real call: read this script's own file metadata as JSON.
    print(take(dll.fm_read(os.path.abspath(__file__).encode("utf-8"))))


if __name__ == "__main__":
    main()
