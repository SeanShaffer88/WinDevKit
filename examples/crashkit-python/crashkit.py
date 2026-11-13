#!/usr/bin/env python3
"""CrashKit from Python (ctypes) — the smallest runnable example.

Crash capture + structured diagnostics for Windows apps: minidumps with context sidecars and a JSON-lines log, behind a small C ABI

Put crashkit.dll (from the CrashKit release zip in this repository's
Releases) next to this script and run:

    python crashkit.py

Strings the DLL returns as char* are caller-owned: copy them out
and free them with ck_free_string, exactly as the header requires. The
version and last-error strings are borrowed — copy, never free.
The full contract is the header: kits/CrashKit/include/crashkit.h.
"""

import ctypes
import os
import sys

if sys.platform != "win32":
    sys.exit("This example loads a Windows DLL and runs on Windows only.")

here = os.path.dirname(os.path.abspath(__file__))
dll = ctypes.CDLL(os.path.join(here, "crashkit.dll"))

dll.ck_version.restype = ctypes.c_char_p        # borrowed
dll.ck_free_string.argtypes = [ctypes.c_void_p]


def take(ptr):
    """Copy a caller-owned string out, then free the original."""
    if not ptr:
        return None
    text = ctypes.cast(ptr, ctypes.c_char_p).value.decode("utf-8")
    dll.ck_free_string(ctypes.c_void_p(ptr))
    return text


def print_version():
    print("CrashKit version:", dll.ck_version().decode("utf-8"))


def main():
    print_version()
    # Your first real call: __declspec — its exact
    # signature from crashkit.h is quoted at the bottom of this
    # file, and the kit README in kits/CrashKit/ shows the input and
    # output shapes. The pattern is the same as above: pass UTF-8
    # (usually JSON), copy the returned string out with take(),
    # and check ck_last_error on failure.


if __name__ == "__main__":
    main()

# Primary entry point, from crashkit.h:
#   CK_API __declspec(dllexport) #elif defined(_WIN32) #define CK_API __declspec(dllimport) #else #define CK_API #endif enum { CK_OK = 0, CK_ERR_INVALID_ARG = 1, CK_ERR_NOT_SUPPORTED = 2, CK_ERR_NOT_INSTALLED = 3, CK_ERR_PLATFORM = 5, CK_ERR_INTERNAL = 6 };
