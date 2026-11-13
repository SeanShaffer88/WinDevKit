#!/usr/bin/env python3
"""PathKit from Python (ctypes) — the smallest runnable example.

Long-path and Unicode compatibility layer behind a small C ABI: path normalization, validation and conversion with plain-language errors

Put path_kit.dll (from the PathKit release zip in this repository's
Releases) next to this script and run:

    python pathkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with pa_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/PathKit/include/pathkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "path_kit.dll"))

dll.pa_version.restype = ctypes.c_char_p        # borrowed
dll.pa_free_string.argtypes = [ctypes.c_void_p]
dll.pa_validate.restype = ctypes.c_void_p        # caller-owned


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.pa_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("PathKit version:", dll.pa_version().decode("utf-8"))


def main():
    print_version()
    # A real call: validate a Windows path (pure string check,
    # nothing on disk is touched).
    print(take(dll.pa_validate(b"C:\\Users\\demo\\file.txt")))


if __name__ == "__main__":
    main()
