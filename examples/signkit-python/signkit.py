#!/usr/bin/env python3
"""SignKit from Python (ctypes) — the smallest runnable example.

Authenticode inspection and verification helpers for PE files, behind a small C ABI

Put sign_kit.dll (from the SignKit release zip in this repository's
Releases) next to this script and run:

    python signkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with sg_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/SignKit/include/signkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "sign_kit.dll"))

dll.sg_version.restype = ctypes.c_char_p        # borrowed
dll.sg_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.sg_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("SignKit version:", dll.sg_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: sg_inspect — its exact
    # signature from signkit.h is quoted at the bottom of this
    # file, and the kit README in kits/SignKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check sg_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from signkit.h:
#   SG_API char *sg_inspect(const char *path);
