#!/usr/bin/env python3
"""RenameKit from Python (ctypes) — the smallest runnable example.

Batch rename and transform engine behind a small C ABI: preview, validate and apply bulk renames with collision detection and rollback

Put rename_kit.dll (from the RenameKit release zip in this repository's
Releases) next to this script and run:

    python renamekit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with rk_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/RenameKit/include/renamekit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "rename_kit.dll"))

dll.rk_version.restype = ctypes.c_char_p        # borrowed
dll.rk_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.rk_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("RenameKit version:", dll.rk_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: rk_preview — its exact
    # signature from renamekit.h is quoted at the bottom of this
    # file, and the kit README in kits/RenameKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check rk_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from renamekit.h:
#   RK_API char *rk_preview(const char *spec_json);
