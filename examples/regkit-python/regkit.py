#!/usr/bin/env python3
"""RegKit from Python (ctypes) — the smallest runnable example.

Registry read/write/list with undo manifests, over a JSON C ABI

Put reg_kit.dll (from the RegKit release zip in this repository's
Releases) next to this script and run:

    python regkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with rg_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/RegKit/include/regkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "reg_kit.dll"))

dll.rg_version.restype = ctypes.c_char_p        # borrowed
dll.rg_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.rg_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("RegKit version:", dll.rg_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: rg_read — its exact
    # signature from regkit.h is quoted at the bottom of this
    # file, and the kit README in kits/RegKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check rg_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from regkit.h:
#   RG_API char *rg_read(const char *spec_json);
